import argparse 

from ambiguous_parsing.generation.fixtures.nps import INDEFINITE_NPS_MAP, NAMES
from ambiguous_parsing.generation.fixtures.vps import VPS_MAP

def write_lark_grammar(base_path, out_path):
    with open(base_path) as f1:
        base_lines = [x.strip() for x in f1.readlines()]

    expr_vals = list(INDEFINITE_NPS_MAP.values()) + list(VPS_MAP.values()) + ["agent", "patient", "instrument", "have"]
    expr_vals = [f'"{x}"' for x in expr_vals]
    expr_rules = "expr: " + " | ".join(expr_vals) 
    name_vals = [f'"{x}"' for x in NAMES]
    const_rules = "const: " + " | ".join(name_vals) 
    grammar_lines = base_lines + [expr_rules, const_rules]

    with open(out_path, "w") as f1:
        f1.write("\n".join(grammar_lines))

def write_bclamp_grammar(base_path, out_path):
    with open(base_path) as f1:
        base_lines = [x.strip() for x in f1.readlines()]

    expr_vals = list(INDEFINITE_NPS_MAP.values()) + list(VPS_MAP.values()) + ["agent", "patient", "instrument", "have"]
    expr_vals = [f'"{x}"' for x in expr_vals]
    expr_rules = "expr -> " + " | ".join(expr_vals) 
    name_vals = [f'"{x}"' for x in NAMES]
    const_rules = "const -> " + " | ".join(name_vals) 
    grammar_lines = base_lines + [expr_rules, const_rules]

    with open(out_path, "w") as f1:
        f1.write("\n".join(grammar_lines))


if __name__ == "__main__": 
    parser = argparse.ArgumentParser()
    parser.add_argument("--base_path", type=str, required=True)
    parser.add_argument("--out_path", type=str, required=True)
    parser.add_argument("--bclamp", action="store_true", help="set to true if generating a benchclamp grammar")

    args = parser.parse_args()

    if args.bclamp:
        write_bclamp_grammar(args.base_path, args.out_path)
    else:
        write_lark_grammar(args.base_path, args.out_path)