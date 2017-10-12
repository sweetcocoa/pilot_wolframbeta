from wolframbeta.tokenizer import TokenManager
from wolframbeta.similar_term import *
from wolframbeta.utils import *
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
    def __init__(self, arg):
        if isinstance(arg, str):
            self.tokenmanager = TokenManager(arg)
        elif isinstance(arg, TokenManager):
            self.tokenmanager = arg

        self.childs = list()
        self.unrolled_childs = list()

    def parse(self):
        return

    def calculate(self):
        return

    def add_childs(self, newobject):
        self.childs.append(newobject)

    def add_unrolled_childs(self, newobject):
        self.unrolled_childs.append(newobject)

    def has_childs(self):
        if len(self.childs) > 0:
            return True
        else:
            return False


class Expr(Nonterminal):
    def __init__(self, arg):
        if isinstance(arg, SimilarTermsDict):
            self.similar_terms_dict = arg
        else:
            self.similar_terms_dict = None
        super(self.__class__, self).__init__(arg)

    def parse(self):
        term = Term(self.tokenmanager)
        term.parse()
        self.add_childs(term)

        expr_tail = ExprTail(self.tokenmanager)
        expr_tail.parse()
        self.add_childs(expr_tail)

        while expr_tail.has_childs():
            ops = expr_tail.get_ops()
            self.add_unrolled_childs(ops)

            expr = expr_tail.get_expr()
            term = expr.get_term()
            self.add_unrolled_childs(term)
            expr_tail = expr.get_tail()

    def calculate(self):
        if self.similar_terms_dict is not None:
            return

        self.similar_terms_dict = SimilarTermsDict()
        term = self.get_term()
        term.calculate()
        self.similar_terms_dict[term.term_dict] = term.term_dict.constant
        expr_tail = self.get_tail()
        debugger(self.similar_terms_dict)
        if expr_tail.has_childs():
            ops = expr_tail.get_ops()
            expr = expr_tail.get_expr()
            expr.calculate()
            debugger("tail's expr's dict: ", self.similar_terms_dict)
            self.similar_terms_dict = calculate_ops(self.similar_terms_dict, ops, expr.similar_terms_dict)

    def get_term(self):
        return self.childs[0]

    def get_tail(self):
        return self.childs[-1]

    def is_constant(self):
        if self.similar_terms_dict is not None:
            return self.similar_terms_dict.is_constant()
        else:
            return False

    def has_one_term(self):
        if len(self.similar_terms_dict.keys()) == 2:
            if self.similar_terms_dict[CONST_KEY] == 0:
                return True
            else:
                return False
        elif len(self.similar_terms_dict.keys()) == 1:
            return True
        else:
            return False

    def __str__(self):
        if self.similar_terms_dict is None:
            return "None_Expr"
        ret_str = ""
        if self.is_constant():
            ret_str += str(self.similar_terms_dict[CONST_KEY])
        else:
            for i, (term, const) in enumerate(reversed(sorted(self.similar_terms_dict.items()))):
                if i == 0 and const > 0:
                    if const == 1:
                        ret_str += str(term)
                    else:
                        ret_str += str(const) + '*' + str(term)
                elif const < 0:
                    ret_str += '-' + str(-const) + '*' + str(term)
                elif const > 0:
                    if const == 1:
                        ret_str += '+' + str(term)
                    else:
                        ret_str += '+' + str(const) + '*' + str(term)
        return ret_str


class ExprTail(Nonterminal):
    def __init__(self, tokenmanager):
        if not isinstance(tokenmanager, TokenManager):
            raise_error("ExprTail expects tokenmanager as initialization, but {} is gotten".str(tokenmanager))
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
    def __init__(self, arg):
        if isinstance(arg, TermDict):
            self.term_dict = arg
        else:
            self.term_dict = None
        super(self.__class__, self).__init__(arg)

    def parse(self):
        factor = Factor(self.tokenmanager)
        factor.parse()
        self.add_childs(factor)
        term_tail = TermTail(self.tokenmanager)
        term_tail.parse()
        self.add_childs(term_tail)

        while term_tail.has_childs():
            ops = term_tail.get_ops()
            self.add_unrolled_childs(ops)

            term = term_tail.get_term()
            factor = term.get_factor()
            self.add_unrolled_childs(factor)
            term_tail = term.get_tail()

    def calculate(self):
        if self.term_dict is not None:
            return

        factor = self.get_factor()
        factor.calculate()
        self.term_dict = factor.term_dict
        term_tail = self.get_tail()
        debugger("term dict of Term", self.term_dict)
        while term_tail.has_childs():
            term = term_tail.get_term()
            factor = term.get_factor()
            factor.calculate()
            self.term_dict = calculate_ops(self.term_dict, term_tail.get_ops(), factor.term_dict)
            term_tail = term.get_tail()

    def __str__(self):
        if self.term_dict is None:
            return "None_Term"
        ret_str = ""

        for i, (factor, power) in enumerate(sorted(self.term_dict.items())):
            if i == 0:
                if power == -1:
                    ret_str = '1/'+str(factor)
                elif power < 0:
                    ret_str = '1/'+str(factor) + '^' + str(power)
                elif power == 1:
                    ret_str = str(factor)
                elif power > 0:
                    ret_str = str(factor)+'^'+str(power)
            else:
                if power == -1:
                    ret_str += '/' + str(factor)
                elif power < 0:
                    ret_str += '/' + str(factor) + '^' + str(power)
                elif power == 1:
                    ret_str += '*' + str(factor)
                elif power > 0:
                    ret_str += '*' + str(factor) + '^' + str(power)
        return ret_str

    def get_factor(self):
        return self.childs[0]

    def get_tail(self):
        return self.childs[-1]


class TermTail(Nonterminal):
    def __init__(self, tokenmanager):
        if not isinstance(tokenmanager, TokenManager):
            raise_error("TermTail expects tokenmanager as initialization, but {} is gotten".str(tokenmanager))
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

    def get_ops(self):
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
    def __init__(self, arg):
        if isinstance(arg, TermDict):
            self.term_dict = arg
        else:
            self.term_dict = None
        super(self.__class__, self).__init__(arg)
        self.negative_sign = 1

    def parse(self):
        token = self.tokenmanager.get_next_token()

        if isinstance(token, float):
            self.add_childs(token)

        elif token == '(':
            # ( <expr> )
            self.add_childs(token)
            self.add_unrolled_childs(token)
            expr = Expr(self.tokenmanager)
            expr.parse()
            expr.calculate()
            self.add_childs(expr)
            self.add_unrolled_childs(expr)
            token = self.tokenmanager.get_next_token()
            self.add_childs(token)
            self.add_unrolled_childs(token)

        elif token == '-':
            sign = token
            self.add_childs(sign)
            self.add_unrolled_childs(sign)
            self.negative_sign = -1
            factor = Factor(self.tokenmanager)
            factor.parse()
            self.add_childs(factor)
            self.add_unrolled_childs(factor)

        elif token in BUILTIN_FUNCTIONS:
            func = Func(self.tokenmanager, token)
            func.parse()
            self.add_childs(func)
            self.add_unrolled_childs(func)
            # elif token in ASSIGNED_FUNCTIONS
            # elif token in ASSIGNED_VARIABLES
        else:  # token is Variable
            variable = Variable(token)
            self.add_childs(variable)
            self.add_unrolled_childs(variable)

        factor_tail = FactorTail(self.tokenmanager)
        factor_tail.parse()
        self.add_childs(factor_tail)

        while factor_tail.has_childs():
            power = factor_tail.get_power()
            self.add_unrolled_childs(power)
            factor = factor_tail.get_factor()
            self.add_unrolled_childs(factor)
            factor_tail = factor.get_tail()

    def add_variable(self, variable):
        if self.variable_set is None:
            self.variable_set = set()
        self.variable_set.add(variable)

    def calculate(self):
        if self.term_dict is not None:
            return

        self.term_dict = TermDict()
        factor_tail = self.get_tail()

        if self.negative_sign == -1:
            self.term_dict.constant *= -1
            factor = self.childs[1]
            factor.calculate()
            self.term_dict = self.term_dict * factor.term_dict

        if isinstance(self.childs[0], float):
            number = self.childs[0]
            if factor_tail.has_childs():
                # number^factor
                factor_power = factor_tail.get_factor()
                factor_power.calculate()
                if factor_power.is_constant():
                    # number^number
                    self.term_dict.constant *= number ** factor_power.term_dict.constant
                else:
                    # number^variable
                    pass
            else:
                # number without power
                self.term_dict.constant *= number
        elif self.childs[0] == '(':
            expr = self.childs[1]
            if factor_tail.has_childs():
                # (expr)^factor 인 경우
                # 단일항인 경우, 다항인 경우
                pass
            else:
                # (expr) 인 경우 :
                expr.calculate()
                if expr.is_constant():
                    # (expr) 이 상수인 경우
                    self.term_dict.constant *= expr.similar_terms_dict[CONST_KEY]
                else:
                    # (expr) 이 상수가 아닌 경우
                    # 단일항인 경우와 다항인 경우로 나눠볼 수 있을 듯.
                    pass
        elif isinstance(self.childs[0], Variable):
            variable = self.childs[0]
            if factor_tail.has_childs():
                # variable^factor 인 경우
                factor_power = factor_tail.get_factor()
                factor_power.calculate()
                if factor_power.is_constant():
                    # variable^constant
                    self.term_dict[self.childs[0]] = factor_power.term_dict.constant
                    pass
                else:
                    # variable^(some expression containing varaible)
                    raise_error("variable^variable is not supported. error - {}^{}".format(self.childs[0], str(factor_power)))
            else:
                # varaible without factor
                self.term_dict[self.childs[0]] = 1

        elif isinstance(self.childs[0], Func):
            # factor = function
            pass

    def __str__(self):
        ret_str = ""

        return ret_str

    def get_tail(self):
        return self.childs[-1]

    def get_something_str(self):
        ret_str = ""
        for some in self.childs[:-1]:
            ret_str += str(some)
        return ret_str

    def is_constant(self):
        if self.term_dict is not None:
            return self.term_dict.is_constant()
        else:
            return False


class FactorTail(Nonterminal):
    """
    <factor_tail> := <power> <factor> | empty
    """
    def __init__(self, tokenmanager):
        if not isinstance(tokenmanager, TokenManager):
            raise_error("FactorTail expects tokenmanager as initialization, but {} is gotten".str(tokenmanager))
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
    := 'sin' | 'cos' | 'tan' | 'cot' | 'sec' | 'cosec' | 'log' | 'exp' | 'pow' ...
    := user_defined_function
    """
    def __init__(self, arg, name=None, user_defined=None):
        super(self.__class__, self).__init__(arg)
        if name is None:
            debugger("Function's name is not defined")
        self.name = name
        self.user_defined = user_defined  # SimilarTermDict

    def parse(self):
        """
        Func class does not have its name as a child.
        Its name is stored in self.name when object is created.
        """
        params = Params(self.tokenmanager)
        params.parse()
        self.add_childs(params)

    def calculate(self):
        pass

    def get_params(self):
        return self.childs[0]

    def func_calculate(self, func_name, params_list):
        """
        :param func_name:
        :param params_list: Expr list
        :return:
        """
        pass

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
    def __init__(self, arg):
        super(self.__class__, self).__init__(arg)
        self.params_list = []

    def parse(self):
        token = self.tokenmanager.get_next_token()
        # token == '('
        self.add_childs(token)
        self.add_unrolled_childs(token)
        expr = Expr(self.tokenmanager)
        expr.parse()
        expr.calculate()
        self.add_childs(expr)
        self.add_unrolled_childs(expr)
        param_tail = ParamTail(self.tokenmanager)
        param_tail.parse()
        self.add_childs(param_tail)

        while param_tail.has_childs():
            comma = param_tail.get_comma()
            self.add_unrolled_childs(comma)
            expr = param_tail.get_expr()
            self.add_unrolled_childs(expr)
            param_tail = param_tail.get_tail()

        token = self.tokenmanager.get_next_token()  # ')' token should exists
        self.add_childs(token)


class ParamTail(Nonterminal):
    """
    < param > = ( < expr > < param_tail > )
    < param_tail > =, < expr > <param_tail> | empty
    """

    def __init__(self, tokenmanager):
        if not isinstance(tokenmanager, TokenManager):
            raise_error("ParamTail expects tokenmanager as initialization, but {} is gotten".str(tokenmanager))
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
                expr.calculate()
                self.add_childs(expr)
                param_tail = ParamTail(self.tokenmanager)
                param_tail.parse()
                self.add_childs(param_tail)

    def get_comma(self):
        return self.childs[0]

    def get_expr(self):
        return self.childs[1]

    def get_tail(self):
        return self.childs[2]

