from typing import List, Dict, Any, Tuple
import pdb
from pathlib import Path
from collections import defaultdict
import numpy as np
import pandas as pd

from ambiguous_parsing.eval.utils import read_jsonl, convert_benchclamp_gold, convert_benchclamp_pred, rerender
from ambiguous_parsing.metrics.metric import DatasetMetric
from ambiguous_parsing.eval.eval import get_score_data

class ZeroshotDatasetMetric(DatasetMetric):
    def __init__(self, either: bool = True): 
        super().__init__()
        self.df_data = []
        self.either = either

    def __call__(self, 
                pred_data: List[Any], 
                gold_data: List[Any], 
                amb_type: str, 
                is_fol: bool = True):

        scores_by_type = self.get_scores(gold_data, pred_data, is_fol=is_fol) 
        for ex_type, data_dict in scores_by_type.items():
            for key, data_list in data_dict.items():
                for i, item in enumerate(data_list):
                    self.df_data.append({"amb_type": amb_type, "type": ex_type, "key": key, "value": item, "idx": i})

    def get_scores(self, test_data, pred_data, is_fol=True): 
        scores_by_type = defaultdict(lambda: defaultdict(list))
        missing_second = 0
        missing_first = 0

        for datum_idx, (test_datum, pred_datum) in enumerate(zip(test_data,  pred_data)):
            # go through and get the predictions
            top_k_outputs = pred_datum['top_k_preds']

            lf_0, lf_1 = test_datum['lf0'], test_datum['lf1']
            lf_0 = rerender(lf_0, is_fol=is_fol)
            lf_1 = rerender(lf_1, is_fol=is_fol)
            ex_type = test_datum['type']

            if len(top_k_outputs) < 5:
                # pad 
                top_k_outputs = top_k_outputs + ['' for _ in range(5 - len(top_k_outputs))]

            for k in range(0, len(top_k_outputs)+1):
                lf_0_in_top_k = lf_0 in top_k_outputs[0:k]
                lf_1_in_top_k = lf_1 in top_k_outputs[0:k]


                scores_by_type[ex_type][f'lf_0_in_top_{k}'].append(lf_0_in_top_k)
                scores_by_type[ex_type][f'lf_1_in_top_{k}'].append(lf_1_in_top_k) 

                
        return scores_by_type

    def safe_mean(self, arr: np.array):
        sum = np.sum(arr)
        if sum == 0:
            return 0 
        return np.mean(arr)

    def get_metric(self, k=1):
        metric_dict = defaultdict(list)
        df = pd.DataFrame(self.df_data)

        lf0_key = f"lf_0_in_top_{k}"
        lf1_key = f"lf_1_in_top_{k}"

        # take average for each ratio across for key = "pred_top_1_matches_lf_0"
        for amb_type in df["amb_type"].unique():
            sub_df = df[df['amb_type'] == amb_type]
            sub_df = sub_df[sub_df['type'] == amb_type]
            lf0_df = sub_df[sub_df['key'] == lf0_key]
            lf1_df = sub_df[sub_df['key'] == lf1_key]
            lf0_vals = lf0_df['value'].astype(int).to_numpy()
            lf1_vals = lf1_df['value'].astype(int).to_numpy()

            assert(np.all(lf0_df['idx'].to_numpy() == lf1_df['idx'].to_numpy()))

            if self.either:
                metric_val = lf0_vals + lf1_vals
            else:
                metric_val = lf0_vals * lf1_vals

            metric_val = self.safe_mean(metric_val)

            metric_dict[amb_type].append(metric_val)

        metric_dict = {k:self.safe_mean(v) for k, v in metric_dict.items()}

        return metric_dict

    @staticmethod
    def from_bclamp_dirs(models_and_paths: Dict[str, List[Tuple[str]]], 
                     checkpoint_dir: str = None,
                     k: int = 1,
                     either: bool = True,
                     is_fol: bool = True):
        """
        models_and_paths: List
            format: {model: [(amb_type, path), ...)]...}
        """

        big_metric_dict = defaultdict(dict)
        if checkpoint_dir is not None:
            checkpoint_dir = Path(checkpoint_dir)
        for model, per_model_data in models_and_paths.items():
            either_metric = ZeroshotDatasetMetric(either=either)
            for amb_type, path in per_model_data:
                fol_test_path = f"/brtx/602-nvme1/estengel/ambiguous_parsing/data/raw/generalization/{amb_type}_fol/test.jsonl"
                fol_eval_path = f"/brtx/602-nvme1/estengel/ambiguous_parsing/data/raw/generalization/{amb_type}_fol/test_eval.jsonl"

                if checkpoint_dir is not None:
                    pred_path = checkpoint_dir / path
                else:
                    pred_path = Path(path)

                try:
                    if str(pred_path).endswith(".jsonl"):
                        pred_file = pred_path
                    else:
                        pred_path = Path(pred_path)
                        # list the files alphabetically and take the last one
                        pred_files = sorted(pred_path.glob("*.jsonl"))
                        pred_file = pred_files[-1]
                except IndexError:
                    print(f"Skipping {model} {amb_type} because no files found")
                    continue

                test_data = read_jsonl(fol_test_path)
                eval_data = read_jsonl(fol_eval_path)
                pred_data = read_jsonl(pred_file)


                # make test data lookup 
                test_data_lut = defaultdict(dict)
                for datum in eval_data:
                    test_data_lut[datum['surface']][str(datum['template_idx'])] = datum
                try:
                    assert(len(test_data) == len(pred_data))
                except AssertionError:
                    print(f"Skipping {model} {amb_type} because len(test_data) != len(pred_data)")
                    continue

                test_data = convert_benchclamp_gold(test_data, test_data_lut, is_fol=is_fol)
                pred_data = convert_benchclamp_pred(pred_data, is_fol=is_fol)
                either_metric(pred_data, test_data, amb_type, is_fol=is_fol)

            metric_val = either_metric.get_metric(k=k)
            big_metric_dict[model] = metric_val
        return big_metric_dict


if __name__ == "__main__":
    CHECKPOINT_DIR= Path("/brtx/602-nvme1/estengel/ambiguous_parsing/logs/1.0/") 
    # fol
    fol_models_and_paths  = defaultdict(list)
    for model in ["codegen-350M", "codegen-2B", "codegen-6B", "codegen-16B"]:
        for _type in ["scope", "revscope", "bound", "conj", "pp"]:
            fol_models_and_paths[model].append((_type, f"{model}_lamp_no_context_all_{_type}_fol_0_test_eval_constrained_bs_5_np_full"))
    for model in ['gpt-3.5-turbo']:
        for _type in ["scope", "revscope", "bound", "conj", "pp"]:
            fol_models_and_paths[model].append((_type, f"{model}_lamp_no_context_all_{_type}_fol_0_test_eval_unconstrained-api_bs_5_np_full"))
            




    metrics_by_k = {}
    for k in range(2, 6):
            
        big_metric_dict = ZeroshotDatasetMetric.from_bclamp_dirs(fol_models_and_paths, checkpoint_dir=CHECKPOINT_DIR, k=k, either=False, is_fol=True)
        metrics_by_k[k] = big_metric_dict


    for k in metrics_by_k.keys():
        print(f"K={k}")
        for model, per_model_data in metrics_by_k[k].items():
            print(f"\t{model}: {per_model_data}")