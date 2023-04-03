import re
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
        if re.match("\w+\[.*\]", char): 
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

        if re.match("\w+\[.*\]", current_token): 
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
        graph.add_node(i, name=token)

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
            print(f"merging {node1} and {node2}")
            node2_outgoing = [e for e in graph.edges if e[0] == node2]
            new_edges = [(node1, e[1]) for e in node2_outgoing]
            graph.remove_node(node2)
            for e in new_edges:
                graph.add_edge(*e)
            break
    return graph

