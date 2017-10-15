def raise_error(*args):
    pass


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
        if statement.find('=') == -1:
            raise_error("Invalid assignment")
        state = statement.split(',')
        ret_dict[state[0]] = float(state[1])

    if len(ret_dict) == 0:
        return None
    else:
        return ret_dict