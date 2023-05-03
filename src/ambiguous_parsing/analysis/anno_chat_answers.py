import json 
import pathlib
import argparse 


def main(args):
    with open(args.chat_file, "r") as f:
        lines = [json.loads(x) for x in f.readlines()]

    new_data = []
    amb_data = []

    out_path = pathlib.Path(args.chat_file).parent / "amb_data.jsonl"
    if args.overwrite:
        out_path.unlink()
        mode = "w"
    else:
        mode = "a"

    with open(out_path, mode) as f1:
        for i, line in enumerate(lines):
            # skip if done 
            if 'idx' in line.keys() and not args.overwrite:
                continue

            outputs = line["outputs"]
            top_output = outputs[0]
            if not (top_output.startswith("forall") or top_output.startswith("exists")):
                print()
                print(f"INPUT: {line['test_datum_natural']}")
                print(f"OUTPUT: {top_output}")
                id_ans = input(f"Identified as ambiguous? (y/n): ")
                line['idx'] = i
                if id_ans.strip().lower() == "y":
                    line['identified_ambiguous'] = True
                else:
                    line['identified_ambiguous'] = False

                print(f"lf1: {line['test_datum_canonical']}")
                post_ans = input(f"LF0, LF1, or both? (0/1/b/n): ")
                if post_ans.strip().lower() == "0":
                    line['chat_predicted_lf'] = "0"
                elif post_ans.strip().lower() == "1":
                    line['chat_predicted_lf'] = "1"
                elif post_ans.strip().lower() == "b":
                    line['chat_predicted_lf'] = "b"
                else:
                    line['chat_predicted_lf'] = "n"
                messy_post_ans = input(f"LF0, LF1, or both captured semantically? (0/1/b/n): ")
                if messy_post_ans.strip().lower() == "0":
                    line['chat_predicted_messy'] = "0"
                elif messy_post_ans.strip().lower() == "1":
                    line['chat_predicted_messy'] = "1"
                elif messy_post_ans.strip().lower() == "b":
                    line['chat_predicted_messy'] = "b"
                else:
                    line['chat_predicted_messy'] = "n"
                amb_data.append(line)

                # save each time 
                f1.write(json.dumps(line) + "\n")
                print("\n\n======================\n")



if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--chat_file", type=str, required=True)
    parser.add_argument("--overwrite", action="store_true")
    args = parser.parse_args()
    main(args)