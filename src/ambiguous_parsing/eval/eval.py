import argparse
import pathlib
import json 
from collections import defaultdict

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

def get_score_data(test_data, pred_data, test_data_lut):
    scores_by_type = defaultdict(lambda: defaultdict(int))
    for test_datum, pred_datum in zip(test_data,  pred_data):
        # go through and get the predictions
        top_k_outputs = pred_datum['outputs']
        cand_lfs = test_data_lut[test_datum['surface']]
        ex_type = test_datum['type']
        correct_lf_idx = test_datum['template_idx']
        correct_lf = cand_lfs[correct_lf_idx]['lf']
        try:
            other_lf = cand_lfs[1 - correct_lf_idx]['lf'] 
        except IndexError:
            assert(len(cand_lfs) == 1)
            other_lf = None
        # do checks 
        pred_top_1_matches_correct = top_k_outputs[0] == correct_lf
        pred_top_2_matches_correct = top_k_outputs[1] == correct_lf
        pred_top_1_matches_other = top_k_outputs[0] == other_lf
        pred_top_2_matches_other = top_k_outputs[1] == other_lf
        pred_top_1_matches_0 = top_k_outputs[0] == cand_lfs[0]['lf']
        if other_lf is not None:
            pred_top_1_matches_1 = top_k_outputs[0] == cand_lfs[1]['lf']
        else:
            pred_top_1_matches_1 = False
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
    return scores_by_type

if __name__ == "__main__": 
    parser = argparse.ArgumentParser()
    parser.add_argument("--test_file", type=pathlib.Path, required=True, help="path to test jsonl file (no bclamp processing)")
    parser.add_argument("--pred_file", type=pathlib.Path, required=True, help="path to prediction jsonl file")
    args = parser.parse_args()

    test_data = read_jsonl(args.test_file)
    pred_data = read_jsonl(args.pred_file)

    assert(len(test_data) == len(pred_data))
    # make test data lookup 
    test_data_lut = defaultdict(list)
    for datum in test_data:
        test_data_lut[datum['surface']].append(datum)

    scores_by_type = get_score_data(test_data, pred_data, test_data_lut)
    format_report(scores_by_type)