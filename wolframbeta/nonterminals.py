from wolframbeta.tokenizer import TokenManager
from wolframbeta.terminals import *

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
    """
    <expr> := <term> <expr_tail>
    <expr_tail> := <add><expr> | empty
    """
    def __init__(self, arg):
        super(self.__class__, self).__init__(arg)
        self.dict = ExprDict(0)

    def parse(self):
        term = Term(self.tokenmanager)
        term.parse()
        self.add_childs(term)

        expr_tail = ExprTail(self.tokenmanager)
        expr_tail.parse()
        self.add_childs(expr_tail)

    def calculate(self):
        term = self.get_term()
        term.calculate()
        self.dict = term.dict
        expr_tail = self.get_tail()

        if expr_tail.has_childs():
            ops = expr_tail.get_ops()
            expr = expr_tail.get_expr()
            expr.calculate()
            self.dict = calculate_ops(self.dict, ops, expr.dict)

    def get_term(self):
        return self.childs[0]

    def get_tail(self):
        return self.childs[-1]

    def __str__(self):
        return str(self.dict)


class ExprTail(Nonterminal):
    """
    <expr> := <term> <expr_tail>
    <expr_tail> := <add><expr> | empty
    """
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
    def __init__(self, arg):
        super(self.__class__, self).__init__(arg)
        self.dict = None

    def parse(self):
        factor = Factor(self.tokenmanager)
        factor.parse()
        self.add_childs(factor)
        term_tail = TermTail(self.tokenmanager)
        term_tail.parse()
        self.add_childs(term_tail)

    def calculate(self):
        factor = self.get_factor()
        factor.calculate()
        self.dict = factor.dict
        term_tail = self.get_tail()

        while term_tail.has_childs():
            term = term_tail.get_term()
            factor = term.get_factor()
            factor.calculate()
            ops = term_tail.get_ops()
            self.dict = calculate_ops(self.dict, ops, factor.dict)
            term_tail = term.get_tail()

    def get_factor(self):
        return self.childs[0]

    def get_tail(self):
        return self.childs[-1]


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
        self.dict = None

    def parse(self):
        token = self.tokenmanager.get_next_token()

        if isinstance(token, float) or isinstance(token, int):
            self.add_childs(token)

        elif token == '(':
            # ( <expr> )
            self.add_childs(token)
            expr = Expr(self.tokenmanager)
            expr.parse()
            self.add_childs(expr)
            token = self.tokenmanager.get_next_token()
            self.add_childs(token)

        elif token == '+':
            sign = token
            self.add_childs(sign)
            factor = Factor(self.tokenmanager)
            factor.parse()
            self.add_childs(factor)

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
        else:  # token is Variable
            variable = Variable(token)
            self.add_childs(variable)

        factor_tail = FactorTail(self.tokenmanager)
        factor_tail.parse()

        self.add_childs(factor_tail)

    def calculate(self):

        factor_tail = self.get_tail()

        if self.childs[0] == '-' or self.childs[0] == '+':
            factor = self.childs[1]
            factor.calculate()
            if self.childs[0] == '-':
                self.dict = -factor.dict
            else:
                self.dict = factor.dict

        elif isinstance(self.childs[0], float) or isinstance(self.childs[0], int):
            number = self.childs[0]
            if factor_tail.has_childs():
                factor_power = factor_tail.get_factor()
                factor_power.calculate()
                self.dict = number ** factor_power.dict
            else:
                self.dict = TermDict(number)
        elif self.childs[0] == '(':
            expr = self.childs[1]
            expr.calculate()
            if factor_tail.has_childs():
                factor_power = factor_tail.get_factor()
                factor_power.calculate()
                self.dict = expr.dict ** factor_power.dict
            else:
                self.dict = expr.dict
        elif isinstance(self.childs[0], Variable):
            var = self.childs[0]
            term_var = TermDict(1)
            term_var[var] = 1

            if factor_tail.has_childs():
                factor_power = factor_tail.get_factor()
                factor_power.calculate()
                self.dict = term_var ** factor_power.dict
            else:
                self.dict = term_var

        elif isinstance(self.childs[0], Func):
            func = self.childs[0]
            func.calculate()
            if factor_tail.has_childs():
                factor_power = factor_tail.get_factor()
                factor_power.calculate()
                self.dict = func.dict ** factor_power.dict
            else:
                self.dict = func.dict



    def get_tail(self):
        return self.childs[-1]


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
    := 'sin' | 'cos' | 'tan' | 'cot' | 'sec' | 'cosec' | 'log' | 'exp' | 'pow' ...
    := user_defined_function
    """
    def __init__(self, arg, name=None):
        super(self.__class__, self).__init__(arg)
        self.dict = None
        self.name = name

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
        params_list = params.get_params_list()
        for param in params_list:
            param.calculate()

        if self.name == 'sqrt':
            if len(params_list) != 1:
                self.calculate_status = "OneParameterError"
                ed_base = ExprDict(0)
            else:
                ed_base = params_list[0].dict
            td_base = TermDict(1)
            td_base[ed_base] = 0.5
            self.dict = td_base
        elif self.name == 'pow':
            if len(params_list) != 2:
                self.calculate_status = "TwoParameterError"
                ed_base = TermDict(1)
                ed_exponent = TermDict(1)
            else:
                ed_base = params_list[0].dict
                ed_exponent = params_list[1].dict
            td_base = TermDict(1)
            td_base[ed_base] = ed_exponent
            self.dict = td_base
        else:
            td_func = TermDict(1)
            val_function = Function(self.name, params_list)
            td_func[val_function] = 1
            self.dict = td_func

    def get_params(self):
        return self.childs[0]


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

    def get_comma(self):
        return self.childs[0]

    def get_expr(self):
        return self.childs[1]

    def get_tail(self):
        return self.childs[2]


