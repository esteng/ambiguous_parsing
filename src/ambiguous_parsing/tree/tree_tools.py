import re
from typing import List, Any
from collections import namedtuple, defaultdict
import networkx as nx
import pdb 
# from https://gist.github.com/ollybritton/3ecdd2b28344b0b25c547cbfcb807ddc

opinfo = namedtuple('Operator', 'precedence associativity')
operator_info = {
    "AND": opinfo(0, "L"),
    "OR": opinfo(0, "L")
}


def tokenize(splitstring):

    output = []
    state = ""
    buf = ""

    while len(splitstring) != 0:
        char = splitstring.pop(0)

        # print(f"CHAR: {char}")
        if re.match(r"\w+\[.*\]", char): 
            if state != "num":
                output.append(buf) if buf != "" else False
                buf = ""

            state = "num"
            buf += char

        elif char in operator_info.keys() or char in ["(", ")"]:
            output.append(buf) if buf != "" else False
            buf = ""

            output.append(char)

        else:
            if state != "func":
                output.append(buf) if buf != "" else False
                buf = ""

            state = "func"
            buf += char

    output.append(buf) if buf != "" else False
    return output


def shunt(tokens):
    tokens += ['end']
    operators = []
    output = []

    idx = 0
    while len(tokens) != 1:
        current_token = tokens.pop(0)

        if re.match(r"\w+\[.*\]", current_token): 
            # Is a number
            # print("number", current_token)
            output.append(current_token)

        elif current_token in operator_info.keys():
            # Is an operator
            # print("op", current_token)

            while True:
                if len(operators) == 0:
                    break

                satisfied = False

                # if operators[-1].isalpha():
                #     # is a function
                #     satisfied = True

                if operators[-1] not in ["(", ")"]:
                    if operator_info[operators[-1]].precedence > operator_info[current_token].precedence:
                        # operator at top has greater precedence
                        satisfied = True

                    elif operator_info[operators[-1]].precedence == operator_info[current_token].precedence:
                        if operator_info[operators[-1]].associativity == "left":
                            # equal precedence and has left associativity
                            satisfied = True

                satisfied = satisfied and operators[-1] != "("

                if not satisfied:
                    break

                output.append(operators.pop())

            operators.append(current_token)

        elif current_token == "(":
            # Is left bracket
            # print("left", current_token)
            operators.append(current_token)

        elif current_token == ")":
            # Is right bracket
            # print("right", current_token)

            while True:
                if len(operators) == 0:
                    break

                if operators[-1] == "(":
                    break

                output.append(operators.pop())

            if len(operators) != 0 and operators[-1] == "(":
                operators.pop()

        else:
            # Is a function name
            # print("func", current_token)
            operators.append(current_token)

        idx += 1 

    output.extend(operators[::-1])
    return convert_to_tree(output) 

def convert_to_tree(output):
    # return as a binary tree, currently only supports binary operations  
    reversed = output[::-1]
    graph = nx.DiGraph()
    parent_stack = []
    child_counter = defaultdict(int)
    for i, token in enumerate(reversed):
        graph.add_node(i, name=f"{token}:{i}")

        if token in operator_info.keys():
            # is an operator, pop all children 
            if i == 0:
                parent = -1
            else:
                parent = parent_stack[-1]
            parent_stack.append(i)
        else:
            parent = parent_stack[-1]
        child_counter[parent] += 1
        # print(f"node: {token}, stack: {parent_stack}, parent: {parent}")
        if parent == -1:
            pass
        else:
            graph.add_edge(parent, i)

        if child_counter[parent] == 2:
            parent_stack = [x for x in parent_stack if x != parent]

    # ammend node names to have more information for sorting later 
    for parent in graph.nodes:
        children = [n2 for n1, n2 in graph.edges() if n1 == parent]
        # check for cases where children are ops 
        child_names = [graph.nodes[n]['name'].split(":")[0] for n in children]
        if all([x in operator_info.keys() for x in child_names]):
            for n in children:
                grandchildren = [n2 for n1, n2 in graph.edges() if n1 == n]
                new_suffix = []
                for gc in grandchildren:
                    node_str = graph.nodes[gc]['name'].split(":")[0].split("[")[0]
                    new_suffix.append(node_str)
                new_suffix = sorted(new_suffix)
                graph.nodes[n]['name'] = f"{graph.nodes[n]['name'].split(':')[0]}:{''.join(new_suffix)}" 
            graph.nodes[parent]['name'] = f"{graph.nodes[parent]['name'].split(':')[0]}:{''.join(child_names)}"

    # naive flatten, O(N)
    for i in range(len(graph.nodes)):
        graph = flatten(graph)
    return graph

def flatten(graph):
    """
    flatten binary tree when operations are the same
    """

    edges = [x for x in graph.edges()]
    for edge in edges: 
        node1, node2 = edge
        name1 = graph.nodes[node1]['name']
        name2 = graph.nodes[node2]['name']
        if name1 == name2 and name1 in operator_info.keys():
            # merge nodes
            node2_outgoing = [e for e in graph.edges if e[0] == node2]
            new_edges = [(node1, e[1]) for e in node2_outgoing]
            graph.remove_node(node2)
            for e in new_edges:
                graph.add_edge(*e)
            break
    return graph



def lisp_to_ast(tokenized: List[str]) -> nx.DiGraph:
    """https://gist.github.com/roberthoenig/30f08b64b6ba6186a2cdee19502040b4"""
    graph = nx.DiGraph()

    global_idx = 0

    def ast_helper(input_norm: List[str], parent: str) -> List[Any]: 
        nonlocal global_idx
        ast = []
        # Go through each element in the input:
        # - if it is an open parenthesis, find matching parenthesis and make recursive
        #   call for content in-between. Add the result as an element to the current list.
        # - if it is an atom, just add it to the current list.
        i = 0
        while i < len(input_norm):
            symbol = input_norm[i]
            if symbol == '(':
                list_content = []
                match_ctr = 1 # If 0, parenthesis has been matched.
                parent_symbol = None
                while match_ctr != 0:
                    i += 1
                    if i >= len(input_norm):
                        raise ValueError("Invalid input: Unmatched open parenthesis.")
                    symbol = input_norm[i]
                    if symbol == '(':
                        match_ctr += 1
                    elif symbol == ')':
                        match_ctr -= 1
                    if match_ctr != 0:
                        list_content.append(symbol)             
                ast.append(ast_helper(list_content, parent))
            elif symbol == ')':
                    raise ValueError("Invalid input: Unmatched close parenthesis.")
            else:
                graph.add_node(global_idx, name=symbol)
                graph.add_edge(parent, global_idx)
                ast.append(symbol)
                if i == 0:
                    parent = global_idx
                global_idx += 1

            i += 1
        return ast

    quantifiers, tokenized = trim_quants(tokenized)


    ast_helper(tokenized, "none")

    graph.remove_node("none")


    return quantifiers, graph


def trim_quants(tokenized):
    quants = []
    quant_idx = 0
    for i, tok in enumerate(tokenized): 
        if tok == "(": 
            continue
        elif tok.startswith("exists_") or tok.startswith("forall_"): 
            quants.append(' '.join(tok.split("_")))
            quant_idx = i
    to_trim = tokenized[-len(quants):]
    for x in to_trim:
        assert(x == ")")
    statement = tokenized[quant_idx+1:]
    statement = statement[:-len(quants)]
    return quants, statement
