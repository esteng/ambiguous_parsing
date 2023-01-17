import itertools 
import copy 
import pdb 

from ambiguous_parsing.generation.fixtures.nps import INDEFINITE_HUMAN_NPS, NAMES, INDEFINITE_NPS, VISUAL_INSTRUMENT_NPS
from ambiguous_parsing.generation.fixtures.vps import VISUAL_VPS, TACTILE_VPS, AUDITORY_VPS, OTHER_VPS, VPS



class Template:
    def __init__(self, 
                 template_list,
                 template_tags):
        # a template list is a mixed type list of strings and lists of options 
        self.template_list = template_list
        self.template_tags = template_tags

        self.denotation_lookup = NAMES
        self.denotation_lookup.update(INDEFINITE_NPS)
        self.denotation_lookup.update(VPS)

        for k, v in self.denotation_lookup.items():
            if type(v) == str:
                self.denotation_lookup[k] = [v]

        if len(self.template_list) != len(self.template_tags):
            raise Exception("template list and template tags must be same length")

        for i, element in enumerate(self.template_list):
            if not isinstance(element, list):
                self.template_list[i] = [element]
                # make sure tag is None
                if isinstance(self.template_tags[i], str):
                    raise Exception("template tag must be None if template element is not a list")

    def product(self, *lists):
        def is_repeat(item, result, pool):
            # if singleton pool, then no repeats
            if len(pool) == 1:
                return False
            return item in result

        # like itertools.product but do not allow duplicate elements anywhere
        # e.g. product([1,2], [1,2]) = [(1,2), (2,1), (2,2)]
        result = []
        pools = [tuple(pool) for pool in lists] 
        result = [[]]
        for pool in pools:
            result = [x+[y] for x in result for y in pool if not is_repeat(y, x, pool)]
        for prod in result:
            yield tuple(prod)

    def expand_template(self):
        all_options = [x for x in self.product(*self.template_list)]
        return all_options

    def generate(self, lf_template):
        # generate iterates through template list and generates all possible combinations of strings
        all_surface = self.expand_template()
        # get LF for each surface form
        

        pairs = []
        for surface in all_surface:
            var_bindings = []
            lf_template_copy = copy.deepcopy(lf_template)
            # fill variables
            for i, token in enumerate(surface):
                if self.template_tags[i] is not None:
                    tag = self.template_tags[i]
                    denotations = self.denotation_lookup[token]
                    # if there are multiple denotations, then we need to fill in multiple times
                    var_bindings.append((tag, denotations))

            product_of_options = [x for x in itertools.product(*[x[1] for x in var_bindings])]
            tags = [x[0] for x in var_bindings]
            all_var_bindings = []

            for product in product_of_options:
                binding = {}
                for i, tok in enumerate(product):
                    tag = tags[i]
                    binding[tag] = tok
                all_var_bindings.append(binding)

            surface = " ".join(surface)
            for var_binding in all_var_bindings:
                filled = lf_template_copy.format(**var_binding)

                data = {"surface": surface, 
                        "lf": filled, 
                        "unfilled_template": lf_template,
                        "template_tags": self.template_tags, 
                        "var_bindings": var_binding}
                pairs.append(data) 

        return pairs 

def generate_pp_pairs():
    # generate pairs of sentences and LFs with PP attachment ambiguities
    # format of sentences: 
    # "The boy saw the man with the telescope." | 
    #   exists x . exists y . exists z . exists e . exists a . 
    #   boy(x) ^ man(y) ^ telescope(z) ^ saw(e) ^ agent(e, x) ^ patient(e, y) ^ instrument(e, z)
    # "Galileo picked up the boy with the gloves."
    # "The woman observed the man in pyjamas."

    template = ["the", INDEFINITE_HUMAN_NPS, VISUAL_VPS, "the", INDEFINITE_HUMAN_NPS, "with the", VISUAL_INSTRUMENT_NPS]
    template_tags = [None, "np1", "vp1", None, "np2", None, "np3"]

    lf_template_1 = "exists x . exists y . exists z . exists a . exists e . {np1}(x) AND {np2}(y)"+\
                    " AND {vp1}(a) AND agent(a, x) AND patient(a, y) AND {np3}(z) AND " +\
                    " have(e) AND agent(e, y) AND patient(e, z)"

    lf_template_2 = "exists x . exists y . exists z . exists a . {np1}(x) AND {np2}(y)"+\
                    " AND {vp1}(a) AND agent(a, x) AND patient(a, y) AND instrument(a, z)"

    template = Template(template, template_tags)
    first_meaning_pairs = template.generate(lf_template_1)
    second_meaning_pairs = template.generate(lf_template_2)

    return first_meaning_pairs + second_meaning_pairs
    

def generate_vp_pairs():
    # generate pairs of sentences and LFs with VP attachment ambiguities
    pass

def generate_wordsense_pairs():
    # generate pairs of sentences and LFs with word sense ambiguities
    pass

def generate_scope_pairs():
    # generate pairs of sentences and LFs with scope ambiguities
    pass


if __name__ == "__main__":
    generate_pp_pairs()