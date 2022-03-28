import math
import os
import matplotlib.pyplot as plt

plt.rcParams.update({'figure.max_open_warning': 0})

import z_utils
from a_config import figure_cfg


# 过滤文件
def file_filter(file):
    flt = ["4", "8", "entity", "position", "none"]
    for s in flt:
        if s in file:
            return False
    return True


# 读取数据文件
def read_data(result_path, label):
    # 处理数据集名称
    names = []
    for x in figure_cfg["dataset"]:
        if label == "ner":
            names.append(x)
        if label == "re":
            if len(figure_cfg["dataset"][x]["relation"]) > 0:
                names.append(x)
    dataset = dict([(z_utils.convert_to_pinyin(x), x) for x in names])
    # 读取数据
    data = {}
    for path in os.listdir(result_path):
        if path.endswith(".json") and file_filter(path):
            data[path[:-5]] = z_utils.read_json_file(result_path + path)
    # 处理每个数据集的标签
    labels = {}
    for _, res in data.items():
        for cur_res in res:
            cur_res = cur_res["result"]
            for ds in cur_res:
                if ds not in labels:
                    labels[ds] = []
                labels[ds] += [x for x in cur_res[ds]["report"] if z_utils.has_chinese(x)]
    labels = dict([(k, list(set(v))) for k, v in labels.items()])
    return dataset, data, labels


# 标签详细结果文件
def generate_dataset_result(labels, data, result_file):
    result = []
    for dataset, entity in labels.items():
        result.append([dataset])
        result.append(["模型"] + entity)
        for model in data:
            cur_data = data[model][-1]["result"][dataset]["report"]
            cur_result = [100*cur_data[l]["f1-score"] if l in cur_data else -1 for l in entity]
            result.append([model] + cur_result)
        result.append([])
    # 格式化
    with open(result_file, mode="w", encoding="utf-8") as f:
        f.write("\n".join([",".join([str(col) for col in row]) for row in result]) + "\n")


# 生成结果文件
def generate_result(dataset, data, result_file):
    result = [["模型"] + list(dataset.values())]
    for model in data:
        tmp_result = {}
        for key, value in data[model][-1]["result"].items():
            if "micro avg" in value["report"]:
                tmp_result[key] = value["report"]["micro avg"]["f1-score"]
            else:
                tmp_result[key] = value["report"]["weighted avg"]["f1-score"]
            tmp_result[key] = 100*tmp_result[key]
        result.append([model] + [tmp_result[k] for k in dataset])
    # 格式化
    with open(result_file, mode="w", encoding="utf-8") as f:
        f.write("\n".join([",".join([str(col) for col in row]) for row in result]) + "\n")


if __name__ == "__main__":
    dataset, data, labels = read_data(figure_cfg["ner_result_path"], "ner")
    generate_result(dataset, data, figure_cfg["ner_result_file"])
    # generate_dataset_result(labels, data, figure_cfg["ner_result_file"])
    dataset, data, labels = read_data(figure_cfg["re_result_path"], "re")
    # generate_result(dataset, data, figure_cfg["re_result_file"])
    generate_dataset_result(labels, data, figure_cfg["re_result_file"])
