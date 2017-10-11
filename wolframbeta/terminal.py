from wolframbeta.utils import *
from wolframbeta.tokenizer import TokenManager


class Value:
    """
    Value : 연산자, 숫자값 등의 terminal
    'number'
    'add'
    'multi'
    'sign'
    'parentheses'
    'power'
    """
    def __init__(self, nType, value):
        self.type = nType
        self.value = value
        #debugger("Value Created", self.type, self.value)

    def __add__(self, other):
        if self.type != 'number':
            raise_error(
                "Type error : Value object expects type 'number', but {}({}) is not supported.".format(self.type,
                                                                                                       self.value))

        if isinstance(other, float):
            return Value("number", self.value + other)

        elif isinstance(other, Value):
            if other.type == 'number':
                return Value("number", self.value + other.value)
            else:
                raise_error(
                    "Type error : Value object expects type 'number', but {}({}) is not supported.".format(self.type,
                                                                                                           self.value))
        else:
            raise_error(
                "Type error : Value object expects float of Value object, but {} is not supported.".format(type(other)))

    def __radd__(self, other):
        return Value('number', float.__add__(other, self.value))

    def __str__(self):
        return str(self.value)

    def __mul__(self, other):
        if self.type != 'number':
            raise_error(
                "Type error : Value object expects type 'number', but {}({}) is not supported.".format(self.type,
                                                                                                       self.value))

        if isinstance(other, float):
            return Value("number", self.value * other)

        elif isinstance(other, Value):
            if other.type == 'number':
                return Value("number", self.value * other.value)
            else:
                raise_error(
                    "Type error : Value object expects type 'number', but {}({}) is not supported.".format(self.type,
                                                                                                           self.value))
        else:
            raise_error(
                "Type error : Value object expects float of Value object, but {} is not supported.".format(type(other)))

    def __rmul__(self, other):
        return Value('number', float.__mul__(other, self.value))

    def __sub__(self, other):
        return self.__add__(-other)

    def __rsub__(self, other):
        return Value('number', float.__sub__(other, self.value))

    def __neg__(self):
        return Value('number', -self.value)

    def __truediv__(self, other):
        if self.type != 'number':
            raise_error(
                "Type error : Value object expects type 'number', but {}({}) is not supported.".format(self.type,
                                                                                                       self.value))

        if isinstance(other, float):
            return Value("number", self.value / other)

        elif isinstance(other, Value):
            if other.type == 'number':
                return Value("number", self.value / other.value)
            else:
                raise_error(
                    "Type error : Value object expects type 'number', but {}({}) is not supported.".format(self.type,
                                                                                                           self.value))
        else:
            raise_error(
                "Type error : Value object expects float of Value object, but {} is not supported.".format(type(other)))

    def __rtruediv__(self, other):
        return Value('number', float.__truediv__(other, self.value))

    def __pow__(self, power, modulo=None):
        if self.type != 'number':
            raise_error(
                "Type error : Value object expects type 'number', but {}({}) is not supported.".format(self.type,
                                                                                                       self.value))

        if isinstance(power, float) or isinstance(power, int):
            return Value("number", self.value ** power)

        elif isinstance(power, Value):
            if power.type == 'number':
                return Value("number", self.value ** power.value)
            else:
                raise_error(
                    "Type error : Value object expects type 'number', but {}({}) is not supported.".format(self.type,
                                                                                                           self.value))
        else:
            raise_error(
                "Type error : Value object expects float of Value object, but {} is not supported.".format(type(power)))

    def __rpow__(self, other):
        return Value('number', float.__pow__(other, self.value))

    def __mod__(self, other):
        if self.type != 'number':
            raise_error(
                "Type error : Value object expects type 'number', but {}({}) is not supported.".format(self.type,
                                                                                                       self.value))

        if isinstance(other, float):
            return Value("number", self.value % other)

        elif isinstance(other, Value):
            if other.type == 'number':
                return Value("number", self.value % other.value)
            else:
                raise_error(
                    "Type error : Value object expects type 'number', but {}({}) is not supported.".format(self.type,
                                                                                                           self.value))
        else:
            raise_error(
                "Type error : Value object expects float of Value object, but {} is not supported.".format(type(other)))

    def __rmod__(self, other):
        return Value('number', float.__mod__(other, self.value))

    def calculate_ops(self, ops, other):
        """
        other : 피연산자
        ops : 연산자
        """
        if ops == "+":
            return self + other
        elif ops == "-":
            return self - other
        elif ops == "*":
            return self * other
        elif ops == "/":
            return self / other
        elif ops == '^':
            return self ** other
        elif ops == '%':
            return self % other

"""
1. 차수, 계수를 저장해두는 경우
**현재 구현: 2. 차수, 계수를 따로 저장하지 않는 경우
"""


class Variable:
    def __init__(self, name):
        self.name = name
        self.value = None
        # debugger("Variable {} created".format(self.name))

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.name

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.name == other.name
        else:
            return False

    def __ne__(self, other):
        if isinstance(other, self.__class__):
            return self.name != other.name
        else:
            return True
"""
    def __pow__(self, power, modulo=None):
        if isinstance(power, float):
            str_expression = self.name + "^" + str(power)
            tokenmanager = TokenManager(str_expression)
            factor = Factor(tokenmanager)
            factor.parse()
            factor.calculate()
            return factor

    def __rpow__(self, other):
        if isinstance(other, float):
            str_expression = other + "^" + str(other)
            tokenmanager = TokenManager(str_expression)
            factor = Factor(tokenmanager)
            factor.parse()
            factor.calculate()
            return factor
"""