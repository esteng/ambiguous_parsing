import pytest 
from ambiguous_parsing.tree.formula import FOLFormula
from ambiguous_parsing.generation.generate_pairs import (
    generate_pp_pairs,
    generate_unambiguous_pp,
    generate_scope_pairs,
    generate_reverse_scope_pairs,
    generate_unambiguous_scope,
    generate_conjunction_pairs,
    generate_unambiguous_conj,
    generate_bound_pronoun_pairs,
    generate_unambigous_bound_pronoun,
    generate_unambiguous_basic,
)

@pytest.fixture
def load_pp_pairs():
    pp_pairs = generate_pp_pairs()
    unambig_pp = generate_unambiguous_pp()
    return pp_pairs + unambig_pp

@pytest.fixture
def load_scope_pairs():
    scope_pairs = generate_scope_pairs()
    reverse_scope_pairs = generate_reverse_scope_pairs()
    unambig_scope = generate_unambiguous_scope()
    return scope_pairs + reverse_scope_pairs + unambig_scope

@pytest.fixture
def load_conj_pairs():
    conj_pairs = generate_conjunction_pairs()
    unambig_conj = generate_unambiguous_conj()
    return conj_pairs + unambig_conj

@pytest.fixture
def load_bound_pairs():
    bound_pairs = generate_bound_pronoun_pairs(is_female=True)+\
                generate_bound_pronoun_pairs(is_female=False)
    unambig_bound = generate_unambigous_bound_pronoun(is_female=True) + \
                    generate_unambigous_bound_pronoun(is_female=False)
    return bound_pairs + unambig_bound

@pytest.fixture
def load_unambiguous():
    unambiguous = generate_unambiguous_basic()
    return unambiguous

def check_fol_roundtrip(formula_str):
    formula_obj = FOLFormula.parse_formula(formula_str) 
    generated_str_1 = formula_obj.render()
    formula_obj_2 = FOLFormula.parse_formula(generated_str_1)
    generated_str_2 = formula_obj_2.render()
    assert (generated_str_1 == generated_str_2)

def test_pp_pairs(load_pp_pairs):
    for pair in load_pp_pairs:
        check_fol_roundtrip(pair['lf'])

def test_scope_pairs(load_scope_pairs):
    for pair in load_scope_pairs:
        check_fol_roundtrip(pair['lf'])

def test_conj_pairs(load_conj_pairs):
    for pair in load_conj_pairs:
        check_fol_roundtrip(pair['lf'])

def test_bound_pairs(load_bound_pairs):
    for pair in load_bound_pairs:
        check_fol_roundtrip(pair['lf'])

def test_unambiguous(load_unambiguous):
    for pair in load_unambiguous:
        print(pair['lf'])
        check_fol_roundtrip(pair['lf'])
