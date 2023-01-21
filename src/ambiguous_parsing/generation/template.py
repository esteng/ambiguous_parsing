import itertools
import copy 

from ambiguous_parsing.generation.fixtures.nps import NPS_MAP
from ambiguous_parsing.generation.fixtures.vps import VPS_MAP

class Template:
    def __init__(self, 
                 template_list,
                 template_tags):
        # a template list is a mixed type list of strings and lists of options 
        self.template_list = template_list
        self.template_tags = template_tags

        self.denotation_lookup = NPS_MAP
        self.denotation_lookup.update(VPS_MAP)

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

    def generate(self, lf_template, template_idx, amb_type):
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
                        "var_bindings": var_binding,
                        "template_idx": template_idx,
                        "type": amb_type}
                pairs.append(data) 

        return pairs 