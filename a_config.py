# 最长数据
MAX_LENGTH = 64

# 原始文件名
RAW_FILE = "b_data/raw_data.json"
# 清洗后数据文件名
CLEANED_FILE = "b_data/cleaned.json"
# 待标注文件名称
ANNOTATION_FILE = "b_data/annotation.zip"
# 已标注文件路径
LABELED_PATH = "b_data/labelled/"
# 提取的标注文件名
EXTRACTED_FILE = "b_data/extracted.json"
# 提取的未标注文件
UNLABELLED_FILE = "b_data/unlabelled.json"

# 词向量路径
WORD2VEC = {
    "char": "f_LexiconAugmentedNER/CNNNERmodel/gigaword_chn.all.a2b.uni.ite50.vec",
    "bi_char": "f_LexiconAugmentedNER/CNNNERmodel/gigaword_chn.all.a2b.bi.ite50.vec",
    "word": "f_LexiconAugmentedNER/CNNNERmodel/ctb.50d.vec",
}

# 字所对应词的词向量表
CHAR2WORD = "b_data/char2word.pkl"
# 语句的BERT嵌入
TEXT_EMB = "b_data/text_emb.pkl"
# 处理后的NER数据
NER_DATA = "b_data/ner_data.pkl"
# 处理后的RE数据
RE_DATA = "b_data/re_data.pkl"

# NER结果路径
NER_RESULT_PATH = "d_result/ner/"
# NER结果
NER_RESULT_FILE = NER_RESULT_PATH + "result.csv"
# RE结果路径
RE_RESULT_PATH = "d_result/re/"
# RE结果
RE_RESULT_FILE = RE_RESULT_PATH + "result.csv"

# NER模型
NER_MODEL_PATH = "e_saved_model/ner/"
# NER处理结果
PARSED_NER_FILE = "b_data/parsed_ner.json"
# RE模型
RE_MODEL_PATH = "e_saved_model/re/"
# RE处理结果
PARSED_RE_FILE = "b_data/parsed_re.json"

# 实体规范化后文件
REG_FILE = "b_data/regulated.json"

# BERT模型路径
BERT_PATH = "c_model/MC-BERT"

# NER模型超参数
EPOCH = 100
BATCH_SIZE = 64
LEARN_RATE = 0.001
NER_DROPOUT = 0.7
RE_DROPOUT = 0.9


# 实体关系标签
ANNOTATION = {
    "主要成份": {
        "entity": ["药物", "辅料"],
        "relation": [],
    },
    "适应症": {
        "entity": ["病症", "功能主治", "中毒", "受伤", "微生物", "化学物质", "手术"],
        "relation": [
            ("病症", "诱因", "病症|中毒|受伤|微生物|化学物质|手术"),
        ],
    },
    "不良反应": {
        "entity": ["病症", "发生率", "用药方案"],
        "relation": [
            ("病症", "几率", "发生率"),
            ("病症", "方案", "用药方案"),
        ],
    },
    "药物相互作用": {
        "entity": ["药物", "药物类别"],
        "relation": [],
    },
    "禁忌": {
        "entity": ["病症", "食物", "普通患者", "老人", "小孩", "计划妊娠", "妊娠", "生产", "哺乳", "年龄", "时期", "建议"],
        "relation": [
            ("病症|食物|普通患者|老人|小孩|计划妊娠|妊娠|生产|哺乳", "使用", "建议"),
            ("老人|小孩", "年龄信息", "年龄"),
            ("计划妊娠", "备孕", "时期"),
            ("妊娠", "怀孕", "时期"),
        ],
    },
    "孕妇及哺乳期妇女用药": {
        "entity": ["计划妊娠", "妊娠", "生产", "哺乳", "时期", "建议"],
        "relation": [
            ("计划妊娠|妊娠|生产|哺乳", "使用", "建议"),
            ("计划妊娠", "备孕", "时期"),
            ("妊娠", "怀孕", "时期"),
        ],
    },
    "儿童用药": {
        "entity": ["小孩", "年龄", "建议"],
        "relation": [
            ("小孩", "使用", "建议"),
            ("小孩", "年龄信息", "年龄"),
        ],
    },
    "老人用药": {
        "entity": ["老人", "年龄",  "建议"],
        "relation": [
            ("老人", "使用", "建议"),
            ("老人", "年龄信息", "年龄"),
        ],
    },
    "用法用量": {
        "entity": ["普通患者", "老人", "小孩", "计划妊娠", "妊娠", "生产", "哺乳", "性别", "年龄", "体重", "时期", "给药途径", "用药剂量", "用药频率", "用药疗程"],
        "relation": [
            ("普通患者|老人|小孩|计划妊娠|妊娠|生产|哺乳", "性别信息", "性别"),
            ("普通患者|老人|小孩|计划妊娠|妊娠|生产|哺乳", "年龄信息", "年龄"),
            ("普通患者|老人|小孩|计划妊娠|妊娠|生产|哺乳", "体重信息", "体重"),
            ("计划妊娠", "备孕", "时期"),
            ("妊娠", "怀孕", "时期"),
            ("用药剂量", "患者", "普通患者|老人|小孩|计划妊娠|妊娠|生产|哺乳"),
            ("用药剂量", "方式", "给药途径"),
            ("用药剂量", "频率", "用药频率"),
            ("用药剂量", "疗程", "用药疗程"),
        ],
    },
}

# 字段过滤
KEY_FILTER = {
    "not_annotation": {
        "通用名称": ["通用名称", "药品"], "商品名称": ["商品名", "商品名称"], "汉语拼音": ["拼音", "汉语拼音"],
        "批准文号": ["批号", "批准文号"], "生产企业": ["生产商", "企业"],
        "性状": ["药物性状", "性状"], "贮藏": ["储藏方法", "储藏"], "有效期": ["保质期", "有效期"], "类别": ["药物类别", "类别"], "处方类型": ["处方类型", "类型"],
    },
    "annotation": list(ANNOTATION.keys()),
}

# 数值实体
NUMBER_ENTITY = ["体重", "年龄", "时期", "用药疗程", "用药剂量", "用药频率"]


# 数据清洗配置
clean_cfg = {
    "raw_file": RAW_FILE,
    "cleaned_file": CLEANED_FILE,
    "key_filter": list(KEY_FILTER["not_annotation"].keys()) + KEY_FILTER["annotation"],
}

# 数据标注配置
annotation_cfg = {
    "max_length": MAX_LENGTH,
    "cleaned_file": CLEANED_FILE,
    "annotation_file": ANNOTATION_FILE,
    "annotation": ANNOTATION,
}

# 标注文件提取配置
extract_cfg = {
    "labeled_path": LABELED_PATH,
    "extracted_file": EXTRACTED_FILE,
}

# 转换数据配置
convert_data_cfg = {
    "annotation": ANNOTATION,
    "max_length": MAX_LENGTH,
    "extracted_file": EXTRACTED_FILE,
    "word2vec": WORD2VEC,
    "bert_path": BERT_PATH,
    "char2word": CHAR2WORD,
    "text_emb": TEXT_EMB,
    "ner_data": NER_DATA,
    "re_data": RE_DATA,
}

# NER训练配置
ner_train_cfg = {
    "data": NER_DATA,
    "epoch": EPOCH,
    "batch_size": BATCH_SIZE,
    "learn_rate": LEARN_RATE,
    "dropout": NER_DROPOUT,
    "ner_result_path": NER_RESULT_PATH,
    "ner_model_path": NER_MODEL_PATH,
}

# RE训练配置
re_train_cfg = {
    "data": RE_DATA,
    "epoch": EPOCH,
    "batch_size": BATCH_SIZE,
    "learn_rate": LEARN_RATE,
    "dropout": RE_DROPOUT,
    "re_result_path": RE_RESULT_PATH,
    "re_model_path": RE_MODEL_PATH,
}

# 提取未标注文件配置
unlabelled_cfg = {
    "labeled_path": LABELED_PATH,
    "max_length": MAX_LENGTH,
    "bert_path": BERT_PATH,
    "unlabelled_file": UNLABELLED_FILE,
}

# ner配置
ner_cfg = {
    "unlabelled_file": UNLABELLED_FILE,
    "max_length": MAX_LENGTH,
    "bert_path": BERT_PATH,
    "model_path": NER_MODEL_PATH,
    "extracted_data": NER_DATA,
    "ner_file": PARSED_NER_FILE,
}

# re配置
re_cfg = {
    "ner_file": PARSED_NER_FILE,
    "max_length": MAX_LENGTH,
    "bert_path": BERT_PATH,
    "model_path": RE_MODEL_PATH,
    "extracted_data": RE_DATA,
    "re_file": PARSED_RE_FILE,
}

# 实体规范化配置
regulate_cfg = {
    "cleaned_data": CLEANED_FILE,
    "labeled_data": EXTRACTED_FILE,
    "pred_data": PARSED_RE_FILE,
    "number_entity": NUMBER_ENTITY,
    "raw_key": KEY_FILTER["not_annotation"],
    "reg_data": REG_FILE,
}

# 绘图配置
figure_cfg = {
    "dataset": ANNOTATION,
    "ner_result_path": NER_RESULT_PATH,
    "ner_result_file": NER_RESULT_FILE,
    "re_result_path": RE_RESULT_PATH,
    "re_result_file": RE_RESULT_FILE,
}
