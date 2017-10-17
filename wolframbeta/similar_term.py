from wolframbeta.utils import *

CONST_KEY = "$const"


class Variable(str):
    pass


class Function(str):
    def __new__(cls, value, *args, **kwargs):
        return str.__new__(cls, value)

    def __init__(self, value, name, param_list):
        self.name = name
        self.param_list = param_list


class PowerOfFloat(str):
    """
    float^term 꼴
    """
    def __new__(cls, value, *args, **kwargs):
        return str.__new__(cls, value)

    def __init__(self, value, base_constant=None, exponent_term=None):
        self.base_constant = base_constant
        self.exponent_term = exponent_term

    def calculate_value(self, variable_dict):
        """
        :param variable_dict:
        :return: PowerOfFloat object
        """
        pass


def get_power_of_float(base_float, exponent_term):
    """
    :param base_float:
    :param exponent_term: TermDict Object
    :return:
    POF object str=base^exponent
    """
    new_term = base_float ** exponent_term
    ret_pof = PowerOfFloat(str(new_term), base_float, exponent_term)
    return ret_pof


class TermDict(dict):
    """
    단일항 dictionary
    key : factor
    value : power
    """
    def __init__(self, *args):
        super(self.__class__, self).__init__(*args)
        if len(args) > 0 and isinstance(args[0], TermDict):
            self.constant = args[0].constant
        else:
            self.constant = 1.0

    def __mul__(self, other):
        if isinstance(other, TermDict):
            ret_dict = TermDict(self)
            const = other.constant
            ret_dict.constant *= const
            if not other.is_constant():
                for other_key in other.keys():
                    if other_key in ret_dict.keys():
                        ret_dict[other_key] += other[other_key]
                        if ret_dict[other_key] == 0:
                            ret_dict.pop(other_key, None)
                    else:
                        ret_dict[other_key] = other[other_key]
            return ret_dict
        elif isinstance(other, SimilarTermsDict):
            return other * self

    def __add__(self, other):
        if isinstance(other, SimilarTermsDict):
            return other + self
        elif isinstance(other, TermDict):
            # Addition between two term
            if str(self) == str(other):
                if self.constant + other.constant == 0:
                    ret_dict = TermDict()
                else:
                    ret_dict = TermDict(self)
                    ret_dict.constant += other.constant

            else:
                ret_dict = SimilarTermsDict()
                ret_dict[self] = self.constant
                ret_dict[other] = other.constant

            return ret_dict

    def __neg__(self):
        ret_dict = TermDict(self)
        ret_dict.constant *= -1.0
        return ret_dict

    def __sub__(self, other):
        if isinstance(other, SimilarTermsDict):
            return self + (-other)
        elif isinstance(other, TermDict):
            if str(self) == str(other):
                if self.constant - other.constant == 0:
                    ret_dict = TermDict()
                else:
                    ret_dict = TermDict(self)
                    ret_dict.constant -= other.constant
            else:
                ret_dict = SimilarTermsDict()
                ret_dict[self] = self.constant
                ret_dict[other] = -other.constant
            return ret_dict

    def __pow__(self, power, modulo=None):
        if isinstance(power, float):
            ret_dict = TermDict(self)
            ret_dict.constant = ret_dict.constant ** power
            for key in ret_dict.keys():
                ret_dict[key] *= power
            return ret_dict
        elif isinstance(power, int):
            return self ** float(power)

    def __rpow__(self, other):
        if isinstance(other, float):
            if self.is_constant():
                ret_dict = TermDict(self)
                ret_dict.constant = other ** ret_dict.constant
            else:
                # 2^(3*x) => (2^3) ^ x
                base = strip_float(other ** self.constant)
                ret_dict = TermDict()
                if len(self) == 1:
                    ret_dict[str(base)+'^'+str(self)] = 1
                else:
                    ret_dict[str(base) + '^(' + str(self) + ')'] = 1
            return ret_dict
        elif isinstance(other, int):
            return float(other) ** self

    def is_constant(self):
        if len(self.keys()) == 0:
            return True
        else:
            return False

    def get_constant(self):
        return self.constant

    def calculate_variable(self, variable_dict):
        """
        :param variable_dict:
        :return: TermDict object that is self's calculated value
        """
        ret_dict = TermDict(self)
        for var, power in self.items():
            if isinstance(var, SimilarTermsDict):
                new_simdict = var.calculate_variable(variable_dict)

                if new_simdict.is_constant():
                    ret_dict.constant *= new_simdict.get_constant() ** power
                    ret_dict.pop(var, None)
                elif new_simdict.has_one_term():


                ret_dict[new_simdict]

            if var in variable_dict.keys():
                ret_dict.constant *= variable_dict[var] ** power
                ret_dict.pop(var, None)

        return ret_dict

    def __truediv__(self, other):
        if isinstance(other, TermDict):
            ret_dict = TermDict(self)
            const = other.constant
            ret_dict.constant /= const
            if not other.is_constant():
                for other_key in other.keys():
                    if other_key in ret_dict.keys():
                        ret_dict[other_key] -= other[other_key]
                        if ret_dict[other_key] == 0:
                            ret_dict.pop(other_key, None)
                    else:
                        ret_dict[other_key] = -other[other_key]
            return ret_dict

    def __hash__(self):
        return hash(str(self))

    def __eq__(self, other):
        if isinstance(other, str):
            return str(self) == other
        return super(self.__class__, self).__eq__(other)

    def __ne__(self, other):
        return not self.__eq__(other)

    def __str__(self):
        if self.is_constant():
            return CONST_KEY
        ret_str = ""
        for i, key in enumerate(sorted(self.keys())):
            power_raw = self[key]
            if isinstance(power_raw, float):
                if power_raw.is_integer():
                    power = int(power_raw)
                else:
                    power = power_raw
            else:
                power = power_raw
            if power == 1:
                ret_str += str(key)
            elif power == -1:
                if key.has_one_term():
                    ret_str += '1' + '/'+str(key)
                else:
                    ret_str += '1' + '/(' + str(key) + ')'
            else:
                ret_str += str(key) + '^' + str(power)

            if i == len(self.keys()) - 1:
                pass
            else:
                ret_str += '*'
        return ret_str

    def __lt__(self, other):
        if isinstance(other, str):
            # const key
            return False
        elif isinstance(other, TermDict):
            if len(self) != len(other):
                return len(self) > len(other)
            else:
                self_dim = 0
                other_dim = 0
                for term, const in other.items():
                    other_dim += const
                for term, const in self.items():
                    self_dim += const

                if self_dim == other_dim:
                    return str(self) > str(other)
                else:
                    return self_dim < other_dim


class SimilarTermsDict(dict):
    """
    동류항 dictionary
    key : 동류항의 string form
    value : 동류항에 곱해지는 상수
    key = CONST_KEY 인 경우는 상수항
    dictionary간 덧셈 := 동류항끼리의 합.
    곱셈 := 분배법칙에 의한 계산 후 동류항 정리.

    dictionary - 상수간 덧셈 : 상수항에 더함
    dictionary - 상수간 곱셈 : dictionary 각 모든 value에 곱함
    """
    def __init__(self, *args):
        super(self.__class__, self).__init__(*args)
        if CONST_KEY not in self.keys():
            self[CONST_KEY] = 0.0
        # if len(args) > 0 and isinstance(args[0], TermDict):
        #     self[args[0]] = args[0].constant

    def __add__(self, other):
        ret_dict = SimilarTermsDict(self)
        if isinstance(other, SimilarTermsDict):
            for other_key in other.keys():
                if other_key in ret_dict.keys():
                    ret_dict[other_key] += other[other_key]
                    if ret_dict[other_key] == 0 and other_key != CONST_KEY:
                        ret_dict.pop(other_key, None)
                else:
                    ret_dict[other_key] = other[other_key]
        
        elif isinstance(other, float):
            ret_dict[CONST_KEY] += other

        elif isinstance(other, TermDict):
            new_dict = self.get_std_from_td(other)
            ret_dict = self - new_dict
            pass
        else:
            raise_error("Unexpected type's STD add ops encountered, {}".format(type(other)))
        return ret_dict

    def __radd__(self, other):
        return self.__add__(other)

    def __mul__(self, other):
        ret_dict = None
        if isinstance(other, SimilarTermsDict):
            ret_dict = SimilarTermsDict()
            for key in self.keys():
                for other_key in other.keys():
                    if key == CONST_KEY:
                        new_key = other_key
                    elif other_key == CONST_KEY:
                        new_key = key
                    else:
                        new_key = key * other_key

                    if new_key in ret_dict.keys():
                        ret_dict[new_key] += other[other_key] * self[key]
                    else:
                        ret_dict[new_key] = other[other_key] * self[key]

                    if ret_dict[new_key] == 0 and new_key != CONST_KEY:
                        ret_dict.pop(new_key, None)

        elif isinstance(other, float):
            if other == 0:
                ret_dict = SimilarTermsDict()
            else:
                ret_dict = SimilarTermsDict(self)
                for key in ret_dict.keys():
                    ret_dict[key] *= other

        elif isinstance(other, TermDict):
            new_dict = self.get_std_from_td(other)
            return self * new_dict

        elif isinstance(other, int):
            return self * float(other)

        if ret_dict is None:
            raise_error("Unexpected type's STD mul ops encountered, {}".format(type(other)))

        return ret_dict

    def __rmul__(self, other):
        return self.__mul__(other)

    def __neg__(self):
        new_dict = SimilarTermsDict(self)
        for key in new_dict.keys():
            new_dict[key] = -new_dict[key]
        return new_dict

    def __truediv__(self, other):
        """
        :param other: TermDict, One Term
        :return: divided SimtermsDict
        """
        if isinstance(other, TermDict):
            ret_dict = SimilarTermsDict(self)
            if other.is_constant():
                for key in ret_dict.keys():
                    ret_dict[key] /= other.constant
            else:
                raise_error("divide by non-constant is not provided {}".format(str(other)))

            return ret_dict

        if isinstance(other, SimilarTermsDict):

            if other.is_constant():
                ret_dict = SimilarTermsDict(self)
                for key in ret_dict.keys():
                    ret_dict[key] /= other[CONST_KEY]
                return ret_dict
            else:


                if self.is_constant():
                    term_dict = TermDict()
                    term_dict.constant = self.get_constant()
                    term_dict[other] = -1
                    ret_dict = SimilarTermsDict()
                    ret_dict[term_dict] = term_dict.constant
                    return ret_dict
                else:
                    term_dict = TermDict()
                    term_dict.constant = 1/other.get_constant()
                    term_dict[other] = -1
                    diver_dict = SimilarTermsDict()
                    diver_dict[term_dict] = term_dict.constant
                    return self * diver_dict

    def __sub__(self, other):
        return self.__add__(-other)

    def __rsub__(self, other):
        return -self.__sub__(other)

    def is_constant(self):
        if len(self.keys()) == 1:
            return True
        else:
            return False

    def get_constant(self):
        return self[CONST_KEY]

    def has_one_term(self):
        if len(self) == 2:
            if self[CONST_KEY] == 0:
                return True
            else:
                return False
        elif len(self) == 1:
            return True
        else:
            return False

    def calculate_variable(self, variable_dict):
        ret_dict = SimilarTermsDict(self)
        for termdict, coeff in self.items():
            if isinstance(termdict, TermDict):
                new_termdict = termdict.calculate_variable(variable_dict)
                if new_termdict.is_constant():
                    ret_dict[CONST_KEY] += new_termdict.constant
                elif new_termdict in self.keys():
                    ret_dict[new_termdict] += new_termdict.constant
                else:
                    ret_dict[new_termdict] = new_termdict.constant
            else: # termdict == CONST_KEY
                pass
        return ret_dict

    def get_std_from_td(self, termdict):
        ret_std = SimilarTermsDict()
        ret_std[termdict] = termdict.constant
        return ret_std

    def get_one_term(self):
        """
        Use only when self has one term
        :return: key(TermDict), item(Coefficient) pair
        """
        for key, value in self.items():
            if key != CONST_KEY:
                return key, value
            elif key == CONST_KEY and value != 0:
                return key, value
        return CONST_KEY, 0.0

    def __rpow__(self, other):
        if isinstance(other, float):
            if self.is_constant():
                # (number)^(number)
                ret_dict = SimilarTermsDict(self)
                ret_dict[CONST_KEY] = other ** self[CONST_KEY]
            else:
                # (number)^(expression)
                key_term = TermDict()

                key_coeff = 1
                for term, term_coeff in self.items():
                    if term == CONST_KEY:
                        key_coeff = other ** self.get_constant()
                    else:
                        key_base = other ** term_coeff
                        key_power_of_float = get_power_of_float(key_base, term)
                        key_term[key_power_of_float] = 1

                ret_dict = SimilarTermsDict()
                ret_dict[key_term] = key_coeff

            return ret_dict

    def __simterm_pow__(self, simterm, power):
        if power < 0:
            raise_error("__simterm_pow__ :: powered by negative")
            return 1
        if power == 0:
            ret_dict = SimilarTermsDict()
            ret_dict[CONST_KEY] = 1.0
            return ret_dict
        elif power == 1:
            return simterm
        elif power % 2 == 0:
            return self.__simterm_pow__(simterm * simterm, power // 2)
        elif power % 2 == 1:
            return simterm * self.__simterm_pow__(simterm * simterm, (power - 1) // 2)

    def __pow__(self, power, modulo=None):
        if isinstance(power, float):
            if power.is_integer() and power >= 0:
                return self.__simterm_pow__(self, power)
            else:  # power != 0:
                if self.is_constant():
                    ret_dict = SimilarTermsDict()
                    ret_dict = ret_dict + self.get_constant() ** power
                    return ret_dict
                elif self.has_one_term():
                    term, coeff = self.get_one_term()
                    ret_dict = SimilarTermsDict()
                    ret_dict[term ** power] = coeff ** power
                    return ret_dict
                else:
                    raise_error("(expr, term) ^ (expr, term) is not supported ")
                    ret_dict = SimilarTermsDict()
                    return ret_dict

        elif isinstance(power, int):
            if power >= 0:
                return self.__simterm_pow__(self, power)
        elif isinstance(power, SimilarTermsDict):

            if self.is_constant():
                # (number) ^ factor
                base = self.get_constant()
                ret_dict = base ** power
                return ret_dict
            elif self.has_one_term():
                ret_dict = SimilarTermsDict()
                if power.is_constant():
                    exponent = power.get_constant()
                    _key, coeff = self.get_one_term()
                    key = TermDict(_key)
                    term_dict = key ** exponent
                    ret_dict[term_dict] = coeff ** exponent
                    return ret_dict
                else:
                    raise_error("(term)^(expr, term) is not supported form")
                    ret_dict = SimilarTermsDict(self)
                    return ret_dict
            else:
                if power.is_constant():
                    exponent = power.get_constant()
                    if exponent < 0:
                        raise_error("divide by expression(or power of negative constant) is not supported")
                        ret_dict = SimilarTermsDict(self)
                        return ret_dict
                    elif isinstance(exponent, float) and exponent.is_integer():
                        return self ** exponent
                    elif isinstance(exponent, int):
                        return self ** exponent
                    else:
                        # (expr) ^ (float)
                        raise_error("(expr)^(floating point number) is not supported.")
                        ret_dict = SimilarTermsDict(self)
                        return ret_dict
                else:
                    raise_error("(expr)^(expr, term) is not supported.")
                    ret_dict = SimilarTermsDict(self)
                    return ret_dict

    def __str__(self):
        ret_str = ""
        if self.is_constant():
            if self[CONST_KEY].is_integer():
                return str(int(self[CONST_KEY]))
            else:
                return str(self[CONST_KEY])
        else:
            for i, (term, const_raw) in enumerate(reversed(sorted(self.items()))):
                if const_raw.is_integer():
                    const = int(const_raw)
                else:
                    const = const_raw
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

    def __hash__(self):
        return hash(str(self))

    def __lt__(self, other):
        return str(self) > str(other)
        if isinstance(other, str):
            # const key
            return False
        elif isinstance(other, TermDict):
            if len(self) != len(other):
                return len(self) > len(other)
            else:
                self_dim = 0
                other_dim = 0
                for term, const in other.items():
                    other_dim += const
                for term, const in self.items():
                    self_dim += const

                if self_dim == other_dim:
                    return str(self) > str(other)
                else:
                    return self_dim < other_dim