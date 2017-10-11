from wolframbeta.utils import *
from collections import OrderedDict

CONST_KEY = "$const"


class Variable(str):
    def __init__(self, *args):
        super(self.__class__, self).__init__(*args)


class TermDict(dict):
    """

    """
    def __init__(self, *args):
        super(self.__class__, self).__init__(*args)

    def get_term_str(self):
        """
        :return: term string
        """
        pass


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

    def __add__(self, other):
        ret_dict = SimilarTermsDict(self)
        if isinstance(other, SimilarTermsDict):
            for other_key in other.keys():
                if other_key in ret_dict.keys():
                    ret_dict[other_key] += other[other_key]
                    if ret_dict[other_key] == 0:
                        ret_dict.pop(other_key, None)
                else:
                    ret_dict[other_key] = other[other_key]
        
        elif isinstance(other, float):
            if CONST_KEY in ret_dict.keys():
                ret_dict[CONST_KEY] += other
                if ret_dict[CONST_KEY] == 0:
                    ret_dict.pop(CONST_KEY, None)
            else:
                ret_dict[CONST_KEY] = other

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

                    if ret_dict[new_key] == 0:
                        ret_dict.pop(new_key, None)

        elif isinstance(other, float):
            if other == 0:
                ret_dict = SimilarTermsDict()
            else:
                ret_dict = SimilarTermsDict(self)
                for key in ret_dict.keys():
                    ret_dict[key] *= other

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

    def __sub__(self, other):
        return self.__add__(-other)

    def __rsub__(self, other):
        return -self.__sub__(other)


