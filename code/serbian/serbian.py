import os
from typing import List
from copy import deepcopy
from collections import defaultdict
import sys
import json

import conllu
import utils as utils


with open("./case_feat_map.json",'r',encoding="utf-8") as f:
    case_feat_map = json.load(f)

VERBAL = {'VERB'}
NOMINAL = {'NOUN', 'PROPN', 'PRON', 'NUM'}

clausal_rels = {'conj','csubj','xcomp','ccomp','advcl','acl','advcl:relcl','acl:relcl'}

#Seems like sve can mean other things as a modal but I'm not sure.
modalities = {'moći':'Pot', 'trebati':'Nec', "sve":"Pot"}#hteti for future? 

# determiners with tuples of the feature name and the feature value
with open("./determiners.json",'r',encoding="utf-8") as f:
    determiners = json.load(f)

def create_abstract_nsubj(head: conllu.Token, auxes: List[conllu.Token]):
    '''
    When the subject is missing but agreement features appear on its head, an abstract node carrying features only is created
    '''
    abstract_nsubj = conllu.Token()
    abstract_nsubj['id'] = head['id'] - 0.9 # to make sure it's between the head and the first child
    abstract_nsubj['form'] = '-' # set all values to '-', but set the head and the deprel
    abstract_nsubj['lemma'] = '-'
    abstract_nsubj['upos'] = '-'
    abstract_nsubj['xpos'] = '-'
    abstract_nsubj['deps'] = '-'
    abstract_nsubj['misc'] = '-'
    abstract_nsubj['head'] = head['id']
    abstract_nsubj['deprel'] = 'nsubj'
    abstract_nsubj['ms feats'] = {}

    if auxes: # if there are auxiliaries, take the features from the first one
        first_aux_id = min([child['id'] for child in auxes])
        feats_source = [aux for aux in auxes if aux['id'] == first_aux_id][0]
    else: # if there are no auxiliaries, take the features from the head
        feats_source = head

    if not(feats_source['feats']):
        #Not clear what that would imply for the abstract subject's ms feats so I set them all to none...
        for attr in ['Number','Person','Gender']:
            abstract_nsubj['ms feats'][attr]=None
    else:
        for attr in ['Number', 'Person', 'Gender']: # copy the features from the head or the auxiliaries
            abstract_nsubj['ms feats'][attr] = feats_source['feats'].get(attr, head['feats'].get(attr, None)) # if the feature is not in the auxiliaries, take it from the head
    abstract_nsubj['ms feats'] = {k:v for k,v in abstract_nsubj['ms feats'].items() if v} #clean up nones

    # in case of some pragmatical omission of subject with no agreement on the predicate - do not create abstract node
    if not abstract_nsubj['ms feats']:
        return None

    return abstract_nsubj


def get_rel_feat(word): # try to get the relation feature from the marker feature map, if not - from the case feature map, if not - return the word itself
    return case_feat_map.get(word, word)


def get_relation_feats(relation_nodes: List[conllu.Token], verb=True, clause=False) -> dict:
    '''
    Generating morpho_syntactic features for relations.
    The mapping from words (or fixed expressions) to features is in 'eng_relations.py' and should be updated there.
    '''
    feats = {}

    relation_nodes = deepcopy(relation_nodes)
    for node in relation_nodes: # if the node is a fixed node, take its fixed lemma, otherwise take its lemma
        node['lemma'] = node.get('fixed lemma', node.get('lemma'))

    feats['Case'] = ';'.join([get_rel_feat(node['lemma']) for node in relation_nodes])

    return feats


def get_nTAM_feats(aux_nodes: List[conllu.Token], head_feats: dict, verb=True) -> dict:
    '''
    generating morpho-syntactic features for a head node based on its own morphological features (head_feats) and its auxiliaries (all concatenated as list in aux_nodes).
    This methods works for both verbal and nominal predicates.
    '''
    feats = defaultdict(str)

    subj_ids = [child['id'] for child in children if child['deprel'] in {'nsubj', 'expl'}] # get the ids of the subjects
    if subj_ids:
        subj_id = min(subj_ids) # take the id of the first subject
        first_aux_id = min([child['id'] for child in aux_nodes]) # take the id of the first auxiliary
        if first_aux_id < subj_id: # if the first auxiliary is before the first subject (subject aux inversion)
            if any([child['form'] == '?' for child in children]): # if there is a question mark in the sentence, assume it's a question
                feats['Mood'] = 'Int'

    aux_lemmas = {aux['lemma'] for aux in aux_nodes} # get the lemmas of the auxiliaries

    # setting the polarity of the main verb, assuming that there is no modality that require internal feature structure.
    # The polarity may be deleted again later if there are modal auxiliaries.
    if 'ne' in aux_lemmas: # if there is a negation marker, set the polarity to negative
        feats['Polarity'] = 'Neg'
    else: # if there is no negation marker, set the polarity to positive
        feats['Polarity'] = 'Pos'
    aux_lemmas.discard('ne')
 
    if 'biti' in aux_lemmas:
        biti_nodes = [aux for aux in aux_nodes if aux['lemma'] == 'biti']  # Get all 'biti' nodes

        if len(biti_nodes) == 1:  # Single 'biti' node case
            biti_node = biti_nodes[0]
            
            if verb:
                # Determine progressive aspect
                if head_feats['VerbForm'] == 'Ger' or (head_feats['VerbForm'], head_feats.get('Tense',None)) == ('Part', 'Pres'):
                    feats['Aspect'] = 'Prog'
                # Determine passive voice
                elif (head_feats['VerbForm'], head_feats.get('Tense',None)) == ('Part', 'Past'):
                    feats['Voice'] = 'Pass'
                # Handle finite "biti"
                elif biti_node['feats']['VerbForm'] == 'Fin':
                    feats['Tense'] = biti_node['feats'].get('Tense', 'Pres')  # Default to 'Pres'
                    feats['Mood'] = biti_node['feats'].get('Mood', 'Ind')  # Default to 'Ind'
                    feats['Aspect'] = feats.get('Aspect', 'Imp')  # Default to 'Imp'
                else:
                    # New fallback for unexpected cases
                    feats['Tense'] = biti_node['feats'].get('Tense', 'Pres')
                    feats['Mood'] = biti_node['feats'].get('Mood', 'Ind')
                    feats['Aspect'] = feats.get('Aspect', 'Imp')
                    print(f"Unhandled single 'biti' case fallback applied. Node: {biti_node}")
            higher_biti = biti_node  # Single 'biti' node is the higher auxiliary

        elif len(biti_nodes) >= 2:  # Two or more 'biti' nodes
            # Default to progressive aspect for multiple "biti"
            feats['Aspect'] = 'Prog'

            # Voice determination: check if the head is a past participle
            if verb and head_feats['VerbForm'] == 'Part' and head_feats['Tense'] == 'Past':
                feats['Voice'] = 'Pass'

            # Sort "biti" nodes by syntactic position
            biti_nodes.sort(key=lambda x: x['id'])

            # Look for conditional "bi"
            higher_biti = next((node for node in biti_nodes if node['form'].startswith('bi')), biti_nodes[0])

        # Set default voice if not determined
        if 'Voice' not in feats and verb:
            feats['Voice'] = 'Act'

        # Transfer features from higher auxiliary "biti"
        if not aux_lemmas - {'biti', 'not'} and feats.get('VerbForm') != 'Inf':
            if 'Tense' in higher_biti['feats']:
                feats['Tense'] = higher_biti['feats']['Tense']
            if not verb:
                if 'Mood' not in feats and 'Mood' in higher_biti['feats']:
                    feats['Mood'] = higher_biti['feats']['Mood']
                if 'VerbForm' not in feats and 'VerbForm' in higher_biti['feats']:
                    feats['VerbForm'] = higher_biti['feats']['VerbForm']

        aux_lemmas.discard('biti')  # Remove 'biti' from auxiliary lemmas

    #discourse particles I'm nost sure what to do with
    discourse_part = {"bilo","li","i","ni","niti","zar","tako","god","evo",'valjda','npr.',
                      'dakle','naime','tj.','možda','čak','štaviše','međutim'}
    if discourse_part&aux_lemmas:
        for p in discourse_part:
            if p in aux_lemmas:
                aux_lemmas.discard(p)
 
    if 'hteti' in aux_lemmas:
        feats['Tense'] = 'Fut'
    aux_lemmas.discard('hteti')

    # treatment of modality
    if aux_lemmas:
        to_remove=set()
        for lemma in aux_lemmas: # look up in modalities
            modality = modalities[lemma]
            to_remove.add(lemma)
        aux_lemmas=aux_lemmas-to_remove

        #not sure if this is likely to happen in Serbian or not (I see somehwere modals can be marked negative on the verb instead of particle)
        if 'ne' in aux_lemmas: # if there is a negation marker, set the modality to negative and remove the Polarity feature
            modality = f'neg({modality})'
            del feats['Polarity']
        aux_lemmas.discard('ne')

        feats['Mood'] += ';' + modality  # add the modality to the mood
        feats['Mood'] = feats['Mood'].strip(';')  # clean up the mood

    else:
        aux_lemmas.discard('ne')

    if aux_lemmas:
        raise ValueError(f'untreated auxiliaries. their lemmas: {aux_lemmas}')

    feats = {k: v.strip(';') for k, v in feats.items() if v}

    return feats


def copy_feats(ms_feats, morpho_feats, values):
    '''
    copies features from morpho_feats to ms_feats only is they do not exist in morpho_feats.
    '''
    for value in values:
        ms_feats[value] = ms_feats.get(value, morpho_feats.get(value, None))
    return ms_feats


def set_nodes(nodes):
    '''
    conllu.Token is not hashable so sets consist of ids
    '''
    return {node['id'] for node in nodes}


def combine_fixed_nodes(head, fixed_children):
    '''
    In cases where several function words are combined to one meaning (e.g., because of, more then) they are tagged with
     a 'fixed' deprel and are combined to one temporary lemma to look for in the relevant map in 'eng_relations.py'.
    '''
    if not fixed_children:
        return head['lemma']

    l = [head] + fixed_children
    l.sort(key=lambda node: node['id'])
    return ' '.join([node['lemma'] for node in l])


def apply_grammar(head: conllu.Token, children: List[conllu.Token]):
    '''
    The main method combining functional children to create the morpho-syntactic features of head.
    '''

    children = [child for child in children if not child['deprel'] in {'parataxis', 'reparandum', 'punct'}] # remove punctuation and parataxis and reparandum

    fixed_children = [child for child in children if child['deprel'] == 'fixed']
    head['fixed lemma'] = combine_fixed_nodes(head, fixed_children) # combine the fixed nodes to one lemma for further processing
    children = [child for child in children if child['deprel'] != 'fixed'] # remove the fixed nodes from the children

    added_nodes = []

    verb = head['upos'] in VERBAL
    #Treat personal pronouns like nouns
    noun = head['upos'] in NOMINAL 

    if verb: # only if the head is not a verb, copy the existing features to ms_feats
        head['ms feats'] = {}
    else:
        head['ms feats'] = deepcopy(head['feats'])

    # if there are auxiliaries "consume" them to change head's feats
    TAM_nodes = [child for child in children if (child['upos'] in {'AUX', 'PART'} and child['deprel'] != "advmod")] 
    if TAM_nodes and head['upos'] not in ("SCONJ","PART"):
        head['ms feats'].update(get_nTAM_feats(TAM_nodes, head['feats'], verb=verb)) # update the head's features with the features of the auxiliaries

        if not head['ms feats'].get('Mood', None): head['ms feats']['Mood'] = 'Ind' #set Mood to Ind by default
        if not head['ms feats'].get('Polarity', None): head['ms feats']['Polarity'] = 'Pos' #set Polarity to Pos by default
        if not head['ms feats'].get('VerbForm', None): head['ms feats']['VerbForm'] = 'Fin' #set VerbForm to Fin by default

    # if there are cases or conjunctures "consume" them as well
    relation_nodes = [child for child in children if
                      (child['deprel'] in {'case', 'mark', 'cc'}
                      or child['lemma'] in case_feat_map)
                      and (child['upos'] not in ['PART','CCONJ'])]

    if relation_nodes:
        to_update = get_relation_feats(relation_nodes, verb=verb, clause=head['deprel'] in clausal_rels)
        if to_update and not head['ms feats']:
            head['ms feats'] = to_update
        else:
            head['ms feats'].update(to_update)

    # make sure we did not use the same node twice
    assert not set_nodes(TAM_nodes) & set_nodes(relation_nodes)
    children = [node for node in children if node not in relation_nodes + TAM_nodes] # remove the auxiliaries and the relations from the children

    if verb:
        # copy values from the morphological feats if they were not set by now
        head['ms feats'] = copy_feats(head['ms feats'], head['feats'], ['Mood','Tense','Aspect','Voice','VerbForm','Polarity'])

        # set default values for feats underspecified in UD
        if not head['ms feats'].get('Voice', None): head['ms feats']['Voice'] = 'Act'

        if (
            head['ms feats']['VerbForm'] == 'Fin' and 
            not any(child['deprel'] in {'nsubj', 'nsubj:pass'} for child in children) and
            not any(child['deprel'] == 'parataxis' for child in children) and 
            not any(child['deprel'] == 'cop' and child['lemma'] == 'biti' for child in children) and
            head['deprel'] not in {'advcl', 'ccomp', 'acl', 'xcomp'} and
            not any(child['deprel'] == 'xcomp' and child['lemma'] == 'prihvatiti' for child in children) and
            head['feats'].get('Person', None) != '3' 
        ):
            abstract_nsubj = create_abstract_nsubj(head, TAM_nodes)
            if abstract_nsubj:
                added_nodes.append(abstract_nsubj)

    elif noun or head['upos'] in {'ADV', 'ADJ'}:
        # treat determiners
        det_nodes = [child for child in children if child['deprel'] == 'det']
        other_advmod = [child for child in children if child['deprel']=='advmod' and child['upos'] not in ["ADV"]]

        if det_nodes:

            #assert len(det_nodes) == 1 # in eng script this was here, seems like in Serbian it doesn't need to be the case ("Neki Njegovi")
            for det_node in det_nodes:
                children = [node for node in children if node != det_node]
                for k,v in list(determiners[det_node['lemma']].items()):
                    head['ms feats'][k] = v

        if other_advmod:
            for node in other_advmod:
                if node['lemma']=="sve":
                    #somehow indicate there's an intensifier..
                    head['ms feats']["Intense"]="Yes"

    if head['ms feats']: # clean up the ms_feats by removing None values
        head['ms feats'] = {k: v for k, v in head['ms feats'].items() if v}

    for child in children:
        if child['upos'] in {'ADV', 'ADJ', 'INTJ', 'X',"SYM"} | VERBAL | NOMINAL and not child.get('ms feats', None): # if the child is a content node and the ms_feats are not set
            ms_feats = deepcopy(child['feats']) # copy the features from the child's feats
            if ms_feats is None: # if the child has no feats, set the feats to an separator
                ms_feats = '|'
            child['ms feats'] = ms_feats
        

    del head['fixed lemma']

    return added_nodes


def get_where_to_add(added_nodes, id2idx): # get where to add the abstract nsubj, right now before the verb
    res = []
    for node in added_nodes:
        idx = int(node['id'])
        if idx == 0:
            res.append(-1)
        else:
            res.append(id2idx[idx])
    return res

def order_alphabetically(feats: str):
    feats = [f"{k}={v}" for k,v in list(feats.items())]
    feats = sorted(feats)
    return '|'.join(feats)

if __name__ == '__main__':

    split = sys.argv[1]
    
    # filepath = os.path.join(ud_dir, lang, bank, splits[bank]['test'])
    # out_path = os.path.join('UD+', lang, bank, 'test.conllu')
    with open(f"../../../UD_Serbian-SET/sr_set-ud-{split}.conllu", encoding='utf8') as f:
        parse_trees = list(conllu.parse_tree_incr(f))
    with open(f"../../../UD_Serbian-SET/sr_set-ud-{split}.conllu", encoding='utf8') as f:
        parse_lists = list(conllu.parse_incr(f))

    assert len(parse_lists) == len(parse_trees)
    with open(f"../../data/serbian/{split}.out.conllu", 'w', encoding='utf8') as outfile:
        for i in range(len(parse_trees)): # iterate over the sentences
            parse_tree = parse_trees[i]
            parse_list: conllu.TokenList = parse_lists[i]

            id2idx = {token['id']:i for i, token in enumerate(parse_list) if isinstance(token['id'], int)}
            idx2id = [token['id'] if isinstance(token['id'], int) else None for token in parse_list]

            heads = utils.span(parse_tree)
            assert utils.verify_span(heads)
            to_add = []
            for head, children in heads[::-1]:
                head: conllu.Token = parse_list[id2idx[head]]
                children = [parse_list[id2idx[child]] for child in children]
                added_nodes = apply_grammar(head, children)
                if added_nodes:
                    added_idxs = get_where_to_add(added_nodes, id2idx)
                    to_add += list(zip(added_nodes, added_idxs))

            for added_node in to_add[::-1]:
                node, idx = added_node
                parse_list.insert(idx + 1, node)

            for node in parse_list:
                # setting ms-feats for content nodes that were not dealt with earlier
                if ((node['upos'] in {'ADJ', 'INTJ'} | VERBAL | NOMINAL) or (node['upos']=="CCONJ" and node['deprel']=="discourse")) and not node.get('ms feats', None): # if the node is a content node and the ms_feats are not set
                    ms_feats = deepcopy(node['feats'])
                    if ms_feats is None:
                        ms_feats = '|'
                    node['ms feats'] = ms_feats
                # function nodes end up with empty ms-feats
                else:
                    node['ms feats'] = node.get('ms feats', None)

                # sort alphabetically the MS features of all nodes
                if node['ms feats'] and len(node["ms feats"])>1:
                    node['ms feats'] = order_alphabetically(node['ms feats'])

            to_write = parse_list.serialize()
            outfile.write(to_write + '\n')