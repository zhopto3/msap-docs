def process(head_tok, children_toks):

	head_tok["ms feats"]["HEAD"] = head_tok["id"]

	for child_tok in children_toks:
		child_tok["ms feats"]["HEAD"] = head_tok["id"]