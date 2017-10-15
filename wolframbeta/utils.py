def raise_error(*args):
    debugger(args)

def calculate_ops(a, ops, b):
    """
    a, b : 피연산자
    ops : 연산자
    """
    if ops == "+":
        return a + b
    elif ops == "-":
        return a - b
    elif ops == "*":
        return a * b
    elif ops == "/":
        return a / b
    elif ops == '^':
        return a ** b
    elif ops == '%':
        return a % b


def debugger(*s):
    # print(s)
    pass


def is_string_add(tok):
    if tok == '+' or tok == '-':
        return True
    else :
        return False


def is_string_multi(tok):
    if tok == '*' or tok == '/' or tok == '%':
        return True
    else:
        return False


def is_string_power(tok):
    if tok == '^':
        return True
    else:
        return False


def get_term_str_expression(const, variables):
    """
    :param const: constant float in front of similar term
    :param variables: variables which compose the similar term
    :return: string expression, which could be used for initialization of Tokenmanager.
    """
    str_expression = str(const)
    for variable in variables.keys():
        exponent = variables[variable]
        if exponent == 1:
            str_expression += "*" + variable
        elif exponent == -1:
            str_expression += '/' + variable
        else:
            str_expression += "*" + variable + "^" + str(exponent)
    return str_expression


