import numpy as np

from bokeh.io import curdoc
from bokeh.layouts import row, widgetbox, column
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
domain_start = None
domain_end = None


def calculate_expr(str_expression):
    expr = Expr(str_expression)
    expr.parse()
    expr.calculate()
    global domain_start, domain_end
    if domain_start is None:
        domain_start = -5.
    if domain_end is None:
        domain_end = 5.
    if domain_end < domain_start:
        domain_start, domain_end = domain_end, domain_start

    definition = np.linspace(domain_start, domain_end, 100)
    y = list()
    for x in definition:
        y.append(expr.calculate_variable({'x':x}).get_constant())

    return definition, y


def make_data(expr):
    print(expr)
    global N
    N = N + 1
    if len(expr)>5:
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


source = ColumnDataSource(make_data(""))


def calculate_handler():
    global text
    expr = text.value
    source.data = make_data(expr)

    # print(source.data)


def get_domain_start(attr, old, new):
    global domain_start
    domain_start = new


def get_domain_end(attr, old, new):
    global domain_end
    domain_end = new


def make_plot():
    xdr = DataRange1d()
    ydr = DataRange1d()

    plot = Plot(x_range=xdr, y_range=ydr, plot_width=400, plot_height=400)
    plot.title.text = "Graph"

    line = Line(x="domain", y="range", line_color="blue")
    plot.add_glyph(source, line)

    xaxis = LinearAxis()
    plot.add_layout(xaxis, 'below')

    yaxis = LinearAxis()
    plot.add_layout(yaxis, 'left')

    plot.add_layout(Grid(dimension=0, ticker=xaxis.ticker))
    plot.add_layout(Grid(dimension=1, ticker=yaxis.ticker))

    # plot.add_tools(HoverTool(tooltips=dict(downloads="@downloads")))
    plot.add_tools(WheelZoomTool())
    plot.add_tools(ResetTool())
    plot.add_tools(SaveTool())

    print("range : ", xdr.start, xdr.end)
    xdr.on_change('start', get_domain_start)
    xdr.on_change('end', get_domain_end)
    return plot, source


text = None


def make_layout():
    global text

    plot, source = make_plot()
    # columns = [
    #     TableColumn(field='prev_expr_index', title='Index'),
    #     TableColumn(field='prev_expr', title='Expr'),
    #     TableColumn(field='prev_expr_result', title='Result')
    # ]

    columns = [
        TableColumn(field="domain", title="x", ),
        TableColumn(field="range", title="y", ),
    ]

    text_expr = ""
    text = TextInput(title="Expression", value=text_expr)

    button = Button(label="Calculate", button_type="success", width=FIG_WIDTH)
    button.on_click(calculate_handler)

    data_table = DataTable(source=source, columns=columns, width=FIG_WIDTH, height=FIG_HEIGHT, editable=False)

    inputs = widgetbox(text, button, data_table)
    col = column(inputs, plot, width=FIG_WIDTH*2)

    return col


layout = make_layout()

document = curdoc()
document.add_root(layout)