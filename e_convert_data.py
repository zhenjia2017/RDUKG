import os
import itertools
import random
import torch
from transformers import BertTokenizer, BertModel

import z_utils
from a_config import convert_data_cfg


# 设置随机数种子
SEED = 1
random.seed(SEED)
torch.manual_seed(SEED)


# 加载并按照训练集和测试集划分数据
def load_data():
    extracted_data = z_utils.read_json_file(convert_data_cfg["extracted_file"])
    texts = []
    parsed_data = {}
    for data in extracted_data:
        texts.append(data["text"])
        if data["folder"] not in parsed_data:
            parsed_data[data["folder"]] = {"train": [], "test": []}
        parsed_data[data["folder"]][data["dataset"]].append(data)
    return texts, parsed_data


# 加载语句的bert嵌入
def load_text_emb(path, texts):
    text_emb = {}
    if os.path.exists(path):
        text_emb = z_utils.load_pkl(path)
    else:
        # 加载bert
        tokenizer = BertTokenizer.from_pretrained(convert_data_cfg["bert_path"])
        bert = BertModel.from_pretrained(convert_data_cfg["bert_path"])
        bert.eval()
        with torch.no_grad():
            for text in texts:
                text_tokens = [x for x in text]
                text_tokens += ["[PAD]"] * (convert_data_cfg["max_length"] - len(text))
                text_tokens = ["[CLS]"] + text_tokens + ["[SEP]"]
                indexed_tokens = tokenizer.convert_tokens_to_ids(text_tokens)
                indexed_tensor = torch.tensor([indexed_tokens])
                bert_emb = bert(indexed_tensor)[0][0][1: -1]
                text_emb[z_utils.calculate_md5(text)] = bert_emb
        z_utils.save_pkl(path, text_emb)
    return text_emb


# 加载词向量并转换为“类别-字：词向量列表”的形式
def load_char2word(path):
    char2word = {}
    if os.path.exists(path):
        char2word = z_utils.load_pkl(path)
    else:
        word2vec = {}
        for _, file in convert_data_cfg["word2vec"].items():
            with open(file, mode="r", encoding="utf-8") as f:
                for line in f:
                    data = line.split()
                    assert len(data) == 51
                    word2vec[data[0]] = [float(x) for x in data[1:]]
        for word, vec in word2vec.items():
            if len(word) == 1:
                char2word["S-" + word] = [vec]
            else:
                if "B-" + word[0] not in char2word:
                    char2word["B-" + word[0]] = []
                char2word["B-" + word[0]].append(vec)
                for char in word[1: -1]:
                    if "M-" + char not in char2word:
                        char2word["M-" + char] = []
                    char2word["M-" + char].append(vec)
                if "E-" + word[-1] not in char2word:
                    char2word["E-" + word[-1]] = []
                char2word["E-" + word[-1]].append(vec)
        z_utils.save_pkl(path, char2word)
    return char2word


# 计算词汇向量
def calculate_lexicon(char2word, lexicon_table, text):
    text_vec = []
    for char in text:
        if char not in lexicon_table:
            char_vec = [torch.zeros(50, dtype=torch.float)] * 4
            for i, x in enumerate(["S-", "B-", "M-", "E-"]):
                if x+char in char2word:
                    char_vec[i] = torch.tensor(char2word[x+char], dtype=torch.float).mean(dim=0)
            lexicon_table[char] = torch.cat(char_vec, dim=0)
        text_vec.append(lexicon_table[char])
    text_vec += [torch.zeros(200, dtype=torch.float)] * (convert_data_cfg["max_length"] - len(text))
    text_vec = torch.stack(text_vec, dim=0)
    return text_vec


# 生成文本的实体标签
def generate_ner_label(tag2ids, entity):
    entity_tags = torch.tensor([0] * convert_data_cfg["max_length"], dtype=torch.long)
    for _, en in entity.items():
        B_ids = tag2ids["B-" + en["type"]]
        I_ids = tag2ids["I-" + en["type"]]
        entity_tags[en["start"]] = B_ids
        entity_tags[en["start"] + 1: en["end"]] = I_ids
    return entity_tags


# 处理实体
def convert_ner_data(text_emb, parsed_data):
    char2word = load_char2word(convert_data_cfg["char2word"])
    # 生成实体标签
    tag2ids = {}
    ids2tag = {}
    for key in convert_data_cfg["annotation"]:
        folder = z_utils.convert_to_pinyin(key)
        tag2ids[folder] = {"O": 0}
        ids2tag[folder] = {0: "O"}
        for i, entity in enumerate(convert_data_cfg["annotation"][key]["entity"]):
            tag2ids[folder]["B-" + entity] = 2 * i + 1
            tag2ids[folder]["I-" + entity] = 2 * i + 2
            ids2tag[folder][2 * i + 1] = "B-" + entity
            ids2tag[folder][2 * i + 2] = "I-" + entity
    # 最终数据
    converted_data = {"tag2ids": tag2ids, "ids2tag": ids2tag, "data": {}}
    # 词汇表
    lexicon_table = {}
    for folder in parsed_data:
        converted_data["data"][folder] = {"train": [], "test": []}
        for dataset in parsed_data[folder]:
            for data in parsed_data[folder][dataset]:
                tmp_converted_data = {}
                tmp_converted_data["text"] = data["text"]
                tmp_converted_data["length"] = torch.tensor(len(data["text"]), dtype=torch.long)
                tmp_converted_data["word2vec"] = text_emb[z_utils.calculate_md5(data["text"])]
                tmp_converted_data["lexicon"] = calculate_lexicon(char2word, lexicon_table, data["text"])
                tmp_converted_data["label"] = generate_ner_label(tag2ids[folder], data["entity"])
                tmp_converted_data["mask"] = torch.tensor([0] * convert_data_cfg["max_length"], dtype=torch.long)
                tmp_converted_data["mask"][: len(data["text"])] = 1
                converted_data["data"][folder][dataset].append(tmp_converted_data)
        print("%s 处理完成。" %(folder))
    return converted_data



# 实体两两组合生成数据
def generate_re_label(ft, entity_tag2ids, relation_tag2ids, data):
    parsed_data = []
    entity = list(data["entity"].items())
    relation = dict([(r["subject"] + "-" + r["object"], r["type"]) for _, r in data["relation"].items()])
    for (en_1, en_2) in itertools.product(entity, entity):
        if en_1[0] == en_2[0] or (en_1[1]["type"], en_2[1]["type"]) not in ft:
            continue
        cur_data = {}
        # 语句
        cur_data["text"] = data["text"]
        # 语句长度
        cur_data["length"] = torch.tensor(len(data["text"]), dtype=torch.long)
        # 词向量
        cur_data["word2vec"] = text_emb[z_utils.calculate_md5(data["text"])]
        # 主语和宾语类型
        cur_data["subject"] = entity_tag2ids[en_1[1]["type"]]
        cur_data["object"] = entity_tag2ids[en_2[1]["type"]]
        # 该字与主语的相对位置
        cur_data["sub_pos"] = torch.tensor([0] * convert_data_cfg["max_length"], dtype=torch.long)
        for i in range(len(data["text"])):
            cur_data["sub_pos"][i] = i - en_1[1]["start"] + 65
        cur_data["sub_pos"][en_1[1]["start"]: en_1[1]["end"]] = 1
        # 该字与宾语的相对位置
        cur_data["obj_pos"] = torch.tensor([0] * convert_data_cfg["max_length"], dtype=torch.long)
        for i in range(len(data["text"])):
            cur_data["obj_pos"][i] = i - en_2[1]["start"] + 65
        cur_data["obj_pos"][en_2[1]["start"]: en_2[1]["end"]] = 1
        # 关系
        key = en_1[0] + "-" + en_2[0]
        cur_data["relation"] = torch.tensor(relation_tag2ids[relation[key]] if key in relation else 0, dtype=torch.long)
        # 分段掩码，用于按照实体位置分隔文本
        cur_data["mask1"] = torch.tensor([0] * convert_data_cfg["max_length"], dtype=torch.long)
        cur_data["mask1"][: max([en_1[1]["end"], en_2[1]["end"]])] = 1
        cur_data["mask2"] = torch.tensor([0] * convert_data_cfg["max_length"], dtype=torch.long)
        cur_data["mask2"][min([en_1[1]["start"], en_2[1]["start"]]): cur_data["length"]] = 1
        # 添加处理后的数据
        parsed_data.append(cur_data)
    return parsed_data


# 处理关系
def convert_re_data(text_emb, parsed_data):
    annotation = convert_data_cfg["annotation"]
    # 根据实体类别过滤不可能存在关系的实体对
    rel_filter = {}
    # 生成实体标签和关系标签
    entity_tag2ids = {}
    entity_ids2tag = {}
    relation_tag2ids = {}
    relation_ids2tag = {}
    for key in annotation:
        # 跳过没有关系的数据集
        if len(annotation[key]["relation"]) == 0:
            continue
        folder = z_utils.convert_to_pinyin(key)
        # 实体
        entity_tag2ids[folder] = {}
        entity_ids2tag[folder] = {}
        for i, entity in enumerate(annotation[key]["entity"]):
            entity_tag2ids[folder][entity] = i
            entity_ids2tag[folder][i] = entity
        # 关系
        rel_filter[folder] = []
        relation_tag2ids[folder] = {"无关系": 0}
        relation_ids2tag[folder] = {0: "无关系"}
        for i, (sub, relation, obj) in enumerate(annotation[key]["relation"]):
            rel_filter[folder] += [m for m in itertools.product(sub.split("|"), obj.split("|"))]
            relation_tag2ids[folder][relation] = i + 1
            relation_ids2tag[folder][i + 1] = relation
    # 最终数据
    converted_data = {
        "rel_filter": rel_filter,
        "entity_tag2ids": entity_tag2ids, "entity_ids2tag": entity_ids2tag,
        "relation_tag2ids": relation_tag2ids, "relation_ids2tag": relation_ids2tag,
        "data": {},
    }
    for folder in parsed_data:
        # 跳过没有关系的数据集
        if folder not in entity_tag2ids:
            continue
        converted_data["data"][folder] = {"train": [], "test": []}
        for dataset in parsed_data[folder]:
            for data in parsed_data[folder][dataset]:
                converted_data["data"][folder][dataset] += generate_re_label(
                    rel_filter[folder],
                    entity_tag2ids[folder], relation_tag2ids[folder], data
                )
            random.shuffle(converted_data["data"][folder][dataset])
        print("%s 处理完成。" %(folder))
    return converted_data


if __name__ == "__main__":
    texts, parsed_data = load_data()
    text_emb = load_text_emb(convert_data_cfg["text_emb"], texts)
    # 实体
    print("----------处理实体----------")
    ner_data = convert_ner_data(text_emb, parsed_data)
    z_utils.save_pkl(convert_data_cfg["ner_data"], ner_data)
    # 关系
    print("----------处理关系----------")
    re_data = convert_re_data(text_emb, parsed_data)
    z_utils.save_pkl(convert_data_cfg["re_data"], re_data)
