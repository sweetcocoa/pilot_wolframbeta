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
    "cosec": cosec,
    "cot": cot,
    "sec": sec,
    "exp": math.exp,
    "pow": math.pow,
    "log": math.log,
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
    "cosec": cosec,
    "cot": cot,
    "sec": sec,
    "exp": math.exp,
}

BUILTIN_FUNCTIONS_WITH_TWO_PARAM = {
    "pow": math.pow,
    "log": math.log,
}

BUILTIN_CONSTANTS = {
    "e": math.e,
    "pi": math.pi,
    "π": math.pi,
}
