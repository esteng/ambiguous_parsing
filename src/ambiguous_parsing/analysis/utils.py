from collections import defaultdict
import re 
import numpy as np 

def detokenize(tokenizer,
               delimiter: str, 
               top_logits: np.array, 
               tokens: np.array,
               agg_fxn=np.min):
            
    tokens = tokenizer.convert_ids_to_tokens(tokens)
    # convert to detokenized 
    tok_idx_to_str_idx = {}
    str_idx_to_tok_idx = defaultdict(list)
    str_toks = []
    curr_tok = []
    str_idx = -1

    # add last token
    str_toks.append(curr_tok)
    for i, tok in enumerate(tokens):
        if tok is None:
            print("None token")
            continue
        # is not a subword 
        if tok.startswith(delimiter):
            if len(curr_tok) > 0:
                str_toks.append(curr_tok)
            # start of a new token  
            curr_tok = [tok]
            str_idx += 1
            tok_idx_to_str_idx[i] = str_idx
            str_idx_to_tok_idx[str_idx].append(i)

        # is a subword 
        else:
            # add to curr tok
            curr_tok.append(tok)
            tok_idx_to_str_idx[i] = str_idx
            str_idx_to_tok_idx[str_idx].append(i) 

    # add last token
    str_toks.append(curr_tok)
    token_ids = np.ones(len(tokens)) * -1
    for i, token in enumerate(str_toks): 
        token = "".join(token).upper()
        token = re.sub(f"^{delimiter}", "", token)
        mapping_idxs = str_idx_to_tok_idx[i]
        # rules:
        for idx in mapping_idxs:
            token_ids[idx] = i

    # average logits for each token 
    new_types = []
    new_tokens = []
    new_top_logits = []
    prev_id = -1
    curr_logits = []
    for token_id, top_logit in zip(token_ids, top_logits):
        if token_id != prev_id and len(curr_logits) > 0:
            # new token, check old token  
            # average logits 
            mean_logit = agg_fxn(curr_logits)

            new_types.append(type)
            new_tokens.append(prev_id)
            new_top_logits.append(mean_logit)
            # whole token correct iff idxs all are correct 
            # is_correct = np.all(self.check_tokens(curr_idxs, curr_labs))
            # new_is_correct.append(is_correct)     
            # initialize with new token
            curr_logits = [top_logit]
        else:
            # add 
            curr_logits.append(top_logit)

        prev_id = token_id

    # once at the end       
    # average logits 
    mean_logit = agg_fxn(curr_logits)
    new_tokens.append(token_id)
    new_top_logits.append(mean_logit)
    # is_correct = True
    # whole token correct iff idxs all are correct 
    # is_correct = np.all(self.check_tokens(curr_idxs, curr_labs))
    # new_is_correct.append(is_correct)     

    top_logits = np.array(new_top_logits)     
    # is_correct = np.array(new_is_correct)
    new_toks = str_toks[1:]
    new_toks = [re.sub(delimiter, "", "".join(tok)) for tok in new_toks]
    return top_logits, new_toks

def detect_amb_type(inp_str):
    if inp_str.startswith("every") or inp_str.startswith('each'):
        return "scope"
    elif "every" in inp_str or "each" in inp_str:
        return "revscope"
    elif "with the" in inp_str:
        return "pp"
    else:
        return "bound"