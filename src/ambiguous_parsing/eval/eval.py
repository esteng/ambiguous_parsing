import argparse
import pathlib
import json 
import pdb 
from collections import defaultdict

import pandas as pd 

from ambiguous_parsing.tree.formula import FOLFormula, LispFormula

def read_jsonl(path):
    with open(path, "r") as f:
        return [json.loads(line) for line in f]

def safe_divide(a,b):
    if b == 0:
        return 0
    return a/b

def format_report(scores_by_type):
    for ex_type, score_dict in scores_by_type.items():
        print(f"Type: {ex_type}")
        total = score_dict['total']
        pred_top_1_matches_correct = score_dict['pred_top_1_matches_correct']
        pred_top_2_matches_correct = score_dict['pred_top_2_matches_correct']
        pred_top_1_matches_0 = score_dict['pred_top_1_matches_0']
        pred_top_1_matches_1 = score_dict['pred_top_1_matches_1']
        pred_top_1_matches_other = score_dict['pred_top_1_matches_other']
        pred_top_2_matches_other = score_dict['pred_top_2_matches_other']
        correct_in_top_k = score_dict['correct_in_top_k']
        other_in_top_k = score_dict['other_in_top_k']

        print(f"\tpred_top_1_matches_correct: {pred_top_1_matches_correct} / {total} = {safe_divide(pred_top_1_matches_correct, total) *100:.2f}")
        print(f"\tpred_top_1_matches_other: {pred_top_1_matches_other} / {total} = {safe_divide(pred_top_1_matches_other, total) *100:.2f}")
        print(f"\tpred_top_1_matches_0: {pred_top_1_matches_0} / {total} = {safe_divide(pred_top_1_matches_0, total) *100:.2f}")
        print(f"\tpred_top_1_matches_1: {pred_top_1_matches_1} / {total} = {safe_divide(pred_top_1_matches_1, total) *100:.2f}")

        print(f"\tpred_top_2_matches_other: {pred_top_2_matches_other} / {total} = {safe_divide(pred_top_2_matches_other, total) *100:.2f}")
        print(f"\tpred_top_2_matches_correct: {pred_top_2_matches_correct} / {total} = {safe_divide(pred_top_2_matches_correct, total) *100:.2f}")
        print(f"\tcorrect_in_top_k: {correct_in_top_k} / {total} = {safe_divide(correct_in_top_k, total) *100:.2f}")
        print(f"\tother_in_top_k: {other_in_top_k} / {total} = {safe_divide(other_in_top_k, total) *100:.2f}")
        print("=====================================")

def rerender(lf: str, is_fol: bool = False) -> str:
    if is_fol:
        formula = FOLFormula.parse_formula(lf) 
    else:
        formula = LispFormula.parse_formula(lf)
        # cast to FOLFormula, more readable 
        formula = FOLFormula.from_formula(formula)

    return formula.render()

def get_score_data(test_data, pred_data, test_data_lut, is_fol=False):
    scores_by_type = defaultdict(lambda: defaultdict(int))
    missing_second = 0
    missing_first = 0
    for datum_idx, (test_datum, pred_datum) in enumerate(zip(test_data,  pred_data)):
        # go through and get the predictions
        top_k_outputs = pred_datum['outputs']
        for i, output in enumerate(top_k_outputs):
            try:
                output = rerender(output, is_fol)
                top_k_outputs[i] = output
            except (ValueError, IndexError, AssertionError, KeyError) as e:
                pass 

        cand_lfs = test_data_lut[test_datum['surface']]
        ex_type = test_datum['type']
        correct_lf_idx = test_datum['template_idx']
        correct_lf = cand_lfs[correct_lf_idx]['lf']

        correct_lf = rerender(correct_lf, is_fol)
        try:
            other_lf = cand_lfs[1 - correct_lf_idx]['lf'] 
            other_lf = rerender(other_lf, is_fol)
        except (IndexError, ValueError, AssertionError, KeyError) as e:
            #pdb.set_trace()
            assert(len(cand_lfs) == 1)
            other_lf = None

        # if pred_datum['metrics']['exact_match/rank1'] == "correct":
        #     pdb.set_trace()

        # do checks 
        try:
            pred_top_1_matches_correct = top_k_outputs[0] == correct_lf
            pred_top_1_matches_other = top_k_outputs[0] == other_lf
            pred_top_1_matches_0 = top_k_outputs[0] == cand_lfs[0]['lf']
            if other_lf is not None:
                pred_top_1_matches_1 = top_k_outputs[0] == cand_lfs[1]['lf']
            else:
                pred_top_1_matches_1 = False
        except IndexError:
            missing_first += 1
            pred_top_1_matches_correct = False
            pred_top_1_matches_other = False
            pred_top_1_matches_0 = False
            pred_top_1_matches_1 = False
        try:
            pred_top_2_matches_correct = top_k_outputs[1] == correct_lf
            pred_top_2_matches_other = top_k_outputs[1] == other_lf
        except IndexError:
            missing_second += 1
            # no second output
            pred_top_2_matches_correct = False
            pred_top_2_matches_other = False

        correct_in_top_k = correct_lf in top_k_outputs
        other_in_top_k = other_lf in top_k_outputs
        # update scores by type
        scores_by_type[ex_type]['pred_top_1_matches_correct'] += pred_top_1_matches_correct
        scores_by_type[ex_type]['pred_top_2_matches_correct'] += pred_top_2_matches_correct
        scores_by_type[ex_type]['pred_top_1_matches_other'] += pred_top_1_matches_other
        scores_by_type[ex_type]['pred_top_2_matches_other'] += pred_top_2_matches_other
        scores_by_type[ex_type]['pred_top_1_matches_0'] += pred_top_1_matches_0
        scores_by_type[ex_type]['pred_top_1_matches_1'] += pred_top_1_matches_1
        scores_by_type[ex_type]['correct_in_top_k'] += correct_in_top_k
        scores_by_type[ex_type]['other_in_top_k'] += other_in_top_k
        scores_by_type[ex_type]['total'] += 1

            
    print(f"{missing_first} = {missing_first / len(pred_data) * 100 :.2f} are missing a first output")
    print(f"{missing_second} = {missing_second / len(pred_data) * 100 :.2f} are missing a second output")

    return scores_by_type

def get_df(test_file, eval_file, pred_file, is_fol):
    test_data = read_jsonl(test_file)
    eval_data = read_jsonl(eval_file)
    pred_data = read_jsonl(pred_file)

    # make test data lookup 
    test_data_lut = defaultdict(list)
    for datum in eval_data:
        test_data_lut[datum['surface']].append(datum)
    assert(len(test_data) == len(pred_data))

    scores_by_type = get_score_data(test_data, pred_data, test_data_lut, is_fol)
    df_data = []
    for ex_type, data_dict in scores_by_type.items():
        for key, count in data_dict.items():
            df_data.append({"type": ex_type, "key": key, "value": count})
    return pd.DataFrame(df_data)

if __name__ == "__main__": 
    parser = argparse.ArgumentParser()
    parser.add_argument("--test_file", type=pathlib.Path, required=True, help="path to test jsonl file that was used to make predictions(no bclamp processing)")
    parser.add_argument("--eval_file", type=pathlib.Path, required=True, help="path to test eval jsonl file that has all of the interpretations") 
    parser.add_argument("--pred_file", type=pathlib.Path, required=True, help="path to prediction jsonl file")
    parser.add_argument("--is_fol", action="store_true", help="predictions are in FOL format")
    args = parser.parse_args()

    test_data = read_jsonl(args.test_file)
    eval_data = read_jsonl(args.eval_file)
    pred_data = read_jsonl(args.pred_file)

    # make test data lookup 
    test_data_lut = defaultdict(list)
    for datum in eval_data:
        test_data_lut[datum['surface']].append(datum)
    assert(len(test_data) == len(pred_data))

    scores_by_type = get_score_data(test_data, pred_data, test_data_lut, args.is_fol)
    format_report(scores_by_type)
