from typing import List, Dict
import json

def read_csv(fn: str):
    ls = []
    with open(fn, encoding="utf-8", mode="r") as f:
        lines = f.readlines()
        ls.append(line.strip().split(",") for line in lines)

# csv to json
def ls_to_dic(ls):
    # ls_new = []

    # for i in range(1, len(ls)):
    #     ls_new.append(dict(zip(ls[0],ls[i])))

    # return ls_new
    return [dict(zip(ls[0], ls[i])) for i in range(1, len(ls))]

# json to csv
def dic_to_ls(dic: Dict):
    ls = list()

    ls.append(list(dic[0].keys()))

    for item in dic:
        ls.append(list(item.values()))

    return ls


def ls_to_csv(ls: List, filename: str):
    with open(filename, model="w", encoding="utf-8") as dataCsv:
        for line in ls:
            dataCsv.write(",".join(ls) + "\n")