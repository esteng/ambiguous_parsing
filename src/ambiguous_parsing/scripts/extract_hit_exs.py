import csv 
import json 
from collections import defaultdict
from pathlib import Path


def detect_amb_type(inp_str):
    if inp_str.startswith("every") or inp_str.startswith('each'):
        return "scope"
    elif "every" in inp_str or "each" in inp_str:
        return "revscope"
    elif "with the" in inp_str:
        return "pp"
    else:
        return "bound"

def main():
    # read csv data
    hit_path = Path("/home/estengel/ambiguous_parsing_hit/data/csv/grouped_hit/")
    csvs = hit_path.glob("*.csv")
    all_data = []
    for fname in csvs:
        with open(fname) as f1:
            reader = csv.DictReader(f1)
            data = [row for row in reader]
            all_data += data

    # split csv data up to get list of inputs for each type 
    data_by_type = defaultdict(list)
    for row in all_data:
        inp_list = json.loads(row['inputStmtList']) 
        for inp in inp_list:
            amb_type = detect_amb_type(inp)
            data_by_type[amb_type].append(inp) 

    for k, v in data_by_type.items():
        data_by_type[k] = list(set(v))

    # get gold lines from data files 
    data_path = Path("/brtx/602-nvme1/estengel/ambiguous_parsing/data/processed")
    data_dirs = data_path.glob("*_fol")
    all_data_by_src = defaultdict(list)
    for ddir in data_dirs: 
        fname = ddir / "dev_eval.jsonl"
        try:
            with open(fname) as f1:
                dev_data = [json.loads(line) for line in f1]
                for line in dev_data:
                    all_data_by_src[line['utterance']].append(line)
        except FileNotFoundError:
            continue

    for _type in ['pp', 'bound', 'scope', 'revscope']:
        old_path = Path(f"/brtx/602-nvme1/estengel/ambiguous_parsing/data/processed/{_type}_fol")
        new_path = Path(f"/brtx/602-nvme1/estengel/ambiguous_parsing/data/processed/{_type}_fol_hit")
        new_path.mkdir(exist_ok=True)
        to_write_eval = []
        to_write = []
        for inp_str in data_by_type[_type]: 
            src_lines = all_data_by_src[inp_str]
            assert(len(src_lines) == 2)
            src_lines = sorted(src_lines, key = lambda x: x['template_idx'])
            to_write_eval += src_lines
            to_write.append(src_lines[-1])

        with open(new_path / "dev_eval.jsonl", 'w') as f1:
            for line in to_write_eval:
                f1.write(json.dumps(line) + "\n")
        with open(new_path / "dev.jsonl", "w") as f1:
            for line in to_write:
                f1.write(json.dumps(line) + "\n")

        with open(old_path / "train.jsonl") as srcf, open(new_path / "train.jsonl", "w") as tgtf:
            for line in srcf:
                tgtf.write(line)
        with open(old_path / "train_eval.jsonl") as srcf, open(new_path / "train_eval.jsonl", "w") as tgtf:
            for line in srcf:
                tgtf.write(line)

if __name__ == "__main__": 
    main()