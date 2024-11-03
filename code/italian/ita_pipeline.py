import logging

import code.italian.lemma_based_decisions as lbd

logger = logging.getLogger(__name__)

def copy_features(node):
	if node.get("feats"):
		for feat in node["feats"]:
			node["ms feats"][feat].append(node["feats"][feat])
	else:
		logger.warning("Node %s has no features", node)


def process_verb(head_tok, children_toks):

	head_tok["ms feats"]["tmp-head"].append("VERB")

	for child_tok in children_toks:
		child_tok["ms feats"]["tmp-child"].append("VERB")

def process_noun(head_tok, children_toks):

	# keep existing features for all nominals
	copy_features(head_tok)

	for child_tok in children_toks:
		logger.debug("Examining child: %s", child_tok)
		# determiners
		if child_tok["deprel"] == "det":
			# add definiteness
			if "Definite" in child_tok["feats"]:
				logger.debug("Adding Definite feature with value %s", child_tok["feats"]["Definite"])
				head_tok["ms feats"]["Definite"].append(child_tok["feats"]["Definite"])
			else:
				logger.warning("DET %s with features %s", child_tok, child_tok["feats"])

		# case relations
		elif child_tok["deprel"] == "case":
			logger.debug("Adding Case feature with value %s", lbd.switch_nominal_case(child_tok))
			head_tok["ms feats"]["Case"].append(lbd.switch_nominal_case(child_tok))
			# print(child_tok, child_tok["feats"])
			# input()

		elif child_tok["upos"] in ["NOUN", "PROPN"]:
			logger.debug("Switching node to content and keeping its features")
			copy_features(child_tok)
			child_tok["content"] = True

		else:
			logger.warning("Node %s/%s needs new rules", child_tok, child_tok["upos"])
			child_tok["ms feats"]["tmp-child"].append("NOUN")


def process_adj(head_tok, children_toks):

	head_tok["ms feats"]["tmp-head"].append("ADJ")

	for child_tok in children_toks:
		child_tok["ms feats"]["tmp-child"].append("ADJ")

def process_adv(head_tok, children_toks):

	logging.info("Here")

	head_tok["ms feats"]["tmp-head"].append("ADV")

	for child_tok in children_toks:
		child_tok["ms feats"]["tmp-child"].append("ADV")
