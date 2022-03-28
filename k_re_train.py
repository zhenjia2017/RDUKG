import torch

# 设置随机数种子
SEED = 1
torch.manual_seed(SEED)
torch.cuda.manual_seed(SEED)
torch.cuda.manual_seed_all(SEED)

from sklearn.metrics import classification_report

import z_utils
from a_config import re_train_cfg
from i_re_data import ReData
from j_re_model import RNN_MAXPOOL, RNN_ATT, CNN_MAXPOOL, CNN_ATT, RNN_CNN, PCNN_MAXPOOL, EN_INFO_PCNN


cur_train_cfg = {
    "save_model": True,
    "model": EN_INFO_PCNN,
    "result_file": "re",
}


def f1(x_pred, y_true):
    length = len(y_true)
    TP = sum([1 for i in range(length) if y_true[i] != "无关系" and y_true[i] == x_pred[i]])
    TN = sum([1 for i in range(length) if y_true[i] == "无关系" and x_pred[i] == "无关系"])
    FP = sum([1 for i in range(length) if y_true[i] == "无关系" and x_pred[i] != "无关系"])
    FN = sum([1 for i in range(length) if y_true[i] != "无关系" and x_pred[i] == "无关系"])
    P = TP / (TP + FP) if (TP + FP) != 0 else 0
    R = TP / (TP + FN) if (TP + FN) != 0 else 0
    F1 = 2 * P * R / (P + R) if (P + R) != 0 else 0
    return P, R, F1


if __name__ == "__main__":
    dev = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
    # 加载数据
    data = ReData(z_utils.load_pkl(re_train_cfg["data"]))
    print("数据加载完成。")
    # 加载模型
    all_model = {}
    for folder in data.all_data:
        all_model[folder] = {}
        all_model[folder]["model"] = cur_train_cfg["model"](
            entity_num=len(data.entity_tag2ids[folder]),
            relation_num=len(data.relation_tag2ids[folder]),
            dropout=re_train_cfg["dropout"],
        )
        all_model[folder]["model"].to(dev)
        all_model[folder]["optimizer"] = torch.optim.Adam(
            filter(lambda p: p.requires_grad, all_model[folder]["model"].parameters()),
            lr=re_train_cfg["learn_rate"],
        )
    print("模型加载完成。")
    # 结果保存
    result = []
    # 训练所有模型
    for epoch in range(re_train_cfg["epoch"]):
        cur_res = {"epoch": epoch + 1, "result": {}}
        for folder in data.all_data:
            # 训练
            all_model[folder]["model"].train()
            epoch_loss = 0
            # 修改数据
            data.change_dataset(folder, "train")
            train_data = torch.utils.data.DataLoader(
                dataset=data,
                batch_size=re_train_cfg["batch_size"],
                shuffle=True,
            )
            for cur_data in train_data:
                length = cur_data["length"].to(dev)
                inp = cur_data["word2vec"].to(dev)
                sub = cur_data["subject"].to(dev)
                obj = cur_data["object"].to(dev)
                sub_pos = cur_data["sub_pos"].to(dev)
                obj_pos = cur_data["obj_pos"].to(dev)
                m1 = cur_data["mask1"].to(dev)
                m2 = cur_data["mask2"].to(dev)
                rel = cur_data["relation"].to(dev)
                # 计算损失
                loss = all_model[folder]["model"](length, inp, sub, obj, sub_pos, obj_pos, m1, m2, rel=rel)
                epoch_loss += loss.item()
                # 优化
                all_model[folder]["optimizer"].zero_grad()
                loss.backward()
                all_model[folder]["optimizer"].step()
            epoch_loss /= len(train_data)
            # 测试
            all_model[folder]["model"].eval()
            epoch_tag = []
            epoch_pred = []
            # 修改数据
            data.change_dataset(folder, "test")
            test_data = torch.utils.data.DataLoader(
                dataset=data,
                batch_size=re_train_cfg["batch_size"],
                shuffle=False,
            )
            for cur_data in test_data:
                length = cur_data["length"].to(dev)
                inp = cur_data["word2vec"].to(dev)
                sub = cur_data["subject"].to(dev)
                obj = cur_data["object"].to(dev)
                sub_pos = cur_data["sub_pos"].to(dev)
                obj_pos = cur_data["obj_pos"].to(dev)
                m1 = cur_data["mask1"].to(dev)
                m2 = cur_data["mask2"].to(dev)
                rel = cur_data["relation"].to(dev)
                pred = all_model[folder]["model"](length, inp, sub, obj, sub_pos, obj_pos, m1, m2)
                # 保存
                epoch_tag += [data.relation_ids2tag[folder][x] for x in rel.cpu().numpy().tolist()]
                epoch_pred += [data.relation_ids2tag[folder][x] for x in pred.cpu().numpy().tolist()]
            # 测试结果
            report = classification_report(epoch_tag, epoch_pred, output_dict=True)
            _, _, report["f1"] = f1(epoch_pred, epoch_tag)
            for key, value in report.items():
                if key not in ["accuracy", "f1"]:
                    value["support"] = float(value["support"])
            # 结果保存
            cur_res["result"][folder] = {
                "loss": epoch_loss,
                "report": report
            }
        result.append(cur_res)
        # 打印
        print("EPOCH: %d." % (cur_res["epoch"]))
        for key, value in cur_res["result"].items():
            print("F1: %f, SUPPORT: %d, DATA SET: %s" %(value["report"]["f1"],  value["report"]["weighted avg"]["support"], key))
    z_utils.write_json_file(result, re_train_cfg["re_result_path"] + cur_train_cfg["result_file"] + ".json")
    if cur_train_cfg["save_model"]:
        z_utils.save_pkl(re_train_cfg["re_model_path"] + cur_train_cfg["result_file"] + ".mdl", all_model)
