
import pytest 
import pdb 
from ambiguous_parsing.tree.formula import Formula, FOLFormula, LispFormula

from test_fol import (load_pp_pairs,
                           load_scope_pairs,
                           load_conj_pairs,
                           load_bound_pairs,
                           load_unambiguous) 



def check_lisp_roundtrip(formula_str):
    fol_formula = FOLFormula.parse_formula(formula_str)
    lisp_formula_1 = LispFormula.from_formula(fol_formula)
    generated_str_1 = lisp_formula_1.render()
    print(generated_str_1)
    lisp_formula_2 = LispFormula.parse_formula(generated_str_1)
    generated_str_2 = lisp_formula_2.render()
    assert (generated_str_1 == generated_str_2)


def test_lisp():
    fol_str = "exists x . exists a . exists e . spyglass(x) AND observed(a) AND agent(a, Ada) AND instrument(a, x)" 
    check_lisp_roundtrip(fol_str)

def test_pp_pairs(load_pp_pairs):
    for pair in load_pp_pairs:
        check_lisp_roundtrip(pair['lf'])

def test_scope_pairs(load_scope_pairs):
    for pair in load_scope_pairs:
        check_lisp_roundtrip(pair['lf'])

def test_conj_pairs(load_conj_pairs):
    for pair in load_conj_pairs:
        check_lisp_roundtrip(pair['lf'])

def test_bound_pairs(load_bound_pairs):
    for pair in load_bound_pairs:
        check_lisp_roundtrip(pair['lf'])

def test_unambiguous(load_unambiguous):
    for pair in load_unambiguous:
        print(pair['lf'])
        check_lisp_roundtrip(pair['lf'])

