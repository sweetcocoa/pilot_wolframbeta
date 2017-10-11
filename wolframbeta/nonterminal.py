from wolframbeta.utils import *
from wolframbeta.terminal import Variable
from wolframbeta.config import *
from wolframbeta.tokenizer import TokenManager
from wolframbeta.similar_term import SimilarTermsDict
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
        self.childs = []          # token을 분해하여 객체화해서 append 해두는 리스트(트리)
        self.tokenmanager = tokenmanager
        self.value = None

        self.childs_list = []  # childs tree를 list화 (Tree -> list).
        # list의 elem들은
        # expr : ops(+,-), term
        # term := ops(*,/,%), factor,
        # factor := ops(^), factor? 고민 중

        self.__similar_terms__ = dict()
        # 비교의 기준이 되는 딕셔너리.
        # key : 동류항.
        # key 정렬 방법
        # 1. Variable 알파벳순
        # 2. Function 이름순
        # 3. Function parameter가 앞서는 순
        # 으로 정렬한 문자열을 사용.
        # y * x^3 => x^3*y
        # sin(x)*y => y*sin(x)
        # pow(y,3)*x => x*pow(y,3)
        # key == $const 인 것을 상수항으로 사용한다.
        # value

    def add_childs(self, newobjects):
        self.childs.append(newobjects)

    def add_childs_list(self, newobjects):
        self.childs_list.append(newobjects)

    def parse(self):
        return

    def has_childs(self):
        if len(self.childs) > 0:
            return True
        else:
            return False

    def value_is_float(self):
        if isinstance(self.value, float):
            return True
        else:
            return False

    def get_summary(self):
        return self.__summary__

    def get_childs_list(self):
        if len(self.childs_list) > 0:
            return self.childs_list


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

        while expr_tail.has_childs():
            ops = expr_tail.get_ops()
            self.add_childs_list(ops)

            expr = expr_tail.get_expr()
            term = expr.get_term()
            self.add_childs(term)
            expr_tail = expr.get_expr_tail()

    def calculate(self):
        """
        args : None
        return : None
        self.childs의 각 value를 이용하여 self.value를 계산
        """
        term = self.get_term()
        term.calculate()

        """
        expr_tail = self.get_expr_tail()
        while expr_tail.has_childs():
            ops = expr_tail.get_ops()
            expr = expr_tail.get_expr()
            expr.calculate()
        """
        expr_tail = self.get_expr_tail()
        if expr_tail.has_childs():
            ops = expr_tail.get_ops()
            expr = expr_tail.get_expr()
            expr.calculate()
            value = calculate_ops(term.value, ops, expr.value)
            self.value = value
        else:
            value = term.value
            self.value = value

    def get_term(self):
        return self.childs[0]

    def get_expr_tail(self):
        return self.childs[1]

    def __str__(self):
        term = self.get_term()
        ret_str = str(term)
        expr_tail = self.get_expr_tail()
        if expr_tail.has_childs():
            ops = expr_tail.get_ops()
            expr = expr_tail.get_expr()
            ret_str += ops + str(expr)
        return ret_str


class ExprTail(Nonterminal):
    def __init__(self, tokenmanager):
        super(self.__class__, self).__init__(tokenmanager)

    def parse(self):
        if self.tokenmanager.has_next_token():
            next_token = self.tokenmanager.show_next_token()
            if is_string_add(next_token):
                token = self.tokenmanager.get_next_token()
                add = token
                self.add_childs(add)
                expr = Expr(self.tokenmanager)
                expr.parse()
                self.add_childs(expr)

    def get_ops(self):
        return self.childs[0]

    def get_expr(self):
        return self.childs[1]


class Term(Nonterminal):
    """
    <Term> := <Factor> <term_tail>
    <Term_tail> := <multi> <Term> | empty
    """
    def __init__(self, tokenmanager):
        super(self.__class__, self).__init__(tokenmanager)
        self.__constant__ = None
        self.__nonconstant_variable_dict__ = dict()

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

        multi_constant = 1
        variables = dict()
        if isinstance(factor.value, float):
            multi_constant = factor.value
        else:
            if isinstance(factor.value, Variable):
                key_str = str(factor.value)
            elif isinstance(factor.value, Factor):
                key_str = factor.value.get_something_str()
            elif isinstance(factor.value, Func):
                key_str = str(factor.value)
            else:
                print("type ", type(factor.value))
            factor_tail = factor.get_factor_tail()
            exponent = 1
            if factor_tail.has_childs():
                exponent = factor_tail.get_factor()
            variables[key_str] = exponent

        ### elif factor.value is expr, factor

        while term_tail.has_childs():
            multi = term_tail.get_multi()
            term = term_tail.get_term()
            factor_child = term.get_factor()
            factor_child.calculate()
            debugger("cal :", multi_constant, multi, str(factor_child))

            if isinstance(factor_child.value, float):
                multi_constant = calculate_ops(multi_constant, multi, factor_child.value)
            elif isinstance(factor_child.value, Variable) or isinstance(factor_child.value, Factor):
                factor_tail = factor_child.get_factor_tail()
                exponent = 1
                if factor_tail.has_childs():
                    exponent = factor_tail.get_factor().value
                    debugger("expon", str(exponent))

                if isinstance(factor_child.value, Variable):
                    similar_term = factor_child.value.name
                else:
                    similar_term = factor_child.value.get_something_str()

                if similar_term in variables.keys():
                    if multi == '*':
                        variables[similar_term] += exponent
                    elif multi == '/':
                        variables[similar_term] -= exponent
                else:
                    if multi == '*':
                        variables[similar_term] = exponent
                    elif multi == '/':
                        variables[similar_term] = -exponent

                debugger("similar_term dict ", variables)
            term_tail = term.get_term_tail()

        self.value = multi_constant
        if len(variables) > 0:
            self.value = self

        self.__constant__ = multi_constant
        self.__nonconstant_variable_dict__ = variables

    def get_factor(self):
        return self.childs[0]

    def get_term_tail(self):
        return self.childs[1]

    def get_const_variable(self):
        return self.__constant__, self.__nonconstant_variable_dict__

    def __str__(self):
        const, variable = self.get_const_variable()
        factor = self.get_factor()
        ret_str = str(factor)
        term_tail = self.get_term_tail()
        if term_tail.has_childs():
            multi = term_tail.get_multi()
            term = term_tail.get_term()
            ret_str += multi + str(term)
        return ret_str

    def __add__(self, other):
        if isinstance(other, Term):
            const1, variable1 = self.get_const_variable()
            const2, variable2 = other.get_const_variable()
            if variable1 == variable2:
                const = const1 + const2
                str_expression = get_term_str_expression(const, variable1)
                tokenmanager = TokenManager(str_expression)
                term = Term(tokenmanager)
                term.parse()
                return term
            else:
                str_expression1 = get_term_str_expression(const1, variable1)
                str_expression2 = get_term_str_expression(const2, variable2)
                tokenmanager = TokenManager(str_expression1 + '+' + str_expression2)
                expr = Expr(tokenmanager)
                expr.parse()
                return expr
        else:
            pass

    def __iadd__(self, other):
        self.__add__(other)

    def __sub__(self, other):
        return self.__add__(-other)

    def __neg__(self):
        const, variable = self.get_const_variable()
        const = -const
        str_expression = get_term_str_expression(const, variable)
        tokenmanager = TokenManager(str_expression)
        term = Term(tokenmanager)
        term.parse()
        term.calculate()
        return term


class TermTail(Nonterminal):
    def __init__(self, tokenmanager):
        super(self.__class__, self).__init__(tokenmanager)

    def parse(self):
        if self.tokenmanager.has_next_token():
            next_token = self.tokenmanager.show_next_token()
            if is_string_multi(next_token):
                token = self.tokenmanager.get_next_token()
                multi = token
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
        self.__something_str__ = None

    def parse(self):
        token = self.tokenmanager.get_next_token()

        if isinstance(token, float):
            self.add_childs(token)

        elif token == '(':
            # ( <expr> )
            self.add_childs(token)
            expr = Expr(self.tokenmanager)
            expr.parse()
            self.add_childs(expr)
            token = self.tokenmanager.get_next_token()
            self.add_childs(token)

        elif token == '-':
            sign = token
            self.add_childs(sign)
            factor = Factor(self.tokenmanager)
            factor.parse()
            self.add_childs(factor)

        elif token in BUILTIN_FUNCTIONS:
            func = Func(self.tokenmanager, token)
            func.parse()
            self.add_childs(func)

            # elif token in ASSIGNED_FUNCTIONS
            # elif token in ASSIGNED_VARIABLES
        else:  # token is Variable
            variable = Variable(token)
            self.add_childs(variable)

        factor_tail = FactorTail(self.tokenmanager)
        factor_tail.parse()
        self.add_childs(factor_tail)

        while factor_tail.has_childs():
            power = factor_tail.get_power()
            self.add_childs_list(power)
            factor = factor_tail.get_factor()
            self.add_childs_list(factor)
            factor_tail = factor.get_factor_tail()

    def calculate(self):
        """
        args : None
        return : None
        Calculate self.value.
        """

        value = None
        if isinstance(self.childs[0], str):
            if self.childs[0] == '-':
                # - <factor>
                factor = self.childs[1]
                factor.calculate()
                value = -factor.value
            elif self.childs[0] == '(':
                expr = self.childs[1]
                expr.calculate()
                value = expr.value
        elif isinstance(self.childs[0], float):
                # number
                value = self.childs[0]
        elif isinstance(self.childs[0], Variable):
            variable = self.childs[0]
            value = variable
        elif isinstance(self.childs[0], Func):
            func = self.childs[0]
            func.calculate()
            value = func.value

        factor_tail = self.get_factor_tail()

        if factor_tail.has_childs():
            power = factor_tail.get_power()
            factor_child = factor_tail.get_factor()
            factor_child.calculate()
            if isinstance(value, float):
                value = calculate_ops(value, power, factor_child.value)
        # debugger("factor value : ", value)

        self.value = value
        if not isinstance(value, float) and factor_tail.has_childs():  # x^3, sin(x)^3 should remain as Factor
            self.value = self

    def __str__(self):
        ret_str = self.get_something_str()
        factor_tail = self.get_factor_tail()
        if factor_tail.has_childs():
            factor_child = factor_tail.get_factor()
            ret_str += '^' + str(factor_child)

        return ret_str

    def get_factor_tail(self):
        return self.childs[-1]

    def get_something_str(self):
        """
        <factor> := <something><factor_tail>
        where <something>
        := - <factor>
        := ( <expr> )
        := number
        := variable
        := <function><param>
        <factor_tail> := <power> <factor> | empty
        :return:
        <something> in a string form.
        """
        if self.__something_str__ is not None:
            return self.__something_str__
        if not self.has_childs():
            return ""
        ret_str = ""
        if isinstance(self.childs[0], str):
            if self.childs[0] == '-':
                # - <factor>
                factor = self.childs[1]
                ret_str = '-' + str(factor)
            elif self.childs[0] == '(':
                expr = self.childs[1]
                ret_str = '('+str(expr)+')'
        elif isinstance(self.childs[0], float):
                number = self.childs[0]
                ret_str = str(number)
        elif isinstance(self.childs[0], Func):
            func = self.childs[0]
            ret_str = str(func)
        elif isinstance(self.childs[0], Variable):
            variable = self.childs[0]
            ret_str = str(variable)
        return ret_str

    def __eq__(self, other):
        if not isinstance(other, Factor):
            return False
        if len(self.childs) != len(other.childs):
            return False
        return str(self) == str(other)

    def __ne__(self, other):
        return not self.__eq__(other)


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
                power = token
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
        # debugger("params : ", params_list)

        value = self.func_calculate(self.name, params_list)
        if value is None:
            self.value = self
        else:
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
        :param parmas_list: Expr list
        :return: calculated functions like "sin", "cos", "pow", "exp"
        """
        if func_name in BUILTIN_FUNCTIONS_WITH_ONE_PARAM.keys():
            if len(params_list) != 1:
                raise_error("{} expected one parameters, but {} is/are received".format(func_name, len(params_list)))
            radian = params_list[0]
            radian.calculate()
            if isinstance(radian.value, float):
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
            if isinstance(base.value, float) and isinstance(exponent.value, float):
                return BUILTIN_FUNCTIONS_WITH_TWO_PARAM[func_name](base.value, exponent.value)
            else:
                #  base or exponent is expr
                pass
        return None

    def __str__(self):
        ret_str = self.name
        param = self.get_params()
        ret_str += str(param)
        return ret_str


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
        self.add_childs(token)
        expr = Expr(self.tokenmanager)
        expr.parse()
        self.add_childs(expr)
        param_tail = ParamTail(self.tokenmanager)
        param_tail.parse()
        self.add_childs(param_tail)
        token = self.tokenmanager.get_next_token()  # ')' token should exists
        self.add_childs(token)

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

    def __str__(self):
        params_list = self.get_params_list()
        ret_str = '('
        for param in params_list:
            ret_str += str(param) + ','
        ret_str = ret_str[:-1] + ')'
        return ret_str


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
                comma = token
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