import math


def cosec(arg):
    return 1/math.sin(arg)


def cot(arg):
    return 1/math.tan(arg)


def sec(arg):
    return 1/math.cos(arg)


BUILTIN_FUNCTIONS = {
    "sin": math.sin,
    "cos": math.cos,
    "tan": math.tan,
    "asin": math.asin,
    "acos": math.acos,
    "atan": math.atan,
    "sinh": math.sinh,
    "cosh": math.cosh,
    "tanh": math.tanh,
    "sqrt": math.sqrt,
    "cosec": cosec,
    "cot": cot,
    "sec": sec,
    "log": math.log,
    "pow": math.pow,
}

BUILTIN_FUNCTIONS_WITH_ONE_PARAM = {
    "sin": math.sin,
    "cos": math.cos,
    "tan": math.tan,
    "asin": math.asin,
    "acos": math.acos,
    "atan": math.atan,
    "sinh": math.sinh,
    "cosh": math.cosh,
    "tanh": math.tanh,
    "sqrt": math.sqrt,
    "cosec": cosec,
    "cot": cot,
    "sec": sec,
}

BUILTIN_FUNCTIONS_WITH_TWO_PARAM = {
    "log": math.log,
    "pow": math.pow,
}

BUILTIN_CONSTANTS = {
    "e": math.e,
    "pi": math.pi,
    "π": math.pi,
}
