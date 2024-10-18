import re


class Node:
    def __init__(self, type, value=None, left=None, right=None):
        self.type = type
        self.value = value
        self.left = left
        self.right = right


def tokenize(rule_string):
    return re.findall(r'\(|\)|AND|OR|[^()\s]+', rule_string)


def parse_rule_string(rule_string):
    tokens = tokenize(rule_string)
    return parse_expression(tokens)


def parse_expression(tokens):
    if not tokens:
        return None

    left = parse_term(tokens)

    while tokens and tokens[0] in ['AND', 'OR']:
        operator = tokens.pop(0)
        right = parse_term(tokens)
        left = Node('operator', operator, left, right)

    return left


def parse_term(tokens):
    if tokens[0] == '(':
        tokens.pop(0)  # Remove opening parenthesis
        node = parse_expression(tokens)
        if tokens[0] == ')':
            tokens.pop(0)  # Remove closing parenthesis
        return node
    else:
        return parse_condition(tokens)


def parse_condition(tokens):
    key = tokens.pop(0)
    operator = tokens.pop(0)
    value = tokens.pop(0)
    return Node('condition', f"{key} {operator} {value}")


def combine_nodes(nodes, operator):
    if len(nodes) == 1:
        return nodes[0]
    return Node('operator', operator, nodes[0], combine_nodes(nodes[1:], operator))


def evaluate(node, data):
    if node.type == 'condition':
        key, op, value = node.value.split()
        if key not in data:
            return False
        if op == '=':
            return str(data[key]) == value.strip("'")
        elif op == '>':
            return float(data[key]) > float(value)
        elif op == '<':
            return float(data[key]) < float(value)
        # Add more operators as needed
    elif node.type == 'operator':
        if node.value == 'AND':
            return evaluate(node.left, data) and evaluate(node.right, data)
        elif node.value == 'OR':
            return evaluate(node.left, data) or evaluate(node.right, data)


def print_tree(node, prefix="", is_last=True):
    if node is not None:
        print(prefix, end="")
        print("└── " if is_last else "├── ", end="")

        if node.type == 'operator':
            print(node.value)
        else:
            print(node.value)

        prefix += "    " if is_last else "│   "

        if node.left or node.right:
            print_tree(node.left, prefix, False)
            print_tree(node.right, prefix, True)


def node_to_dict(node):
    if node is None:
        return None
    return {
        'type': node.type,
        'value': node.value,
        'left': node_to_dict(node.left),
        'right': node_to_dict(node.right)
    }