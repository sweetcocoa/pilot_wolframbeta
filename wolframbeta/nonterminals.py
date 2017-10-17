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

    def differentiate_variable(self, variable):
        var = variable

        pass

    def assign_function(self, function_dict):
        pass

    def calculate_variable(self, variable_dict):
        """
        :param variable_dict: { Variable:float ... }
        :return: calculated value (similar_terms_dict)
        """
        similar_new_dict = SimilarTermsDict()
        for term, const in self.similar_terms_dict.items():
            if term == CONST_KEY:
                similar_new_dict = similar_new_dict + const
            else:
                new_term_dict = TermDict(term)
                new_term_dict.constant = const
                for var, power in term.items():

                    if isinstance(var, Function):

                        func = Func(var[len(var.name):], var.name)
                        func.parse()
                        func.calculate()
                        cal_func = func.calculate_variable(variable_dict)

                        if cal_func.is_constant():
                            val_func = cal_func.get_constant()
                            new_term_dict.constant *= val_func ** power
                            new_term_dict.pop(var, None)
                        elif cal_func.has_one_term():
                            func_term, coeff = cal_func.get_one_term()
                            new_term_dict.pop(var, None)
                            if func_term in new_term_dict.keys():
                                new_term_dict[func_term] += 1
                            else:
                                new_term_dict[func_term] = 1

                        else:
                            raise_error("Unexpected : calculated function has more than two terms")
                            pass

                    elif isinstance(var, PowerOfFloat):
                        # e^(x^2 * y)

                        exponent_term = TermDict(var.exponent_term)
                        var_exist = False
                        for term, power in var.exponent_term.items():
                            if term in variable_dict.keys():
                                exponent_term.constant *= variable_dict[term] ** power
                                exponent_term.pop(term, None)
                                var_exist = True

                        base_constant = var.base_constant ** exponent_term.constant  # e

                        # e -> e^9
                        if exponent_term.is_constant():
                            new_term_dict.constant *= base_constant
                            new_term_dict.pop(var, None)
                        elif var_exist:
                            # 9*y -> y
                            exponent_term.constant = 1.0

                            new_power_of_float = get_power_of_float(base_constant, exponent_term)

                            if str(new_power_of_float) not in new_term_dict.keys():
                                new_term_dict[new_power_of_float] = 1.0
                            else:

                                new_key_base = base_constant ** (new_term_dict[new_power_of_float] + 1)
                                new_key_pof = get_power_of_float(new_key_base, exponent_term)
                                new_term_dict.pop(new_power_of_float, None)
                                new_term_dict[new_key_pof] = 1.0

                            new_term_dict.pop(var, None)

                    elif var in variable_dict.keys():
                        new_term_dict.constant *= variable_dict[var] ** power
                        new_term_dict.pop(var, None)

                if new_term_dict in similar_new_dict.keys():
                    similar_new_dict[new_term_dict] += new_term_dict.constant
                else:
                    similar_new_dict[new_term_dict] = new_term_dict.constant

        return similar_new_dict

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
        return str(self.similar_terms_dict)


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

        elif token == '+':
            sign = token
            self.add_childs(sign)
            self.negative_sign = 1.0
            factor = Factor(self.tokenmanager)
            factor.parse()
            self.add_childs(factor)

        elif token == '-':
            sign = token
            self.add_childs(sign)
            self.negative_sign = -1.0
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

        if self.negative_sign == -1 or self.childs[0] == '+':
            factor = self.childs[1]
            factor.calculate()
            self.similar_terms_dict = self.negative_sign * factor.similar_terms_dict

        elif isinstance(self.childs[0], float):
            number = self.childs[0]
            if factor_tail.has_childs():
                # number^factor
                factor_power = factor_tail.get_factor()
                factor_power.calculate()
                self.similar_terms_dict = number ** factor_power.similar_terms_dict
            else:
                # number without power
                self.similar_terms_dict[CONST_KEY] = number
        elif self.childs[0] == '(':
            expr = self.childs[1]
            expr.calculate()

            if factor_tail.has_childs():
                # (expr, term, constant)^(constant, term, expr)
                factor_power = factor_tail.get_factor()
                factor_power.calculate()
                self.similar_terms_dict = expr.similar_terms_dict ** factor_power.similar_terms_dict

            else:
                # (expr) 인 경우 :
                self.similar_terms_dict = expr.similar_terms_dict

        elif isinstance(self.childs[0], Variable):
            variable = self.childs[0]
            term_dict = TermDict()
            term_dict[variable] = 1.0
            if factor_tail.has_childs():
                # variable^factor 인 경우
                factor_power = factor_tail.get_factor()
                factor_power.calculate()
                if factor_power.is_constant():
                    # variable^constant
                    term_dict[variable] = factor_power.get_constant()
                    self.similar_terms_dict[term_dict] = 1.0
                else:
                    # variable^(some expression containing varaible)
                    raise_error("(expr)^(term, expr) error - {}^{}".format(self.childs[0], str(factor_power)))
                    self.similar_terms_dict[term_dict] = 1.0
            else:
                # varaible without factor
                self.similar_terms_dict[term_dict] = 1.0

        elif isinstance(self.childs[0], Func):
            func = self.childs[0]
            func.calculate()
            # function = Function(value=str(func), func=func)
            if factor_tail.has_childs():
                factor_power = factor_tail.get_factor()
                factor_power.calculate()
                self.similar_terms_dict = func.similar_terms_dict ** factor_power.similar_terms_dict
            else:
                if func.is_constant():
                    self.similar_terms_dict[CONST_KEY] = func.get_constant()
                else:
                    self.similar_terms_dict = func.similar_terms_dict

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
        """
        :param arg: string or tokenmanager
        :param name: function name
        :param user_defined: user_defined similar terms dict
        :param params_list: expr_list (calculated)
        """
        super(self.__class__, self).__init__(arg)
        if name is None:
            debugger("Function's name is not defined")
        self.name = name
        self.user_defined = user_defined  # SimilarTermDict

        self.similar_terms_dict = SimilarTermsDict()

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

        if self.name in BUILTIN_FUNCTIONS.keys():
            self.similar_terms_dict = self.calculate_builtin_function(self.name, params_list)
        else:
            # User_defined_function
            pass

    def calculate_variable(self, variable_dict):
        """
        :param variable_dict: { Variable:float ... }
        :return: calculated value
        """

        params = self.get_params()
        params_list = params.get_params_list()

        calculated_list = list()
        for expr in params_list:
            similar_terms_dict = expr.calculate_variable(variable_dict=variable_dict)
            calculated_list.append(similar_terms_dict)

        if self.name in BUILTIN_FUNCTIONS.keys():
            similar_terms_dict = self.calculate_builtin_function(self.name, calculated_list)
            return similar_terms_dict
        else:  # User_defined_function:
            pass

    def calculate_builtin_function(self, func_name, params_list):

        term_dict = TermDict()

        function_str = self.name
        function_str += '('
        for calculated_dict in params_list:
            function_str += str(calculated_dict) + ','
        function_str = function_str[:-1] + ')'

        func_var = Function(function_str, self.name, params_list)
        # func = Func(function_str, name=self.name, params_list=params_list)

        if func_name == 'pow':
            if len(params_list) != 2:
                raise_error("{} expected two parameters, but {} is/are received".format(func_name, len(params_list)))
            base = params_list[0]
            exponent = params_list[1]
            similar_terms_dict = base.similar_terms_dict ** exponent.similar_terms_dict

        elif func_name == 'sqrt':
            if len(params_list) != 1:
                raise_error("{} expected one parameters, but {} is/are received".format(func_name, len(params_list)))
            expr = params_list[0]
            similar_terms_dict = expr.similar_terms_dict ** 0.5

        elif func_name in BUILTIN_FUNCTIONS_WITH_ONE_PARAM.keys():
            if len(params_list) != 1:
                raise_error("{} expected one parameters, but {} is/are received".format(func_name, len(params_list)))
            radian = params_list[0]
            if radian.is_constant():
                func_value = BUILTIN_FUNCTIONS_WITH_ONE_PARAM[func_name](radian.get_constant())
                term_dict.constant = func_value
            else:
                term_dict[func_var] = 1.0
                # term_dict[func] = 1.0

            similar_terms_dict = SimilarTermsDict()
            similar_terms_dict[term_dict] = term_dict.constant

        elif func_name in BUILTIN_FUNCTIONS_WITH_TWO_PARAM.keys():
            if len(params_list) != 2:
                raise_error("{} expected two parameters, but {} is/are received".format(func_name, len(params_list)))
            # log(value, base)
            upper = params_list[0]
            lower = params_list[1]
            if upper.is_constant() and lower.is_constant():
                func_value = BUILTIN_FUNCTIONS_WITH_TWO_PARAM[func_name](upper.get_constant(), lower.get_constant())
                term_dict.constant = func_value
            elif not upper.is_constant() and not lower.is_constant():
                raise_error("{}({},{}) is not supported.".format(func_name, str(upper), str(lower)))

            elif not upper.is_constant() and lower.is_constant():
                term_dict[func_var] = 1.0
                # term_dict[func] = 1.0
            else:
                raise_error("{}({},{}) is not supported.".format(func_name, str(upper), str(lower)))

            similar_terms_dict = SimilarTermsDict()
            similar_terms_dict[term_dict] = term_dict.constant
        else:
            raise_error("Unexpected : unrecognizable function name {}".format(func_name))
            similar_terms_dict = SimilarTermsDict()

        return similar_terms_dict

    def get_params(self):
        return self.childs[0]

    def is_constant(self):
        return self.similar_terms_dict.is_constant()

    def get_constant(self):
        return self.similar_terms_dict.get_constant()

    def __str__(self):
        ret_str = self.name

        param = self.get_params()
        ret_str += str(param)
        return ret_str

    def __hash__(self):
        return hash(str(self))


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

