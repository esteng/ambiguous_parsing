import re 
from typing import List
import pdb
from ambiguous_parsing.eval.shunt import shunt, tokenize

class Formula:

    def __init__(self,
                quantifiers: List[str],
                statements: List[List[str]],
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
    def parse_statements(string):
        string = f"( {string} )"
        string = re.sub("(\w)\(", r"\1[", string)
        string = re.sub("(\w)\)", r"\1]", string)
        string = re.sub("\[(\w+), (\w+)\]", r"[\1,\2]", string)

        splitstring = re.split("\s+", string)
        tokenized = tokenize(splitstring)
        shunted = shunt(tokenized)
        pdb.set_trace()
        nested_statements = Formula.parse_helper(splitstring, [])
        pdb.set_trace()
        return nested_statements



    @staticmethod 
    def parse_helper(statement, statements):
        """Generate parenthesized contents in string as pairs (level, contents).
        https://gist.github.com/constructor-igor/5f881c32403e3f313e6f"""
        stack = []
        connector_stack = []
        statements = []
        # base case 
        if "(" not in statement:
            # split on connectives 
            # statement = " ".join(statement)
            statements.append(statement)
            # return Formula.reorder(statement)

        for i, c in enumerate(statement):
            if c == '(':
                stack.append(i)
            elif c == ')' and stack:
                start = stack.pop()
                statements.append(Formula.parse_helper(statement[start + 1: i], statements))
        return statements

    @staticmethod
    def reorder(statement):
        """
        reorder statement so that elements are in alphabetic order 
        """
        # first assert that there's only one connector type 
        if "OR" in statement:
            assert "AND" not in statement
            connector = "OR"
        elif "AND" in statement:
            assert "OR" not in statement
            connector = "AND"
        else:
            # no connector
            return statement  
        statement = re.split(connector, statement)
        non_connector_preds = [x for x in statement if x != connector]
        sorted(non_connector_preds)
        return f" {connector} ".join(non_connector_preds)

if __name__ == "__main__":
        formula1 = "exists x . exists a . exists e . exists i . man(x) AND eat(a) AND agent(a, x) AND ( ( drank(e) AND agent(e, x) ) OR ( slept(i) AND agent(i, x) ) )"
        formula2 = "exists x . exists a . exists e . exists i . ( man(x) AND eat(a) AND agent(a, x) AND drank(e) AND agent(e, x) ) OR ( slept(i) AND agent(i, x) ) )"

        print(formula1)
        formula = Formula.parse_formula(formula1)