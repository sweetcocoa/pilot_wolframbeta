def raise_error(*args):
    debugger(args)

def is_float_type(x):
    return type(x) == float

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


def debugger(*s):
    #print(s)
    pass


def is_string_add(tok):
    if tok == '+' or tok == '-':
        return True
    else :
        return False


def is_string_multi(tok):
    if tok == '*' or tok == '/':
        return True
    else:
        return False


def is_string_power(tok):
    if tok == '^':
        return True
    else:
        return False