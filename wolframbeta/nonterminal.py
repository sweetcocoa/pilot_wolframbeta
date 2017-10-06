from wolframbeta.utils import *
from wolframbeta.terminal import Value
from wolframbeta.config import *
"""

<expr> := <term> <expr_tail>
<expr_tail> := <add><expr> | empty
<term> := <factor> <term_tail>
<term_tail> := <multi> <term> | empty 
<factor> := <something><factor_tail>
where <something> 
:= - <factor>
:= ( <expr> )
:= number
:= variable
:= <function><param>
<factor_tail> := <power> <factor> | empty

<param> = ( <expr><param_tail> )
<param_tail> = , <expr> | empty
<function> 
:= 'sin' | 'cos' | 'tan' | 'cot' | 'sec' | 'cosec' | 'log' | 'exp' | 'pow'
:= user_defined_function

 

"""


class Nonterminal:
    def __init__(self, tokenmanager):
        self.childs = []          # token을 분해하여 객체화해서 append 해두는 리스트
        self.tokenmanager = tokenmanager
        self.value = None

    def add_childs(self, newobjects):
        self.childs.append(newobjects)

    def parse(self):
        return

    def has_childs(self):
        if len(self.childs) > 0:
            return True
        else:
            return False

    def value_is_float(self):
        if type(self.value) == float:
            return True
        else:
            return False


class Expr(Nonterminal):
    """
    <Expr> := <term> <Expr_tail>
    <Expr_tail> := <add> <expr> | empty
    """
    def __init__(self, tokenmanager):
        super(self.__class__, self).__init__(tokenmanager)

    def parse(self):
        """
        args : None
        return : None
        expr의 구성 요소(term, add, expr) 를 객체로 만들어 self.childs에 add
        """
        term = Term(self.tokenmanager)
        term.parse()
        self.add_childs(term)

        expr_tail = ExprTail(self.tokenmanager)
        expr_tail.parse()
        self.add_childs(expr_tail)

    def calculate(self):
        """
        args : None
        return : None
        self.childs의 각 value를 이용하여 self.value를 계산
        """
        term = self.childs[0]
        term.calculate()

        expr_tail = self.childs[1]
        if expr_tail.has_childs():
            ops = expr_tail.childs[0]
            expr = expr_tail.childs[1]
            expr.calculate()
            # debugger("?", term.value, ops.value, expr.value)
            value = calculate_ops(term.value, ops.value, expr.value)
            self.value = value
        else:
            value = term.value
            self.value = value


class ExprTail(Nonterminal):
    def __init__(self, tokenmanager):
        super(self.__class__, self).__init__(tokenmanager)

    def parse(self):
        if self.tokenmanager.has_next_token():
            next_token = self.tokenmanager.show_next_token()
            if is_string_add(next_token):
                token = self.tokenmanager.get_next_token()
                add = Value('add', token)
                self.add_childs(add)
                expr = Expr(self.tokenmanager)
                expr.parse()
                self.add_childs(expr)


class Term(Nonterminal):
    """
    <Term> := <Factor> <term_power_tail>
    <Term_power_tail> := <power> <factor> <Term_multi_tail> | <Term_multi_tail>
    <Term_multi_tail> := <multi> <Term> | empty
    """
    def __init__(self, tokenmanager):
        super(self.__class__, self).__init__(tokenmanager)

    def parse(self):
        """
        args : None
        return : None
        term의 구성 요소(factor, multi, term) 를 객체로 만들어 self.childs에 add
        """
        factor = Factor(self.tokenmanager)
        factor.parse()
        self.add_childs(factor)
        term_tail = TermTail(self.tokenmanager)
        term_tail.parse()
        self.add_childs(term_tail)

    def calculate(self):
        """
        args : None
        return : None
        self.childs의 각 value를 이용하여 self.value를 계산
        """
        factor = self.get_factor()
        factor.calculate()

        term_tail = self.get_term_tail()

        self.value = factor.value
        while term_tail.has_childs():
            multi = term_tail.get_multi()
            term = term_tail.get_term()
            factor_child = term.get_factor()
            factor_child.calculate()
            debugger("cal :", self.value, multi.value, factor_child.value)
            self.value = calculate_ops(self.value, multi.value, factor_child.value)
            term_tail = term.get_term_tail()

    def get_factor(self):
        return self.childs[0]

    def get_term_tail(self):
        return self.childs[1]


class TermTail(Nonterminal):
    def __init__(self, tokenmanager):
        super(self.__class__, self).__init__(tokenmanager)

    def parse(self):
        if self.tokenmanager.has_next_token():
            next_token = self.tokenmanager.show_next_token()
            if is_string_multi(next_token):
                token = self.tokenmanager.get_next_token()
                multi = Value('multi', token)
                self.add_childs(multi)
                term = Term(self.tokenmanager)
                term.parse()
                self.add_childs(term)

    def get_multi(self):
        return self.childs[0]

    def get_term(self):
        return self.childs[1]


class Factor(Nonterminal):
    """
    <Factor> := <something> <factor_tail>
    where
    something
    := ( <expr> )
    := -<Factor>
    := Number
    := <function> = <func><params>
    """
    def __init__(self, tokenmanager):
        super(self.__class__, self).__init__(tokenmanager)

    def parse(self):
        token = self.tokenmanager.get_next_token()

        if type(token) == float:
            self.add_childs(Value("number", token))

        elif token == '(':
            # ( <expr> )
            self.add_childs(Value("parentheses", token))
            expr = Expr(self.tokenmanager)
            expr.parse()
            self.add_childs(expr)
            token = self.tokenmanager.get_next_token()
            self.add_childs(Value("parentheses", token))

        elif token == '-':
            term = Value('sign', '-')
            self.add_childs(term)
            factor = Factor(self.tokenmanager)
            factor.parse()
            self.add_childs(factor)

        elif token in BUILTIN_FUNCTIONS:
            func = Func(self.tokenmanager, token)
            func.parse()
            self.add_childs(func)
        factor_tail = FactorTail(self.tokenmanager)
        factor_tail.parse()
        self.add_childs(factor_tail)

    def calculate(self):
        """
        args : None
        return : None
        self.childs의 각 value를 이용하여 self.value를 계산
            - <factor>
            number
            variable
        """
        l1_type = type(self.childs[0])
        l1_child = self.childs[0]
        if l1_type == Value:
            if l1_child.value == '-':
                # - <factor>

                factor = self.childs[1]
                factor.calculate()
                debugger("minus sign : ", factor.value)
                self.value = -factor.value
            elif l1_child.value == '(':
                expr = self.childs[1]
                expr.calculate()
                self.value = expr.value
            else:
                # number
                self.value = l1_child.value
        else:
            func = self.childs[0]
            func.calculate()
            self.value = func.value

        factor_tail = self.childs[-1]
        if factor_tail.has_childs():
            power = factor_tail.get_power()
            factor_child = factor_tail.get_factor()
            factor_child.calculate()
            self.value = calculate_ops(self.value, power.value, factor_child.value)
            debugger("power cal : ", self.value, power.value, factor_child.value)
        debugger("factor value : ", self.value)


class FactorTail(Nonterminal):
    """
    <factor_tail> := <power> <factor> | empty
    """
    def __init__(self, tokenmanager):
        super(self.__class__, self).__init__(tokenmanager)

    def parse(self):
        if self.tokenmanager.has_next_token():
            next_token = self.tokenmanager.show_next_token()
            if is_string_power(next_token):
                token = self.tokenmanager.get_next_token()
                power = Value('power', token)
                self.add_childs(power)
                factor = Factor(self.tokenmanager)
                factor.parse()
                self.add_childs(factor)

    def get_power(self):
        return self.childs[0]

    def get_factor(self):
        return self.childs[1]


class Func(Nonterminal):
    """
    <function>
    := 'sin' | 'cos' | 'tan' | 'cot' | 'sec' | 'cosec' | 'log' | 'exp' | 'pow'
    := user_defined_function
    """
    def __init__(self, tokenmanager, name=None):
        super(self.__class__, self).__init__(tokenmanager)
        if name is None:
            debugger("Function's name is not defined")
        self.name = name

    def parse(self):
        params = Params(self.tokenmanager)
        params.parse()
        self.add_childs(params)
        # print(params.get_Params())

    def calculate(self):
        debugger("functions name : ", self.name)
        params = self.get_params()
        params_list = params.get_params_list()
        debugger("params : ", params_list)

        value = self.func_calculate(self.name, params_list)
        self.value = value

        #self.value = 0

    def get_params(self):
        return self.childs[0]

    def func_calculate(self, func_name, param_list):
        ret = None
        if func_name in BUILTIN_FUNCTIONS.keys():
            ret = self._builtin_function_calculate(func_name, param_list)

        return ret

    def _builtin_function_calculate(self, func_name, params_list):
        """
        :param func_name:
        :param parmas_list: Value object whose value is float
        :return: calculated functions like "sin", "cos", "pow", "exp"
        """
        if func_name in BUILTIN_FUNCTIONS_WITH_ONE_PARAM.keys():
            if len(params_list) != 1:
                raise_error("{} expected one parameters, but {} is/are received".format(func_name, len(params_list)))
            radian = params_list[0]
            radian.calculate()
            if is_float_type(radian.value):
                return BUILTIN_FUNCTIONS_WITH_ONE_PARAM[func_name](radian.value)
            else:
                # arg of sin is expr
                pass

        elif func_name in BUILTIN_FUNCTIONS_WITH_TWO_PARAM.keys() :
            if len(params_list) != 2:
                raise_error("{} expected two parameters, but {} is/are received".format(func_name, len(params_list)))
            base = params_list[0]  # pow 함수의 경우 첫번째 argument가 base. log 함수는 두 번째 argument가 base임.
            exponent = params_list[1]
            base.calculate()
            exponent.calculate()
            if is_float_type(base.value) and is_float_type(exponent.value):
                return BUILTIN_FUNCTIONS_WITH_TWO_PARAM[func_name](base.value, exponent.value)
            else:
                #  base or exponent is expr
                pass
        return None

class Params(Nonterminal):
    """
    < param > = ( < expr > < param_tail > )
    < param_tail > =, < expr > | empty
    """
    def __init__(self, tokenmanager):
        super(self.__class__, self).__init__(tokenmanager)
        self.params_list = []

    def parse(self):
        token = self.tokenmanager.get_next_token()
        # token == '('
        self.add_childs(Value("parenthesis", token))
        expr = Expr(self.tokenmanager)
        expr.parse()
        self.add_childs(expr)
        param_tail = ParamTail(self.tokenmanager)
        param_tail.parse()
        self.add_childs(param_tail)
        token = self.tokenmanager.get_next_token()  # ')' token should exists
        self.add_childs(Value("parenthesis", token))

    def get_param_tail(self):
        return self.childs[2]

    def get_expr(self):
        return self.childs[1]

    def get_params_list(self):
        """
        :return: list object which contains parameter objects
        """
        if len(self.params_list) > 0:
            return self.params_list

        self.params_list.append(self.get_expr())
        param_tail = self.get_param_tail()
        while param_tail.has_childs():
            expr = param_tail.get_expr()
            self.params_list.append(expr)
            param_tail = param_tail.get_param_tail()

        return self.params_list


class ParamTail(Nonterminal):
    """
    < param > = ( < expr > < param_tail > )
    < param_tail > =, < expr > <param_tail> | empty
    """
    def __init__(self, tokenmanager):
        super(self.__class__, self).__init__(tokenmanager)

    def parse(self):
        if self.tokenmanager.has_next_token():
            token = self.tokenmanager.show_next_token()
            if token == ',':
                token = self.tokenmanager.get_next_token()
                comma = Value("comma", token)
                self.add_childs(comma)
                expr = Expr(self.tokenmanager)
                expr.parse()
                self.add_childs(expr)
                param_tail = ParamTail(self.tokenmanager)
                param_tail.parse()
                self.add_childs(param_tail)

    def get_expr(self):
        return self.childs[1]

    def get_param_tail(self):
        return self.childs[2]


tree_depth = 0
def print_tree(nonterm):
    global tree_depth
    local_depth = tree_depth
    if type(nonterm) != Value:
        for child in nonterm.childs:
            if type(child) != Value:
                print_tree(child)
            else:
                debugger(child.value)

