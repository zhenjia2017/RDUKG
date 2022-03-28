import torch

# 设置随机数种子
SEED = 1
torch.manual_seed(SEED)
torch.cuda.manual_seed(SEED)
torch.cuda.manual_seed_all(SEED)

import torch.utils.data as Data
from transformers import BertModel

import z_utils
from a_config import ner_cfg


MODEL_NAME = "ner.mdl"
BATCH_SIZE = 256


class TextData(Data.Dataset):
    def __init__(self, data):
        super(TextData, self).__init__()
        self.data = data

    def __getitem__(self, index):
        data = self.data[index]
        mask = torch.zeros(ner_cfg["max_length"], dtype=torch.long)
        mask[: len(data["text"])] = 1
        return {
            "text": data["text"],
            "length": torch.tensor(len(data["text"]), dtype=torch.long),
            "index": torch.tensor(data["index"], dtype=torch.long),
            "mask": mask,
            "file": "-".join(data["file"]),
        }

    def __len__(self):
        return len(self.data)


def decode_ner(ids, ids2tag):
    entity = []
    idx = 0
    while idx < len(ids):
        if "B-" in ids2tag[ids[idx]]:
            idx_end = idx + 1
            while idx_end < len(ids):
                if ids2tag[ids[idx_end]] == "I-" + ids2tag[ids[idx]].split("-")[1]:
                    idx_end += 1
                else:
                    break
            entity.append({
                "begin": idx,
                "end": idx_end,
                "type": ids2tag[ids[idx]].split("-")[1],
            })
            idx = idx_end
        else:
            idx += 1
    return entity


if __name__ == "__main__":
    out_data = []
    dev = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
    # 加载数据
    data = {}
    for tmp in z_utils.read_json_file(ner_cfg["unlabelled_file"]):
        if tmp["folder"] not in data:
            data[tmp["folder"]] = []
        data[tmp["folder"]].append(tmp)
    # 加载实体标签
    ids2tag = z_utils.load_pkl(ner_cfg["extracted_data"])["ids2tag"]
    # 加载模型
    all_model = z_utils.load_pkl(ner_cfg["model_path"] + MODEL_NAME)
    for _, model in all_model.items():
        model["model"].to(dev)
        model["model"].eval()
    # 加载bert
    bert = BertModel.from_pretrained(ner_cfg["bert_path"])
    bert.to(dev)
    bert.eval()
    # NER
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
                mask = batch_data["mask"].to(dev)
                pred = all_model[folder]["model"](length, word2vec, mask)
                # 解码
                for i in range(len(batch_data["text"])):
                    text = batch_data["text"][i]
                    index = batch_data["index"][i]
                    file = batch_data["file"][i]
                    entity = decode_ner(pred[i], ids2tag[folder])
                    out_data.append({
                        "text": text,
                        "index": index.numpy().tolist(),
                        "file": file.split("-"),
                        "entity": dict([("T"+str(i+1), {
                                "type": x["type"],
                                "start": x["begin"],
                                "end": x["end"],
                                "value": text[x["begin"]: x["end"]],
                            })for i, x in enumerate(entity)]),
                        "relation": {},
                        "folder": folder,
                    })
            print("%s 处理完成。" %(folder))
    z_utils.write_json_file(out_data, ner_cfg["ner_file"])
