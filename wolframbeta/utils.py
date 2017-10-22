from wolframbeta.config import *

# ERROR_STATE = "SUCCESS"


def raise_error(args):
    # raise Exception(args)
    # try:
    #     global ERROR_STATE
    #     ERROR_STATE.append(args)
    # except NameError:
    #     pass
    debugger(args)
    print(args)


def calculate_ops(a, ops, b):
    """
    a, b : 피연산자
    ops : 연산자
    """
    if ops == "+":
        return a + b
    elif ops == "-":
        return a - b
    elif ops == "*":
        return a * b
    elif ops == "/":
        return a / b
    elif ops == '^':
        return a ** b
    elif ops == '%':
        return a % b


def debugger(*s):
    # print(s)
    pass


def is_string_add(tok):
    if tok == '+' or tok == '-':
        return True
    else :
        return False


def is_string_multi(tok):
    if tok == '*' or tok == '/' or tok == '%':
        return True
    else:
        return False


def is_string_power(tok):
    if tok == '^':
        return True
    else:
        return False


def get_assignment_dict(assign):
    """
    :param assign: variable assignment statedment
    for example, "x=3, y=2"
    :return: dictionary object which contains "'x':3, 'y':2"
    """
    assign.replace(' ', '')

    assigns = assign.split(',')
    ret_dict = dict()
    for statement in assigns:
        state = statement.split('=')
        if state[1] in BUILTIN_CONSTANTS.keys():
            ret_dict[state[0]] = BUILTIN_CONSTANTS[state[1]]
        else:
            ret_dict[state[0]] = float(state[1])

    if len(ret_dict) == 0:
        return None
    else:
        return ret_dict


def is_assignment(statement):
    ret_code = SUCCESS_CODE
    if statement.find('=') != -1:
        statement.replace(' ', '')
        assigns = statement.split(',')
        for assign in assigns:
            if assign.find('=') == -1:
                # raise_error("assign ops(=) is not found")
                ret_code = "assign ops(=) is not found"
            sides = assign.split('=')
            if len(sides) != 2:
                # raise_error("too many assign ops(=)")
                ret_code = "too many assign ops(=)"
            if sides[1] in BUILTIN_CONSTANTS.keys():
                pass
            else:
                try:
                    float(sides[1])
                except ValueError:
                    # raise_error("There should be float value on the right side")
                    ret_code = "There should be float value on the right side"

            try:
                float(sides[0])
            except ValueError:
                pass
            else:
                # raise_error("There should not be float value on the left side")
                ret_code = "There should not be float value on the left side"
    else:
        ret_code = "There is no assignment"

    return ret_code


def get_var_range_assignment(statement):
    ret_dict = None
    var = None
    if statement.find('(') != -1:
        var = statement[:statement.find('(')]
        if statement.find(')') != -1:
            assignment_statement = statement[statement.find('(') + 1: statement.find(')')]
            if is_assignment(assignment_statement) == SUCCESS_CODE:
                assignment_dict = get_assignment_dict(assignment_statement)
                if "start" in assignment_dict.keys() and "end" in assignment_dict.keys():
                    ret_dict = assignment_dict
    return var, ret_dict


def strip_float(num):
    if isinstance(num, float) and num.is_integer():
        return int(num)
    else:
        return num
