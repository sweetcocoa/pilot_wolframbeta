import numpy as np

from functools import partial

from bokeh.io import curdoc
from bokeh.layouts import layout, row, column
from bokeh.models import ColumnDataSource, \
    Plot, ColumnDataSource, \
    DataRange1d, LinearAxis, \
    Grid, HoverTool, WheelZoomTool, ResetTool, SaveTool, \
    BoxZoomTool

from bokeh.models.glyphs import Line, Circle, MultiLine
from bokeh.models import TextInput, DataTable, TableColumn, Button, Label, Text

from wolframbeta.nonterminals import Expr
from wolframbeta.terminals import ExprDict
from wolframbeta.utils import *
from wolframbeta.config import *
from wolframui.uiconfig import *
from wolframui.assign import *


def calculate_expr(expr_dict, **kwargs):
    """
    :param expr_dict: dict object which is calculated by expr
    :param var: str variable.
    :param domain_range:
    :param output_range:
    :return: domain x values, corresponding y values, return code
    """

    var = kwargs['var']
    domain_start = kwargs['domain_range']['start']
    domain_end = kwargs['domain_range']['end']

    output_start = kwargs['output_range']['start']
    output_end = kwargs['output_range']['end']

    if domain_end < domain_start:
        domain_start, domain_end = domain_end, domain_start

    if output_start != 'auto' and output_end != 'auto':
        if output_end < output_start:
            output_start, output_end = output_end, output_start

    definition = np.linspace(domain_start, domain_end, 1001)

    domains = list()
    ys = list()

    domain = list()
    y = list()

    ret_code = SUCCESS_CODE

    for x in definition:
        y_val, y_code = expr_dict.calculate_variable({var: x})
        if y_code == SUCCESS_CODE and y_val.is_constant():
            y_val = y_val.get_constant()
            append = False
            if output_start == 'auto' and output_end == 'auto':
                append = True
            elif output_start == 'auto' and output_end != 'auto' and y_val <= output_end:
                append = True
            elif output_start != 'auto' and y_val >= output_start and output_end == 'auto':
                append = True
            elif output_start != 'auto' and output_end != 'auto' and output_start < y_val < output_end:
                append = True

            if append:
                y.append(y_val)
                domain.append(x)
            elif len(domain) > 0:
                domains.append(domain)
                domain = list()
                ys.append(y)
                y = list()

        else:
            if y_code != SUCCESS_CODE:
                ret_code = y_code

            if not y_val.is_constant():
                ret_code = "Not Constant Result"

            if len(domain) > 0:
                domains.append(domain)
                domain = list()
                ys.append(y)
                y = list()

    if len(domain) > 0:
        domains.append(domain)
        ys.append(y)

    return domains, ys, ret_code


def make_data_func(expr_dict=None, var='x', domain_range=None, output_range=None):
    if expr_dict is None:
        expr_dict = ExprDict(0)
    if domain_range is None:
        domain_range = {'start': 0.1, 'end': 5}
    if output_range is None:
        output_range = {'start': 'auto', 'end': 'auto'}

    x, y, ret_code = calculate_expr(expr_dict, var=var, domain_range=domain_range, output_range=output_range)

    ret_dict = dict(
        domain=x,
        range=y,
    )
    return ret_dict, ret_code


def calculate_handler(**kwargs):
    """
    :param plot_list: list(plot)
    :param source_list: list(plot source)
    :param result_list: list(textinput which contains result expr)
    :param expr: str(expr text's value)
    :param assign_value: str(assign text's value)
    :param var_range: str(variable range)
    :param function_range:
    :param derivative_range:
    :return:
    """

    plot_list = kwargs['plot_list']
    source_list = kwargs['source_list']
    result_list = kwargs['result_list']
    expr = kwargs['expr']
    assign_value = kwargs['assign_value']
    var_range = kwargs['var_range']
    function_range = kwargs['function_range']
    derivative_range = kwargs['derivative_range']

    expr = expr.value
    assign_value = assign_value.value
    var_range = var_range.value
    function_range = function_range.value
    derivative_range = derivative_range.value

    assign_dict, assign_value = get_assignment_dict(assign_value)
    var, domain_range = get_var_range_assignment(var_range)
    function_range = get_range_assignment(function_range)
    derivative_range = get_range_assignment(derivative_range)

    expr = Expr(expr)
    expr.parse()
    expr.calculate()
    source_list[0].data, ret_func = make_data_func(expr_dict=expr.dict, var=var, domain_range=domain_range, output_range=function_range)

    diff_dict, diff_code = expr.dict.differentiate_variable([var])
    source_list[1].data, ret_diff = make_data_func(expr_dict=diff_dict, var=var, domain_range=domain_range, output_range=derivative_range)

    # Setting Plot's title
    if len(assign_dict) > 0:
        expr_assign, expr_assign_code = expr.dict.calculate_variable(assign_dict)
        text = str(expr_assign) + " at (" + str(assign_value) + ")"
        if expr_assign_code != SUCCESS_CODE:
            text += "Error : " + expr_assign_code
        plot_list[0].title.text = text

        diff_assign, diff_assign_code = diff_dict.calculate_variable(assign_dict)
        text = str(diff_assign) + " at (" + str(assign_value) + ")"
        if diff_assign_code != SUCCESS_CODE:
            text += "Error : " + diff_assign_code
        plot_list[1].title.text = text
    else:
        plot_list[0].title.text = "Graph"
        plot_list[1].title.text = "Graph"

    # Setting Plot's label
    if ret_func != SUCCESS_CODE:
        result_list[0].value = str(expr.dict)
    else:
        result_list[0].value = str(expr.dict)

    if ret_diff != SUCCESS_CODE:
        result_list[1].value = str(diff_dict)
    else:
        result_list[1].value = str(diff_dict)


def make_plot(source, color):
    xdr = DataRange1d()
    ydr = DataRange1d()

    plot = Plot(x_range=xdr, y_range=ydr, plot_width=FIG_WIDTH, plot_height=FIG_HEIGHT)
    plot.title.text = "Graph"

    # line = Line(x="domain", y="range", line_color=color)
    # plot.add_glyph(source, line)

    line = MultiLine(xs="domain", ys="range", line_color=color)
    plot.add_glyph(source, line)

    # circle = Circle(x="domain", y="range", fill_color=color, size=2)
    # plot.add_glyph(source, circle)

    xaxis = LinearAxis()
    plot.add_layout(xaxis, 'below')

    yaxis = LinearAxis()
    plot.add_layout(yaxis, 'left')

    plot.add_layout(Grid(dimension=0, ticker=xaxis.ticker))
    plot.add_layout(Grid(dimension=1, ticker=yaxis.ticker))

    # plot.add_tools(WheelZoomTool())
    plot.add_tools(ResetTool())
    plot.add_tools(SaveTool())
    # plot.add_tools(BoxZoomTool())

    return plot, source


def make_layout():

    sample_expr = Expr("sin(x)")
    sample_expr.parse()
    sample_expr.calculate()
    sample_data, ret_code = make_data_func(sample_expr.dict)
    source_func = ColumnDataSource(sample_data)
    source_diff = ColumnDataSource(sample_data)

    plot_func, source_func = make_plot(source_func, 'Blue')
    plot_diff, source_diff = make_plot(source_diff, 'Black')

    str_expr = ""
    textinput_expr = TextInput(title="Expression", value="", placeholder="sin(x)^2 + x^2 * y", sizing_mode='scale_width')

    str_assign_value = ""
    textinput_assign_value = TextInput(title="assign_value", value=str_assign_value, placeholder="x=3, y=2")

    str_domain_range = ""
    textinput_domain_range = TextInput(title="domain range", value=str_domain_range, placeholder="x(0.1, 5)")

    textinput_result_func = TextInput(title="Calculated Function", value="", disabled=True, width=FIG_WIDTH*2)
    textinput_result_diff = TextInput(title="Differentiated Function", value="", disabled=True, width=FIG_WIDTH*2)

    textinput_function_range = TextInput(title="function's output range", value="(auto, auto)", placeholder="(auto, auto)")
    textinput_derivative_range = TextInput(title="derivative's output range", value="(auto, auto)", placeholder="(auto, auto)")

    button = Button(label="Calculate", button_type="success", width=FIG_WIDTH)

    result_list = [textinput_result_func, textinput_result_diff]
    plot_list = [plot_func, plot_diff]
    source_list = [source_func, source_diff]

    button.on_click(partial(calculate_handler,
                            plot_list=plot_list,
                            source_list=source_list,
                            result_list=result_list,
                            expr=textinput_expr,
                            assign_value=textinput_assign_value,
                            var_range=textinput_domain_range,
                            function_range=textinput_function_range,
                            derivative_range=textinput_derivative_range,
                            )
                    )

    lay = layout([
        [textinput_expr, textinput_assign_value, textinput_domain_range],
        [textinput_function_range, textinput_derivative_range],
        [button],
        [textinput_result_func, textinput_result_diff],
        [plot_func, plot_diff],
    ], sizing_mode='scale_width')
    return lay


lay = make_layout()
document = curdoc()
document.add_root(lay)
