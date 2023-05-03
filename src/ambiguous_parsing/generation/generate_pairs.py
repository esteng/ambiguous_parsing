import itertools 
import copy 
import pdb 


from ambiguous_parsing.generation.fixtures.nps import (
    INDEFINITE_NPS,
    INDEFINITE_HUMAN_NPS, 
    NAMES, 
    MALE_NAMES,
    FEMALE_NAMES,
    INDEFINITE_MALE_NPS,
    INDEFINITE_FEMALE_NPS,
    VISUAL_INSTRUMENT_NPS, 
    NONVISUAL_NPS,
    TACTILE_INSTRUMENT_NPS,
    INDEFINITE_SENTIENT_NPS
)
from ambiguous_parsing.generation.fixtures.vps import (
    VISUAL_VPS, 
    TACTILE_VPS, 
    INTRANSITIVE_VPS,
    TRANSITIVE_VPS,
    INTRANSITIVE_VPS_FOR_BOUND,
    VPS
)
from ambiguous_parsing.generation.template import Template

def generate_pp_pairs():
    """generate pairs of sentences and LFs with PP attachment ambiguities
    format of sentences: 
    "The boy saw the man with the telescope." | 
       exists x . exists y . exists z . exists e . exists a . 
       boy(x) ^ man(y) ^ telescope(z) ^ saw(e) ^ agent(e, x) ^ patient(e, y) ^ instrument(e, z)
    "Galileo picked up the boy with the gloves."
    "The woman observed the man in pyjamas."
    """
    visual_pp_pairs = generate_with_pp_pairs(vp_list=VISUAL_VPS,
                                             pp_str="with the",
                                             pp_np_list = VISUAL_INSTRUMENT_NPS)

    instrument_pp_pairs = generate_with_pp_pairs(vp_list = TACTILE_VPS,
                                                pp_str = "with the",
                                                pp_np_list = TACTILE_INSTRUMENT_NPS)

    return visual_pp_pairs + instrument_pp_pairs

def generate_with_pp_pairs(vp_list = VISUAL_VPS,
                             pp_str = "with the",
                             pp_np_list = VISUAL_INSTRUMENT_NPS):
    """generate pairs of sentences and LFs with PP attachment ambiguities
    format of sentences: 
    "The boy saw the man with the telescope." | 
       exists x . exists y . exists z . exists e . exists a . 
       boy(x) ^ man(y) ^ telescope(z) ^ saw(e) ^ agent(e, x) ^ patient(e, y) ^ instrument(e, z)
    """
    pairs = []
    
    # visual templates 
    indef_indef_template_text = ["the", INDEFINITE_HUMAN_NPS, vp_list, "the", INDEFINITE_HUMAN_NPS, pp_str, pp_np_list]
    indef_indef_template_tags = [None, "np1", "vp1", None, "np2", None, "np3"]
    indef_indef_template = Template(indef_indef_template_text, indef_indef_template_tags)
    
    indef_indef_lf_template_1 = "exists x . exists y . exists z . exists a . exists e . {np1}(x) AND {np2}(y)"+\
                    " AND {vp1}(a) AND agent(a, x) AND patient(a, y) AND {np3}(z) AND " +\
                    "have(e) AND agent(e, y) AND patient(e, z)"

    indef_indef_lf_template_2 = "exists x . exists y . exists z . exists a . {np1}(x) AND {np2}(y) AND {np3}(z)"+\
                    " AND {vp1}(a) AND agent(a, x) AND patient(a, y) AND instrument(a, z)"

    pairs += indef_indef_template.generate(indef_indef_lf_template_1, 0, "pp")
    pairs += indef_indef_template.generate(indef_indef_lf_template_2, 1, "pp")

    # no good for tactile, not ambiguous 
    if pp_np_list == VISUAL_INSTRUMENT_NPS:
        indef_def_template_text = ["the", INDEFINITE_HUMAN_NPS, vp_list, NAMES, pp_str, pp_np_list]
        indef_def_template_tags = [None, "np1", "vp1", "np2", None, "np3"]
        indef_def_template = Template(indef_def_template_text, indef_def_template_tags)

        indef_def_lf_template_1 = "exists x . exists y . exists a . exists e . {np1}(x) AND {np3}(y)"+\
                        " AND {vp1}(a) AND agent(a, x) AND patient(a, {np2}) AND " +\
                        "have(e) AND agent(e, {np2}) AND patient(e, y)"

        indef_def_lf_template_2 = "exists x . exists y . exists a . {np1}(x) AND {np3}(y)"+\
                        " AND {vp1}(a) AND agent(a, x) AND patient(a, {np2}) AND instrument(a, y)"

        pairs += indef_def_template.generate(indef_def_lf_template_1, 0, "pp")
        pairs += indef_def_template.generate(indef_def_lf_template_2, 1, "pp")

    def_indef_template_text = [NAMES, vp_list, "the", INDEFINITE_HUMAN_NPS,  pp_str, pp_np_list]
    def_indef_template_tags = ["np1", "vp1", None, "np2", None, "np3"]
    def_indef_template = Template(def_indef_template_text, def_indef_template_tags) 

    def_indef_lf_template_1 = "exists x . exists y . exists a . exists e . {np2}(x) AND {np3}(y)"+\
                    " AND {vp1}(a) AND agent(a, {np1}) AND patient(a, x) AND " +\
                    "have(e) AND agent(e, x) AND patient(e, y)"

    def_indef_lf_template_2 = "exists x . exists y . exists a . {np2}(x) AND {np3}(y)"+\
                    " AND {vp1}(a) AND agent(a, {np1}) AND patient(a, x) AND instrument(a, y)"

    pairs += def_indef_template.generate(def_indef_lf_template_1, 0, "pp")
    pairs += def_indef_template.generate(def_indef_lf_template_2, 1, "pp")


    # no good for tactile, not ambiguous
    if pp_np_list == VISUAL_INSTRUMENT_NPS:
        def_def_template_text = [NAMES, vp_list, NAMES,  pp_str, pp_np_list]
        def_def_template_tags = ["np1", "vp1", "np2", None, "np3"]
        def_def_template = Template(def_def_template_text, def_def_template_tags) 

        def_def_lf_template_1 = "exists x . exists a . exists e . {np3}(x)"+\
                        " AND {vp1}(a) AND agent(a, {np1}) AND patient(a, {np2}) AND " +\
                        "have(e) AND agent(e, {np2}) AND patient(e, x)"

        def_def_lf_template_2 = "exists x . exists a . {np3}(x)"+\
                        " AND {vp1}(a) AND agent(a, {np1}) AND patient(a, {np2}) AND instrument(a, x)"

        pairs += def_def_template.generate(def_def_lf_template_1, 0, "pp")
        pairs += def_def_template.generate(def_def_lf_template_2, 1, "pp")

    return pairs

def generate_unambiguous_pp(): 
    """ generate unambiguous PP sentences
    like "The man saw the boy with the mittens" 
    "The woman saw the man with the pyjamas" 
    """
    pairs = []
    
    # visual templates 
    indef_indef_template_text = ["the", INDEFINITE_HUMAN_NPS, VISUAL_VPS, "the", INDEFINITE_HUMAN_NPS, "with the", NONVISUAL_NPS]
    indef_indef_template_tags = [None, "np1", "vp1", None, "np2", None, "np3"]
    indef_indef_template = Template(indef_indef_template_text, indef_indef_template_tags)
    
    indef_indef_lf_template_1 = "exists x . exists y . exists z . exists a . exists e . {np1}(x) AND {np2}(y)"+\
                    " AND {vp1}(a) AND agent(a, x) AND patient(a, y) AND {np3}(z) AND " +\
                    "have(e) AND agent(e, y) AND patient(e, z)"

    pairs += indef_indef_template.generate(indef_indef_lf_template_1, 0, "pp_unambig")

    def_indef_template_text = [NAMES, VISUAL_VPS, "the", INDEFINITE_HUMAN_NPS,  "with the", NONVISUAL_NPS]
    def_indef_template_tags = ["np1", "vp1", None, "np2", None, "np3"]
    def_indef_template = Template(def_indef_template_text, def_indef_template_tags) 

    def_indef_lf_template_1 = "exists x . exists y . exists a . exists e . {np2}(x) AND {np3}(y)"+\
                    " AND {vp1}(a) AND agent(a, {np1}) AND patient(a, x) AND " +\
                    "have(e) AND agent(e, x) AND patient(e, y)"

    pairs += def_indef_template.generate(def_indef_lf_template_1, 0, "pp_unambig")

    return pairs  

def generate_conjunction_pairs():
    """generate pairs of sentences with conjunction ambiguities
    of the form:
    "The man ate and drank or slept"
        exists x . exists a . exists e . exists i . man(x) AND eat(a) AND agent(a, x) AND ( ( drank(e) AND agent(e, x) ) OR ( slept(i) AND agent(i, x) ) )
        exists x . exists a . exists e . exists i . ( man(x) AND eat(a) AND agent(a, x) AND drank(e) AND agent(e, x) ) OR ( slept(i) AND agent(i, x) ) )
    """
    pairs = []
    and_first_template_text = ["the", INDEFINITE_SENTIENT_NPS, INTRANSITIVE_VPS, "and", INTRANSITIVE_VPS, "or", INTRANSITIVE_VPS]
    and_first_template_tags = [None, "np1", "vp1", None, "vp2", None, "vp3"] 
    and_first_template = Template(and_first_template_text, and_first_template_tags)

    and_first_lf_template_1 = "exists x . exists a . exists e . exists i . {np1}(x) AND {vp1}(a) AND agent(a, x) AND ( ( {vp2}(e) AND agent(e, x) ) OR ( {vp3}(i) AND agent(i, x) ) )"
    and_first_lf_template_2 = "exists x . exists a . exists e . exists i . {np1}(x) AND ( {vp1}(a) AND agent(a, x) AND {vp2}(e) AND agent(e, x) ) OR ( {vp3}(i) AND agent(i, x) )"

    pairs += and_first_template.generate(and_first_lf_template_1, 0, "conj")
    pairs += and_first_template.generate(and_first_lf_template_2, 1, "conj")

    or_first_template_text = ['the', INDEFINITE_SENTIENT_NPS, INTRANSITIVE_VPS, 'or', INTRANSITIVE_VPS, 'and', INTRANSITIVE_VPS]
    or_first_template_tags = [None, 'np1', 'vp1', None, 'vp2', None, 'vp3']

    or_first_template = Template(or_first_template_text, or_first_template_tags)

    or_first_lf_template_1 = "exists x . exists a . exists e . exists i . {np1}(x) AND ( ( {vp1}(a) AND agent(a, x) ) OR ( {vp2}(e) AND agent(e, x) ) ) AND {vp3}(i) AND agent(i, x)" 
    or_first_lf_template_2 = "exists x . exists a . exists e . exists i . {np1}(x) AND ( {vp1}(a) AND agent(a, x) ) OR ( {vp2}(e) AND agent(e, x) AND {vp3}(i) AND agent(i, x) )"

    pairs += or_first_template.generate(or_first_lf_template_1, 0, "conj")
    pairs += or_first_template.generate(or_first_lf_template_2, 1, "conj")

    return pairs

def generate_scope_pairs():
    """generate pairs of sentences and LFs with scope ambiguities
    of the form
    "every man hears a bird"
        exists x . forall y . exists a . man(y) AND bird(x) AND hear(a) AND agent(a, y) AND patient(a, x) 
        forall x . exists y . exists a . man(x) AND bird(y) AND hear(a) AND agent(a, x) AND patient(a, y)
    """
    pairs = []
    
    every_template_text = ["every", INDEFINITE_SENTIENT_NPS, TRANSITIVE_VPS, "a", INDEFINITE_NPS]
    every_template_tags = [None, "np1", "vp1", None, "np2"]
    every_template = Template(every_template_text, every_template_tags)
    
    lf_template_1 = "exists x . forall y . exists a . {np1}(y) AND {np2}(x) AND {vp1}(a) AND agent(a, y) AND patient(a, x)"
    lf_template_2 = "forall x . exists y . exists a . {np1}(x) AND {np2}(y) AND {vp1}(a) AND agent(a, x) AND patient(a, y)"

    pairs += every_template.generate(lf_template_1, 0, "scope")
    pairs += every_template.generate(lf_template_2, 1, "scope")

    each_template_text = ["each", INDEFINITE_SENTIENT_NPS, TRANSITIVE_VPS, "a", INDEFINITE_NPS]
    each_template_tags = [None, "np1", "vp1", None, "np2"]
    each_template = Template(each_template_text, each_template_tags)

    pairs += each_template.generate(lf_template_1, 0, "scope")
    pairs += each_template.generate(lf_template_2, 1, "scope")

    return pairs 

def generate_reverse_scope_pairs():
    """generate pairs of sentences and LFs with scope ambiguities but with quants at the end
    of the form
    "a man heard every bird"
        exists x . forall y . exists a . man(y) AND bird(x) AND hear(a) AND agent(a, y) AND patient(a, x) 
        forall x . exists y . exists a . man(x) AND bird(y) AND hear(a) AND agent(a, x) AND patient(a, y)
    """
    pairs = []
    
    # every_template_text = ["every", INDEFINITE_SENTIENT_NPS, TRANSITIVE_VPS, "a", INDEFINITE_NPS]
    every_template_text = ["a", INDEFINITE_SENTIENT_NPS, TRANSITIVE_VPS, "every", INDEFINITE_NPS]
    every_template_tags = [None, "np1", "vp1", None, "np2"]
    every_template = Template(every_template_text, every_template_tags)
    
    lf_template_1 = "exists x . forall y . exists a . {np1}(x) AND {np2}(y) AND {vp1}(a) AND agent(a, x) AND patient(a, y)"
    lf_template_2 = "forall x . exists y . exists a . {np1}(y) AND {np2}(x) AND {vp1}(a) AND agent(a, y) AND patient(a, x)"
    
    pairs += every_template.generate(lf_template_1, 0, "scope_reverse")
    pairs += every_template.generate(lf_template_2, 1, "scope_reverse")

    # each_template_text = ["each", INDEFINITE_SENTIENT_NPS, TRANSITIVE_VPS, "a", INDEFINITE_NPS]
    each_template_text = ["a", INDEFINITE_SENTIENT_NPS, TRANSITIVE_VPS, "each", INDEFINITE_NPS]
    each_template_tags = [None, "np1", "vp1", None, "np2"]
    each_template = Template(each_template_text, each_template_tags)

    pairs += each_template.generate(lf_template_1, 0, "scope_reverse")
    pairs += each_template.generate(lf_template_2, 1, "scope_reverse")

    return pairs 

def generate_unambiguous_scope():
    """
    generate unambiguous scope sentences  
    e.g. "every man walks" 
    "each person sees the dog"
    """
    pairs = []

    every_trans_template_text = ["every", INDEFINITE_SENTIENT_NPS, TRANSITIVE_VPS, "the", INDEFINITE_NPS]
    every_trans_template_tags = [None, "np1", "vp1", None, "np2"]
    every_trans_template = Template(every_trans_template_text, every_trans_template_tags)
    trans_lf_template = "exists x . forall y . exists a . {np1}(y) AND {np2}(x) AND {vp1}(a) AND agent(a, y) AND patient(a, x)"
    pairs += every_trans_template.generate(trans_lf_template, 0, "scope_unambig")

    each_trans_template_text = ["each", INDEFINITE_SENTIENT_NPS, TRANSITIVE_VPS, "the", INDEFINITE_NPS]
    each_trans_template_tags = [None, "np1", "vp1", None, "np2"]
    each_trans_template = Template(each_trans_template_text, each_trans_template_tags)
    pairs += each_trans_template.generate(trans_lf_template, 0, "scope_unambig")

    every_intrans_template_text = ["every", INDEFINITE_SENTIENT_NPS, INTRANSITIVE_VPS]
    every_intrans_template_tags = [None, "np1", "vp1"]
    every_intrans_template = Template(every_intrans_template_text, every_intrans_template_tags)
    intrans_lf_template = "forall y . exists a . {np1}(y) AND {vp1}(a) AND agent(a, y)"
    pairs += every_intrans_template.generate(intrans_lf_template, 0, "scope_unambig")
    
    each_intrans_template_text = ["each", INDEFINITE_SENTIENT_NPS, INTRANSITIVE_VPS]
    each_intrans_template_tags = [None, "np1", "vp1"]
    each_intrans_template = Template(each_intrans_template_text, each_intrans_template_tags)
    pairs += each_intrans_template.generate(intrans_lf_template, 0, "scope_unambig")


    return pairs 

def generate_unambiguous_quant_only():
    """
    sentences with quantifiers but no VP
    "every man"
    "each person"
    """
    pairs = []
    every_template_text = ["every", INDEFINITE_NPS]
    template_tags = [None, "np1"]
    every_template = Template(every_template_text, template_tags)
    lf_template = "forall x . {np1}(x)"
    pairs += every_template.generate(lf_template, 0, "unambig_quant")

    each_template_text = ["each", INDEFINITE_NPS]
    each_template = Template(each_template_text, template_tags)
    pairs += each_template.generate(lf_template, 0, "unambig_quant")
    return pairs 

def generate_bound_pronoun_pairs(is_female=True):
    """
    generate ambiguous pairs with bound gendered pronouns 
    i.e. 
    "Bill saw John and he waved"
    "The woman observed Mary and she lept"
    """
    pairs = []

    if is_female:
        name_choices = FEMALE_NAMES
        indef_choices = INDEFINITE_FEMALE_NPS
        conj_statement = "and she"
    else:
        name_choices = MALE_NAMES
        indef_choices = INDEFINITE_MALE_NPS
        conj_statement = "and he"

    def_def_template_text = [name_choices, VISUAL_VPS, name_choices, conj_statement, INTRANSITIVE_VPS_FOR_BOUND]
    def_def_template_tags = ["np1", "vp1", "np2", None, "vp2"]
    def_def_template = Template(def_def_template_text, def_def_template_tags)
    def_def_lf_template_1  = "exists a . exists e . {vp1}(a) AND agent(a, {np1}) AND patient(a, {np2}) AND {vp2}(e) AND agent(e, {np1})"
    def_def_lf_template_2  = "exists a . exists e . {vp1}(a) AND agent(a, {np1}) AND patient(a, {np2}) AND {vp2}(e) AND agent(e, {np2})"

    pairs += def_def_template.generate(def_def_lf_template_1, 0, "bound")
    pairs += def_def_template.generate(def_def_lf_template_2, 1, "bound") 


    indef_def_template_text = ["the", indef_choices, VISUAL_VPS, name_choices, conj_statement, INTRANSITIVE_VPS_FOR_BOUND]
    indef_def_template_tags = [None, "np1", "vp1", "np2", None, "vp2"]
    indef_def_template = Template(indef_def_template_text, indef_def_template_tags)
    indef_def_lf_template_1  = "exists x . exists a . exists e . {np1}(x) AND {vp1}(a) AND agent(a, x) AND patient(a, {np2}) AND {vp2}(e) AND agent(e, x)"
    indef_def_lf_template_2  = "exists x . exists a . exists e . {np1}(x) AND {vp1}(a) AND agent(a, x) AND patient(a, {np2}) AND {vp2}(e) AND agent(e, {np2})"

    pairs += indef_def_template.generate(indef_def_lf_template_1, 0, "bound")
    pairs += indef_def_template.generate(indef_def_lf_template_2, 1, "bound")

    def_indef_template_text = [name_choices, VISUAL_VPS, "the", indef_choices, conj_statement, INTRANSITIVE_VPS_FOR_BOUND]
    def_indef_template_tags = ["np1", "vp1", None, "np2", None, "vp2"]
    def_indef_template = Template(def_indef_template_text, def_indef_template_tags)
    def_indef_lf_template_1  = "exists x . exists a . exists e . {np2}(x) AND {vp1}(a) AND agent(a, {np1}) AND patient(a, x) AND {vp2}(e) AND agent(e, {np1})"
    def_indef_lf_template_2  = "exists x . exists a . exists e . {np2}(x) AND {vp1}(a) AND agent(a, {np1}) AND patient(a, x) AND {vp2}(e) AND agent(e, x)"

    pairs += def_indef_template.generate(def_indef_lf_template_1, 0, "bound")
    pairs += def_indef_template.generate(def_indef_lf_template_2, 1, "bound")

    indef_indef_template_text = ["the", indef_choices, VISUAL_VPS, "the", indef_choices, conj_statement, INTRANSITIVE_VPS_FOR_BOUND]
    indef_indef_template_tags = [None, "np1", "vp1", None, "np2", None, "vp2"]
    indef_indef_template = Template(indef_indef_template_text, indef_indef_template_tags)
    indef_indef_lf_template_1  = "exists x . exists y . exists a . exists e . {np1}(x) AND {np2}(y) AND {vp1}(a) AND agent(a, x) AND patient(a, y) AND {vp2}(e) AND agent(e, x)"
    indef_indef_lf_template_2  = "exists x . exists y . exists a . exists e . {np1}(x) AND {np2}(y) AND {vp1}(a) AND agent(a, x) AND patient(a, y) AND {vp2}(e) AND agent(e, y)"

    pairs += indef_indef_template.generate(indef_indef_lf_template_1, 0, "bound")
    pairs += indef_indef_template.generate(indef_indef_lf_template_2, 1, "bound")

    return pairs 

def generate_unambigous_bound_pronoun(is_female=True):
    """
    generate unambiguous pairs with bound gendered pronouns 
    i.e. 
    "Bill saw Mary and he waved"
    "The woman observed John and he lept"
    """

    pairs = []

    if is_female:
        subj_name_choices = FEMALE_NAMES
        subj_indef_choices = INDEFINITE_FEMALE_NPS
        obj_name_choices = MALE_NAMES
        obj_indef_choices = INDEFINITE_MALE_NPS
        subj_conj_statement = "and she"
        obj_conj_statement = "and he"
    else:
        subj_name_choices = MALE_NAMES
        subj_indef_choices = INDEFINITE_MALE_NPS
        obj_name_choices = FEMALE_NAMES
        obj_indef_choices = INDEFINITE_FEMALE_NPS
        subj_conj_statement = "and he"
        obj_conj_statement = "and she"

    def_def_subj_template_text = [subj_name_choices, VISUAL_VPS, obj_name_choices, subj_conj_statement, INTRANSITIVE_VPS_FOR_BOUND]
    def_def_subj_template_tags = ["np1", "vp1", "np2", None, "vp2"]
    def_def_subj_template = Template(def_def_subj_template_text, def_def_subj_template_tags)
    def_def_subj_lf_template  = "exists a . exists e . {vp1}(a) AND agent(a, {np1}) AND patient(a, {np2}) AND {vp2}(e) AND agent(e, {np1})"
    pairs += def_def_subj_template.generate(def_def_subj_lf_template, 0, "bound_unambig")

    def_def_obj_template_text = [subj_name_choices, VISUAL_VPS, obj_name_choices, obj_conj_statement, INTRANSITIVE_VPS_FOR_BOUND]
    def_def_obj_template_tags = ["np1", "vp1", "np2", None, "vp2"]
    def_def_obj_template = Template(def_def_obj_template_text, def_def_obj_template_tags)
    def_def_obj_lf_template  = "exists a . exists e . {vp1}(a) AND agent(a, {np1}) AND patient(a, {np2}) AND {vp2}(e) AND agent(e, {np2})"
    pairs += def_def_obj_template.generate(def_def_obj_lf_template, 0, "bound_unambig")


    indef_def_subj_template_text = ["the", subj_indef_choices, VISUAL_VPS, obj_name_choices, subj_conj_statement, INTRANSITIVE_VPS_FOR_BOUND]
    indef_def_subj_template_tags = [None, "np1", "vp1", "np2", None, "vp2"]
    indef_def_subj_template = Template(indef_def_subj_template_text, indef_def_subj_template_tags)
    indef_def_subj_lf_template  = "exists x . exists a . exists e . {np1}(x) AND {vp1}(a) AND agent(a, x) AND patient(a, {np2}) AND {vp2}(e) AND agent(e, x)"
    pairs += indef_def_subj_template.generate(indef_def_subj_lf_template, 0, "bound_unambig") 

    indef_def_obj_template_text = ["the", subj_indef_choices, VISUAL_VPS, obj_name_choices, obj_conj_statement, INTRANSITIVE_VPS_FOR_BOUND]
    indef_def_obj_template_tags = [None, "np1", "vp1", "np2", None, "vp2"]
    indef_def_obj_template = Template(indef_def_obj_template_text, indef_def_obj_template_tags)
    indef_def_obj_lf_template  = "exists x . exists a . exists e . {np1}(x) AND {vp1}(a) AND agent(a, x) AND patient(a, {np2}) AND {vp2}(e) AND agent(e, {np2})"
    pairs += indef_def_obj_template.generate(indef_def_obj_lf_template, 0, "bound_unambig")

    def_indef_subj_template_text = [subj_name_choices, VISUAL_VPS, "the", obj_indef_choices, subj_conj_statement, INTRANSITIVE_VPS_FOR_BOUND]
    def_indef_subj_template_tags = ["np1", "vp1", None, "np2", None, "vp2"]
    def_indef_subj_template = Template(def_indef_subj_template_text, def_indef_subj_template_tags)
    def_indef_subj_lf_template  = "exists x . exists a . exists e . {np2}(x) AND {vp1}(a) AND agent(a, {np1}) AND patient(a, x) AND {vp2}(e) AND agent(e, {np1})"
    pairs += def_indef_subj_template.generate(def_indef_subj_lf_template, 0, "bound_unambig")

    def_indef_obj_template_text = [subj_name_choices, VISUAL_VPS, "the", obj_indef_choices, obj_conj_statement, INTRANSITIVE_VPS_FOR_BOUND]
    def_indef_obj_template_tags = ["np1", "vp1", None, "np2", None, "vp2"]
    def_indef_obj_template = Template(def_indef_obj_template_text, def_indef_obj_template_tags)
    def_indef_obj_lf_template = "exists x . exists a . exists e . {np2}(x) AND {vp1}(a) AND agent(a, {np1}) AND patient(a, x) AND {vp2}(e) AND agent(e, x)"
    pairs += def_indef_obj_template.generate(def_indef_obj_lf_template, 0, "bound_unambig")

    indef_indef_subj_template_text = ["the", subj_indef_choices, VISUAL_VPS, "the", obj_indef_choices, subj_conj_statement, INTRANSITIVE_VPS_FOR_BOUND]
    indef_indef_subj_template_tags = [None, "np1", "vp1", None, "np2", None, "vp2"]
    indef_indef_subj_template = Template(indef_indef_subj_template_text, indef_indef_subj_template_tags)
    indef_indef_subj_lf_template  = "exists x . exists y . exists a . exists e . {np1}(x) AND {np2}(y) AND {vp1}(a) AND agent(a, x) AND patient(a, y) AND {vp2}(e) AND agent(e, x)"
    pairs += indef_indef_subj_template.generate(indef_indef_subj_lf_template, 0, "bound_unambig")

    indef_indef_obj_template_text = ["the", subj_indef_choices, VISUAL_VPS, "the", obj_indef_choices, obj_conj_statement, INTRANSITIVE_VPS_FOR_BOUND]
    indef_indef_obj_template_tags = [None, "np1", "vp1", None, "np2", None, "vp2"]
    indef_indef_obj_template = Template(indef_indef_obj_template_text, indef_indef_obj_template_tags)
    indef_indef_obj_lf_template  = "exists x . exists y . exists a . exists e . {np1}(x) AND {np2}(y) AND {vp1}(a) AND agent(a, x) AND patient(a, y) AND {vp2}(e) AND agent(e, y)"
    pairs += indef_indef_obj_template.generate(indef_indef_obj_lf_template, 0, "bound_unambig")

    return pairs 

def generate_unambiguous_basic():
    pairs = generate_unambiguous_basic_helper("the")
    pairs += generate_unambiguous_basic_helper("a")
    return pairs 

def generate_unambiguous_basic_helper(article="the"):
    """
    generate unambiguous sentences
    of the form:
    "The man saw the boy"
    "The man walked"
    """
    pairs = []
    indef_indef_transitive_text = [article, INDEFINITE_SENTIENT_NPS, TRANSITIVE_VPS, article, INDEFINITE_NPS]
    indef_indef_transitive_tags = [None, 'np1', 'vp1', None, 'np2']
    indef_indef_transitive_template = Template(indef_indef_transitive_text, indef_indef_transitive_tags)
    indef_indef_lf_template = "exists x . exists y . exists a . {np1}(x) AND {np2}(y) AND {vp1}(a) AND agent(a, x) AND patient(a, y)"
    pairs += indef_indef_transitive_template.generate(indef_indef_lf_template, 0, "unambig")

    indef_def_transitive_text = [article, INDEFINITE_SENTIENT_NPS, TRANSITIVE_VPS, NAMES]
    indef_def_transitive_tags = [None, 'np1', 'vp1', 'np2']
    indef_def_transitive_template = Template(indef_def_transitive_text, indef_def_transitive_tags)
    indef_def_lf_template = "exists x . exists a . {np1}(x) AND {vp1}(a) AND agent(a, x) AND patient(a, {np2})"
    pairs += indef_def_transitive_template.generate(indef_def_lf_template, 0, "unambig")

    def_indef_transitive_text = [NAMES, TRANSITIVE_VPS, article, INDEFINITE_NPS]
    def_indef_transitive_tags = ['np1', 'vp1', None, 'np2']
    def_indef_transitive_template = Template(def_indef_transitive_text, def_indef_transitive_tags)
    def_indef_lf_template = "exists x . exists a . {np2}(x) AND {vp1}(a) AND agent(a, {np1}) AND patient(a, x)"
    pairs += def_indef_transitive_template.generate(def_indef_lf_template, 0, "unambig")

    if article == "the": # only generate for one article so they're not doubled
        def_def_transitive_text = [NAMES, TRANSITIVE_VPS, NAMES]
        def_def_transitive_tags = ['np1', 'vp1', 'np2']
        def_def_transitive_template = Template(def_def_transitive_text, def_def_transitive_tags)
        def_def_lf_template = "exists a . {vp1}(a) AND agent(a, {np1}) AND patient(a, {np2})"
        pairs += def_def_transitive_template.generate(def_def_lf_template, 0, "unambig")

    indef_intransitive_text = [article, INDEFINITE_SENTIENT_NPS, INTRANSITIVE_VPS + INTRANSITIVE_VPS_FOR_BOUND]
    indef_intransitive_tags = [None, 'np1', 'vp1']
    indef_intransitive_template = Template(indef_intransitive_text, indef_intransitive_tags)
    indef_intransitive_lf_template = "exists x . exists a . {np1}(x) AND {vp1}(a) AND agent(a, x)"
    pairs += indef_intransitive_template.generate(indef_intransitive_lf_template, 0, "unambig")

    if article == "the": # only generate for one article so they're not doubled
        def_intransitive_text = [NAMES, INTRANSITIVE_VPS + INTRANSITIVE_VPS_FOR_BOUND]
        def_intransitive_tags = ['np1', 'vp1']
        def_intransitive_template = Template(def_intransitive_text, def_intransitive_tags)
        def_intransitive_lf_template = "exists a . {vp1}(a) AND agent(a, {np1})"
        pairs += def_intransitive_template.generate(def_intransitive_lf_template, 0, "unambig")

    return pairs 

def generate_unambiguous_conj():
    """Generate unambigous examples with conjunctions and disjunctions
    "The man walked or ate"
    """
    pairs = []

    conj_indef_intransitive_text = ['the', INDEFINITE_SENTIENT_NPS, INTRANSITIVE_VPS + INTRANSITIVE_VPS_FOR_BOUND, "and", INTRANSITIVE_VPS + INTRANSITIVE_VPS_FOR_BOUND]
    conj_indef_intransitive_tags = [None, 'np1', 'vp1', None, "vp2"]
    conj_indef_intransitive_template = Template(conj_indef_intransitive_text, conj_indef_intransitive_tags)
    conj_indef_intransitive_lf_template = "exists x . exists a . exists e . {np1}(x) AND {vp1}(a) AND agent(a, x) AND {vp2}(e) AND agent(e, x)"
    pairs += conj_indef_intransitive_template.generate(conj_indef_intransitive_lf_template, 0, "unambig")

    conj_def_intransitive_text = [NAMES, INTRANSITIVE_VPS + INTRANSITIVE_VPS_FOR_BOUND, "and", INTRANSITIVE_VPS + INTRANSITIVE_VPS_FOR_BOUND]
    conj_def_intransitive_tags = ['np1', 'vp1', None, "vp2"]
    conj_def_intransitive_template = Template(conj_def_intransitive_text, conj_def_intransitive_tags)
    conj_def_intransitive_lf_template = "exists a . exists e . {vp1}(a) AND agent(a, {np1}) AND {vp2}(e) AND agent(e, {np1})"
    pairs += conj_def_intransitive_template.generate(conj_def_intransitive_lf_template, 0, "unambig")

    disj_indef_intransitive_text = ['the', INDEFINITE_SENTIENT_NPS, INTRANSITIVE_VPS + INTRANSITIVE_VPS_FOR_BOUND, "or", INTRANSITIVE_VPS + INTRANSITIVE_VPS_FOR_BOUND]
    disj_indef_intransitive_tags = [None, 'np1', 'vp1', None, "vp2"]
    disj_indef_intransitive_template = Template(disj_indef_intransitive_text, disj_indef_intransitive_tags)
    disj_indef_intransitive_lf_template = "exists x . exists a . exists e . {np1}(x) AND ( {vp1}(a) AND agent(a, x) ) OR ( {vp2}(e) AND agent(e, x) )"
    pairs += disj_indef_intransitive_template.generate(disj_indef_intransitive_lf_template, 0, "unambig")

    disj_def_intransitive_text = [NAMES, INTRANSITIVE_VPS + INTRANSITIVE_VPS_FOR_BOUND, "or", INTRANSITIVE_VPS + INTRANSITIVE_VPS_FOR_BOUND]
    disj_def_intransitive_tags = ['np1', 'vp1', None, "vp2"]
    disj_def_intransitive_template = Template(disj_def_intransitive_text, disj_def_intransitive_tags)
    disj_def_intransitive_lf_template = "exists a . exists e . ( {vp1}(a) AND agent(a, {np1}) ) OR ( {vp2}(e) AND agent(e, {np1}) )"
    pairs += disj_def_intransitive_template.generate(disj_def_intransitive_lf_template, 0, "unambig")

    return pairs  

def generate_unambiguous_double_conj():
    """
    Generate unambiguous examples with two subjects and conjunction and disjuction
    "The man walked and slept and ate"
    "the boy napped or drew or drank"
    """
    pairs = []
    and_template_text = ["the", INDEFINITE_SENTIENT_NPS, INTRANSITIVE_VPS, "and", INTRANSITIVE_VPS, "and", INTRANSITIVE_VPS]
    and_first_template_tags = [None, "np1", "vp1", None, "vp2", None, "vp3"] 
    and_template = Template(and_template_text, and_first_template_tags)

    and_first_lf_template_1 = "exists x . exists a . exists e . exists i . {np1}(x) AND {vp1}(a) AND agent(a, x) AND ( ( {vp2}(e) AND agent(e, x) ) AND ( {vp3}(i) AND agent(i, x) ) )"
    and_first_lf_template_2 = "exists x . exists a . exists e . exists i . {np1}(x) AND ( {vp1}(a) AND agent(a, x) AND {vp2}(e) AND agent(e, x) ) AND {vp3}(i) AND agent(i, x)"

    pairs += and_template.generate(and_first_lf_template_1, 0, "unambig_conj")
    pairs += and_template.generate(and_first_lf_template_2, 1, "unambig_conj")

    or_template_text = ['the', INDEFINITE_SENTIENT_NPS, INTRANSITIVE_VPS, 'or', INTRANSITIVE_VPS, 'or', INTRANSITIVE_VPS]
    or_template_tags = [None, 'np1', 'vp1', None, 'vp2', None, 'vp3']

    or_template = Template(or_template_text, or_template_tags)

    or_lf_template_1 = "exists x . exists a . exists e . exists i . {np1}(x) ( ( AND {vp1}(a) AND agent(a, x) ) OR ( {vp2}(e) AND agent(e, x) ) ) OR ( {vp3}(i) AND agent(i, x) )" 
    or_lf_template_2 = "exists x . exists a . exists e . exists i . {np1}(x) ( AND {vp1}(a) AND agent(a, x) ) OR ( ( {vp2}(e) AND agent(e, x) ) OR ( {vp3}(i) AND agent(i, x) ) )"

    pairs += or_template.generate(or_lf_template_1, 0, "unambig_conj")
    pairs += or_template.generate(or_lf_template_2, 1, "unambig_conj")

    return pairs


def generate_unambiguous_instrument(vp_list, pp_str, pp_np_list):
    """
    Generate unambiguous examples of intransitive verbs being used with instruments.
    E.g. the man observed with a telescope.
    """
    # visual templates 
    pairs = []
    indef_indef_template_text = ["the", INDEFINITE_HUMAN_NPS, vp_list, pp_str, pp_np_list]
    indef_indef_template_tags = [None, "np1", "vp1", None, "np2"] 
    indef_indef_template = Template(indef_indef_template_text, indef_indef_template_tags)

    indef_indef_lf_template = "exists x . exists y . exists a . {np1}(x) AND {np2}(y)"+\
                    " AND {vp1}(a) AND agent(a, x) AND instrument(a, y)"

    pairs += indef_indef_template.generate(indef_indef_lf_template, 0, "instr_unambig")


    def_indef_template_text = [NAMES, vp_list,  pp_str, pp_np_list]
    def_indef_template_tags = ["np1", "vp1", None, "np2"]
    def_indef_template = Template(def_indef_template_text, def_indef_template_tags) 


    def_indef_lf_template = "exists x . exists a . {np2}(x)"+\
                    " AND {vp1}(a) AND agent(a, {np1}) AND instrument(a, x)"

    pairs += def_indef_template.generate(def_indef_lf_template, 0, "pp")

    return pairs

def generate_unambiguous_instr_pairs():
    visual_pairs = generate_unambiguous_instrument(vp_list=VISUAL_VPS,
                                             pp_str="with the",
                                             pp_np_list = VISUAL_INSTRUMENT_NPS)

    tactile_pairs = generate_unambiguous_instrument(vp_list = TACTILE_VPS,
                                                pp_str = "with the",
                                                pp_np_list = TACTILE_INSTRUMENT_NPS)

    return visual_pairs + tactile_pairs

def generate_unambiguous_possession(np_list=VISUAL_INSTRUMENT_NPS):
    """
    Generate unambious examples of the `have` predicate with `with` surface form, e.g.
    "the man with the telescope"
    """
    pairs = []
    indef_template_text = ["the", INDEFINITE_HUMAN_NPS, "with the", np_list]
    indef_template_tags = [None, "np1", None, "np2"]
    indef_template = Template(indef_template_text, indef_template_tags)
    indef_lf_template = "exists x . exists y . exists a . {np1}(x) AND {np2}(y) AND have(a)"+\
                        " AND agent(a, x) AND patient(a, y)"
    pairs += indef_template.generate(indef_lf_template, 0, 'possession')

    def_template_text = [NAMES, "with the", np_list]
    def_template_tags = ["np1", None, "np2"]
    def_template = Template(def_template_text, def_template_tags)
    def_lf_template = "exists x . exists a . {np2}(x) AND have(a)"+\
                        " AND agent(a, {np1}) AND patient(a, x)"

    pairs += def_template.generate(def_lf_template, 0, 'possession')
    return pairs 

def generate_unambiguous_possession_pairs():
    visual_pairs = generate_unambiguous_possession(VISUAL_INSTRUMENT_NPS)
    tactile_pairs = generate_unambiguous_possession(TACTILE_INSTRUMENT_NPS)
    return visual_pairs + tactile_pairs 


if __name__ == "__main__":
    pp_pairs = generate_pp_pairs()
    unambig_pp = generate_unambiguous_pp()

    scope_pairs = generate_scope_pairs()
    reverse_scope_pairs = generate_reverse_scope_pairs()
    unambig_scope = generate_unambiguous_scope()

    conj_pairs = generate_conjunction_pairs()
    unambig_conj = generate_unambiguous_conj()

    bound_pairs = generate_bound_pronoun_pairs(is_female=True)+\
                generate_bound_pronoun_pairs(is_female=False)
    unambig_bound = generate_unambigous_bound_pronoun(is_female=True) + \
                    generate_unambigous_bound_pronoun(is_female=False)

    unambiguous = generate_unambiguous_basic()

    all_data = pp_pairs + unambig_pp + \
               scope_pairs + reverse_scope_pairs + unambig_scope + \
                conj_pairs + unambig_conj + \
                bound_pairs + unambig_bound + \
                unambiguous
    pdb.set_trace()