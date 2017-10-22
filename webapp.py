import numpy as np

from functools import partial

from bokeh.io import curdoc
from bokeh.layouts import row, widgetbox, column, layout
from bokeh.models import ColumnDataSource, \
    Plot, ColumnDataSource, \
    DataRange1d, LinearAxis, \
    DatetimeAxis, Grid, HoverTool, WheelZoomTool, ResetTool, SaveTool
from bokeh.models.glyphs import Line, Circle
from bokeh.models import TextInput, DataTable, TableColumn, Button
from bokeh.plotting import figure

from wolframbeta.nonterminals import Expr
from wolframbeta.terminals import ExprDict
from wolframbeta.utils import *
from wolframbeta.config import *
from wolframui.uiconfig import *


def calculate_expr(expr_dict, var='x', domain_start=0.1, domain_end=5):
    """
    :param expr_dict: dict object which is calculated by expr
    :param var: str variable.
    :param domain_start:
    :param domain_end:
    :return: range, y values, return code
    """
    if domain_end < domain_start:
        domain_start, domain_end = domain_end, domain_start

    definition = np.linspace(domain_start, domain_end, 100)
    ret_code = SUCCESS_CODE
    y = list()
    for x in definition:
        y_val, y_code = expr_dict.calculate_variable({var: x})
        if y_code != SUCCESS_CODE:
            ret_code = y_code
            y_val = 0
        else:
            if y_val.is_constant():
                y_val = y_val.get_constant()
            else:
                ret_code = "Not Constant Result"
                y_val = 0
        y.append(y_val)

    return definition, y, ret_code


def make_data_func(expr_dict=None, var='x', range_dict=None):
    if expr_dict is None:
        expr_dict = ExprDict(0)
    if range_dict is None:
        range_dict = {'start': 0.1, 'end': 5}

    x, y, ret_code = calculate_expr(expr_dict, var, range_dict['start'], range_dict['end'])
    ret_dict = dict(
        domain=x,
        range=y,
    )
    print (ret_dict)
    return ret_dict, ret_code


def calculate_handler(source_list, expr, assign_value, var_range):
    """
    :param source_list: list(plot source)
    :param expr: str(expr text's value)
    :param assign_value: str(assign text's value)
    :param var_range: str(variable range)
    :return:
    """
    assign_dict = None
    if is_assignment(assign_value) == SUCCESS_CODE:
        assign_dict = get_assignment_dict(assign_value)

    var, range_dict = get_var_range_assignment(var_range)

    expr = Expr(expr)
    expr.parse()
    expr.calculate()

    source_list[0].data, ret_func = make_data_func(expr.dict, var, range_dict)
    if var is None: var = 'x'
    diff_dict = expr.dict.differentiate_variable([var])
    source_list[1].data, ret_diff = make_data_func(diff_dict, var, range_dict)

    # print(source.data)


def make_plot(source, color):
    xdr = DataRange1d()
    ydr = DataRange1d()

    plot = Plot(x_range=xdr, y_range=ydr, plot_width=400, plot_height=400)
    plot.title.text = "Graph"

    line = Line(x="domain", y="range", line_color=color)
    plot.add_glyph(source, line)

    xaxis = LinearAxis()
    plot.add_layout(xaxis, 'below')

    yaxis = LinearAxis()
    plot.add_layout(yaxis, 'left')

    plot.add_layout(Grid(dimension=0, ticker=xaxis.ticker))
    plot.add_layout(Grid(dimension=1, ticker=yaxis.ticker))

    plot.add_tools(WheelZoomTool())
    plot.add_tools(ResetTool())
    plot.add_tools(SaveTool())

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

    columns_func = [
        TableColumn(field="domain", title="x", ),
        TableColumn(field="range", title="y", ),
    ]

    columns_diff = [
        TableColumn(field="domain", title="x", ),
        TableColumn(field="range", title="y", ),
    ]

    str_expr = ""
    textinput_expr = TextInput(title="Expression", value=str_expr, placeholder="sin(x)^2 + x^2 * y", sizing_mode='scale_width')

    str_assign_value = ""
    textinput_assign_value = TextInput(title="assign_value", value=str_assign_value, placeholder="x=3, y=5")

    str_assign_range = ""
    textinput_assign_range = TextInput(title="assign_range", value=str_assign_range, placeholder="x(start=0.1, end=5)")


    button = Button(label="Calculate", button_type="success", width=FIG_WIDTH)

    source_list = [source_func, source_diff]
    button.on_click(partial(calculate_handler,
                            source_list=source_list,
                            expr=textinput_expr.value,
                            assign_value=textinput_assign_value.value,
                            var_range=textinput_assign_range.value))

    data_table_func = DataTable(source=source_func, columns=columns_func, width=FIG_WIDTH, height=FIG_HEIGHT, editable=False)
    data_table_diff = DataTable(source=source_diff, columns=columns_diff, width=FIG_WIDTH, height=FIG_HEIGHT, editable=False)
    # inputs = widgetbox(text, button, data_table)
    # col = column(inputs, plot, width=FIG_WIDTH*2)

    # ro = row(textinput_expr, textinput_assign_value, textinput_assign_range)
    lay = layout([
        #[inputs],
        # [text, text2],
        [textinput_expr, textinput_assign_value, textinput_assign_range],
        [button],
        [plot_func, plot_diff],
        [data_table_func, data_table_diff],
    ], sizing_mode='scale_width')
    return lay


lay = make_layout()

document = curdoc()
document.add_root(lay)
