import logging

import code.italian.lemma_based_decisions as lbd

logger = logging.getLogger(__name__)

def process_verb(head_tok, children_toks):

	head_tok["ms feats"]["tmp-head"].append("VERB")

	for child_tok in children_toks:
		child_tok["ms feats"]["tmp-child"].append("VERB")

def process_noun(head_tok, children_toks):

	# head_tok["ms feats"]["tmp-head"].append("NOUN")

	# keep existing features for all nominals
	if head_tok.get("feats"):
		for feat in head_tok["feats"]:
			head_tok["ms feats"][feat].append(head_tok["feats"][feat])
	else:
		logger.warning("Head %s has no features", head_tok)

	for child_tok in children_toks:

		# determiners
		if child_tok["deprel"] == "det":

			# add definiteness
			if "Definite" in child_tok["feats"]:
				head_tok["ms feats"]["Definite"].append(child_tok["feats"]["Definite"])
			else:
				logger.warning("DET %s with features %s", child_tok, child_tok["feats"])

		# case relations
		elif child_tok["deprel"] == "case":
			head_tok["ms feats"]["Case"].append(lbd.switch_nominal_case(child_tok))
			# print(child_tok, child_tok["feats"])
			# input()

		else:
			logger.info("Node %s needs new rules", child_tok)
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