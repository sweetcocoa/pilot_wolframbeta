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
