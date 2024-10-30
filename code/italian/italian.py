"""
usage (launch from msap-docs directory):
python code.italian.italian SOURCE_TREEBANK.conllu OUTPUT_FILEPATH

e.g.

python code.italian.italian data/italian/dev.conllu data/italian/dev.out.conllu
"""
import code.utils as utils
import code.italian.ita_pipeline as pipeline
import conllu


if __name__ == '__main__':
	import sys

	filepath = sys.argv[1]
	out_path = sys.argv[2]

	with open(filepath, encoding='utf8') as f:
		parse_trees = list(conllu.parse_tree_incr(f))

	with open(filepath, encoding='utf8') as f:
		parse_lists = list(conllu.parse_incr(f))

	with open(out_path, "w", encoding="utf-8") as fout:
		for tree, tokenlist in zip(parse_trees, parse_lists):
			for node in tokenlist:
				node["ms feats"] = {}

			# filter out useless nodes
			filtered_tokenlist = tokenlist.filter(id=lambda x: isinstance(x, int)).filter(deprel=lambda x: x != "punct")
			tree = filtered_tokenlist.to_tree()

			id2idx = {token['id']:i for i, token in enumerate(filtered_tokenlist)}
			idx2id = {y:x for x, y in id2idx.items()}

			heads = utils.span(tree)
			heads_dict = {}
			for element in heads:
				head, children = element
				heads_dict[head] = children

			assert utils.verify_span(heads) #TODO: a che serve?

			for head, children in heads_dict.items():
				head_tok = tokenlist[id2idx[head]]
				children_toks = [filtered_tokenlist[id2idx[child]] for child in children]

				pipeline.process(head_tok, children_toks)

				# TODO: here do stuff to update tree

			for node in tokenlist:
				if node.get("feats"):

					node_feats = node['feats']
					node_msfeats = node["ms feats"]

					for feat, value in node["feats"].items():
						if feat in node["ms feats"]:
							assert node["ms feats"][feat] == node["feats"][feat]
						else:
							node["ms feats"][feat] = node["feats"][feat]

				sorted_msfeats = sorted(node["ms feats"].items())
				sorted_msfeats = [f"{x}={y}" for x, y in sorted_msfeats]
				node['ms feats'] = "|".join(sorted_msfeats)

			to_write = tokenlist.serialize()
			print(to_write, file=fout)


	# with open(out_path, 'w', encoding='utf8') as outfile:
	#     for i in range(len(parse_trees)): # iterate over the sentences
	#         parse_tree = parse_trees[i]
	#         parse_list: conllu.TokenList = parse_lists[i]

	#         id2idx = {token['id']:i for i, token in enumerate(parse_list) if isinstance(token['id'], int)}
	#         idx2id = [token['id'] if isinstance(token['id'], int) else None for token in parse_list]

	#         heads = utils.span(parse_tree)
	#         assert utils.verify_span(heads)

	#         to_add = []
	#         for head, children in heads[::-1]:
	#             head: conllu.Token = parse_list[id2idx[head]]
	#             children = [parse_list[id2idx[child]] for child in children]
	#             added_nodes = apply_grammar(head, children)
	#             if added_nodes:
	#                 added_idxs = get_where_to_add(added_nodes, id2idx)
	#                 to_add += list(zip(added_nodes, added_idxs))

	#         for added_node in to_add[::-1]:
	#             node, idx = added_node
	#             parse_list.insert(idx + 1, node)

	#         for node in parse_list:
	#             # setting ms-feats for content nodes that were not dealt with earlier
	#             if node['upos'] in {'ADJ', 'INTJ'} | VERBAL | NOMINAL and not node.get('ms feats', None): # if the node is a content node and the ms_feats are not set
	#                 ms_feats = deepcopy(node['feats'])
	#                 if ms_feats is None:
	#                     ms_feats = '|'
	#                 node['ms feats'] = ms_feats
	#             # function nodes end up with empty ms-feats
	#             else:
	#                 node['ms feats'] = node.get('ms feats', None)

	#             # sort alphabetically the MS features of all nodes
	#             node['ms feats'] = order_alphabetically(node['ms feats'])
	#         assert utils.verify_treeness(parse_list)

	#         to_write = parse_list.serialize()
	#         outfile.write(to_write + '\n')
