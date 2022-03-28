import json
import zipfile
import re
import os
import pickle

from hashlib import md5
from xpinyin import Pinyin


pinyin = Pinyin()


def convert_to_pinyin(text):
    return "".join([x.capitalize() for x in pinyin.get_pinyin(text).split("-")])


def calculate_md5(text):
    return md5(text.encode(encoding="utf-8")).hexdigest()


def has_chinese(text):
    for ch in text:
        if "\u4e00" <= ch <= "\u9fff":
            return True
    return False


def read_json_file(file_name):
    with open(file_name, mode="r", encoding="utf-8") as f:
        data = [json.loads(line) for line in f]
    return data


def write_json_file(data, file_name):
    with open(file_name, mode="w", encoding="utf-8") as f:
        f.write("\n".join([json.dumps(d, ensure_ascii=False) for d in data]) + "\n")


def load_pkl(path):
    with open(path, mode="rb") as f:
        data = pickle.load(f)
    return data


def save_pkl(path, data):
    with open(path, mode="wb") as f:
        pickle.dump(data, f)


def creat_zip_file(file_name):
    return zipfile.ZipFile(file_name, "w")


def close_zip_file(zip_file):
    zip_file.close()


def write_zip_file(zip_file, file_name, data):
    zip_file.writestr(file_name, data, compress_type=zipfile.ZIP_DEFLATED)
