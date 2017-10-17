from wolframbeta.utils import *

CONST_KEY = "$const"
COEFF_KEY = "$coeff"



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
                    self[CONST_KEY] = 0.0
            else:
                super(self.__class__, self).__init__(*args)
                if CONST_KEY not in self.keys():
                    self[CONST_KEY] = 0.0

    def __add__(self, other):
        ret_dict = None
        if isinstance(other, int) or isinstance(other, float):
            ret_dict = ExprDict(self)
            ret_dict[CONST_KEY] += other
            return ret_dict
        elif isinstance(other, TermDict):
            ret_dict = ExprDict(self)
            if other in ret_dict.keys():
                ret_dict[other] += other.get_coefficient()
            else:
                ret_dict[other] = other.get_coefficient()
            return ret_dict


class TermDict(dict):
    def __init__(self, *args):
        if isinstance(*args, float) or isinstance(*args, int):
            super(self.__class__, self).__init__()
            self[COEFF_KEY] = args[0]
        else:
            super(self.__class__, self).__init__(*args)
            if len(args) > 0 and isinstance(args[0], TermDict):
                self[COEFF_KEY] = args[0][COEFF_KEY]
            else:
                self[COEFF_KEY] = 1.0

    def __add__(self, other):

        ret_dict = None
        if isinstance(other, ExprDict):
            return other + self
        elif isinstance(other, TermDict):
            if str(self) == str(other):
                if self[COEFF_KEY] + other[COEFF_KEY] == 0:
                    ret_dict = TermDict()
                else:
                    ret_dict = TermDict(self)
                    ret_dict[COEFF_KEY] += other[COEFF_KEY]
            else:
                ret_dict = ExprDict(other)
                ret_dict = ret_dict + self
        elif isinstance(other, float) or isinstance(other, int):
            ret_dict = ExprDict(other)
            ret_dict = ret_dict + self

        if ret_dict is None:
            raise_error("Error : TermDict + unknown")
            ret_dict = TermDict()

        return ret_dict

    def __radd__(self, other):
        return self + other

    def __sub__(self, other):
        return self - other

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
            return ExprDict * self

        elif isinstance(other, float) or isinstance(other, int):
            ret_dict = TermDict(self)
            ret_dict[COEFF_KEY] *= float(other)
            return ret_dict

        else:
            raise_error("Not implemented : termdict * unknown")

    def __rmul__(self, other):
        pass

    def __truediv__(self, other):
        if isinstance(other, TermDict):
            ret_dict = TermDict(self)
            ret_dict[COEFF_KEY] /= other.get_coefficient()
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
            return other.__rtruediv__(self)
        else:
            raise_error("Not implemented : TermDict / Unknown")

    def __rtruediv__(self, other):
        if isinstance(other, float) or isinstance(other, int):
            ret_dict = TermDict(self)
            for factor, power in self.items():
                if factor == COEFF_KEY:
                    ret_dict[COEFF_KEY] = 1/ret_dict[COEFF_KEY]
                else:
                    ret_dict[factor] = -ret_dict[factor]
            return ret_dict
        else:
            raise_error("Not implemented : unknown / termdict")

    def __pow__(self, power, modulo=None):
        if isinstance(power, float):
            ret_dict = TermDict(self)
            for key in ret_dict.keys():
                ret_dict[key] *= power
            return ret_dict
        elif isinstance(power, int):
            return self ** float(power)
        elif isinstance(power, TermDict):
            if power.is_constant():
                return self ** power.get_coefficient()

            pass
        elif isinstance(power, ExprDict):
            pass

    def __rpow__(self, other):
        pass

    def __neg__(self):
        ret_dict = TermDict(self)
        ret_dict[COEFF_KEY] *= -1.0
        return ret_dict

    def __str__(self):
        if self.is_constant():
            if isinstance(self[COEFF_KEY], float) and self[COEFF_KEY].is_integer():
                return str(int(self[COEFF_KEY]))
            else:
                return str(self[COEFF_KEY])
        ret_str = ""
        for i, (factor, _power) in enumerate(sorted(self.items())):
            if isinstance(_power, float) and _power.is_integer():
                power = int(_power)
            else:
                power = _power

            if i > 0 and i < len(self.keys()):
                ret_str += "*"
            if factor == COEFF_KEY:
                ret_str += str(power)
            else:
                if isinstance(power, float) or isinstance(power, int):
                    if power == 1:
                        ret_str += str(factor)
                    elif power == -1:
                        ret_str += '1' + '/(' + str(factor) + ')'
                    else:
                        ret_str += str(factor) + '^' + str(power)
                else:
                    ret_str += str(factor) + '^' + str(power)
            if ret_str[0] == '*':
                ret_str = ret_str[1:]
        return ret_str

    def __lt__(self, other):
        if isinstance(other, str):
            return False
        elif isinstance(other, TermDict):
            if len(self) != len(other):
                return len(self) > len(other)
            else:
                self_dim = 0
                other_dim = 0
                for factor, power in other.items():
                    other_dim = other_dim + power
                for factor, power in self.items():
                    self_dim = self_dim + power

                if (isinstance(self_dim, float) or isinstance(self_dim, int)) and (
                    isinstance(other_dim, float) or isinstance(other_dim, int)):
                    return self_dim < other_dim
                else:
                    return str(self) > str(other)

    def __hash__(self):
        return hash(self.get_str_without_coeff())

    def is_constant(self):
        return len(self) == 1

    def get_coefficient(self):
        return self[COEFF_KEY]

    def calculate_variable(self, variable_dict):
        pass

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



            if i-write_coeff > 0 and i-write_coeff < len(self.keys()):
                ret_str += "*"
            if factor == COEFF_KEY:
                ret_str += str(power)
            else:
                if isinstance(power, float) or isinstance(power, int):
                    if power == 1:
                        ret_str += str(factor)
                    elif power == -1:
                        ret_str += '1' + '/(' + str(factor) + ')'
                    else:
                        ret_str += str(factor) + '^' + str(power)
                else:
                    ret_str += str(factor) + '^' + str(power)
            if ret_str[0] == '*':
                ret_str = ret_str[1:]
        return ret_str

a = TermDict(2)
a['x'] = 1
ex = ExprDict(a)
print(ex)