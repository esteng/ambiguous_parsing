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
    AUDITORY_VPS, 
    OTHER_VPS, 
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
    pdb.set_trace()


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
                    " have(e) AND agent(e, y) AND patient(e, z)"

    indef_indef_lf_template_2 = "exists x . exists y . exists z . exists a . {np1}(x) AND {np2}(y)"+\
                    " AND {vp1}(a) AND agent(a, x) AND patient(a, y) AND instrument(a, z)"

    pairs += indef_indef_template.generate(indef_indef_lf_template_1)
    pairs += indef_indef_template.generate(indef_indef_lf_template_2)

    indef_def_template_text = ["the", INDEFINITE_HUMAN_NPS, vp_list, NAMES, pp_str, pp_np_list]
    indef_def_template_tags = [None, "np1", "vp1", "np2", None, "np3"]
    indef_def_template = Template(indef_def_template_text, indef_def_template_tags)

    indef_def_lf_template_1 = "exists x . exists y .  exists a . exists e . {np1}(x) AND {np3}(y)"+\
                    " AND {vp1}(a) AND agent(a, x) AND patient(a, {np2})  AND " +\
                    " have(e) AND agent(e, {np2}) AND patient(e, y)"

    indef_def_lf_template_2 = "exists x . exists y . exists a . {np1}(x) AND {np3}(y)"+\
                    " AND {vp1}(a) AND agent(a, x) AND patient(a, {np2}) AND instrument(a, y)"

    pairs += indef_def_template.generate(indef_def_lf_template_1)
    pairs += indef_def_template.generate(indef_def_lf_template_2)


    def_indef_template_text = [NAMES, vp_list, "the", INDEFINITE_HUMAN_NPS,  pp_str, pp_np_list]
    def_indef_template_tags = ["np1", "vp1", None, "np2", None, "np3"]
    def_indef_template = Template(def_indef_template_text, def_indef_template_tags) 

    def_indef_lf_template_1 = "exists x . exists y . exists a . exists e . {np2}(x) AND {np3}(y)"+\
                    " AND {vp1}(a) AND agent(a, {np1}) AND patient(a, x) AND " +\
                    " have(e) AND agent(e, x) AND patient(e, y)"

    def_indef_lf_template_2 = "exists x . exists y . exists a . {np2}(x) AND {np3}(y)"+\
                    " AND {vp1}(a) AND agent(a, {np1}) AND patient(a, x) AND instrument(a, y)"

    pairs += def_indef_template.generate(def_indef_lf_template_1)
    pairs += def_indef_template.generate(def_indef_lf_template_2)

    def_def_template_text = [NAMES, vp_list, NAMES,  pp_str, pp_np_list]
    def_def_template_tags = ["np1", "vp1", "np2", None, "np3"]
    def_def_template = Template(def_def_template_text, def_def_template_tags) 

    def_def_lf_template_1 = "exists x . exists a . exists e . {np3}(x)"+\
                    " AND {vp1}(a) AND agent(a, {np1}) AND patient(a, {np2}) AND " +\
                    " have(e) AND agent(e, {np2}) AND patient(e, x)"

    def_def_lf_template_2 = "exists x . exists a . {np3}(x)"+\
                    " AND {vp1}(a) AND agent(a, {np1}) AND patient(a, {np2}) AND instrument(a, x)"

    pairs += def_def_template.generate(def_def_lf_template_1)
    pairs += def_def_template.generate(def_def_lf_template_2)

    return pairs
    

def generate_conjunction_pairs():
    """generate pairs of sentences with conjunction ambiguities
    of the form:
    "The man ate and drank or slept"
        exists x . exists a . exists e . exists i . man(x) AND eat(a) AND agent(a, x) AND ( ( drank(e) AND agent(e, x) ) OR ( slept(i) AND agent(i, x) ) )
        exists x . exists a . exists e . exists i . ( man(x) AND eat(a) AND agent(a, x) AND drank(e) AND agent(e, x) ) OR ( slept(i) AND agent(i, x) ) )
    """
    pass

def generate_wordsense_pairs():
    # generate pairs of sentences and LFs with word sense ambiguities
    pass

def generate_scope_pairs():
    """generate pairs of sentences and LFs with scope ambiguities
    of the form
    "every man hears a bird"
        exists x . forall y . exists a . man(y) AND bird(x) AND hear(a) AND agent(a, y) AND patient(a, x) 
        forall x . exists y . exists a . man(x) AND bird(y) AND hear(a) AND agent(a, x) AND patient(a, y)
    """
    
    template_text = ["every", INDEFINITE_SENTIENT_NPS, VPS, "a", INDEFINITE_NPS]
    template_tags = [None, "np1", "vp1", None, "np2"]
    template = Template(template_text, template_tags)
    
    lf_template_1 = "exists x . forall y . exists a . {np1}(y) AND {np2}(x) AND {vp1}(a) AND agent(a, y) AND patient(a, x)"
    lf_template_2 = "forall x . exists y . exists a . {np1}(x) AND {np2}(y) AND {vp1}(a) AND agent(a, x) AND patient(a, y)"

    pairs = []
    pairs += template.generate(lf_template_1)
    pairs += template.generate(lf_template_2)

    pdb.set_trace()
    return pairs 


if __name__ == "__main__":
    # generate_pp_pairs()
    generate_scope_pairs()