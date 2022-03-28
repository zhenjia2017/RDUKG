import re
import json
import random
import cn2an.cn2an as cn2an

import z_utils
from a_config import regulate_cfg


random.seed(1)


# 读取数据
def read_data():
    # 处理无需抽取的数据
    raw_data = {}
    for data in z_utils.read_json_file(regulate_cfg["cleaned_data"]):
        raw_data[z_utils.calculate_md5(data["批准文号"])] = dict([
            (k, v) for k, v in data.items()
            if k in regulate_cfg["raw_key"]
        ])
    # 读取抽取的数据
    extract_data = z_utils.read_json_file(regulate_cfg["labeled_data"])
    extract_data += z_utils.read_json_file(regulate_cfg["pred_data"])
    # 处理数值类实体
    num_entity = dict([[e, {}] for e in regulate_cfg["number_entity"]])
    for data in extract_data:
        for entity in data["entity"].values():
            if entity["type"] in num_entity:
                if entity["value"] not in num_entity[entity["type"]]:
                    num_entity[entity["type"]][entity["value"]] = {}
    return raw_data, extract_data, num_entity


# 规范实体表述
def correct_entity(entity):
    correct_dict = {
        "l岁以下": "1岁以下",
        "每次0.8一1.6g": "每次0.8～1.6g",
        "一日200万～200ｏ万单位": "一日200万～2000万单位",
        ".万单位/kg": "单位/kg",
        "10一12.5mg/kg": "10～12.5mg/kg",
        "一日0.25一0.5g": "一日0.25～0.5g",
        "６０万～１２０万Ｕ／次": "60万～120万U/次",
        "一0.6ml/kg": "一次0.6ml/kg",
        "7.5一12.5mg/kg": "7.5～12.5mg/kg",
        "一20毫升": "一次20毫升",
        "一日0.51.5g": "一日0.5～1.5g",
        "一次9一15粒": "一次9～15粒",
        "一次500.000～1.000.000单位一日2.000.000～4.000.000单位": "一次50万～100万单位一日200万～400万单位",
        "1OO万国际单位": "100万国际单位",
        "1.2.5毫克～5毫克/次": "2.5毫克～5毫克/次",
        "6一10周": "6～10周",
        "小于l岁": "小于1岁",
        "周岁以内": "小于1岁",
        "未满周岁": "小于1岁",
        "周岁或周岁以下": "小于等于1岁",
        "周岁": "1岁",
        "周岁以下": "小于1岁",
        "不满周岁": "小于1岁",
        "周岁以上": "大于1岁",
        "周岁内": "小于1岁",
        "３岁以下": "3岁以下",
        "６月至６岁的": "6月至6岁的",
        "低于lOkg": "低于10kg",
        "每次２片": "每次2片",
        "１５～４０ｍｇ": "15～40mg",
        "每次l片": "每次1片",
        "每次６～７片": "每次6～7片",
        "每次２～５ｇ": "每次2～5g",
        "每次１０ｍｌ": "每次10ml",
        "每次４～１０ｍｌ": "每次4～10ml",
        "每服３片": "每服3片",
        "每次4粒": "每次4粒",
        "每次l包": "每次1包",
        "１克": "1克",
        "每次１ｍｌ": "每次1ml",
        "每次０.３～１.０ｍｌ": "每次0.3～1.0ml",
        "每次２～６穴": "每次2～6穴",
        "每次２粒": "每次2粒",
        "５～２０ｇ": "5～20g",
        "每次l袋": "每次1袋",
        "每次lmg／公斤": "每次1mg/公斤",
        "２克/天": "2克/天",
        "每次１～２支": "每次1～2支",
        "―次": "1次",
        "每次５ｍｇ": "每次5mg",
        "每日３次": "每日3次",
        "每日―次": "每日1次",
        "分２～４次": "分2～4次",
        "每日最多服用-次": "每日最多服用1次",
        "每日－次": "每日1次",
        "分２次": "分2次",
        "每日服用―次": "每日服用1次",
        "１日３次": "1日3次",
        "分３次": "分3次",
        "分２～３次": "分2～3次",
        "每日１次": "每日1次",
        "２～４周１次": "2～4周1次",
        "每日或隔日１次": "每日或隔日1次",
        "每日２次": "每日2次",
        "每日l次": "每日1次",
        "５～７日": "5～7日",
        "３个月": "3个月",
        "４～６周": "4～6周",
        "４周": "4周",
        "１０日": "10日",
        "一次半岁1/4瓶": "一次0.25瓶",
        "一次1-2亳升（1-2支）": "一次1-2毫升（1-2支）",
        "2.2-6岁": "2-6岁",
        "1.1-18岁": "1-18岁",
        "7-lo日": "7-10日",
        "l/3": "1/3",
        "每次?40?万～?80?万单位": "每次40万～80万单位",
    }
    replace_dict = {
        "公斤": "kg",
        "千克": "kg",
        "千g": "kg",
        "毫克": "mg",
        "毫g": "mg",
        "微克": "μg",
        "微g": "μg",
        "克": "g",
        "毫升": "ml",
        "升": "l",
        "公分": "cm",
        "iu/m/天": "iu/m*m/d",
        "iu/m2/天": "iu/m*m/d",
        "mg/m2": "mg/m*m",
        "一次每kg": "kg/次",
        "一半": "0.5",
        "半": "0.5",
        "／": "/",
        "/次": "/一次",
        "每次": "一次",
        "/日": "/一日",
        "每日": "一日",
        "/天": "/一天",
        "每天": "一天",
        "每周": "一周",
        "每月": "一月",
        "每小时": "一小时",
        "每分钟": "一分钟",
    }
    # 数据纠正
    corrected_entity = correct_dict[entity] if entity in correct_dict else entity
    # 部分纠正
    for k, v in replace_dict.items():
        corrected_entity = corrected_entity.replace(k, v)
    # 转换为小写字母
    corrected_entity = corrected_entity.lower()
    return corrected_entity


# 转换数字
def convert_number(entity):
    reg = "[0-9零一二三四五六七八九十百千万亿壹贰叁肆伍陆柒捌玖拾佰仟两俩.]+"
    # 匹配数字
    numbers = [(x.span(), entity[x.span()[0]: x.span()[1]]) for x in re.finditer(reg, entity)]
    # 去除首尾小数点
    numbers = [(x[0], x[1].strip(".")) for x in numbers]
    # 去除空数据
    numbers = [x for x in numbers if len(x[1]) > 0]
    # 中文数字转阿拉伯数字
    numbers = [(x[0], cn2an(x[1], "smart")) for x in numbers]
    return numbers


# 处理数字的单位
def parse_unit(corrected_entity, converted_numbers):
    unit_list = [
        "年", "岁", "周岁", "月", "周", "日", "天", "d", "小时", "h", "分钟", "m",
        "kg", "g", "mg", "μg",
        "l", "ml",
        "cm",
        "次", "kg/次",
        "片", "丸", "颗", "粒", "瓶", "包", "袋", "盒", "贴", "支", "滴", "下", "喷", "瓶盖",
        "单位", 
        "g/kg", "mg/kg", "μg/kg", "ml/kg", "l/kg", "iu", "iu/m*m/天", "mg/m*m", "μg/kg/分速",
    ]
    # 查找单位下标
    unit_idx = {}
    for unit in unit_list:
        for idx in re.finditer(unit, corrected_entity):
            idx = idx.span()[0]
            if idx in unit_idx:
                unit_idx[idx] = unit if len(unit) > len(unit_idx[idx]) else unit_idx[idx]
            else:
                unit_idx[idx] = unit
    # 将数字后第一个出现的年龄单位作为该数字的单位
    num_unit = {}
    for i, ((_, idx), _) in enumerate(converted_numbers):
        while idx < len(corrected_entity):
            if idx in unit_idx:
               num_unit[i] = unit_idx[idx]
               break
            idx += 1
        else:
             num_unit[i] = ""
    return num_unit


# 处理数字范围
def parse_limit(corrected_entity, converted_numbers):
    limits = {
        "＜": [
            "<", "＜", "小于", "未满", "不满", "以下", "低于",
        ],
        "≤": [
            "≤", "小于等于", "不大于", "不超", "不超过", "未超过", "不能超过", "不应超过", "不得超过", "及以下",
            "初", "前", "头", "起", "内", "以内", "开始",
        ],
        "＞": [
            ">", "＞", "大于", "超过", "以上",
        ],
        "≥": [
            "≥", "大于等于", "不小于", "及以上",
            "末", "后", "分娩前",
        ],
    }
    # 数字的范围对齐
    limit_dict = {}
    for k, v in limits.items():
        limit_dict.update(dict([(vi, k) for vi in v]))
    # 查找数值范围
    all_limit = []
    for limit in limit_dict:
        all_limit += [(limit_dict[limit], x.span())for x in re.finditer(limit, corrected_entity)]
    # 去重并匹配数字范围
    num_limit = {}
    for a in all_limit:
        # 去重，保证数字的范围不重叠
        for b in all_limit:
            if a != b:
                if a[1][0] >= b[1][0] and a[1][1] <= b[1][1]:
                    break
        # 匹配数字的范围
        else:
            if len(converted_numbers) > 0:
                left = min([(abs(a[1][0]-x[0][1]), i) for i, x in enumerate(converted_numbers)], key=lambda k: k[0])
                right = min([(abs(x[0][0]-a[1][1]), i) for i, x in enumerate(converted_numbers)], key=lambda k: k[0])
                num_limit[left[1] if left[0] < right[0] else right[1]] = a[0]
    return num_limit


# 生成规范化数据
def generate_regulation(regulated, entity_type, corrected_entity, converted_numbers, number_units, number_limits):
    unit_convert = {
        "年": 365, "岁": 365, "周岁": 365,
        "月": 30,
        "周": 7,
        "日": 1, "天": 1,
        "用药剂量": ["次", "月", "周", "日", "天", "d", "小时", "h", "分钟", "m",],
        "用药频率": ["月", "周", "日", "天", "d", "小时", "h", "分钟", "m",],
    }
    # 以单位分组匹配数字和范围
    matched = {}
    for num_idx, unit in number_units.items():
        value = converted_numbers[num_idx][1]
        # 时间实体单位换算
        if entity_type in ["年龄", "时期", "用药疗程"]:
            if unit in unit_convert:
                value *= unit_convert[unit]
                unit = "天"
        # 增加数据
        if unit not in matched:
            matched[unit] = []
        number = {
            "value": value,
            "limit": number_limits[num_idx] if num_idx in number_limits else "",
        }
        if number not in matched[unit]:
            matched[unit].append(number)
    # 补全数字的范围
    for numbers in matched.values():
        numbers.sort(key=lambda x: x["value"])
        if len(numbers) == 2:
            if numbers[0]["limit"] == "":
                numbers[0]["limit"] = "≥"
            if numbers[1]["limit"] == "":
                numbers[1]["limit"] = "≤"
        else:
            for number in numbers:
                if number["limit"] == "":
                    number["limit"] = "="
    # 生成数据
    regulated["corrected entity"] = corrected_entity
    regulated["dimension"] = dict([
        (unit, numbers) for unit, numbers in matched.items()
        if entity_type in ["用药剂量", "用药频率"] and unit in unit_convert[entity_type]
    ])
    regulated["number"] = dict([
        (unit, numbers) for unit, numbers in matched.items()
        if entity_type not in ["用药剂量", "用药频率"] or unit not in unit_convert[entity_type]
    ])


# 实体规范化
def regulate_entity(number_entity):
    for en_tp, ens in number_entity.items():
        for i, (en, regulated) in enumerate(ens.items()):
            crt_en = correct_entity(en)
            cvt_nums = convert_number(crt_en)
            nums_unit = parse_unit(crt_en, cvt_nums)
            nums_lmt = parse_limit(crt_en, cvt_nums)
            generate_regulation(regulated, en_tp, crt_en, cvt_nums, nums_unit, nums_lmt)
    number_entity["时长"] = number_entity["时期"]
    del number_entity["时期"]


# 匹配药品的宾语
def match_drug_object(entity, types):
    obj_set = set([
        (obj["type"], obj["value"])
        for obj in entity.values() if obj["type"] in types
    ])
    return obj_set


# 匹配三元组
def match_triple(entity, relation, sub_type, obj_types, rel_type):
    triple = {}
    for sub_id, sub in entity.items():
        if sub_type == sub["type"] and sub_id not in [rel["object"] for rel in relation.values()]:
            if sub_id not in triple:
                triple[sub_id] = set()
            obj_set = set([
                (entity[rel["object"]]["type"], entity[rel["object"]]["value"])
                for rel in relation.values()
                if sub_id == rel["subject"] and entity[rel["object"]]["type"] in obj_types
            ])
            if len(obj_set):
                for obj in obj_set:
                    triple[sub_id].add(((sub["type"], sub["value"]), rel_type, obj))
            else:
                triple[sub_id].add((sub["type"], sub["value"]))
    return triple


# 处理人群
def extract_people(entity, relation):
    entity_convert = {
        "普通患者": "普通患者", "老人": "老人", "小孩": "儿童",
        "计划妊娠": "计划妊娠妇女", "妊娠": "孕妇", "生产": "产妇", "哺乳": "哺乳期妇女",
    }
    properties = ["性别", "年龄", "体重", "时期"]
    RenQun = {}
    for sub_id, sub in entity.items():
        if sub["type"] in entity_convert:
            if sub_id not in RenQun:
                RenQun[sub_id] = set()
            obj_set = set([(
                    rel["type"],
                    "时长" if entity[rel["object"]]["type"] == "时期" else entity[rel["object"]]["type"],
                    entity[rel["object"]]["value"]
                ) for rel in relation.values()
                if sub_id == rel["subject"] and entity[rel["object"]]["type"] in properties
            ])
            sub = (entity_convert[sub["type"]], entity_convert[sub["type"]])
            if len(obj_set):
                for obj in obj_set:
                    RenQun[sub_id].add((sub, obj[0], (obj[1], obj[2])))
            else:
                RenQun[sub_id].add(sub)
    return RenQun


# 组合宾语
def combine_object(obj_1, obj_2):
    if len(obj_1) != 0 and len(obj_2) != 0:
        if len(obj_1) == 1 and len(list(obj_1)[0]) == 2:
            return obj_2
        if len(obj_2) == 1 and len(list(obj_2)[0]) == 2:
            return obj_1
        combined = set()
        for en_1 in obj_1:
            for en_2 in obj_2:
                tmp = list(en_1)
                for x in en_2[1:]:
                    tmp.append(x)
                combined.add(tuple(tmp))
        return combined
    return obj_1 if len(obj_1) else obj_2


# 三元组补全和去重
def parse_triple(extract_data):
    # 获取所有文件
    files = []
    for data in extract_data:
        files += data["file"]
    folder_convert = {
        "ZhuYaoChengFen": "成分",
        "ShiYingZheng": "治疗",
        "BuLiangFanYing": "不良反应",
        "YaoWuXiangHuZuoYong": "相互作用", 
        "JinJi": "使用", 
        "YunFuJiBuRuQiFuNvYongYao": "使用", 
        "ErTongYongYao": "使用", 
        "LaoRenYongYao": "使用", 
        "YongFaYongLiang": "用药",
    }
    parsed_data = dict([
        (f, dict([(k, set()) for k in ["成分", "治疗", "功用", "不良反应", "相互作用", "使用", "用药"]
    ])) for f in list(set(files))])
    # 处理数据
    for data in extract_data:
        cur_parsed = set()
        entitys = data["entity"]
        relations = data["relation"]
        # 处理主要成份
        if data["folder"] == "ZhuYaoChengFen":
            cur_parsed.update(match_drug_object(entitys, ["药物", "辅料"]))
        # 处理适应症
        if data["folder"] == "ShiYingZheng":
            YouYin = match_triple(entitys, relations, "病症", ["病症", "中毒", "受伤", "微生物", "化学物质", "手术"], "诱因").values()
            for triple in YouYin:
                cur_parsed.update(triple)
            GongYong = match_drug_object(entitys, ["功能主治"])
            for file in data["file"]:
                parsed_data[file]["功用"].update(GongYong)
        # 处理不良反应
        if data["folder"] == "BuLiangFanYing":
            JiLv =  match_triple(entitys, relations, "病症", ["发生率"], "几率")
            FangAn =  match_triple(entitys, relations, "病症", ["用药方案"], "方案")
            for sub_id in JiLv:
                cur_parsed.update(combine_object(JiLv[sub_id], FangAn[sub_id]))
        # 处理药物相互作用
        if data["folder"] == "YaoWuXiangHuZuoYong":
            cur_parsed.update(match_drug_object(entitys, ["药物", "药物类别"]))
        # 处理禁忌
        if data["folder"] == "JinJi":
            RenQun = extract_people(entitys, relations)
            for obj_id, en in entitys.items():
                if en["type"] == "建议" and obj_id not in [rel["subject"] for rel in relations.values()]:
                    obj = (entitys[obj_id]["type"], entitys[obj_id]["value"])
                    for sub_id in set([rel["subject"] for rel in relations.values() if obj_id == rel["object"]]):
                        sub = (entitys[sub_id]["type"], entitys[sub_id]["value"])
                        if sub[0] == "病症":
                            cur_parsed.add((obj, "禁忌病症", sub))
                        if sub[0] == "食物":
                            cur_parsed.add((obj, "同服忌口", sub))
                        if sub[0] in ["普通患者", "老人", "小孩", "计划妊娠", "妊娠", "生产", "哺乳"]:
                            for rq_sub in RenQun[sub_id]:
                                cur_parsed.add((obj, "特殊人群", rq_sub))
        # 处理特殊人群用药
        if data["folder"] in ["YunFuJiBuRuQiFuNvYongYao", "ErTongYongYao", "LaoRenYongYao"]:
            RenQun = extract_people(entitys, relations)
            for obj_id, en in entitys.items():
                if en["type"] == "建议" and obj_id not in [rel["subject"] for rel in relations.values()]:
                    obj = (entitys[obj_id]["type"], entitys[obj_id]["value"])
                    sub_set = set([rel["subject"] for rel in relations.values() if obj_id == rel["object"]])
                    if len(sub_set) == 0:
                        if data["folder"] == "YunFuJiBuRuQiFuNvYongYao":
                            cur_parsed.add((obj, "特殊人群", ("孕妇", "孕妇")))
                            cur_parsed.add((obj, "特殊人群", ("哺乳期妇女", "哺乳期妇女")))
                        if data["folder"] == "ErTongYongYao":
                            cur_parsed.add((obj, "特殊人群", ("儿童", "儿童")))
                        if data["folder"] == "LaoRenYongYao":
                            cur_parsed.add((obj, "特殊人群", ("老人", "老人")))
                    else:
                        for sub_id in sub_set:
                            for rq_sub in RenQun[sub_id]:
                                cur_parsed.add((obj, "特殊人群", rq_sub))
        # 处理用法用量
        if data["folder"] == "YongFaYongLiang":
            # 组合用药方法
            FangShi = match_triple(entitys, relations, "用药剂量", ["给药途径"], "方式")
            PinLv = match_triple(entitys, relations, "用药剂量", ["用药频率"], "频率")
            LiaoCheng = match_triple(entitys, relations, "用药剂量", ["用药疗程"], "疗程")
            tmp_1 = dict([(k, combine_object(FangShi[k], PinLv[k])) for k in FangShi])
            tmp_2 = dict([(k, combine_object(tmp_1[k], LiaoCheng[k])) for k in tmp_1])
            # 人群
            RenQun = extract_people(entitys, relations)
            # 组合人群及用药方法
            for yy_id, en in entitys.items():
                if en["type"] == "用药剂量" and yy_id not in [rel["object"] for rel in relations.values()]:
                    rq_set = set([
                        rel["object"] for rel in relations.values()
                        if yy_id == rel["subject"] and
                        entitys[rel["object"]]["type"] in ["普通患者", "老人", "小孩", "计划妊娠", "妊娠", "生产", "哺乳"]
                    ])
                    if len(rq_set) == 0:
                        for cur_yy in tmp_2[yy_id]:
                            cur_yy = [cur_yy] if len(cur_yy) == 2 else list(cur_yy)
                            cur_parsed.add(tuple([("普通患者", "普通患者"), "剂量"] + cur_yy))
                    else:
                        for rq_id in rq_set:
                            for cur_rq in RenQun[rq_id]:
                                for cur_yy in tmp_2[yy_id]:
                                    cur_yy = [cur_yy] if len(cur_yy) == 2 else list(cur_yy)
                                    cur_parsed.add(tuple([cur_rq, "剂量"] + cur_yy))
            # 其他单个的用药
            relation_convert = {
                "给药途径": "方式", "用药频率": "频率", "用药疗程": "疗程",
            }
            cur_parsed.update(set([
                (("普通患者", "普通患者"), relation_convert[v["type"]], (v["type"], v["value"]))
                for k, v in entitys.items()
                if v["type"] in relation_convert and k not in [rel["object"] for rel in relations.values()]
            ]))
        for file in data["file"]:
            parsed_data[file][folder_convert[data["folder"]]].update(cur_parsed)
    return parsed_data


# 转换元组为字符串
def tuple2str(tup):
    if isinstance(tup, str):
        return tup
    out = ""
    for x in tup:
        out += tuple2str(x)
    return out


def add_triple(entity, relation, drug_id, tup, tup_rel):
    tup_id = z_utils.calculate_md5(tuple2str(tup))
    relation.add((drug_id, tup_id, tup_rel))
    if len(tup) == 2:
        entity.add((tup_id, tup[0], tup[1]))
    else:
        sub = tup[0]
        if len(sub) == 2:
            entity.add((tup_id, sub[0], sub[1]))
            for i in range(1, len(tup), 2):
                obj = tup[i+1]
                obj_id = z_utils.calculate_md5(tuple2str(obj))
                relation.add((tup_id, obj_id, tup[i]))
                if len(obj) == 2:
                    entity.add((obj_id, obj[0], obj[1]))
                if len(obj) == 3:
                    entity.add((obj_id, obj[0][0], obj[0][1]))
                    obj_obj = obj[2]
                    obj_obj_id = z_utils.calculate_md5(tuple2str(obj_obj))
                    entity.add((obj_obj_id, obj_obj[0], obj_obj[1]))
                    relation.add((obj_id, obj_obj_id, obj[1]))
        if len(sub) == 3:
            entity.add((tup_id, sub[0][0], sub[0][1]))
            sub_obj = sub[2]
            sub_obj_id = z_utils.calculate_md5(tuple2str(sub_obj))
            entity.add((sub_obj_id, sub_obj[0], sub_obj[1]))
            relation.add((tup_id, sub_obj_id, sub[1]))


# 生成本体实例
def generate_KG(raw_data, extract_data, num_entity):
    # 处理数据
    parsed_data = parse_triple(extract_data)
    # 规范化数值类实体
    regulate_entity(num_entity)
    # 转换为三元组
    entity = set()
    relation = set()
    for file, data in parsed_data.items():
        drug_id = file
        drug_type = "药品"
        drug_name = raw_data[file]["通用名称"]
        entity.add((drug_id, drug_type, drug_name))
        # 处理原始数据
        for k, v in raw_data[file].items():
            if k != "通用名称":
                obj = (regulate_cfg["raw_key"][k][1], v)
                add_triple(entity, relation, drug_id, obj, regulate_cfg["raw_key"][k][0])
        # 处理抽取的三元组
        for k, v in data.items():
            for tmp in v:
                add_triple(entity, relation, drug_id, tmp, k)
    # 处理逗号和数值实体
    new_entity = set()
    for data in entity:
        data_id = data[0]
        data_type = data[1]
        data_value = data[2]
        if data_type in num_entity:
            data_value = json.dumps(num_entity[data_type][data_value], ensure_ascii=False)
        data_value = data_value.replace(",", "，")
        new_entity.add((data_id, data_type, data_value))
    return new_entity, relation


if __name__ == "__main__":
    raw_data, extract_data, num_entity = read_data()


    entity, relation = generate_KG(raw_data, extract_data, num_entity)
    with open("b_data/entity.csv", mode="w", encoding="utf-8") as f:
        f.write(",".join([":ID", ":LABEL", "name"])+"\n")
        f.write("\n".join([",".join(x) for x in entity])+"\n")
    with open("b_data/relation.csv", mode="w", encoding="utf-8") as f:
        f.write(",".join([":START_ID", ":END_ID", ":TYPE"])+"\n")
        f.write("\n".join([",".join(x) for x in relation])+"\n")


    # regulate_entity(num_entity)
    # 随机选择100个处理后数据，用于统计准确率（90/100）
    # tmp = []
    # for en_tp, ens in num_entity.items():
    #     for en, regulated in ens.items():
    #         tmp.append((en_tp, regulated))
    # random.shuffle(tmp)
    # for tt in tmp[:100]:
    #     print(tt)
