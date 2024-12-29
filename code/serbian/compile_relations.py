import json

import conllu


def init_case_map(rel: dict):
    case_feat_map = {}
    for k,v in rel_dict.items():
        if v == "NONE":
            continue
        else:
            assert type(v)==list, v
            for items in v:
                case_feat_map[items]=k
    return case_feat_map

if __name__ == '__main__':
    """Make a case_relation mapping similar to the English one."""
    with open("./rel.json",'r',encoding="utf-8") as rel:
        rel_dict = json.load(rel)

    case_feat_map = init_case_map(rel_dict)

    with open("./case_feat_map.json","w",encoding="utf-8") as outfile:
        json.dump(case_feat_map,outfile)