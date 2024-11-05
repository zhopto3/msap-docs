import logging

import code.italian.ita_utils as ita_utils

logger = logging.getLogger(__name__)

def process_verb(head_tok, children_toks):

	head_tok["ms feats"]["tmp-head"].add("VERB")

	for child_tok in children_toks:
		child_tok["ms feats"]["tmp-child"].add("VERB")
