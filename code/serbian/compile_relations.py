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

def get_unlabeled_function(split: str, current_function_words: set):
    with open(f"../../../UD_Serbian-SET/sr_set-ud-{split}.conllu", encoding="utf-8") as f:
        parse_lists = list(conllu.parse_incr(f))

    split_function_words = {}
    for i in range(len(parse_lists)):
        tree = parse_lists[i]
        #make set of this sents toks
        #NEED TO SOMEHOW SPLIT TO FUNCTION WORDS ??? 
        new_function_words=current_function_words.union(set([str(token) for token in tree]))
    
    return {item:item for item in list(current_function_words)}

if __name__ == '__main__':
    """Make a case_relation mapping similar to the English one."""
    with open("./rel.json",'r',encoding="utf-8") as rel:
        rel_dict = json.load(rel)

    case_feat_map = init_case_map(rel_dict)
    
    #Now in the train, dev, and test sets, check which formal words are not accounted for in the list above:
    for split in ["train",'dev','test']:
        case_feat_map |= get_unlabeled_function(split,set(list(case_feat_map.keys())))
    
    print(case_feat_map)
