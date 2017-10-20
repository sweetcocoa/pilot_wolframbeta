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
from wolframbeta.utils import *
from wolframbeta.config import *
from wolframui.uiconfig import *

from datetime import date
import random

prev_expr_index = [0]
prev_expr = [""]
prev_expr_result = ["Result"]


N = 5


def calculate_expr(str_expression, domain_start=None, domain_end=None):
    expr = Expr(str_expression)
    expr.parse()
    expr.calculate()
    if domain_start is None:
        domain_start = 0.1
    if domain_end is None:
        domain_end = 5.
    if domain_end < domain_start:
        domain_start, domain_end = domain_end, domain_start

    definition = np.linspace(domain_start, domain_end, 100)
    y = list()
    for x in definition:
        y.append(expr.dict.calculate_variable({'x':x})[0].get_constant())

    return definition, y


def make_data_func(expr):
    print(expr)
    global N
    N = N + 1
    if len(expr) > 5:
        x, y = calculate_expr(expr)
        return dict(
            domain=x,
            range=y,
        )

    else:
        return dict(
            domain=[ date(2014, 3, i+1) for i in range(N) ],
            range=[ random.randint(0, 100) for i in range(N) ],
        )



def calculate_handler(source_list):
    global text
    expr = text.value
    source_list[0].data = make_data_func(expr)
    source_list[1].data = make_data_func(expr)

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


text = None


def make_layout():
    global text

    source_func = ColumnDataSource(make_data_func(""))
    source_diff = ColumnDataSource(make_data_func(""))

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
    textinput_assign_range = TextInput(title="assign_range", value=str_assign_range, placeholder="x(0.1,5)")


    button = Button(label="Calculate", button_type="success", width=FIG_WIDTH)
    button.on_click(partial(calculate_handler, source_list=[source_func, source_diff]))

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
    ] , sizing_mode='scale_width')
    return lay


layout = make_layout()

document = curdoc()
document.add_root(layout)