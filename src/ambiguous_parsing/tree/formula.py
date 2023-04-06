import re 
from typing import List, Tuple
import pdb
from copy import deepcopy
import networkx as nx
from ambiguous_parsing.tree.tree_tools import shunt, tokenize, operator_info, lisp_to_ast
from ambiguous_parsing.generation.fixtures.vps import VPS_MAP


class Formula:

    def __init__(self,
                quantifiers: List[str],
                statements: nx.DiGraph,
                ):
        self.quantifiers = quantifiers
        self.statements = statements

    @classmethod
    def parse_formula(cls, formula: str) -> "Formula":
        raise NotImplementedError

    def render(self) -> str: 
        raise NotImplementedError

    def determine_event(self, var: str, statements: nx.DiGraph) -> bool: 
        """
        determine if a given variable is an event or nominal variable
        """
        vps = VPS_MAP.values() 
        for n in statements.nodes:
            name = statements.nodes[n]['name']
            args = re.search("\[(.+)\]", name)
            if args is not None:
                args = args.group(1).split(",")
                fxn_name = name.split("[")[0]
                if var in args: 
                    # predicate vars are first arg of agent or patient 
                    if fxn_name in ['agent', 'patient'] and args.index(var) == 0: 
                        return True
                    # predicate vars given as event(var)
                    elif fxn_name in vps and len(args) == 1:
                        return True
                    else:
                        pass 
        return False

    def anonymize_vars(self, ordered_vars) -> Tuple[List[str], nx.DiGraph]: 
        """anonymize variables in the tree"""
        quant_str = deepcopy(self.quantifiers)
        statements = deepcopy(self.statements)
        old_to_new_map = {}
        new_quants = []
        event_vars = ['a', 'e', 'i']
        nominal_vars = ['x', 'y', 'z']
        for i, var_stmt in enumerate(quant_str): 
            quant, var = var_stmt.split(" ")
            if ordered_vars: 
                # determine if is an event or a nominal 
                is_event = self.determine_event(var, statements)
                if is_event:
                    new_var = event_vars.pop(0)
                else:
                    new_var = nominal_vars.pop(0)
            else:
                new_var = f"v{i}"
            old_to_new_map[var] = new_var
            new_quants.append(f"{quant} {new_var}")

        used_in_statements = []  
        for n in statements.nodes:
            name = statements.nodes[n]['name']
            args = re.search("\[(.+)\]", name)
            if args is not None:
                args = args.group(1).split(',')
                new_args = []
                for a in args:
                    try:
                        new_var = old_to_new_map[a]
                        new_args.append(new_var) 
                        used_in_statements.append(new_var)
                    except KeyError:
                        if a[0].isupper():
                            # name 
                            new_args.append(a)
                        else:
                            raise ValueError(f"Unbound local variable: {a}")
                    
                new_name = name.split("[")[0] + "[" + ",".join(new_args) + "]"
            else:
                new_name = name
            statements.nodes[n]['name'] = new_name

        # remove unused quantifiers 
        for i, q in enumerate(new_quants):
            quant, var = q.split(" ")
            if var not in used_in_statements:
                new_quants[i] = None
        new_quants = [q for q in new_quants if q is not None]

        return new_quants, statements



class FOLFormula(Formula):
    """
    a first-order logic formula  
    """

    @classmethod
    def from_formula(cls, formula: Formula) -> "FOLFormula":
        return cls(formula.quantifiers, formula.statements)

    @classmethod
    def parse_formula(cls, formula: str) -> "Formula":
        """
        parse a formula into a list of quantifiers and a list of statements
        """

        # split into quantifiers and statements 
        split_on_dot = re.split(r" \. ", formula)
        quantifiers = split_on_dot[:-1]
        statements = split_on_dot[-1]

        # parse statements 
        statements = FOLFormula.parse_fol_statements(statements)
        return cls(quantifiers, statements)

    @staticmethod 
    def parse_fol_statements(string: str) -> nx.DiGraph:
        # wrap outer parens 
        string = f"( {string} )"
        # replace function calls with brackets and remove spaces 
        string = re.sub(r"(\w)\(", r"\1[", string)
        string = re.sub(r"(\w)\)", r"\1]", string)
        string = re.sub(r"\[(\w+), (\w+)\]", r"[\1,\2]", string)

        splitstring = re.split(r"\s+", string)
        tokenized = tokenize(splitstring)
        statement_tree = shunt(tokenized, flatten=True)
        return statement_tree 

    def render(self, ordered_vars: bool = False) -> str: 
        """convert the formula into a canonical FOL form.
        1. replace all quantified variables with numbers
        2. remove un-used variables/quantifiers
        3. order statements alphabetically """

        # 1. replace quantified vars and 2. remove un-used vars  
        # 1.1 if ordered vars, return to ordered (x,y,z,a,e,i) format, otherwise use v0, v1, v2,...
        quantifiers, statements = self.anonymize_vars(ordered_vars) 

        # 3. order statements alphabetically
        statements = self.order_statements(statements) 
        quantifier_str = " . ".join(quantifiers)
        return f"{quantifier_str} . {statements}"

    def order_statements(self, statements: nx.DiGraph) -> str: 
        """order statements alphabetically and stringify.
        Statements are already sorted topologically"""
        seq = []
        op = None            
        curr_par = None

        def split_name(node, atom=False):
            splitname = node.split(":")[0]
            if atom:
                args = re.search(r"\[(.+?)\]", splitname).group(1)
                args = args.split(',')
                new_name = splitname.split("[")[0] + "(" + ", ".join(args) + ")"
                return new_name
            return splitname

        def order_helper(node, parent_op=None):
            # base case: is atom, return 
            # recursive case: return ( +  op.join([helper(child) for child in children]) +   )

            children = [n2 for n1, n2 in statements.edges if n1 == node]
            children = sorted(children, key = lambda x: statements.nodes[x]['name'])
            # child_names = [statements.nodes[n]['name'] for n in children]
            # print(f"children of {statements.nodes[node]['name']} are {child_names}")
            if len(children) == 0: 
                return split_name(statements.nodes[node]['name'], atom=True) 
            op = f" {split_name(statements.nodes[node]['name'])} "

            if parent_op is None:
                for n in statements.nodes:
                    print(f"{n}: {statements.nodes[n]['name']}")
            # don't use parens if the same type of parent and parent is AND or OR 
            # i.e. instead of ((a AND b) AND c) allow (a AND b AND c)
            if op.strip() in ["AND", "OR"] and (op.strip() == parent_op or parent_op is None):
                return op.join([order_helper(n, op.strip()) for n in children])
            else:
                return "( " + op.join([order_helper(n, op.strip()) for n in children]) + " )"

        seq = order_helper(0)
        return seq




class LispFormula(Formula):

    @classmethod
    def from_formula(cls, formula: Formula) -> "LispFormula":
        return cls(formula.quantifiers, formula.statements)

    @classmethod
    def parse_formula(cls, formula: str) -> "Formula":
        """
        parse a LISP formula into a list of quantifiers and a list of statements
        """
        # go in and replace atomic functions 
        atomic_fxn_gex = re.compile("\( ([\w ]+?) \)")
        for atom in atomic_fxn_gex.findall(formula):
            fxn_and_args = atom.split(" ")
            fxn = fxn_and_args[0]
            args = fxn_and_args[1:]
            new_str = f"{fxn}[{','.join(args)}]"
            formula = re.sub(f"\( {atom} \)", new_str, formula)

        # manipulate quantifiers to make parsing easy 
        quant_gex = re.compile("(exists [\w\d]+)|(forall [\w\d]+)")
        for quant_list in quant_gex.findall(formula):
            quant_str = [x for x in quant_list if x != ''][0]
            quant, var = quant_str.split(" ")
            formula = re.sub(quant_str, f"{quant}_{var}", formula)

        splitstring = re.split("\s+", formula)
        quantifiers, statement = lisp_to_ast(splitstring)
        return cls(quantifiers, statement) 

    def render(self, ordered_vars: bool = False) -> str:
        """convert the formula into a canonical Lisp form."""
        quantifiers, statements = self.anonymize_vars(ordered_vars) 

        # get root of statement graph 
        children = [n2 for n1, n2 in statements.edges]
        roots = list(set([n1 for n1, n2 in statements.edges if n1 not in children])) 
        assert(len(roots) == 1)
        root = roots[0]
        new_root = None
        # add quantifiers to graph starting at the top
        for i, q in enumerate(quantifiers):
            if i == 0: 
                new_root = f"quant:{i}" 
            statements.add_node(f"quant:{i}", name = q)
            if i < len(quantifiers)-1: 
                statements.add_edge(f"quant:{i}", f"quant:{i+1}")
            else:
                statements.add_edge(f"quant:{i}", root)

        # order and render simultaneously, recurring through graph top to bottom 
        statements = self.order_statements(statements, new_root)
        return statements 

    def order_statements(self, statements: nx.DiGraph, root: str) -> nx.DiGraph: 
        """order statements alphabetically and stringify.
        Statements are already sorted topologically"""
        seq = []

        def split_fxn_name(node):
            fxn_str = node.split(":")[0]
            fxn, __, args = re.split(r"(\[)", fxn_str) 
            args = re.sub(r"\]", "", args)
            arg_list = [x.strip() for x in args.split(",")] 
            arg_str = " ".join(arg_list)
            full_str = f"( {fxn} {arg_str} )"
            return full_str

        def split_name(node):
            return node.split(":")[0]

        def order_helper(node):
            # base case: is atom, return 
            # recursive case: return ( +  op.join([helper(child) for child in children]) +   )

            children = [n2 for n1, n2 in statements.edges if n1 == node]
            children = sorted(children, key = lambda x: statements.nodes[x]['name'])
            # child_names = [statements.nodes[n]['name'] for n in children]
            # print(f"children of {statements.nodes[node]['name']} are {child_names}")
            if len(children) == 0: 
                fxn_str = split_fxn_name(statements.nodes[node]['name']) 
                return fxn_str 
            op = f"{split_name(statements.nodes[node]['name'])}"

            return f"( {op} {' '.join([order_helper(n) for n in children])} )"

        seq = order_helper(root) 
        return seq


if __name__ == "__main__":
        formula1 = "exists x . exists a . exists e . exists i . man(x) AND eat(a) AND agent(a, x) AND ( ( drank(e) AND agent(e, x) ) OR ( slept(i) AND agent(i, x) ) )"
        formula2 = "exists x . exists a . exists e . exists i . ( man(x) AND eat(a) AND agent(a, x) AND drank(e) AND agent(e, x) ) OR ( slept(i) AND agent(i, x) ) )"

        print(formula1)
        formula = Formula.parse_formula(formula1)
        print(formula.canonicalize())