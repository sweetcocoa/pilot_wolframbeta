from wolframbeta.config import *
from wolframbeta.nonterminals import Expr


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
        if len(state) == 2:
            expr = Expr(state[1])
            expr.parse()
            expr.calculate()
            if expr.dict.is_constant():
                ret_dict[state[0]] = expr.dict.get_constant()

    if len(ret_dict) == 0:
        return dict({})
    else:
        return ret_dict


def get_var_range_assignment(statement):
    """
    :param statement: x(0.1, 2*pi)
    :return: x, dict({'start':0.1, 'end':6.28})
    """
    statement = statement.replace(' ', '')
    ret_dict = None
    var = None

    if statement.find('(') != -1:
        var = statement[:statement.find('(')]
        if statement.find(')') != -1:
            assignment_statement = statement[statement.find('(') + 1: statement.find(')')]
            if assignment_statement.find(',') != -1:
                assignments = assignment_statement.split(',')
                if len(assignments) == 2:
                    start_expr = Expr(assignments[0])
                    end_expr = Expr(assignments[1])
                    start_expr.parse()
                    start_expr.calculate()
                    end_expr.parse()
                    end_expr.calculate()
                    if start_expr.dict.is_constant() and end_expr.dict.is_constant():
                        ret_dict = dict({'start': start_expr.dict.get_constant(),
                                        'end': end_expr.dict.get_constant()})
    return var, ret_dict
