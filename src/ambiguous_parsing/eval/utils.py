import json 
import numpy as np 
from collections import defaultdict
from ambiguous_parsing.tree.formula import FOLFormula, LispFormula

def read_jsonl(path):
    with open(path, "r") as f:
        return [json.loads(line) for line in f]

def safe_divide(a,b):
    if b == 0:
        return 0
    return a/b

def rerender(lf: str, is_fol: bool = False) -> str:
    if is_fol:
        formula = FOLFormula.parse_formula(lf) 
    else:
        formula = LispFormula.parse_formula(lf)
        # cast to FOLFormula, more readable 
        formula = FOLFormula.from_formula(formula)

    return formula.render()

def convert_benchclamp_pred(pred_data, is_fol: bool = False): 
    """
    convert BenchClamp pred output format to metrics format 
    """
    to_ret = []
    # format: each line has a list of top-k outputs 
    for pred_datum in pred_data:
        top_k_outputs = pred_datum['outputs']
        for i, pred in enumerate(top_k_outputs):
            try:
                # rerender to canonicalize 
                top_k_outputs[i] = rerender(pred, is_fol=is_fol)
            except (ValueError, IndexError, AssertionError, KeyError) as e:
                # error, keep the original 
                top_k_outputs[i] = pred
        to_ret.append({"top_k_preds": top_k_outputs})
    return to_ret 

def convert_benchclamp_gold(gold_data, gold_data_lut, is_fol: bool = False): 
    """
    Convert gold file from BenchClamp format to metrics format 
    """
    # format: each line has lf0 and lf1 
    to_ret = []
    sniff_datum = gold_data[0]
    if "surface" in sniff_datum.keys():
        src_key = "surface"
        tgt_key = "lf"
    else:
        src_key = "utterance"
        tgt_key = "plan"
    for gold_datum in gold_data: 
        cand_lfs = gold_data_lut[gold_datum[src_key]]
        lf_0 = cand_lfs['0'][tgt_key]
        lf_0 = rerender(lf_0, is_fol)
        if len(cand_lfs) == 2:
            lf_1 = cand_lfs['1'][tgt_key]
            lf_1 = rerender(lf_1, is_fol)
        else:
            lf_1 = None
        line = {"lf0": lf_0,
                "lf1": lf_1,
                "type": gold_datum['type']}
        to_ret.append(line)
    return to_ret 

def read_logits_file(path):
    data_by_src = defaultdict(list)
    with open(path, "r") as f1:
        for line in f1:
            line = json.loads(line)
            # trim off last token (EOS)
            line['logit_at_label'] = np.array(line['logit_at_label'][0:-1])
            data_by_src[line['natural']].append(line)

    # for src, list_ in data_by_src.items():
        # assert(len(list_) == 2)

    return data_by_src
