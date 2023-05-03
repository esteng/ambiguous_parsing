import argparse
import pathlib
import json 
import pdb 
from collections import defaultdict

import pandas as pd 

from ambiguous_parsing.eval.utils import (
    read_jsonl, 
    safe_divide, 
    rerender,
    convert_benchclamp_pred,
    convert_benchclamp_gold,
)


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

def get_score_data(test_data, pred_data, test_data_lut, is_fol=False, convert = True):
    scores_by_type = defaultdict(lambda: defaultdict(int))
    missing_second = 0
    missing_first = 0

    if convert:
        test_data = convert_benchclamp_gold(test_data, test_data_lut, is_fol=is_fol)
        pred_data = convert_benchclamp_pred(pred_data, is_fol=is_fol)

    for datum_idx, (test_datum, pred_datum) in enumerate(zip(test_data,  pred_data)):
        # go through and get the predictions
        top_k_outputs = pred_datum['top_k_preds']

        lf_0, lf_1 = test_datum['lf0'], test_datum['lf1']
        ex_type = test_datum['type']

        # do checks 
        if len(top_k_outputs) == 0:
            missing_first += 1
            pred_top_1_matches_lf_0 = False
            pred_top_1_matches_lf_1 = False
            lf_1 = None
        else:
            pred_top_1_matches_lf_0 = top_k_outputs[0] == lf_0

        if lf_1 is not None:
            pred_top_1_matches_lf_1 = top_k_outputs[0] == lf_1
        else:
            pred_top_1_matches_lf_1 = False
        try:
            pred_top_2_matches_lf_0 = top_k_outputs[1] == lf_0
            pred_top_2_matches_lf_1 = top_k_outputs[1] == lf_1
        except IndexError:
            missing_second += 1
            # no second output
            pred_top_2_matches_lf_0 = False
            pred_top_2_matches_lf_1 = False

        lf_0_in_top_k = lf_0 in top_k_outputs
        lf_1_in_top_k = lf_1 in top_k_outputs
        # update scores by type
        scores_by_type[ex_type]['pred_top_1_matches_lf_0'] += pred_top_1_matches_lf_0
        scores_by_type[ex_type]['pred_top_2_matches_lf_0'] += pred_top_2_matches_lf_0
        scores_by_type[ex_type]['pred_top_1_matches_lf_1'] += pred_top_1_matches_lf_1
        scores_by_type[ex_type]['pred_top_2_matches_lf_1'] += pred_top_2_matches_lf_1
        scores_by_type[ex_type]['pred_top_1_matches_either'] += pred_top_1_matches_lf_0 or pred_top_1_matches_lf_1

        scores_by_type[ex_type]['lf_0_in_top_k'] += lf_0_in_top_k
        scores_by_type[ex_type]['lf_1_in_top_k'] += lf_1_in_top_k
        scores_by_type[ex_type]['total'] += 1

            
    print(f"{missing_first} = {missing_first / len(pred_data) * 100 :.2f} are missing a first output")
    print(f"{missing_second} = {missing_second / len(pred_data) * 100 :.2f} are missing a second output")

    # divide everything by the total
    for k, v in scores_by_type.items():
        for k2, v2 in v.items():
            if k2 == "total":
                continue
            v[k2] = safe_divide(v2, v['total']) * 100
        scores_by_type[k] = v 

    return scores_by_type

def get_df(test_file, eval_file, pred_path, is_fol):
    if str(pred_path).endswith(".jsonl"):
        pred_file = pred_path
    else:
        pred_path = pathlib.Path(pred_path)
        # list the files alphabetically and take the last one
        pred_files = sorted(pred_path.glob("*.jsonl"))
        pred_file = pred_files[-1]

    test_data = read_jsonl(test_file)
    eval_data = read_jsonl(eval_file)
    pred_data = read_jsonl(pred_file)

    # make test data lookup 
    test_data_lut = defaultdict(dict)
    for datum in eval_data:
        test_data_lut[datum['surface']][str(datum['template_idx'])] = datum
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
    test_data_lut = defaultdict(dict)
    for datum in eval_data:
        test_data_lut[datum['surface']][str(datum['template_idx'])] = datum
    assert(len(test_data) == len(pred_data))

    scores_by_type = get_score_data(test_data, pred_data, test_data_lut, args.is_fol)
    format_report(scores_by_type)
