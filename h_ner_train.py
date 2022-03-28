import torch

# 设置随机数种子
SEED = 1
torch.manual_seed(SEED)
torch.cuda.manual_seed(SEED)
torch.cuda.manual_seed_all(SEED)

from seqeval.metrics import classification_report

import z_utils
from a_config import ner_train_cfg
from f_ner_data import NerData
from g_ner_model import BERT_CRF, BERT_BiGRU_CRF, BERT_BiGRU_ATT_CRF, BERT_BiGRU_STACK_CNN_CRF


cur_train_cfg = {
    "use_lexicon": False,
    "model": BERT_BiGRU_STACK_CNN_CRF,
    "save_model": True,
    "result_file": "ner",
}


def convert_entity_tag(ids2tag, lengths, tags, preds):
    out_tags = []
    out_preds = []
    for i in range(len(lengths)):
        label = tags[i]
        pred = preds[i]
        out_tags.append([ids2tag[label[j]] for j in range(lengths[i])])
        out_preds.append([ids2tag[pred[j]] for j in range(lengths[i])])
    return out_tags, out_preds


if __name__ == "__main__":
    dev = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
    # 加载数据
    data = NerData(z_utils.load_pkl(ner_train_cfg["data"]))
    print("数据加载完成。")
    # 加载模型
    all_model = {}
    for folder in data.all_data:
        all_model[folder] = {}
        all_model[folder]["model"] = cur_train_cfg["model"](
            num_labels=len(data.tag2ids[folder]),
            dropout=ner_train_cfg["dropout"],
        )
        all_model[folder]["model"].to(dev)
        all_model[folder]["optimizer"] = torch.optim.Adam(
            filter(lambda p: p.requires_grad, all_model[folder]["model"].parameters()),
            lr=ner_train_cfg["learn_rate"],
        )
    print("模型加载完成。")
    # 结果保存
    result = []
    # 训练所有模型
    for epoch in range(ner_train_cfg["epoch"]):
        cur_res = {"epoch": epoch + 1, "result": {}}
        for folder in data.all_data:
            # 训练
            all_model[folder]["model"].train()
            epoch_loss = 0
            # 修改数据
            data.change_dataset(folder, "train")
            train_data = torch.utils.data.DataLoader(
                dataset=data,
                batch_size=ner_train_cfg["batch_size"],
                shuffle=True,
            )
            for cur_data in train_data:
                length = cur_data["length"].to(dev)
                word2vec = cur_data["word2vec"].to(dev)
                lexicon = cur_data["lexicon"].to(dev)
                label = cur_data["label"].to(dev)
                mask = cur_data["mask"].to(dev)
                # 计算损失
                if cur_train_cfg["use_lexicon"]:
                    loss = all_model[folder]["model"](length, torch.cat([word2vec, lexicon], dim=2), mask, label=label)
                else:
                    loss = all_model[folder]["model"](length, word2vec, mask, label=label)
                epoch_loss += loss.item()
                # 优化
                all_model[folder]["optimizer"].zero_grad()
                loss.backward()
                all_model[folder]["optimizer"].step()
            epoch_loss /= len(train_data)
            # 测试
            all_model[folder]["model"].eval()
            epoch_length = []
            epoch_tag = []
            epoch_pred = []
            # 修改数据
            data.change_dataset(folder, "test")
            test_data = torch.utils.data.DataLoader(
                dataset=data,
                batch_size=ner_train_cfg["batch_size"],
                shuffle=False,
            )
            for cur_data in test_data:
                length = cur_data["length"].to(dev)
                word2vec = cur_data["word2vec"].to(dev)
                lexicon = cur_data["lexicon"].to(dev)
                mask = cur_data["mask"].to(dev)
                label = cur_data["label"].numpy().tolist()
                # 预测
                if cur_train_cfg["use_lexicon"]:
                    pred = all_model[folder]["model"](length, torch.cat([word2vec, lexicon], dim=2), mask)
                else:
                    pred = all_model[folder]["model"](length, word2vec, mask)
                # 计算P、R、F1
                epoch_length = epoch_length + length.cpu().numpy().tolist()
                epoch_tag = epoch_tag + label
                epoch_pred = epoch_pred + pred
            epoch_tag, epoch_pred = convert_entity_tag(
                data.ids2tag[folder],
                epoch_length, epoch_tag, epoch_pred
            )
            # 测试结果
            report = classification_report(epoch_tag, epoch_pred, output_dict=True)
            for _, value in report.items():
                value["support"] = float(value["support"])
            # 结果保存
            cur_res["result"][folder] = {
                "loss": epoch_loss,
                "report": report
            }
        result.append(cur_res)
        # 打印
        print("EPOCH: %s." % (cur_res["epoch"]))
        for key, value in cur_res["result"].items():
            print("F1: %f, SUPPORT: %d, DATA SET: %s." %
                (value["report"]["micro avg"]["f1-score"],  value["report"]["micro avg"]["support"], key))
    z_utils.write_json_file(result, ner_train_cfg["ner_result_path"] + cur_train_cfg["result_file"] + ".json")
    if cur_train_cfg["save_model"]:
        z_utils.save_pkl(ner_train_cfg["ner_model_path"] + cur_train_cfg["result_file"] + ".mdl", all_model)
