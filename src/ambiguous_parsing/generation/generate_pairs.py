import itertools 
import copy 
import pdb 


from ambiguous_parsing.generation.fixtures.nps import (
    INDEFINITE_NPS,
    INDEFINITE_HUMAN_NPS, 
    NAMES, 
    VISUAL_INSTRUMENT_NPS, 
    TACTILE_INSTRUMENT_NPS,
    INDEFINITE_SENTIENT_NPS
)
from ambiguous_parsing.generation.fixtures.vps import (
    VISUAL_VPS, 
    TACTILE_VPS, 
    INTRANSITIVE_VPS,
    TRANSITIVE_VPS,
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

    indef_indef_lf_template_2 = "exists x . exists y . exists z . exists a . {np1}(x) AND {np2}(y)"+\
                    " AND {vp1}(a) AND agent(a, x) AND patient(a, y) AND instrument(a, z)"

    pairs += indef_indef_template.generate(indef_indef_lf_template_1, 0, "pp")
    pairs += indef_indef_template.generate(indef_indef_lf_template_2, 1, "pp")

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
    

def generate_conjunction_pairs():
    """generate pairs of sentences with conjunction ambiguities
    of the form:
    "The man ate and drank or slept"
        exists x . exists a . exists e . exists i . man(x) AND eat(a) AND agent(a, x) AND ( ( drank(e) AND agent(e, x) ) OR ( slept(i) AND agent(i, x) ) )
        exists x . exists a . exists e . exists i . ( man(x) AND eat(a) AND agent(a, x) AND drank(e) AND agent(e, x) ) OR ( slept(i) AND agent(i, x) ) )
    """
    pairs = []
    and_first_template_text = ["the", INDEFINITE_NPS, INTRANSITIVE_VPS, "and", INTRANSITIVE_VPS, "or", INTRANSITIVE_VPS]
    and_first_template_tags = [None, "np1", "vp1", None, "vp2", None, "vp3"] 
    and_first_template = Template(and_first_template_text, and_first_template_tags)

    and_first_lf_template_1 = "exists x . exists a . exists e . exists i . {np1}(x) AND {vp1}(a) AND agent(a, x) AND ( ( {vp2}(e) AND agent(e, x) ) OR ( {vp3}(i) AND agent(i, x) ) )"
    and_first_lf_template_2 = "exists x . exists a . exists e . exists i . ( {np1}(x) AND {vp1}(a) AND agent(a, x) AND {vp2}(e) AND agent(e, x) ) OR ( {vp3}(i) AND agent(i, x) )"

    pairs += and_first_template.generate(and_first_lf_template_1, 0, "conj")
    pairs += and_first_template.generate(and_first_lf_template_2, 1, "conj")

    or_first_template_text = ['the', INDEFINITE_NPS, INTRANSITIVE_VPS, 'or', INTRANSITIVE_VPS, 'and', INTRANSITIVE_VPS]
    or_first_template_tags = [None, 'np1', 'vp1', None, 'vp2', None, 'vp3']

    or_first_template = Template(or_first_template_text, or_first_template_tags)

    or_first_lf_template_1 = "exists x . exists a . exists e . exists i . ( ( {np1}(x) AND {vp1}(a) AND agent(a, x) ) OR ( {vp2}(e) AND agent(e, x) ) ) AND {vp3}(i) AND agent(i, x)" 
    or_first_lf_template_2 = "exists x . exists a . exists e . exists i . ( {np1}(x) AND {vp1}(a) AND agent(a, x) ) OR ( {vp2}(e) AND agent(e, x) AND {vp3}(i) AND agent(i, x) )"

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
    
    every_template_text = ["every", INDEFINITE_SENTIENT_NPS, VPS, "a", INDEFINITE_NPS]
    every_template_tags = [None, "np1", "vp1", None, "np2"]
    every_template = Template(every_template_text, every_template_tags)
    
    lf_template_1 = "exists x . forall y . exists a . {np1}(y) AND {np2}(x) AND {vp1}(a) AND agent(a, y) AND patient(a, x)"
    lf_template_2 = "forall x . exists y . exists a . {np1}(x) AND {np2}(y) AND {vp1}(a) AND agent(a, x) AND patient(a, y)"

    pairs += every_template.generate(lf_template_1, 0, "scope")
    pairs += every_template.generate(lf_template_2, 1, "scope")

    each_template_text = ["each", INDEFINITE_SENTIENT_NPS, VPS, "a", INDEFINITE_NPS]
    each_template_tags = [None, "np1", "vp1", None, "np2"]
    each_template = Template(each_template_text, each_template_tags)

    pairs += each_template.generate(lf_template_1, 0, "scope")
    pairs += each_template.generate(lf_template_2, 1, "scope")

    return pairs 

def generate_unambiguous():
    """
    generate unambiguous sentences
    of the form:
    "The man saw the boy"
    "The man walked"
    and maybe also: 
    "The man saw the boy and the girl"
    "The man walked and ate
    """
    pairs = []
    indef_indef_transitive_text = ['the', INDEFINITE_SENTIENT_NPS, TRANSITIVE_VPS, 'the', INDEFINITE_NPS]
    indef_indef_transitive_tags = [None, 'np1', 'vp1', None, 'np2']
    indef_indef_transitive_template = Template(indef_indef_transitive_text, indef_indef_transitive_tags)
    indef_indef_lf_template = "exists x . exists y . exists a . {np1}(x) AND {np2}(y) AND {vp1}(a) AND agent(a, x) AND patient(a, y)"
    pairs += indef_indef_transitive_template.generate(indef_indef_lf_template, 0, "unambig")

    indef_def_transitive_text = ['the', INDEFINITE_SENTIENT_NPS, TRANSITIVE_VPS, NAMES]
    indef_def_transitive_tags = [None, 'np1', 'vp1', 'np2']
    indef_def_transitive_template = Template(indef_def_transitive_text, indef_def_transitive_tags)
    indef_def_lf_template = "exists x . exists a . {np1}(x) AND {vp1}(a) AND agent(a, x) AND patient(a, {np2})"
    pairs += indef_def_transitive_template.generate(indef_def_lf_template, 0, "unambig")

    def_indef_transitive_text = [NAMES, TRANSITIVE_VPS, 'the', INDEFINITE_NPS]
    def_indef_transitive_tags = ['np1', 'vp1', None, 'np2']
    def_indef_transitive_template = Template(def_indef_transitive_text, def_indef_transitive_tags)
    def_indef_lf_template = "exists x . exists a . {np2}(x) AND {vp1}(a) AND agent(a, {np1}) AND patient(a, y)"
    pairs += def_indef_transitive_template.generate(def_indef_lf_template, 0, "unambig")

    def_def_transitive_text = [NAMES, TRANSITIVE_VPS, NAMES]
    def_def_transitive_tags = ['np1', 'vp1', 'np2']
    def_def_transitive_template = Template(def_def_transitive_text, def_def_transitive_tags)
    def_def_lf_template = "exists a . {vp1}(a) AND agent(a, {np1}) AND patient(a, {np2})"
    pairs += def_def_transitive_template.generate(def_def_lf_template, 0, "unambig")

    indef_intransitive_text = ['the', INDEFINITE_SENTIENT_NPS, INTRANSITIVE_VPS]
    indef_intransitive_tags = [None, 'np1', 'vp1']
    indef_intransitive_template = Template(indef_intransitive_text, indef_intransitive_tags)
    indef_intransitive_lf_template = "exists x . exists a . {np1}(x) AND {vp1}(a) AND agent(a, x)"
    pairs += indef_intransitive_template.generate(indef_intransitive_lf_template, 0, "unambig")

    def_intransitive_text = [NAMES, INTRANSITIVE_VPS]
    def_intransitive_tags = ['np1', 'vp1']
    def_intransitive_template = Template(def_intransitive_text, def_intransitive_tags)
    def_intransitive_lf_template = "exists a . {vp1}(a) AND agent(a, {np1})"
    pairs += def_intransitive_template.generate(def_intransitive_lf_template, 0, "unambig")

    conj_indef_intransitive_text = ['the', INDEFINITE_SENTIENT_NPS, INTRANSITIVE_VPS, "and", INTRANSITIVE_VPS]
    conj_indef_intransitive_tags = [None, 'np1', 'vp1', None, "vp2"]
    conj_indef_intransitive_template = Template(conj_indef_intransitive_text, conj_indef_intransitive_tags)
    conj_indef_intransitive_lf_template = "exists x . exists a . exists e . {np1}(x) AND {vp1}(a) AND agent(a, x) AND {vp2}(e) AND agent(e, x)"
    pairs += conj_indef_intransitive_template.generate(conj_indef_intransitive_lf_template, 0, "unambig")

    conj_def_intransitive_text = [NAMES, INTRANSITIVE_VPS, "and", INTRANSITIVE_VPS]
    conj_def_intransitive_tags = ['np1', 'vp1', None, "vp2"]
    conj_def_intransitive_template = Template(conj_def_intransitive_text, conj_def_intransitive_tags)
    conj_def_intransitive_lf_template = "exists a . exists e . {vp1}(a) AND agent(a, {np1}) AND {vp2}(e) AND agent(e, {np1})"
    pairs += conj_def_intransitive_template.generate(conj_def_intransitive_lf_template, 0, "unambig")

    disj_indef_intransitive_text = ['the', INDEFINITE_SENTIENT_NPS, INTRANSITIVE_VPS, "or", INTRANSITIVE_VPS]
    disj_indef_intransitive_tags = [None, 'np1', 'vp1', None, "vp2"]
    disj_indef_intransitive_template = Template(disj_indef_intransitive_text, disj_indef_intransitive_tags)
    disj_indef_intransitive_lf_template = "exists x . exists a . exists e . ( {np1}(x) AND {vp1}(a) AND agent(a, x) ) OR ( {vp2}(e) AND agent(e, x) )"
    pairs += disj_indef_intransitive_template.generate(disj_indef_intransitive_lf_template, 0, "unambig")

    disj_def_intransitive_text = [NAMES, INTRANSITIVE_VPS, "or", INTRANSITIVE_VPS]
    disj_def_intransitive_tags = ['np1', 'vp1', None, "vp2"]
    disj_def_intransitive_template = Template(disj_def_intransitive_text, disj_def_intransitive_tags)
    disj_def_intransitive_lf_template = "exists a . exists e . ( {vp1}(a) AND agent(a, {np1}) ) OR ( {vp2}(e) AND agent(e, {np1}) )"
    pairs += disj_def_intransitive_template.generate(disj_def_intransitive_lf_template, 0, "unambig")

    return pairs    

if __name__ == "__main__":
    # generate_pp_pairs()
    # generate_scope_pairs()
    # generate_conjunction_pairs()
    unambiguous = generate_unambiguous()
    pdb.set_trace()