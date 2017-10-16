ERROR_STATE = "SUCCESS"


def raise_error(args):
    global ERROR_STATE
    ERROR_STATE = args
    debugger(args)


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


def get_term_str_expression(const, variables):
    """
    :param const: constant float in front of similar term
    :param variables: variables which compose the similar term
    :return: string expression, which could be used for initialization of Tokenmanager.
    """
    str_expression = str(const)
    for variable in variables.keys():
        exponent = variables[variable]
        if exponent == 1:
            str_expression += "*" + variable
        elif exponent == -1:
            str_expression += '/' + variable
        else:
            str_expression += "*" + variable + "^" + str(exponent)
    return str_expression


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
        ret_dict[state[0]] = float(state[1])

    if len(ret_dict) == 0:
        return None
    else:
        return ret_dict


def is_assignment(statement):
    if statement.find('=') != -1:
        statement.replace(' ', '')
        assigns = statement.split(',')
        for assign in assigns:
            if assign.find('=') == -1:
                raise_error("assign ops(=) is not found")
                return False
            sides = assign.split('=')
            if len(sides) != 2:
                raise_error("too many assign ops(=)")
                return False
            try:
                float(sides[1])
            except ValueError:
                raise_error("There should be float value on the right side")
                return False

            try:
                float(sides[0])
            except ValueError:
                pass
            else:
                raise_error("There should not be float value on the left side")
                return False
        return True
    else:
        return False
