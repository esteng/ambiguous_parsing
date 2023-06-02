# LAmP: Linguistically Ambiguous Parsing

This repo contains the code and data for this paper: [Zero and Few-shot Semantic Parsing with Ambiguous Inputs](https://arxiv.org/abs/2306.00824). 

## Dataset
LAmP focuses on semantic parsing with ambiguous utterances. Currently, 5 ambiguity types are supported
- Prepositional-phrase attachement (PP)
- Pronominal coreference (bound)
- Quantifier scope (scope) and inverted quantifier scope (revscope)
- Conjunctions (conj)

For an ambiguous input sentence, there are two possible semantic parses.  
More details about the ambiguity types can be found in the paper. 
Ambiguous parsing is tested in two settings: Zero-shot and few-shot. 
These are described in more detail below. 

### Note about data
In an effort to prevent the data here from being used for future pre-training, we have released in in a compressed format. 
**Please do not re-upload the data in a machine-readable format (e.g. .txt, .json, etc.).**
**Note that the additional third clause of the license prohibits this**
We have specifically included all `.jsonl` files in the `.gitignore` so that they aren't accidentally committed to the repo. 
To use the data locally, you can decompress it via `scripts/uncompress.sh`. 

### Data format 
All data is stored in `jsonlines` format. 
There are two data formats.

The raw LAmP dataset is released in jsonlines format, with the following fields for each line.
- `utterance`: the ambiguous utterance 
- `plan`: the semantic parse
- `unfilled_template`: the template used to construct the utterance
- `var_bindings`: the variables used to fill the template
- `template_idx`: the index of the LF (0 or 1 if the utterance is ambiguous) 
- `type`: the ambiguity type 

There are two files for each split: `<split>.jsonl` and `<split>_eval.jsonl`. 
The first is in the format required to be ingested by BenchCLAMP, but only contains *one* of the two LFs, so it cannot be used for evaluation. 
The `eval` files contain both LFs and are used by the evaluation scripts. 

To facilitate replicating our experiments, we also release our prompt-ready data. 
For each example in our zero and few-shot experiments, we release the test set with the full prompts used to obtain our results.
These files have the following fields:
- `prompt`: a list of dicts. Each dict is `{"line_type": "Human"|"Computer", "line_content": <utterance|program>}` 
- `test_sent`: the input utterance 
- `gold_tgt`: the gold semantic parse (LF0 if ambiguous)

### Zero-shot setting 
In the zero-shot setting, models are given the ingredients to produce both LFs. 
The prompts are constructed by defining a number of unambiuous fragments which are intended to show the model different components needed to produce an LF at test time.
The model should ideally be able to recombine and modify the pieces of the prompt to produce both LFs. 

For example, for PP attachment, the test sentence `the boy saw the man with the telescope` would have a prompt with LFs for `the boy saw the man`, `the boy saw with the telescope`, and `the man with the telescope`.
Based on these inputs, the model should be able to parse the ambiguous test sentence two ways. 

Zero-shot data is in `data/zeroshot` 
### Few-shot setting
In few-shot learning, the model receives direct examples of how to parse ambiguous sentences. 
However, the prompt given contains a mixed set of examples (some LF0, some LF1). 
Here, we retrieve similar examples and concatenate them into a prompt.
Each prompt has 10 examples, and the ratio determines the percentage of those examples that are LF0 or LF1. 
For example, the files in the `20-80` folder have prompts for each ambiguity type with 2 examples of sentences being parsed as LF0 and and 8 sentences parsed as LF1. 

Here, the model should capture the input percentage, i.e. a model tested on prompts from the `20-80` split should put about `p=0.2` on LF0 and produce LF0 about 20% of the time. 

Few-shot data is in `data/fewshot` 

### Grammars 
Because the models used have not been finetuned on LAmP data, we use constrained decoding for locally-run models. 
BenchCLAMP allows decoding according to a context-free grammar (CFG), so that the model's output space is reduced according to the CFG's productions. 
This ensures that the model produces only syntactically-correct programs. 
The `grammar/cfgs` directory contains CFGs for FOL and Lisp. 
`grammar/create_grammar.py` can be used to update these grammars if new lexical items are added. 
Note that if you add new lexical items and fail to include them in the grammar, then grammar-constrained decoding will lead to the model failing to predict the correct program 100% of the time, since the new lexical item would not be allowed.

## Generating data
In addition to the existing data, we include the code and scripts used to generate the data, allowing future users to expand the types of ambiguities and the diversity of the sentences and lexical items used. 

### Templates 
Data is generated via templates, defined for each ambiguity type. 
We choose to use templates rather than generating data from a CFG because ambiguity is very sensitive to lexical items. 
For example, `the boy saw the man with a telescope` is ambiguous but `the boy saw the man with a yellow t-shirt` is not. 
To ensure that our ambiguous examples are actually ambiguous, we define templates that can be filled with certain lexical items. 

The `generation/Template` class is used to store templates and generate data from them. 
It takes two arguments: `template_list` and `template_tags`. 
`template_list` is a mixed list of strings and lists of lexical items. For example, unambiguous PP-attachment examples are generated from this list: `["the", INDEFINITE_HUMAN_NPS, VISUAL_VPS, "the", INDEFINITE_HUMAN_NPS, "with the", NONVISUAL_NPS]` 
The lexical items are defined in `generation/fixtures/` and can be expanded. 
`template_tags` tell the template which variables to fill. These tags need to match up with the lexical items; the tag is `None` when the list has a string, and a variable name when the list has a set of lexical items. 
For the example list, the tags are `[None, "np1", "vp1", None, "np2", None, "np3"]`; these variables are used to fill in the LFs.

The LFs are defined outside of the `Template` class and passed to `Template.generate()`.
An LF is a string with variables in brackets, like this one: 

```
"exists x . exists y . exists z . exists a . exists e . {np1}(x) AND {np2}(y)"+\
                    " AND {vp1}(a) AND agent(a, x) AND patient(a, y) AND {np3}(z) AND " +\
                    "have(e) AND agent(e, y) AND patient(e, z)"
``` 

These variables are then filled by the lexical items, matched via the tags. 
The separation of templates and LFs allows multiple LFs to be paired with the same input template. 
`Template.generate()` goes through all possible combinations of items in the lexical item sets, and generates input/output pairs accordingly. 

While our current ambiguities support only two LFs, the framework can extend to an arbitrary number of LFs. 

### Canonicalization 
The data used in the paper is in first-order-logic (FOL) format. 
In order to properly evaluate predicted strings, we add the option to parse and canonicalize FOL formulae. 
The motivation for this is that a formula like `man(x) AND boy(y)` is logically equivalent to `boy(y) AND man(x)` and `man(y) AND boy(x)`, but an exact match metric would treat these latter two as incorrect predictions. 

In order to make sure that logically-equivalent programs are counted as correct, we include utilities in `tree` to parse formulae into trees. 
These trees can then be traversed with nodes sorted in alphabetic order and variables anonymized, which means that the final representation for all the above formulae would be the same (`boy(v0) AND man(v1)`).  


### Lisp data 
We can also use the tree in the `Formula` object to translate into other representation formats. 
Specifically, we include utilities to translate between FOL and Lisp formats. 
In Lisp, quantifiers are expressed as global-scope statements (e.g. `(exists x (forall y (...)))`) and the functions `AND` and `OR` can have an arbitrary number of arguments (e.g. `(AND (man x) (boy y) (dog z)...)`).

## Metrics and Evaluation 
Model performance on LAmP is measured not by accuracy against one reference parse, but against multiple reference parses (since there are two possible parses for ambiguous utterances). 
Different metrics are used for evaluating the quality. 
All metrics are computed against canonicalized parses.

### Eval report 
An eval report can be generated via `eval/eval.py`. 
It can either be printed, or returned in a pandas DataFrame with `get_df`.
To obtain an eval report, the `<split>_eval.jsonl` file is required, since it has both possible LFs for ambiguous examples. 

## Adding ambiguities and generating data 
Additional templates and lexical items can be specified.
Currently, all templates are defined in `generation/generate_pairs.py`.
Splits are created by `generation/create_splits.py` and `generation/create_fewshot_splits.py`.
These files take a dataset config, which is a Hydra config file. 
All configs are stored in `generation/data_configs/`. 

## Parsing results 
All parsing is handled by [this fork of BenchCLAMP](https://github.com/esteng/semantic_parsing_with_constrained_lm/tree/lamp).
See the README there for more details. 
