from wolframbeta.config import *

# ERROR_STATE = "SUCCESS"


def raise_error(args):
    # raise Exception(args)
    # try:
    #     global ERROR_STATE
    #     ERROR_STATE.append(args)
    # except NameError:
    #     pass
    debugger(args)
    print(args)


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


def strip_float(num):
    if isinstance(num, float) and num.is_integer():
        return int(num)
    else:
        return num
