import re 
from typing import List, Tuple
import pdb
import networkx as nx
from ambiguous_parsing.eval.tree_tools import shunt, tokenize, operator_info

class Formula:

    def __init__(self,
                quantifiers: List[str],
                statements: nx.DiGraph,
                ):
        self.quantifiers = quantifiers
        self.statements = statements

    @classmethod
    def parse_formula(cls, formula: str) -> "Formula":
        """
        parse a formula into a list of quantifiers and a list of statements
        """

        # split into quantifiers and statements 
        split_on_dot = re.split(" \. ", formula)
        quantifiers = split_on_dot[:-1]
        statements = split_on_dot[-1]

        # parse statements 
        statements = Formula.parse_statements(statements)
        return cls(quantifiers, statements)

    @staticmethod 
    def parse_statements(string: str) -> nx.DiGraph:
        # wrap outer parens 
        string = f"( {string} )"
        # replace function calls with brackets and remove spaces 
        string = re.sub("(\w)\(", r"\1[", string)
        string = re.sub("(\w)\)", r"\1]", string)
        string = re.sub("\[(\w+), (\w+)\]", r"[\1,\2]", string)

        splitstring = re.split("\s+", string)
        tokenized = tokenize(splitstring)
        statement_tree = shunt(tokenized)
        return statement_tree 


    def canonicalize(self) -> str: 
        """convert the formula into a canonical form.
        1. replace all quantified variables with numbers
        2. remove un-used variables/quantifiers
        3. order statements alphabetically """

        # 1. replace quantified vars and 2. remove un-used vars  
        quantifiers, statements = self.anonymize_vars() 
        # 3. order statements alphabetically
        statements = self.order_statements(statements) 
        return statements

    def anonymize_vars(self) -> Tuple[List[str], nx.DiGraph]: 
        quant_str = self.quantifiers
        statements = self.statements
        old_to_new_map = {}
        new_quants = []
        for i, var_stmt in enumerate(quant_str): 
            quant, var = var_stmt.split(" ")
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
    
    def order_statements(self, statements: nx.DiGraph) -> nx.DiGraph:
        """order statements alphabetically and stringify.
        Statements are already sorted topologically"""
        seq = []
        op = None            
        curr_par = None

        def order_helper(node):
            # base case: is atom, return 
            # recursive case: return ( +  op.join([helper(child) for child in children]) +   )

            children = [n2 for n1, n2 in statements.edges if n1 == node]
            children = sorted(children, key = lambda x: statements.nodes[x]['name'])

            if len(children) == 0: 
                return statements.nodes[node]['name']
            op = f" {statements.nodes[node]['name']} "

            return "( " + op.join([order_helper(n) for n in children]) + " )"

        seq = order_helper(0)
        return seq
    


if __name__ == "__main__":
        formula1 = "exists x . exists a . exists e . exists i . man(x) AND eat(a) AND agent(a, x) AND ( ( drank(e) AND agent(e, x) ) OR ( slept(i) AND agent(i, x) ) )"
        formula2 = "exists x . exists a . exists e . exists i . ( man(x) AND eat(a) AND agent(a, x) AND drank(e) AND agent(e, x) ) OR ( slept(i) AND agent(i, x) ) )"

        print(formula1)
        formula = Formula.parse_formula(formula1)
        print(formula.canonicalize())