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

    def parse(self):
        return

    def calculate(self):
        return

    def add_childs(self, newobject):
        self.childs.append(newobject)

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

    def calculate(self):
        if self.similar_terms_dict is not None:
            return

        self.similar_terms_dict = SimilarTermsDict()
        term = self.get_term()
        term.calculate()
        self.similar_terms_dict = term.similar_terms_dict

        expr_tail = self.get_tail()
        if expr_tail.has_childs():
            ops = expr_tail.get_ops()
            expr = expr_tail.get_expr()
            expr.calculate()
            debugger("tail's expr's dict: ", self.similar_terms_dict)
            self.similar_terms_dict = calculate_ops(self.similar_terms_dict, ops, expr.similar_terms_dict)

    def calculate_variable(self, variable_dict):
        """
        :param variable_dict: { Variable:float ... }
        :return: calculated value
        """
        similar_new_dict = SimilarTermsDict()
        for term, const in self.similar_terms_dict.items():
            if term == CONST_KEY:
                similar_new_dict = similar_new_dict + const
            else:
                for var, power in term:
                    if var in variable_dict.keys():
                        pass

    def get_term(self):
        return self.childs[0]

    def get_tail(self):
        return self.childs[-1]

    def is_constant(self):
        if self.similar_terms_dict is not None:
            return self.similar_terms_dict.is_constant()
        else:
            return False

    def get_constant(self):
        return self.similar_terms_dict[CONST_KEY]

    def has_one_term(self):
        return self.similar_terms_dict.has_one_term()

    def __str__(self):
        if self.similar_terms_dict is None:
            return "None_Expr"
        ret_str = ""
        if self.is_constant():
            ret_str += str(self.get_constant())
        else:
            for i, (term, const) in enumerate(reversed(sorted(self.similar_terms_dict.items()))):
                if i == 0 and const > 0:
                    if const == 1:
                        ret_str += str(term)
                    else:
                        ret_str += str(const) + '*' + str(term)
                elif const < 0:
                    if term == CONST_KEY:
                        ret_str += '-' + str(-const)
                    elif const == -1:
                        ret_str += '-' + str(term)
                    else:
                        ret_str += '-' + str(-const) + '*' + str(term)
                elif const > 0:
                    if const == 1:
                        if term == CONST_KEY:
                            ret_str += '+' + str(const)
                        else:
                            ret_str += '+' + str(term)
                    else:
                        if term == CONST_KEY:
                            ret_str += '+' + str(const)
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
        super(self.__class__, self).__init__(arg)
        self.similar_terms_dict = None

    def parse(self):
        factor = Factor(self.tokenmanager)
        factor.parse()
        self.add_childs(factor)
        term_tail = TermTail(self.tokenmanager)
        term_tail.parse()
        self.add_childs(term_tail)

    def calculate(self):
        if self.similar_terms_dict is not None:
            return

        factor = self.get_factor()
        factor.calculate()
        self.similar_terms_dict = factor.similar_terms_dict
        term_tail = self.get_tail()

        while term_tail.has_childs():
            term = term_tail.get_term()
            factor = term.get_factor()
            factor.calculate()
            ops = term_tail.get_ops()
            self.similar_terms_dict = calculate_ops(self.similar_terms_dict, ops, factor.similar_terms_dict)
            term_tail = term.get_tail()

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
        super(self.__class__, self).__init__(arg)
        self.negative_sign = 1
        self.similar_terms_dict = None  # ( expr )'s expr value

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
            self.negative_sign = -1
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

    def calculate(self):
        if self.similar_terms_dict is not None:
            return

        self.similar_terms_dict = SimilarTermsDict()
        factor_tail = self.get_tail()

        if self.negative_sign == -1:
            factor = self.childs[1]
            factor.calculate()
            self.similar_terms_dict = -factor.similar_terms_dict

        if isinstance(self.childs[0], float):
            number = self.childs[0]
            if factor_tail.has_childs():
                # number^factor
                factor_power = factor_tail.get_factor()
                factor_power.calculate()
                if factor_power.is_constant():
                    # number^number
                    exponent = factor_power.get_constant()
                    self.similar_terms_dict[CONST_KEY] = number ** exponent
                elif factor_power.has_one_term():
                    # number^term
                    key, value = factor_power.similar_terms_dict.get_one_term()
                    term_dict = number**key
                    self.similar_terms_dict[term_dict] = value
                else:
                    # number ^ (multi-term)
                    pass
            else:
                # number without power
                self.similar_terms_dict[CONST_KEY] = number
        elif self.childs[0] == '(':
            expr = self.childs[1]
            expr.calculate()

            if factor_tail.has_childs():
                # (expr, term, constant)^(constant, term, expr)
                factor_power = factor_tail.get_factor()
                factor_power.calculate()\

                if expr.is_constant():
                    number = expr.get_constant()
                    if factor_power.is_constant():
                        # (number) ^ number
                        exponent = factor_power.get_constant()
                        self.similar_terms_dict[CONST_KEY] = number ** exponent
                    elif factor_power.has_one_term():
                        # (number) ^ term
                        key, value = factor_power.similar_terms_dict.get_one_term()
                        term_dict = number ** key
                        self.similar_terms_dict[term_dict] = value
                    else:
                        # (number) ^ (muiti-term)
                        pass
                    pass
                elif expr.has_one_term():
                    if factor_power.is_constant():
                        # (term)^(constant)
                        exponent = factor_power.get_constant()
                        key, value = expr.similar_terms_dict.get_one_term()
                        key.constant = 1
                        term_dict = key ** exponent
                        self.similar_terms_dict[term_dict] = value ** exponent
                    else:
                        raise_error("(term)^(expr, term) is not supported form")
                    pass
                else:
                    if factor_power.is_constant():
                        pass
                    else:
                        raise_error("(expr)^(expr, term) Does not supported.")
                    pass

            else:
                # (expr) 인 경우 :
                self.similar_terms_dict = expr.similar_terms_dict

        elif isinstance(self.childs[0], Variable):
            variable = self.childs[0]
            term_dict = TermDict()
            term_dict[variable] = 1
            if factor_tail.has_childs():
                # variable^factor 인 경우
                factor_power = factor_tail.get_factor()
                factor_power.calculate()
                if factor_power.is_constant():
                    # variable^constant
                    term_dict[variable] = factor_power.get_constant()
                    self.similar_terms_dict[term_dict] = 1
                else:
                    # variable^(some expression containing varaible)
                    raise_error("variable^variable is not supported. error - {}^{}".format(self.childs[0], str(factor_power)))
            else:
                # varaible without factor
                self.similar_terms_dict[term_dict] = 1

        elif isinstance(self.childs[0], Func):
            func = self.childs[0]
            func.calculate()
            term_dict = func.term_dict
            if factor_tail.has_childs():
                factor_power = factor_tail.get_factor()
                factor_power.calculate()
                if factor_power.is_constant():
                    term_dict = term_dict ** factor_power.get_constant()
                    pass
                else:
                    # func^(expr, term .. )
                    pass
            self.similar_terms_dict[term_dict] = term_dict.constant
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
        #if self.similar_terms_dict is not None:
        return self.similar_terms_dict.is_constant()

    def get_constant(self):
        return self.similar_terms_dict[CONST_KEY]

    def has_one_term(self):
        return self.similar_terms_dict.has_one_term()


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
        self.term_dict = None

    def parse(self):
        """
        Func class does not have its name as a child.
        Its name is stored in self.name when object is created.
        """
        params = Params(self.tokenmanager)
        params.parse()
        self.add_childs(params)

    def calculate(self):
        params = self.get_params()
        if self.name in BUILTIN_FUNCTIONS.keys():
            self.term_dict = self.calculate_builtin_function(self.name, params)
        else:
            # User_defined_function
            pass

    def calculate_builtin_function(self, func_name, params):
        params_list = params.get_params_list()
        term_dict = TermDict()
        if func_name in BUILTIN_FUNCTIONS_WITH_ONE_PARAM.keys():
            if len(params_list) != 1:
                raise_error("{} expected one parameters, but {} is/are received".format(func_name, len(params_list)))
            radian = params_list[0]
            radian.calculate()
            if radian.is_constant():
                func_value = BUILTIN_FUNCTIONS_WITH_ONE_PARAM[func_name](radian.get_constant())
                term_dict.constant = func_value
            else:
                term_dict[str(self)] = 1
        elif func_name in BUILTIN_FUNCTIONS_WITH_TWO_PARAM.keys():
            if len(params_list) != 2:
                raise_error("{} expected two parameters, but {} is/are received".format(func_name, len(params_list)))
            # log(value, base)
            # pow(base, exponent)
            base = params_list[0]
            exponent = params_list[1]
            base.calculate()
            exponent.calculate()
            if base.is_constant() and exponent.is_constant():
                func_value = BUILTIN_FUNCTIONS_WITH_TWO_PARAM[func_name](base.get_constant(), exponent.get_constant())
                term_dict.constant = func_value
            elif not base.is_constant() and not exponent.is_constant():
                raise_error("Only Polynomial calculation is supported. {}({},{}) is not a polynomial.".format(func_name, str(base), str(exponent)))
            elif not base.is_constant() and exponent.is_constant():
                if base.has_one_term():
                    pass
                else:
                    pass
                pass
            elif base.is_constant() and not exponent.is_constant():
                # 2^(x+1) 은 2*2^x, 뭐 이런 연산 필요
                pass
        return term_dict

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
        expr = Expr(self.tokenmanager)
        expr.parse()
        self.add_childs(expr)
        param_tail = ParamTail(self.tokenmanager)
        param_tail.parse()
        self.add_childs(param_tail)

        while param_tail.has_childs():
            comma = param_tail.get_comma()
            expr = param_tail.get_expr()
            param_tail = param_tail.get_tail()

        token = self.tokenmanager.get_next_token()  # ')' token should exists
        self.add_childs(token)

    def get_tail(self):
        return self.childs[2]

    def get_expr(self):
        return self.childs[1]

    def get_params_list(self):
        """
        :return: list of expr objects which are contained in params.
        """
        if len(self.params_list) > 0:
            return self.params_list
        expr = self.get_expr()
        self.params_list.append(expr)

        param_tail = self.get_tail()
        while param_tail.has_childs():
            expr = param_tail.get_expr()
            self.params_list.append(expr)
            param_tail = param_tail.get_tail()

        return self.params_list

    def __str__(self):
        ret_str = '('
        params_list = self.get_params_list()
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

