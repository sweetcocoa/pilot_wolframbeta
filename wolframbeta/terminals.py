from wolframbeta.utils import *
from wolframbeta.config import *


class Variable:

    def __init__(self, name):
        self.name = str(name)

    def __str__(self):
        return self.name

    def __hash__(self):
        return hash(self.name)

    def __lt__(self, other):
        return self.name < other

    def __eq__(self, other):
        return self.name == other

    def __gt__(self, other):
        return self.name > other

    def is_constant(self):
        return False

    def has_one_term(self):
        return True

    def has_variable(self, variable):
        return self.name == variable

    def calculate_variable(self, variable_dict):
        if self in variable_dict.keys():
            return variable_dict[self], SUCCESS_CODE
        else:
            return self, SUCCESS_CODE

    def differentiate_varaible(self, variable_list):
        ret_code = SUCCESS_CODE
        if variable_list == 1:
            var = variable_list[0]
            if self == var:
                ret_val = 1
            else:
                ret_val = 0
        else:
            ret_code = "DiffVariableOneError"
            ret_val = self

        return ret_val, ret_code


class Function(Variable):
    def __init__(self, name, params=None):
        """
        :param name: function name sin, cos, ...
        :param params: params list which contains expr
        """
        super(Function, self).__init__(name)
        if params is None or len(params) == 0:
            raise ValueError("Function received no params")
        self.params = params

    def __str__(self):
        ret_str = self.name + '('
        for param in self.params:
            ret_str += str(param) + ','
        ret_str = ret_str[:-1] + ')'
        return ret_str

    def is_constant(self):
        is_const = True
        for param in self.params:
            if not param.dict.is_constant():
                is_const = False
                break
        return is_const

    def __hash__(self):
        return hash(str(self))

    def __lt__(self, other):
        return str(self) < other

    def __eq__(self, other):
        return str(self) == other

    def __gt__(self, other):
        return str(self) > other

    def calculate_variable(self, variable_dict):
        new_params = []
        ret_dict = None
        ret_code = SUCCESS_CODE

        for param in self.params:
            new_param, param_code = param.dict.calculate_variable(variable_dict)
            new_params.append(new_param)
            if param_code != SUCCESS_CODE:
                ret_code = param_code

        if self.name in BUILTIN_FUNCTIONS:
            if self.name in BUILTIN_FUNCTIONS_WITH_ONE_PARAM.keys():
                if len(new_params) != 1:
                    ret_code = "OneParameterError"
                    if len(new_params) < 1:
                        radian = TermDict(0)
                    else:
                        radian = new_params[0]
                else:
                    radian = new_params[0]

                if radian.is_constant():
                    radian = radian.get_constant()
                    func_value = BUILTIN_FUNCTIONS_WITH_ONE_PARAM[self.name](radian)
                    td_const = TermDict(func_value)
                    ret_dict = td_const
                else:
                    new_params = [radian]
                    new_function = Function(self.name, new_params)
                    td_func = TermDict(1)
                    td_func[new_function] = 1
                    ret_dict = td_func

            elif self.name in BUILTIN_FUNCTIONS_WITH_TWO_PARAM:
                if len(new_params) != 2:
                    ret_code = "TwoParameterError"
                    if len(new_params) == 0:
                        exponent = TermDict(1)
                        base = TermDict(2)
                    elif len(new_params) == 1:
                        exponent = new_params[0]
                        base = TermDict(10)
                    else:
                        exponent = new_params[0]
                        base = new_params[1]
                else:
                    exponent = new_params[0]
                    base = new_params[1]

                if exponent.is_constant() and base.is_constant():
                    exponent = exponent.get_constant()
                    base = base.get_constant()
                    if base <= 0 or base == 1:
                        ret_code = "LogBaseError"
                        base = 2
                    if exponent <= 0:
                        ret_code = "LogExponentError"
                        exponent = 1

                    func_value = BUILTIN_FUNCTIONS_WITH_TWO_PARAM[self.name](exponent, base)
                    td_const = TermDict(func_value)
                    ret_dict = td_const
                elif base.is_constant():
                    base = base.get_constant()
                    if base <= 0 or base == 1:
                        ret_code = "LogBaseError"
                        base = 2
                    td_const = TermDict(base)
                    new_params = [exponent, td_const]
                    new_function = Function(self.name, new_params)
                    td_func = TermDict(1)
                    td_func[new_function] = 1
                    ret_dict = td_func
                elif exponent.is_constant():
                    exponent = exponent.get_constant()
                    if exponent <= 0:
                        ret_code = "LogExponentError"
                        exponent = 1
                    td_const = TermDict(exponent)
                    new_params = [td_const, base]
                    new_function = Function(self.name, new_params)
                    td_func = TermDict(1)
                    td_func[new_function] = 1
                    ret_dict = td_func
                else:
                    new_params = [exponent, base]
                    new_function = Function(self.name, new_params)
                    td_func = TermDict(1)
                    td_func[new_function] = 1
                    ret_dict = td_func
        else:
            ret_code = "UndefinedFunctionError"
            ret_dict = TermDict(1)

        return ret_dict, ret_code

    def has_variable(self, variable):
        has = False
        for param in self.params:
            has = param.dict.has_variable(variable)
            if has:
                break
        return has

    def differentiate_varaible(self, variable_list):
        """
        sin, cos, tan, cot,
        sinh, cosh

        """
        ret_code = SUCCESS_CODE
        new_name = None
        new_coeff = 0
        new_power = 0
        ret_dict = None

        if self.name == "sin":
            new_name = "cos"
            new_coeff = 1
            new_power = 1
        elif self.name == "cos":
            new_name = "sin"
            new_coeff = -1
            new_power = 1
        elif self.name == "tan":
            new_name = "sec"
            new_coeff = 1
            new_power = 2
        elif self.name == "cot":
            new_name = "cosec"
            new_coeff = -1
            new_power = 2
        elif self.name == "sinh":
            new_name = "cosh"
            new_coeff = 1
            new_power = 1
        elif self.name == "cosh":
            new_name = "sinh"
            new_coeff = 1
            new_power = 1

        if new_name is not None:
            new_function = Function(new_name, self.params)
            if len(self.params) != 1:
                ret_code = "OneParameterError"
                ret_dict = TermDict(0)
            else:
                if new_function.params[0].dict.is_constant():
                    ret_dict = TermDict(0)
                else:
                    rad_diff, rad_code = new_function.params[0].dict.differentiate_variable(variable_list)
                    if rad_code != SUCCESS_CODE:
                        ret_code = rad_code
                    td_function = TermDict(new_coeff)
                    td_function[new_function] = new_power
                    ret_dict = td_function * rad_diff
        else:
            """
            
            """

            pass


        return ret_dict, ret_code


class ExprDict(dict):
    def __init__(self, *args):
        if isinstance(*args, float) or isinstance(*args, int):
            super(self.__class__, self).__init__()
            self[CONST_KEY] = args[0]
        else:
            if len(args) > 0 and isinstance(args[0], TermDict):
                super(self.__class__, self).__init__()
                if args[0].is_constant():
                    self[CONST_KEY] = args[0][COEFF_KEY]
                else:
                    self[args[0]] = args[0][COEFF_KEY]
                    self[CONST_KEY] = 0
            else:
                super(self.__class__, self).__init__(*args)
                if CONST_KEY not in self.keys():
                    self[CONST_KEY] = 0

    def __add__(self, other):
        ret_dict = None
        if isinstance(other, int) or isinstance(other, float):
            ret_dict = ExprDict(self)
            ret_dict[CONST_KEY] += other

        elif isinstance(other, TermDict):
            ret_dict = ExprDict(self)
            if other.is_constant():
                const = other.get_coefficient()
                ret_dict = self + const
            else:

                if other in ret_dict.keys():

                    ret_dict[other] += other.get_coefficient()
                    if ret_dict[other] == 0:
                        ret_dict.pop(other, None)
                else:

                    ret_dict[other] = other.get_coefficient()

        elif isinstance(other, ExprDict):
            ret_dict = ExprDict(self)
            for term, coeff in other.items():
                if term == CONST_KEY:
                    ret_dict = ret_dict + coeff
                else:
                    term[COEFF_KEY] = coeff
                    ret_dict = ret_dict + term
        if ret_dict.is_constant():
            ret_dict = TermDict(ret_dict.get_constant())

        return ret_dict

    def __radd__(self, other):
        return self + other

    def __sub__(self, other):
        return self + -other

    def __rsub__(self, other):
        return -self + other

    def __mul__(self, other):
        ret_dict = None
        if isinstance(other, int) or isinstance(other, float):
            if other == 0:
                ret_dict = ExprDict(0)
            else:
                ret_dict = ExprDict(self)
                for term, coeff in ret_dict.items():
                    ret_dict[term] = coeff * other
        elif isinstance(other, ExprDict):
            ret_dict = ExprDict(0)
            for a_term, a_coeff in self.items():
                for b_term, b_coeff in other.items():
                    if a_term == CONST_KEY:
                        new_term = b_term
                    elif b_term == CONST_KEY:
                        new_term = a_term
                    else:
                        new_term = a_term * b_term

                    if new_term in ret_dict.keys():
                        ret_dict[new_term] = ret_dict[new_term] + (b_coeff * a_coeff)
                    else:
                        ret_dict[new_term] = (b_coeff * a_coeff)

                    if ret_dict[new_term] == 0 and new_term != CONST_KEY:
                        ret_dict.pop(new_term, None)
        elif isinstance(other, TermDict):
            ret_dict = ExprDict(0)
            if other.is_constant():
                return self * other.get_constant()
            else:
                for term, coeff in self.items():
                    if term == CONST_KEY:
                        ret_dict = ret_dict + self.get_constant() * other
                    else:
                        term.set_coefficient(coeff)
                        ret_dict = ret_dict + term * other
            return ret_dict

        if ret_dict is None:
            raise_error("ExprDict add :: + unknown")
            ret_dict = ExprDict(0)

        return ret_dict

    def __rmul__(self, other):
        return self * other

    def __truediv__(self, other):
        ret_dict = None
        if isinstance(other, int) or isinstance(other, float):
            try:
                diver = 1 / other
            except ZeroDivisionError:
                raise_error("Expr truediv :: ZeroDivisionError")
                diver = 1
            ret_dict = self * diver
        elif isinstance(other, TermDict):
            if other.is_constant():
                coeff = other.get_constant()
                ret_dict = self / coeff
            else:
                ret_dict = ExprDict(0)
                for term, coeff in self.items():
                    if term == CONST_KEY:
                        if coeff == 0:
                            continue
                        else:
                            ret_term = TermDict(coeff)
                    else:
                        ret_term = TermDict(term)
                    ret_term[COEFF_KEY] = coeff
                    ret_term = ret_term / other
                    if ret_term.is_constant():
                        ret_dict[CONST_KEY] += ret_term.get_constant()
                    else:
                        ret_dict[ret_term] = ret_term.get_constant()

        elif isinstance(other, ExprDict):
            ret_dict = ExprDict(0)
            for a_term, a_coeff in self.items():
                if a_term == CONST_KEY:
                    ret_dict = ret_dict + a_coeff / other
                else:
                    a_term[COEFF_KEY] = a_coeff
                    ret_dict = ret_dict + a_term / other

        else:
            raise_error("Unexpected opreation Expr.__truediv__ :: {}".format(type(other)))
            ret_dict = ExprDict(1)
        return ret_dict

    def __rtruediv__(self, other):
        ret_dict = None
        if isinstance(other, float) or isinstance(other, int):
            ret_td = TermDict(other)
            ret_dict = ret_td / self
        if ret_dict is None:
            raise_error("Unexpected operation Expr.__rtruediv__ :: {}".format(type(other)))
            ret_dict = ExprDict(1)
        return ret_dict

    def __expr_pow__(self, exprdict, power):
        if power < 0:
            return self.__expr_pow__(1 / exprdict, -power)
        elif power == 0:
            ret_dict = ExprDict(1)
        elif power == 1:
            ret_dict = ExprDict(exprdict)
        elif power % 2 == 0:
            return self.__expr_pow__(exprdict * exprdict, power // 2)
        elif power % 2 == 1:
            return exprdict * self.__expr_pow__(exprdict * exprdict, (power - 1) // 2)
        return ret_dict

    def __pow__(self, power, modulo=None):
        ret_dict = None
        if isinstance(power, float):
            if power.is_integer():
                ret_dict = self ** int(power)
            else:
                ret_dict = TermDict(1)
                ret_dict[self] = power
        elif isinstance(power, int):
            ret_dict = self.__expr_pow__(self, power)
        elif power.is_constant():
            return self ** power.get_constant()
        elif isinstance(power, ExprDict):
            pass
        elif isinstance(power, TermDict):
            pass
        return ret_dict

    def __rpow__(self, other):
        ret_dict = None
        if isinstance(other, float) or isinstance(other, int):
            ret_td = ConstDict(other)
            ret_dict = ret_td ** self
        else:
            raise_error("Unexpected calculation :: Expr.__rpow__")
            ret_dict = ExprDict(1)
        return ret_dict

    def __neg__(self, other):
        ret_dict = ExprDict(self)
        for term, coeff in ret_dict.items():
            ret_dict[term] = -coeff
        return ret_dict

    def __eq__(self, other):
        if isinstance(other, int) or isinstance(other, float):
            if self.is_constant():
                return self.get_constant() == other
            else:
                return False
        elif isinstance(other, ExprDict):
            return super(self.__class__, self).__eq__(other)
        elif isinstance(other, TermDict):
            return str(self) == str(self)
        else:
            return False

    def __lt__(self, other):
        if isinstance(other, int) or isinstance(other, float):
            return self.get_constant() < other
        elif isinstance(other, Variable):
            return True
        elif isinstance(other, str):
            return True
        elif isinstance(other, ExprDict):
            if len(self) != len(other):
                return len(self) < len(other)
            else:
                return str(self) < str(other)

    def __gt__(self, other):
        return not (self == other or self < other)

    def __str__(self):
        ret_str = ""
        if self.is_constant():
            ret_str = str(self.get_constant())
        else:
            for i, (term, _coeff) in enumerate(sorted(self.items())):
                coeff = strip_float(_coeff)
                if term == CONST_KEY:
                    if i == 0:
                        ret_str += str(coeff)
                    elif coeff > 0:
                        ret_str += '+' + str(coeff)
                    elif coeff < 0:
                        ret_str += '-' + str(-coeff)
                    # else coeff == 0
                    continue

                if i == 0:
                    if coeff == 1:
                        ret_str += term.get_str_without_coeff()
                    elif coeff == -1:
                        ret_str += '-' + term.get_str_without_coeff()
                    else:
                        ret_str += str(coeff) + '*' + term.get_str_without_coeff()
                else:
                    if coeff == 1:
                        ret_str += '+' + term.get_str_without_coeff()
                    elif coeff == -1:
                        ret_str += '-' + term.get_str_without_coeff()
                    elif coeff > 0:
                        ret_str += '+' + str(coeff) + '*' + term.get_str_without_coeff()
                    else:  # coeff < 0
                        ret_str += str(coeff) + '*' + term.get_str_without_coeff()
        return ret_str

    def __hash__(self):
        return hash(str(self))

    def get_constant(self):
        return strip_float(self[CONST_KEY])

    def get_one_term(self):
        """
        return (one term, its coefficient)
        """
        if self.is_constant():
            return TermDict(self.get_constant()), 1
        else:
            for term, coeff in self.items():
                if term == CONST_KEY:
                    continue
                else:
                    return term, coeff

    def is_constant(self):
        return len(self) == 1

    def has_one_term(self):
        if self.get_constant() == 0:
            if len(self) == 2:
                return True
            else:
                return False
        else:
            return len(self) == 1

    def set_constant(self, const):
        self[CONST_KEY] = const

    def calculate_variable(self, variable_dict):
        ret_dict = ExprDict(0)
        ret_code = SUCCESS_CODE
        for term, coeff in self.items():
            if term == CONST_KEY:
                ret_dict = ret_dict + self.get_constant()
            else:
                new_term = TermDict(term)
                new_term[COEFF_KEY] = coeff
                new_term, new_code = new_term.calculate_variable(variable_dict)
                if new_code != SUCCESS_CODE:
                    ret_code = new_code
                    continue
                if new_term.is_constant():
                    ret_dict = ret_dict + new_term.get_constant()
                else:
                    ret_dict = ret_dict + new_term

        if ret_dict.is_constant():
            ret_dict = TermDict(ret_dict.get_constant())
        elif isinstance(ret_dict, ExprDict) and ret_dict.has_one_term():
            ret_dict, coeff = ret_dict.get_one_term()
            ret_dict[COEFF_KEY] = coeff

        return ret_dict, ret_code

    def get_expr_core(self):
        """
        return self / self.highest order's coefficient.
        if self is constant, return exprdict 1
        if self = 0 then raise error.
        """
        ret_dict = None
        div_const = 1
        for term, _coeff in sorted(self.items()):
            div_const = _coeff
            break

        ret_dict = self / div_const

        return ret_dict, div_const

    def has_variable(self, variable):
        has = False
        for term, coeff in self.items():
            if term == CONST_KEY:
                continue
            has = term.has_variable(variable)
            if has:
                break
        return has

    def differentiate_variable(self, variable_list):
        ret_code = SUCCESS_CODE
        if len(variable_list) == 1:
            var = variable_list[0]
            ret_dict = ExprDict(0)
            for term, coeff in self.items():
                if term == CONST_KEY:
                    pass
                else:
                    if term.has_variable(var):
                        term[COEFF_KEY] = coeff
                        diffed_term, term_code = term.differentiate_variable(variable_list)
                        if term_code != SUCCESS_CODE:
                            ret_code = term_code
                        ret_dict = ret_dict + diffed_term
        elif len(variable_list) > 1:
            ret_code = "TooManyDiffVariableError"
            ret_dict = ExprDict(self)
        else:
            ret_code = "NeedDiffVariableError"
            ret_dict = ExprDict(self)
        return ret_dict, ret_code


class TermDict(dict):
    def __init__(self, *args):
        if isinstance(*args, float) or isinstance(*args, int):
            super(TermDict, self).__init__()
            self[COEFF_KEY] = args[0]
        else:
            super(self.__class__, self).__init__(*args)
            if len(args) > 0 and isinstance(args[0], TermDict):
                self[COEFF_KEY] = args[0].get_coefficient()
            else:
                self[COEFF_KEY] = 1

    def __add__(self, other):

        ret_dict = None
        if isinstance(other, ExprDict):
            return other + self
        elif isinstance(other, TermDict):
            if self.is_constant() and other.is_constant():
                ret_dict = TermDict(self.get_constant() + other.get_constant())
            elif str(self) == str(other):
                if self[COEFF_KEY] + other.get_coefficient() == 0:
                    ret_dict = TermDict(0)
                else:
                    ret_dict = TermDict(self)
                    ret_dict[COEFF_KEY] += other.get_coefficient()
            else:
                ret_dict = ExprDict(other)
                ret_dict = ret_dict + self
        elif isinstance(other, float) or isinstance(other, int):
            ret_dict = ExprDict(other)
            ret_dict = ret_dict + self

        if ret_dict is None:
            raise_error("Error : TermDict + unknown")
            ret_dict = TermDict(0)

        return ret_dict

    def __radd__(self, other):
        return self + other

    def __sub__(self, other):
        return self + -other

    def __rsub__(self, other):
        return other + -self

    def __mul__(self, other):
        if isinstance(other, TermDict):
            ret_dict = TermDict(self)
            ret_dict[COEFF_KEY] *= other.get_coefficient()
            for factor, power in other.items():
                if factor == COEFF_KEY:
                    continue
                if factor in ret_dict.keys():
                    ret_dict[factor] = ret_dict[factor] + power
                    if ret_dict[factor] == 0:
                        ret_dict.pop(factor, None)
                else:
                    ret_dict[factor] = power
            return ret_dict

        elif isinstance(other, ExprDict):
            return other * self

        elif isinstance(other, float) or isinstance(other, int):
            if other == 0:
                return TermDict(0)
            ret_dict = TermDict(self)
            ret_dict[COEFF_KEY] *= float(other)
            return ret_dict

        else:
            raise_error("Not implemented : termdict * unknown")

    def __rmul__(self, other):
        return self * other

    def __truediv__(self, other):
        if isinstance(other, TermDict):
            ret_dict = TermDict(self)
            try:
                ret_dict[COEFF_KEY] /= other.get_coefficient()
            except ZeroDivisionError:
                ret_dict[COEFF_KEY] = 1
                raise_error("Term truediv :: ZeroDivisionError")
            for factor, power in other.items():
                if factor == COEFF_KEY:
                    continue
                if factor in ret_dict.keys():
                    ret_dict[factor] = ret_dict[factor] - other[factor]
                    if ret_dict[factor] == 0:
                        ret_dict.pop(factor, None)
                else:
                    ret_dict[factor] = -other[factor]
            return ret_dict
        elif isinstance(other, int) or isinstance(other, float):
            ret_dict = TermDict(self)
            ret_dict[COEFF_KEY] /= float(other)
            return ret_dict
        elif isinstance(other, ExprDict):
            if other.is_constant():
                return self / other.get_constant()
            if other.has_one_term():
                oneterm, coeff = other.get_one_term()
                oneterm[COEFF_KEY] = coeff
                return self / oneterm
            else:
                ret_dict = TermDict(self)
                ret_dict[other] = -1
                return ret_dict
        else:
            raise_error("Not implemented : TermDict / Unknown")

    def __rtruediv__(self, other):
        if isinstance(other, float) or isinstance(other, int):
            ret_dict = TermDict(self)
            for factor, power in self.items():
                if factor == COEFF_KEY:
                    try:
                        ret_dict[COEFF_KEY] = 1 / ret_dict.get_coefficient() * other
                    except ZeroDivisionError:
                        ret_dict[COEFF_KEY] = 1
                        raise_error("Term rtruediv :: ZeroDivisionError")
                else:
                    ret_dict[factor] = -ret_dict[factor]
            return ret_dict
        else:
            raise_error("Not implemented : unknown / termdict")

    def __pow__(self, power, modulo=None):
        if isinstance(power, float):
            if power == 0:
                return TermDict(1)
            ret_dict = TermDict(self)
            for key in self.keys():
                if key == COEFF_KEY:
                    ret_dict[key] = ret_dict[key] ** power
                else:
                    ret_dict[key] *= power
            return ret_dict
        elif isinstance(power, int):
            return self ** float(power)
        elif isinstance(power, TermDict):
            if power.is_constant():
                return self ** power.get_coefficient()
            else:
                ret_dict = TermDict(self)
                for factor, po in self.items():
                    if factor == COEFF_KEY:
                        if self.get_coefficient() != 1:
                            if power.get_coefficient() == 1:
                                coff_td = ConstDict(self.get_coefficient())
                                ret_dict[coff_td] = power
                            else:
                                coff_td = ConstDict(self.get_coefficient() ** power.get_coefficient())
                                try:
                                    ret_dict[coff_td] = power / power.get_coefficient()
                                except ZeroDivisionError:
                                    ret_dict[coff_td] = 1
                                    raise_error("Term Pow :: ZeroDivisionError")
                        ret_dict[COEFF_KEY] = 1

                    else:
                        ret_dict[factor] = ret_dict[factor] * power
                return ret_dict
        elif isinstance(power, ExprDict):
            ret_dict = TermDict(1)
            if self.is_constant():
                if self.get_constant() == 1:
                    return ret_dict
                else:
                    const_dict = ConstDict(self.get_constant())
                    ret_dict[const_dict] = power
            else:
                if self.get_constant() == 1:
                    pass
                else:
                    const_dict = ConstDict(self.get_constant())
                    ret_dict[const_dict] = power
                for factor, po in self.items():
                    if factor == COEFF_KEY:
                        continue
                    else:
                        ret_dict[factor] = po * power

            return ret_dict
            pass

    def __rpow__(self, other):
        if isinstance(other, float) or isinstance(other, int):
            new_const = ConstDict(other)
            return new_const ** self

    def __neg__(self):
        ret_dict = TermDict(self)
        ret_dict[COEFF_KEY] *= -1.0
        return ret_dict

    def __str__(self):
        if self.is_constant():
            ret_str = str(self.get_coefficient())
        else:
            if self.get_coefficient() == 1:
                ret_str = self.get_str_without_coeff()
            elif self.get_coefficient() == -1:
                ret_str = "-" + self.get_str_without_coeff()
            else:
                ret_str = str(self.get_coefficient()) + "*" + self.get_str_without_coeff()
        return ret_str

    def __eq__(self, other):
        if isinstance(other, TermDict):
            return hash(self) == hash(other)
            # return str(self) == str(other)
        elif isinstance(other, float) or isinstance(other, int):
            if self.is_constant():
                return self.get_constant() == other
        return super(TermDict, self).__eq__(other)

    def __lt__(self, other):
        if isinstance(other, str):
            return True
        elif isinstance(other, TermDict):
            if len(self) != len(other):
                return len(self) < len(other)
            else:
                self_dim = 0
                other_dim = 0
                for factor, power in other.items():
                    if factor != COEFF_KEY:
                        other_dim = other_dim + power
                for factor, power in self.items():
                    if factor != COEFF_KEY:
                        self_dim = self_dim + power
                if self_dim != other_dim:
                    return self_dim > other_dim
                else:
                    return str(self) < str(other)
        elif isinstance(other, int) or isinstance(other, float):
            if self.is_constant():
                return self.get_constant() < other
            else:
                return False

    def __gt__(self, other):
        return not (self == other or self < other)

    def __hash__(self):
        return hash(self.get_str_without_coeff())

    def is_constant(self):
        return len(self) == 1

    def has_one_term(self):
        return True

    def get_one_term(self):
        return self, self.get_coefficient()

    def get_coefficient(self):
        return strip_float(self[COEFF_KEY])

    def set_coefficient(self, coeff):
        self[COEFF_KEY] = coeff

    def get_constant(self):
        return strip_float(self[COEFF_KEY])

    def calculate_variable(self, variable_dict):
        """
        ret_dict, ret_code(계산 가능한지? SUCCESS이면 가능)
        """
        ret_dict = TermDict(1)
        ret_code = "SUCCESS"

        for factor, power in self.items():
            if factor == COEFF_KEY:
                ret_dict[COEFF_KEY] *= power
                continue
            else:
                factor_calculated, fac_code = factor.calculate_variable(variable_dict)
                if fac_code != SUCCESS_CODE:
                    ret_code = fac_code

            if isinstance(power, int) or isinstance(power, float):
                power_calculated = power
            else:
                power_calculated, pow_code = power.calculate_variable(variable_dict)
                if pow_code != SUCCESS_CODE:
                    ret_code = pow_code

            if isinstance(power_calculated, float) or isinstance(power_calculated, int):
                # 계산한 지수가 상수
                if power_calculated == 0:
                    continue

                if isinstance(factor_calculated, float) or isinstance(factor_calculated, int):
                    try:
                        ret_dict[COEFF_KEY] *= factor_calculated ** power_calculated
                    except ZeroDivisionError:
                        ret_dict[COEFF_KEY] = 1
                        ret_code = "ZeroDivisionError"

                elif isinstance(factor_calculated, Variable):
                    new_factor = TermDict(1)
                    new_factor[factor_calculated] = power_calculated
                    ret_dict = ret_dict * new_factor

                else:
                    if factor_calculated.is_constant():
                        try:
                            ret_dict[COEFF_KEY] *= factor_calculated.get_constant() ** power_calculated
                        except ZeroDivisionError:
                            ret_dict[COEFF_KEY] = 1
                            ret_code = "ZeroDivisionError"
                    else:
                        ret_dict = ret_dict * (factor_calculated ** power_calculated)

            elif isinstance(power_calculated, Variable):
                # 계산한 지수가 변수
                new_power = TermDict(1)
                new_power[power_calculated] = 1

                if isinstance(factor_calculated, float) or isinstance(factor_calculated, int):
                    ret_dict = ret_dict * (factor_calculated ** new_power)

                elif isinstance(factor_calculated, Variable):
                    # 변수 ^ 변수
                    new_factor = TermDict(1)
                    new_factor[factor_calculated] = power_calculated
                    ret_dict = ret_dict * new_factor

                else:
                    # (식, 항) ^ 변수
                    ret_dict = ret_dict * (factor_calculated ** new_power)

            else:
                # 계산한 지수가 항 또는 식
                # 계산한 지수가 변수
                if isinstance(factor_calculated, float) or isinstance(factor_calculated, int):
                    # 수 ^ 식항
                    ret_dict = ret_dict * (factor_calculated ** power_calculated)

                elif isinstance(factor_calculated, Variable):
                    # 변수 ^ 식항
                    new_power = TermDict(1)
                    new_power[factor_calculated] = 1
                    ret_dict = ret_dict * (new_power ** power_calculated)

                else:
                    # 식항 ^ 식항
                    ret_dict = ret_dict * (factor_calculated ** power_calculated)

        return ret_dict, ret_code

    def get_str_without_coeff(self):
        if self.is_constant():
            return CONST_KEY
        ret_str = ""
        write_coeff = 0
        for i, (factor, _power) in enumerate(sorted(self.items())):
            if factor == COEFF_KEY:
                write_coeff = 1
                continue

            if isinstance(_power, float) and _power.is_integer():
                power = int(_power)
            else:
                power = _power

            if factor.has_one_term():
                str_factor = str(factor)
            else:
                str_factor = '(' + str(factor) + ')'

            if i - write_coeff > 0 and i - write_coeff < len(self.keys()):
                ret_str += "*"
            if factor == COEFF_KEY:
                ret_str += str(power)
            else:
                if isinstance(power, float) or isinstance(power, int):
                    if power == 1:
                        ret_str += str(factor)
                    elif power == -1:
                        ret_str += '1' + '/' + str_factor
                    elif power < 0:
                        ret_str += '1' + '/' + str_factor + '^' + str(-power)
                    else:
                        ret_str += str_factor + '^' + str(power)
                else:
                    if power.has_one_term():
                        ret_str += str_factor + '^' + str(power)
                    else:
                        ret_str += str_factor + '^(' + str(power) + ')'
            if ret_str[0] == '*':
                ret_str = ret_str[1:]
        return ret_str

    def differentiate_variable(self, variable_list):
        ret_code = SUCCESS_CODE
        if len(variable_list) == 1:
            var = Variable(variable_list[0])
            if self.is_constant():
                ret_dict = TermDict(0)
            else:
                ret_dict = ExprDict(0)
                for factor, power, in self.items():
                    diff_term = TermDict(self)
                    if factor == COEFF_KEY:
                        continue
                    elif isinstance(factor, Function):
                        if factor.has_variable(var):
                            if isinstance(power, int) or isinstance(power, float):
                                if power != 1:
                                    diff_term[COEFF_KEY] *= power
                                    diff_term[factor] = power - 1
                                else:
                                    diff_term.pop(factor, None)
                            elif power.is_constant():
                                if power.get_constant() != 1:
                                    diff_term[COEFF_KEY] *= power.get_constant()
                                    diff_term[factor] = power.get_constant() -1
                                else:
                                    diff_term.pop(factor, None)
                            else:
                                if power.has_variable(var):
                                    ret_code = "Var^VarDiffError"
                                    diff_term = TermDict(0)
                                else:
                                    diff_term = diff_term * power
                                    diff_term[factor] = power - 1
                            diff_func, func_code = factor.differentiate_varaible(variable_list)
                            if func_code != SUCCESS_CODE:
                                ret_code = func_code

                            diff_term = diff_term * diff_func

                    elif isinstance(factor, Variable):
                        if factor.has_variable(var):
                            if isinstance(power, int) or isinstance(power, float):
                                if power != 1:
                                    diff_term[COEFF_KEY] *= (power)
                                    diff_term[factor] = power - 1
                                else:
                                    diff_term.pop(factor, None)
                            elif power.is_constant():
                                if power.get_constant() != 1:
                                    diff_term[COEFF_KEY] *= (power.get_constant())
                                    diff_term[factor] = power.get_constant() - 1
                                else:
                                    diff_term.pop(factor, None)
                            else:
                                if power.has_variable(var):
                                    ret_code = "Var^VarDiffError"
                                    diff_term = TermDict(0)
                                else:
                                    diff_term = diff_term * power
                                    diff_term[factor] = power - 1
                        else:
                            continue
                    elif isinstance(factor, ConstDict):
                        pass
                    elif isinstance(factor, ExprDict):
                        if factor.has_variable(var):
                            diffed_factor, diff_code = factor.differentiate_variable(variable_list)
                            if diff_code != SUCCESS_CODE:
                                ret_code = diff_code

                            if isinstance(power, int) or isinstance(power, float):
                                if power != 1:
                                    diff_term[COEFF_KEY] *= power
                                    diff_term[factor] = power - 1
                                else:
                                    diff_term.pop(factor, None)
                            elif power.is_constant():
                                if power.get_constant() != 1:
                                    diff_term[COEFF_KEY] *= power.get_constant()
                                    diff_term[factor] = power.get_constant() - 1
                                else:
                                    diff_term.pop(factor, None)
                            else:
                                if power.has_variable():
                                    ret_code = "Var^VarDiffError"
                                    diff_term = TermDict(0)
                                else:
                                    diff_term = diff_term * power
                                    diff_term[factor] = power - 1
                            diff_term = diff_term * diffed_factor
                        else:
                            continue
                    else:
                        pass

                    ret_dict = ret_dict + diff_term

        elif len(variable_list) > 1:
            ret_code = "TooManyDiffVariableError"
            ret_dict = TermDict(self)
        else:
            ret_code = "NeedDiffVariableError"
            ret_dict = TermDict(self)
        return ret_dict, ret_code

    def has_variable(self, variable):
        """
        :param variable: Variable('x')
        :return: True or False
        """
        has = False
        for factor, power in self.items():
            if factor == COEFF_KEY:
                continue
            else:
                has = factor.has_variable(variable)
                if has:
                    break

                if isinstance(power, int) or isinstance(power, float):
                    continue
                has = power.has_variable(variable)
                if has:
                    break
        return has


class ConstDict(TermDict):
    def __init__(self, *args):
        super(ConstDict, self).__init__(*args)

    def __hash__(self):
        return hash("$b"+str(self.get_constant()))

    def has_variable(self, variable):
        return False


# x = Variable('x')
# y = Variable('y')
# z = Variable('z')
# td_x = TermDict(1)
# td_x[x] = 1
# td_y = TermDict(1)
# td_y[y] = 1
# e1 = TermDict(2) ** (td_x * td_y)
# e2 = TermDict(2) ** (3 * td_y)
# print(e1 * e2)

#
# x = Variable('x')
# y = Variable('y')
# z = Variable('z')
# td_x = TermDict(1)
# td_x[x] = 1
# td_y = TermDict(1)
# td_y[y] = 1
# td_z = TermDict(2)
# td_z[z] = 2
#
#
# print( td_z ** (td_x + td_y) )
# exit()
#
# x = Variable('x')
# y = Variable('y')
# z = Variable('z')
# td3 = TermDict(3)
# td_exp = TermDict(3)
# td_x = TermDict(1)
# td_x[x] = 1
# td_exp = td_exp ** td_x
#
# td_y = TermDict(1)
# td_y[y] = 1
# td_eyp = TermDict(3) ** td_y
#
# print(td_x + td_y)
# print(td_y + td_x)