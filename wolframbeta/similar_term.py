from wolframbeta.utils import *
from collections import OrderedDict

CONST_KEY = "$const"


class Variable(str):
    pass


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
            self.constant = 1

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
        ret_dict.constant *= -1
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

    def is_constant(self):
        if len(self.keys()) == 0:
            return True
        else:
            return False

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
                        ret_dict[other_key] = other[other_key]
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
            if self[key] != 1:
                ret_str += key + '^' + str(self[key])
            else:
                ret_str += key
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
                return len(self) < len(other)
            else:
                return str(self) < str(other)

    def __pow__(self, power, modulo=None):
        if isinstance(power, float):
            ret_dict = TermDict(self)
            ret_dict.constant = ret_dict.constant**power
            for key in ret_dict.keys():
                ret_dict[key] = ret_dict[key]*power
            return ret_dict

    def __rpow__(self, other):
        if isinstance(other, float):
            if self.is_constant():
                ret_dict = TermDict(self)
                ret_dict.constant = other ** ret_dict.constant
            else:
                # 2^(3*x) => (2^3) ^ x
                base = other ** self.constant
                ret_dict = TermDict()
                ret_dict[str(base)+'^'+str(self)] = 1
            return ret_dict


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
            self[CONST_KEY] = 0
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
                    """
                    TODO
                    key 간의 곱셈 구현 필요
                    """
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

        if ret_dict is None:
            raise_error("Unexpected type's STD mul ops encountered, {}".format(type(other)))

        return ret_dict

    # def __truediv__(self, other):

    def __rmul__(self, other):
        return self.__mul__(other)

    def __neg__(self):
        new_dict = SimilarTermsDict(self)
        for key in new_dict.keys():
            new_dict[key] = -new_dict[key]
        return new_dict

    def __truediv__(self, other):
        # TODO : 없는 변수를 나눌 때 1/x, 1/x^2..
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
                return None
            return ret_dict

        if isinstance(other, SimilarTermsDict):
            ret_dict = SimilarTermsDict(self)
            if other.is_constant():
                for key in ret_dict.keys():
                    ret_dict[key] /= other[CONST_KEY]
                return ret_dict
            elif other.has_one_term():
                raise_error("divide by variable terms is not provided")
                pass
            else:
                raise_error("divide by multiple terms is not provided")
                return None



    def __sub__(self, other):
        return self.__add__(-other)

    def __rsub__(self, other):
        return -self.__sub__(other)

    def is_constant(self):
        if len(self.keys()) == 1:
            return True
        else:
            return False

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

    def get_std_from_td(self, termdict):
        ret_std = SimilarTermsDict()
        ret_std[termdict] = termdict.constant
        return ret_std

    def get_one_term(self):
        """
        Use only when self has one term
        :return: key, item pair
        """
        for key, value in self.items():
            if key != CONST_KEY:
                return key, value
            elif key == CONST_KEY and value != 0:
                return key, value
        return CONST_KEY, 0

    def __rpow__(self, other):
        if isinstance(other, float):
            if self.is_constant():
                ret_dict = SimilarTermsDict(self)
                ret_dict[CONST_KEY] = other ** ret_dict.constant
            else:
                ret_dict = SimilarTermsDict()
                for key in self.keys():
                    term_dict = other ** key
                    ret_dict[term_dict] = term_dict.constant

            return ret_dict

    def __str__(self):
        ret_str = ""
        if self.is_constant():
            return str(self[CONST_KEY])
        else:
            for i, (term, const) in enumerate(reversed(sorted(self.items()))):
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
