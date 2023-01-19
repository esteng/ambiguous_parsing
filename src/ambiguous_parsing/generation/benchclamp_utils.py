import argparse
import pathlib 
import json 


def read_data(path):
    with open(path.joinpath("train.jsonl")) as trn_f, \
        open(path.joinpath("dev.jsonl")) as dev_f, \
        open(path.joinpath("test.jsonl")) as tst_f:
        train = [json.loads(line) for line in trn_f]
        dev = [json.loads(line) for line in dev_f]
        test = [json.loads(line) for line in tst_f]
    return train, dev, test

def convert_line(line, idx):
    new_line = {"dialogue_id": idx,
                "turn_part_index": 0,
                "last_agent_utterance": "",
                "last_user_utterance": "",
                "plan": line["lf"],
                "utterance": line["surface"]}
    return new_line

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--data_dir", type=pathlib.Path, required=True, help="directory to read splits from")
    parser.add_argument("--out_dir", type=pathlib.Path, required=True, help="directory to write splits to")
    args = parser.parse_args()

    train, dev, test = read_data(args.data_dir)

    train = [convert_line(line, idx) for idx, line in enumerate(train)]
    dev = [convert_line(line, idx) for idx, line in enumerate(dev)]
    test = [convert_line(line, idx) for idx, line in enumerate(test)]

    with open(args.out_dir.joinpath("train.jsonl"), "w") as trn_f: 
        for line in train:
            trn_f.write(json.dumps(line) + "\n")

    with open(args.out_dir.joinpath("dev.jsonl"), "w") as dev_f: 
        for line in dev:
            dev_f.write(json.dumps(line) + "\n")

    with open(args.out_dir.joinpath("test.jsonl"), "w") as test_f: 
        for line in test:
            test_f.write(json.dumps(line) + "\n")
