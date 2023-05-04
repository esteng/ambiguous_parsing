import pytest 
import pdb

from ambiguous_parsing.eval.utils import rerender
from ambiguous_parsing.metrics.fewshot_metrics import FewshotDatasetMetric, FewshotInstanceMetric
from ambiguous_parsing.metrics.zeroshot_metrics import ZeroshotDatasetMetric


def test_fewshot_dataset_all_correct():
    pred_data = [{"top_k_preds": ["mocklf0 ( arg0 ) AND mocklf0 ( arg1 )"]},
                 {"top_k_preds": ["mocklf1 ( arg0 ) AND mocklf1 ( arg1 )"]}]
    gold_data = [{"natural": f"mock example {i}",
                 "lf0": "mocklf0 ( arg0 ) AND mocklf0 ( arg1 )",
                  "lf1": "mocklf1 ( arg0 ) AND mocklf1 ( arg1 )",
                  "type": "mocktype"} for i in range(2)]
    ratio = 0.5
    is_fol = True

    metric = FewshotDatasetMetric()
    metric(pred_data, gold_data, is_fol=is_fol, ratio=ratio)
    assert metric.get_metric()['mocktype'] == 0.0

def test_fewshot_dataset_all_incorrect():
    pred_data = [{"top_k_preds": ["notmocklf0 ( arg0 ) AND notmocklf0 ( arg1 )"],
                  } for _ in range(2)]
    gold_data = [{"natural": f"mock example {i}",
                 "lf0": "mocklf0 ( arg0 ) AND mocklf0 ( arg1 )",
                  "lf1": "mocklf1 ( arg0 ) AND mocklf1 ( arg1 )",
                  "type": "mocktype"} for i in range(2)]
    ratio = 0.5
    is_fol = True

    metric = FewshotDatasetMetric()
    metric(pred_data, gold_data, is_fol=is_fol, ratio=ratio)
    assert metric.get_metric()['mocktype'] == 1.0

def test_fewshot_dataset_half_correct():
    pred_data = [{"top_k_preds": ["mocklf0 ( arg0 ) AND mocklf0 ( arg1 )"]},
                 {"top_k_preds": ["notmocklf1 ( arg0 ) AND notmocklf1 ( arg1 )"]}]
    gold_data = [{"natural": f"mock example {i}",
                 "lf0": "mocklf0 ( arg0 ) AND mocklf0 ( arg1 )",
                  "lf1": "mocklf1 ( arg0 ) AND mocklf1 ( arg1 )",
                  "type": "mocktype"} for i in range(2)]
    ratio = 0.5
    is_fol = True

    metric = FewshotDatasetMetric()
    metric(pred_data, gold_data, is_fol=is_fol, ratio=ratio)
    assert metric.get_metric()['mocktype'] == 0.5

def test_fewshot_instance_all_correct():
    data_by_src = {"mock example 0": [{"template_idx": "0", "logit_at_label": [1.0, 1.0, 1.0]},
                                       {"template_idx": "1", "logit_at_label": [0.0, 0.0, 0.0]}],
                   "mock example 1": [{"template_idx": "0", "logit_at_label": [1.0, 1.0, 1.0]},
                                       {"template_idx": "1", "logit_at_label": [0.0, 0.0, 0.0]}]}
    
    gold_data_lut = {"mock example 0": {"0": {"type": "mocktype"},
                                        "1": {"type": "mocktype"}},
                     "mock example 1": {"0": {"type": "mocktype"},
                                        "1": {"type": "mocktype"}}}
    ratio = 1.0
    metric = FewshotInstanceMetric()
    metric(data_by_src, gold_data_lut, ratio=ratio)
    assert metric.get_metric()['mocktype'] == 0.0



def test_fewshot_instance_all_incorrect():
    data_by_src = {"mock example 0": [{"template_idx": "0", "logit_at_label": [1.0, 1.0, 1.0]},
                                       {"template_idx": "1", "logit_at_label": [0.0, 0.0, 0.0]}],
                   "mock example 1": [{"template_idx": "0", "logit_at_label": [1.0, 1.0, 1.0]},
                                       {"template_idx": "1", "logit_at_label": [0.0, 0.0, 0.0]}]}
    
    gold_data_lut = {"mock example 0": {"0": {"type": "mocktype"},
                                        "1": {"type": "mocktype"}},
                     "mock example 1": {"0": {"type": "mocktype"},
                                        "1": {"type": "mocktype"}}}
    ratio = 0.0
    metric = FewshotInstanceMetric()
    metric(data_by_src, gold_data_lut, ratio=ratio)
    assert metric.get_metric()['mocktype'] == 1.0

def test_fewshot_instance_half_correct():
    data_by_src = {"mock example 0": [{"template_idx": "0", "logit_at_label": [1.0, 1.0, 1.0]},
                                       {"template_idx": "1", "logit_at_label": [0.0, 0.0, 0.0]}],
                   "mock example 1": [{"template_idx": "0", "logit_at_label": [0.0, 0.0, 0.0]},
                                       {"template_idx": "1", "logit_at_label": [1.0, 1.0, 1.0]}]}
    
    gold_data_lut = {"mock example 0": {"0": {"type": "mocktype"},
                                        "1": {"type": "mocktype"}},
                     "mock example 1": {"0": {"type": "mocktype"},
                                        "1": {"type": "mocktype"}}}
    ratio = 1.0
    metric = FewshotInstanceMetric()
    metric(data_by_src, gold_data_lut, ratio=ratio)
    assert metric.get_metric()['mocktype'] == 0.5

def test_fewshot_instance_custom_MSE():
    data_by_src = {"mock example 0": [{"template_idx": "0", "logit_at_label": [1.0, 0.5, 1.0]},
                                       {"template_idx": "1", "logit_at_label": [1.0, 0.5, 1.0]}]}
    
    gold_data_lut = {"mock example 0": {"0": {"type": "mocktype"},
                                        "1": {"type": "mocktype"}}}

    ratio = 1.0
    metric = FewshotInstanceMetric()
    metric(data_by_src, gold_data_lut, ratio=ratio)
    assert metric.get_metric()['mocktype'] == 0.25

def test_zeroshot_dataset_all_correct_k1_either():
    pred_data = [{"top_k_preds": ["exists arg0 . exists arg1 . mocklf0(arg0) AND mocklf0(arg1)", "exists arg0 . exists arg1 . mocklf1(arg0) AND mocklf1(arg1)"]},
                 {"top_k_preds": ["exists arg0 . exists arg1 . mocklf0(arg0) AND mocklf0(arg1)", "exists arg0 . exists arg1 . mocklf1(arg1) AND mocklf1(arg0)"]}]
    gold_data = [{"natural": f"mock example {i}",
                 "lf0": "exists arg0 . exists arg1 . mocklf0(arg0) AND mocklf0(arg1)",
                  "lf1": "exists arg0 . exists arg1 . mocklf1(arg0) AND mocklf1(arg1)",
                  "type": "mocktype"} for i in range(2)]
    amb_type = "mocktype"
    is_fol = True

    metric = ZeroshotDatasetMetric(either=True)
    for i, d in enumerate(pred_data):
        for j, p in enumerate(d['top_k_preds']):
            pred_data[i]['top_k_preds'][j] = rerender(p, is_fol=True)
    metric(pred_data, gold_data, is_fol=is_fol, amb_type=amb_type)
    assert metric.get_metric(k=1)['mocktype'] == 1.0

def test_zeroshot_dataset_all_correct_k2_either_positive():
    pred_data = [{"top_k_preds": ["exists arg0 . exists arg1 . notmocklf0(arg0) AND notmocklf0(arg1)", "exists arg0 . exists arg1 . mocklf1(arg0) AND mocklf1(arg1)"]},
                 {"top_k_preds": ["exists arg0 . exists arg1 . notmocklf0(arg0) AND notmocklf0(arg1)", "exists arg0 . exists arg1 . mocklf1(arg1) AND mocklf1(arg0)"]}]
    gold_data = [{"natural": f"mock example {i}",
                 "lf0": "exists arg0 . exists arg1 . mocklf0(arg0) AND mocklf0(arg1)",
                  "lf1": "exists arg0 . exists arg1 . mocklf1(arg0) AND mocklf1(arg1)",
                  "type": "mocktype"} for i in range(2)]
    amb_type = "mocktype"
    is_fol = True

    metric = ZeroshotDatasetMetric(either=True)
    for i, d in enumerate(pred_data):
        for j, p in enumerate(d['top_k_preds']):
            pred_data[i]['top_k_preds'][j] = rerender(p, is_fol=True)
    metric(pred_data, gold_data, is_fol=is_fol, amb_type=amb_type)
    assert metric.get_metric(k=2)['mocktype'] == 1.0

def test_zeroshot_dataset_all_correct_k2_either_negative():
    pred_data = [{"top_k_preds": ["exists arg0 . exists arg1 . notmocklf0(arg0) AND notmocklf0(arg1)", "exists arg0 . exists arg1 . notmocklf1(arg0) AND notmocklf1(arg1)"]},
                 {"top_k_preds": ["exists arg0 . exists arg1 . notmocklf0(arg0) AND notmocklf0(arg1)", "exists arg0 . exists arg1 . mocklf1(arg1) AND mocklf1(arg0)"]}]
    gold_data = [{"natural": f"mock example {i}",
                 "lf0": "exists arg0 . exists arg1 . mocklf0(arg0) AND mocklf0(arg1)",
                  "lf1": "exists arg0 . exists arg1 . mocklf1(arg0) AND mocklf1(arg1)",
                  "type": "mocktype"} for i in range(2)]
    amb_type = "mocktype"
    is_fol = True

    metric = ZeroshotDatasetMetric(either=True)
    for i, d in enumerate(pred_data):
        for j, p in enumerate(d['top_k_preds']):
            pred_data[i]['top_k_preds'][j] = rerender(p, is_fol=True)
    metric(pred_data, gold_data, is_fol=is_fol, amb_type=amb_type)
    assert metric.get_metric(k=2)['mocktype'] == 0.5


def test_zeroshot_dataset_all_correct_k2_both_positive():
    pred_data = [{"top_k_preds": ["exists arg0 . exists arg1 . mocklf0(arg0) AND mocklf0(arg1)", "exists arg0 . exists arg1 . mocklf1(arg0) AND mocklf1(arg1)"]},
                 {"top_k_preds": ["exists arg0 . exists arg1 . mocklf0(arg0) AND mocklf0(arg1)", "exists arg0 . exists arg1 . mocklf1(arg1) AND mocklf1(arg0)"]}]
    gold_data = [{"natural": f"mock example {i}",
                 "lf0": "exists arg0 . exists arg1 . mocklf0(arg0) AND mocklf0(arg1)",
                  "lf1": "exists arg0 . exists arg1 . mocklf1(arg0) AND mocklf1(arg1)",
                  "type": "mocktype"} for i in range(2)]
    amb_type = "mocktype"
    is_fol = True

    metric = ZeroshotDatasetMetric(either=False)
    for i, d in enumerate(pred_data):
        for j, p in enumerate(d['top_k_preds']):
            pred_data[i]['top_k_preds'][j] = rerender(p, is_fol=True)
    metric(pred_data, gold_data, is_fol=is_fol, amb_type=amb_type)
    assert metric.get_metric(k=2)['mocktype'] == 1.0

def test_zeroshot_dataset_all_correct_k2_both_half():
    pred_data = [{"top_k_preds": ["exists arg0 . exists arg1 . notmocklf0(arg0) AND notmocklf0(arg1)", "exists arg0 . exists arg1 . mocklf1(arg0) AND mocklf1(arg1)"]},
                 {"top_k_preds": ["exists arg0 . exists arg1 . mocklf0(arg0) AND mocklf0(arg1)", "exists arg0 . exists arg1 . mocklf1(arg1) AND mocklf1(arg0)"]}]
    gold_data = [{"natural": f"mock example {i}",
                 "lf0": "exists arg0 . exists arg1 . mocklf0(arg0) AND mocklf0(arg1)",
                  "lf1": "exists arg0 . exists arg1 . mocklf1(arg0) AND mocklf1(arg1)",
                  "type": "mocktype"} for i in range(2)]
    amb_type = "mocktype"
    is_fol = True

    metric = ZeroshotDatasetMetric(either=False)
    for i, d in enumerate(pred_data):
        for j, p in enumerate(d['top_k_preds']):
            pred_data[i]['top_k_preds'][j] = rerender(p, is_fol=True)
    metric(pred_data, gold_data, is_fol=is_fol, amb_type=amb_type)
    assert metric.get_metric(k=2)['mocktype'] == 0.5

def test_zeroshot_dataset_all_correct_k2_both_negative():
    pred_data = [{"top_k_preds": ["exists arg0 . exists arg1 . notmocklf0(arg0) AND notmocklf0(arg1)", "exists arg0 . exists arg1 . mocklf1(arg0) AND mocklf1(arg1)"]},
                 {"top_k_preds": ["exists arg0 . exists arg1 . notmocklf0(arg0) AND notmocklf0(arg1)", "exists arg0 . exists arg1 . mocklf1(arg1) AND mocklf1(arg0)"]}]
    gold_data = [{"natural": f"mock example {i}",
                 "lf0": "exists arg0 . exists arg1 . mocklf0(arg0) AND mocklf0(arg1)",
                  "lf1": "exists arg0 . exists arg1 . mocklf1(arg0) AND mocklf1(arg1)",
                  "type": "mocktype"} for i in range(2)]
    amb_type = "mocktype"
    is_fol = True

    metric = ZeroshotDatasetMetric(either=False)
    for i, d in enumerate(pred_data):
        for j, p in enumerate(d['top_k_preds']):
            pred_data[i]['top_k_preds'][j] = rerender(p, is_fol=True)
    metric(pred_data, gold_data, is_fol=is_fol, amb_type=amb_type)
    assert metric.get_metric(k=2)['mocktype'] == 0.0
