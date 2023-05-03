import numpy as np 
import pandas as pd 
import pdb 
from pathlib import Path
from collections import defaultdict 
from typing import List, Dict, Tuple, Any

from ambiguous_parsing.metrics.metric import DatasetMetric, InstanceMetric
from ambiguous_parsing.eval.eval import get_score_data
from ambiguous_parsing.eval.utils import read_jsonl, convert_benchclamp_gold, convert_benchclamp_pred, read_logits_file

class FewshotDatasetMetric(DatasetMetric):
    def __init__(self):
        super().__init__()
        self.df_data = []

    def __call__(self, 
                pred_data: List[Any], 
                gold_data: List[Any], 
                gold_data_lut: Dict[str, Any], 
                ratio: float, 
                is_fol: bool = True):

        scores_by_type = get_score_data(gold_data, pred_data, gold_data_lut, is_fol=is_fol, convert=False)
        for ex_type, data_dict in scores_by_type.items():
            for key, count in data_dict.items():
                self.df_data.append({"ratio": ratio, "type": ex_type, "key": key, "value": count})


    def get_metric(self) -> float:
        metric_dict = defaultdict(list)
        df = pd.DataFrame(self.df_data)
        # take average for each ratio across for key = "pred_top_1_matches_lf_0"
        for ratio in self.df["ratio"].unique():
            for amb_type in self.df["type"].unique():
                sub_df = df[df['ratio'] == ratio]
                sub_df = sub_df[sub_df['type'] == amb_type]
                lf0_df = sub_df[sub_df['key'] == 'pred_top_1_matches_lf_0']
                lf1_df = sub_df[sub_df['key'] == 'pred_top_1_matches_lf_1']
                lf0_avg = lf0_df['value'].mean()/100
                lf1_avg = lf1_df['value'].mean()/100
                lf0_diff = np.abs(lf0_avg - ratio)
                lf1_diff = np.abs(lf1_avg - (1-ratio))
                metric_val = lf0_diff + lf1_diff
                metric_dict[amb_type].append(metric_val)

        metric_dict = {k:np.mean(v) for k, v in metric_dict.items()}

        return metric_dict

class FewshotInstanceMetric(InstanceMetric):
    def __init__(self):
        super().__init__()
        self.df_data = []

    def __call__(self, 
                data_by_src: Dict[str, Dict], 
                test_data_lut: Dict[str, Dict], 
                ratio: float):

        for src, lines in data_by_src.items():
            try:
                gold_line = test_data_lut[src]['0']
            except KeyError:
                continue

            amb_type = gold_line['type']
            min_lf0, min_lf1 = None, None
            for line in lines:
                template_idx = str(line['template_idx'])

                min_logit_at_label = np.min(line['logit_at_label']) 
                if template_idx == '0':
                    min_lf0 = min_logit_at_label
                else:
                    min_lf1 = min_logit_at_label

            # turn into a proper probability by normalizing 
            norm_min_p_lf0 = min_lf0 / (min_lf0 + min_lf1)
            self.df_data.append({"ratio": ratio, "type": amb_type, "pred_p_lf0": norm_min_p_lf0})

    def get_metric(self) -> float:
        df = pd.DataFrame(self.df_data)
        metric_dict = defaultdict(list)
        for ratio in df["ratio"].unique():
            for amb_type in df["type"].unique():
                sub_df = df[df['ratio'] == ratio]
                sub_df = sub_df[sub_df['type'] == amb_type]
                sub_df['diff'] = np.abs(sub_df['ratio'] - sub_df['pred_p_lf0'])
                metric_dict[amb_type].append(sub_df['diff'].mean())
        metric_dict = {k: np.mean(v) for k,v in metric_dict.items()}
        return metric_dict

if __name__ == "__main__":
    fewshot = False

    if fewshot:
        CHECKPOINT_DIR= Path("/brtx/602-nvme1/estengel/ambiguous_parsing/logs/1.0/") 
        fol_models_and_paths = [
            ("0-100", "codegen-2B_lamp_no_context_all_0-100-5k-train-100-perc-ambig_fol_fewshot_2_test_eval_constrained_bs_5_np_10/"),
            ("10-90", "codegen-2B_lamp_no_context_all_10-90-5k-train-100-perc-ambig_fol_fewshot_2_test_eval_constrained_bs_5_np_10/"),
            ("20-80", "codegen-2B_lamp_no_context_all_20-80-5k-train-100-perc-ambig_fol_fewshot_2_test_eval_constrained_bs_5_np_10/"),
            ("30-70", "codegen-2B_lamp_no_context_all_30-70-5k-train-100-perc-ambig_fol_fewshot_2_test_eval_constrained_bs_5_np_10/"),
            ("40-60", "codegen-2B_lamp_no_context_all_40-60-5k-train-100-perc-ambig_fol_fewshot_2_test_eval_constrained_bs_5_np_10/"),
            ("50-50", "codegen-2B_lamp_no_context_all_50-50-5k-train-100-perc-ambig_fol_fewshot_2_test_eval_constrained_bs_5_np_10/"),
            ("60-40", "codegen-2B_lamp_no_context_all_60-40-5k-train-100-perc-ambig_fol_fewshot_2_test_eval_constrained_bs_5_np_10/"),
            ("70-30", "codegen-2B_lamp_no_context_all_70-30-5k-train-100-perc-ambig_fol_fewshot_2_test_eval_constrained_bs_5_np_10/"),
            ("80-20", "codegen-2B_lamp_no_context_all_80-20-5k-train-100-perc-ambig_fol_fewshot_2_test_eval_constrained_bs_5_np_10/"),
            ("90-10", "codegen-2B_lamp_no_context_all_90-10-5k-train-100-perc-ambig_fol_fewshot_2_test_eval_constrained_bs_5_np_10/"),
            ("100-0", "codegen-2B_lamp_no_context_all_100-0-5k-train-100-perc-ambig_fol_fewshot_2_test_eval_constrained_bs_5_np_10/"),
        ]
        # all test files are same 
        fol_test_path = "/brtx/602-nvme1/estengel/ambiguous_parsing/data/raw/50-50-5k-train-100-perc-ambig_fol/test.jsonl"
        fol_eval_path = "/brtx/602-nvme1/estengel/ambiguous_parsing/data/raw/50-50-5k-train-100-perc-ambig_fol/test_eval.jsonl"

        metric = FewshotDatasetMetric()

        for model_name, path in fol_models_and_paths:
            pred_path = CHECKPOINT_DIR / path
            ratio = int(model_name.split("-")[0])

            if str(pred_path).endswith(".jsonl"):
                pred_file = pred_path
            else:
                pred_path = Path(pred_path)
                # list the files alphabetically and take the last one
                pred_files = sorted(pred_path.glob("*.jsonl"))
                pred_file = pred_files[-1]

            test_data = read_jsonl(fol_test_path)
            eval_data = read_jsonl(fol_eval_path)
            pred_data = read_jsonl(pred_file)


            # make test data lookup 
            test_data_lut = defaultdict(dict)
            for datum in eval_data:
                test_data_lut[datum['surface']][str(datum['template_idx'])] = datum
            assert(len(test_data) == len(pred_data))

            test_data = convert_benchclamp_gold(test_data, test_data_lut, is_fol=True)
            pred_data = convert_benchclamp_pred(pred_data, is_fol=True)

            metric(pred_data, test_data, test_data_lut, ratio = ratio/100, is_fol=True)

        print(metric.get_metric())
    else: 
        metric = FewshotInstanceMetric()

        for model in ["codegen-350M", "codegen-2B", "codegen-6B", "codegen-16B"]:
            for s1 in range(0, 110, 10):
                s2 = 100 - s1

                fol_eval_path = f"/brtx/602-nvme1/estengel/ambiguous_parsing/data/raw/{s1}-{s2}-5k-train-100-perc-ambig_fol/test_eval.jsonl"
                eval_data = read_jsonl(fol_eval_path)
                test_data_lut = defaultdict(dict)
                for datum in eval_data:
                    test_data_lut[datum['surface']][str(datum['template_idx'])] = datum
                    
                path = f"/brtx/602-nvme1/estengel/ambiguous_parsing/model_outputs/{model}/{s1}-{s2}-5k-train-100-perc-ambig_fol_fewshot/outputs/test_eval.logits"
                print(f"reading {path}")
                try:
                    data_by_src = read_logits_file(path)
                except FileNotFoundError:
                    print(f"file not found: {path}")
                    continue

                metric(data_by_src, test_data_lut, ratio = s1/100)

        print(metric.get_metric())