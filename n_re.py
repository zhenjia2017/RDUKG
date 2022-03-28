import torch

# 设置随机数种子
SEED = 1
torch.manual_seed(SEED)
torch.cuda.manual_seed(SEED)
torch.cuda.manual_seed_all(SEED)

import itertools
import torch.utils.data as Data
from transformers import BertModel

import z_utils
from a_config import re_cfg


MODEL_NAME = "re.mdl"
BATCH_SIZE = 256


class TextData(Data.Dataset):
    def __init__(self, data):
        super(TextData, self).__init__()
        self.data = data

    def __getitem__(self, index):
        return self.data[index]

    def __len__(self):
        return len(self.data)


def generate_triple(ids, data, sub, obj, entity_tag2ids):
    parsed = {}
    parsed["ids"] = ids
    parsed["entity"] = sub[0] + "-" + obj[0]
    parsed["length"] = torch.tensor(len(data["text"]), dtype=torch.long)
    parsed["index"] = torch.tensor(data["index"], dtype=torch.long)
    # 主语和宾语
    parsed["sub"] = torch.tensor(entity_tag2ids[sub[1]["type"]], dtype=torch.long)
    parsed["obj"] = torch.tensor(entity_tag2ids[obj[1]["type"]], dtype=torch.long)
    # 该字与主语的相对位置
    parsed["sub_pos"] = torch.zeros(re_cfg["max_length"], dtype=torch.long)
    for i in range(parsed["length"]):
        parsed["sub_pos"][i] = i - sub[1]["start"] + 65
    parsed["sub_pos"][sub[1]["start"]: sub[1]["end"]] = 1
    # 该字与宾语的相对位置
    parsed["obj_pos"] = torch.zeros(re_cfg["max_length"], dtype=torch.long)
    for i in range(parsed["length"]):
        parsed["obj_pos"][i] = i - obj[1]["start"] + 65
    parsed["obj_pos"][obj[1]["start"]: obj[1]["end"]] = 1
    # 生成掩码，用于按照实体位置分隔文本
    mask1 = torch.zeros(re_cfg["max_length"], dtype=torch.long)
    mask1[: max([sub[1]["end"], obj[1]["end"]])] = 1
    mask2 = torch.zeros(re_cfg["max_length"], dtype=torch.long)
    mask2[min([sub[1]["start"], obj[1]["start"]]): parsed["length"]] = 1
    parsed["mask1"] = mask1
    parsed["mask2"] = mask2
    return parsed


def parse_data():
    rel_info = dict([(k, v) for k, v in z_utils.load_pkl(re_cfg["extracted_data"]).items() if k != "data"])
    raw_data = z_utils.read_json_file(re_cfg["ner_file"])
    data = {}
    for ids, tmp in enumerate(raw_data):
        folder = tmp["folder"]
        if folder not in rel_info["rel_filter"]:
            continue
        if folder not in data:
            print("处理：%s。" %(folder))
            data[folder] = []
        entity = list(tmp["entity"].items())
        for (sub, obj) in itertools.product(entity, entity):
            if sub[0] == obj[0] or (sub[1]["type"], obj[1]["type"]) not in rel_info["rel_filter"][folder]:
                continue
            parsed = generate_triple(ids, tmp, sub, obj, rel_info["entity_tag2ids"][folder])
            data[folder].append(parsed)
        del tmp["index"]
    return rel_info, raw_data, data


data = None
if __name__ == "__main__":
    dev = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
    # 加载数据
    rel_info, raw_data, data = parse_data()
    # 加载模型
    all_model = z_utils.load_pkl(re_cfg["model_path"] + MODEL_NAME)
    for _, model in all_model.items():
        model["model"].to(dev)
        model["model"].eval()
    # 加载bert
    bert = BertModel.from_pretrained(re_cfg["bert_path"])
    bert.to(dev)
    bert.eval()
    # RE
    parsed_data = []
    with torch.no_grad():
        for folder, cur_data in data.items():
            cur_data = torch.utils.data.DataLoader(
                dataset=TextData(cur_data),
                batch_size=BATCH_SIZE,
                shuffle=False,
            )
            for batch_data in cur_data:
                length = batch_data["length"].to(dev)
                word2vec = bert(batch_data["index"].to(dev))[0][:, 1: -1, :]
                sub = batch_data["sub"].to(dev)
                obj = batch_data["obj"].to(dev)
                sub_pos = batch_data["sub_pos"].to(dev)
                obj_pos = batch_data["obj_pos"].to(dev)
                m1 = batch_data["mask1"].to(dev)
                m2 = batch_data["mask2"].to(dev)
                pred = all_model[folder]["model"](length, word2vec, sub, obj, sub_pos, obj_pos, m1, m2)
                # 解码
                for i in range(len(batch_data["ids"])):
                    ids = batch_data["ids"][i]
                    entity = batch_data["entity"][i].split("-")
                    relation = rel_info["relation_ids2tag"][folder][int(pred[i])]
                    if relation != "无关系":
                        raw_data[ids]["relation"]["R"+str(len(raw_data[ids]["relation"])+1)] = {
                            "type": relation,
                            "subject": entity[0],
                            "object": entity[1],
                        }
            print("%s 处理完成。" %(folder))
    z_utils.write_json_file(raw_data, re_cfg["re_file"])
