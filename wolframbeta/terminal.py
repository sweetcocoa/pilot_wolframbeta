from wolframbeta.utils import *


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

"""
1. 차수, 계수를 저장해두는 경우
**현재 구현: 2. 차수, 계수를 따로 저장하지 않는 경우
"""


class Variable:
    def __init__(self, name):
        self.name = name
        self.value = None
        # debugger("Variable {} created".format(self.name))

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