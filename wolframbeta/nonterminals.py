from wolframbeta.tokenizer import TokenManager
from wolframbeta.similar_term import SimilarTermsDict, TermDict, Variable
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
        return

    def get_term(self):
        return self.childs[0]

    def get_tail(self):
        return self.childs[-1]

    def __str__(self):
        if self.similar_terms_dict is None:
            return "None_Expr"
        ret_str = ""
        for i, (term, const) in enumerate(sorted(self.similar_terms_dict.items())):
            if i == 0 and const > 0:
                ret_str += str(const) + '*' + str(term)
            elif const < 0:
                ret_str += '-' + str(-const) + '*' + str(term)
            elif const > 0:
                ret_str += '+' + str(-const) + '*' + str(term)
        return ret_str


class ExprTail(Nonterminal):
    def __init__(self, tokenmanager):
        if not isinstance(tokenmanager, TokenManager):
            raise_error("ExprTail expects tokenmanger as initialization, but {} is gotten".str(tokenmanager))
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
        return

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
            raise_error("TermTail expects tokenmanger as initialization, but {} is gotten".str(tokenmanager))
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
    def __init__(self, arg):
        if isinstance(arg, TermDict):
            self.term_dict = arg
        else:
            self.term_dict = None
        super(self.__class__, self).__init__(arg)
        self.variable_set = None  # Factor에 연관 있는 variable set
        self.negative_sign = False

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
            self.add_childs(expr)
            self.add_unrolled_childs(expr)
            token = self.tokenmanager.get_next_token()
            self.add_childs(token)
            self.add_unrolled_childs(token)

        elif token == '-':
            sign = token
            self.add_childs(sign)
            self.add_unrolled_childs(sign)
            self.negative_sign = True
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
            factor_tail = factor.get_factor_tail()

    def add_variable(self, variable):
        if self.variable_set is None:
            self.variable_set = set()
        self.variable_set.add(variable)

    def calculate(self):
        return

    def __str__(self):
        ret_str = ""
        ret_str = self.get_something_str()
        factor_tail = self.get_factor_tail()
        if factor_tail.has_childs():
            factor_child = factor_tail.get_factor()
            ret_str += '^' + str(factor_child)

        return ret_str