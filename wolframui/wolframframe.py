import matplotlib
matplotlib.use('TkAgg')

import numpy as np
import matplotlib.pyplot as plt

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
# implement the default mpl key bindings
from matplotlib.backend_bases import key_press_handler

import tkinter as Tk

from wolframbeta.tokenizer import TokenManager
from wolframbeta.nonterminals import Expr
from wolframui.utils import *

class WolframFrame(Tk.Frame):

    def draw_graph(self, expr=None, variable_dict=None):
        f = plt.figure(figsize=(5, 4), dpi=100)
        # a = f.add_subplot(111)
        # t = arange(0.0, 3.0, 0.01)
        # s = sin(2 * pi * t)
        #
        # a.plot(t, s)

        # a tk.DrawingArea
        canvas = FigureCanvasTkAgg(f, master=self)
        canvas.show()
        canvas.get_tk_widget().pack(side=Tk.TOP, fill=Tk.BOTH, expand=1)

        toolbar = NavigationToolbar2TkAgg(canvas, self)
        toolbar.update()
        canvas._tkcanvas.pack(side=Tk.TOP, fill=Tk.BOTH, expand=1)

    def wolfram_calculate(self):
        str_expression = self.entry_expr.get()
        if len(str_expression) < 1:
            return

        if str_expression.find('=') != -1:
            # Variable Assignment
            variable_dict = None
            if self.last_expr is not None:
                variable_dict = get_assignment_dict(str_expression)
            else:
                raise_error("Expression is not defined")

            calculate_result = self.last_expr.calculate_variable(variable_dict)
            self.lbl_result['text'] = str(str(calculate_result))

        else:
            tokenmanager = TokenManager(str_expression)
            self.last_expr = Expr(tokenmanager)
            self.last_expr.parse()
            self.last_expr.calculate()
            self.lbl_result['text'] = str(self.last_expr)

        self.entry_text.set("")
        self.add_previous(str_expression)



        # self.draw_graph()
        pass

    def add_previous(self, expr):
        lbl_previous = Tk.Label(self.frame_prev, text=expr)
        lbl_previous.pack(padx=10, pady=10)
        self.list_lbl_prev.append(lbl_previous)
        if len(self.list_lbl_prev) > 5:
            self.list_lbl_prev[-5].pack_forget()

    def __init__(self, master):
        Tk.Frame.__init__(self, master)

        self.master = master
        self.master.title("WolframBeta")
        self.pack(fill=Tk.BOTH, expand=True)

        # previous expressions
        self.frame_prev = Tk.Frame(self)
        self.frame_prev.pack(fill=Tk.X)
        self.list_lbl_prev = list()
        lbl_previous = Tk.Label(self.frame_prev, text="Previous expressions")
        lbl_previous.pack(side=Tk.LEFT, padx=10, pady=10)
        self.list_lbl_prev.append(lbl_previous)

        # expression
        frame1 = Tk.Frame(self)
        frame1.pack(fill=Tk.X)

        self.lbl_expr = Tk.Label(frame1, text="식(Expression)", width=10)
        self.lbl_expr.pack(side=Tk.LEFT, padx=10, pady=10)

        self.entry_text = Tk.StringVar()
        self.entry_expr = Tk.Entry(frame1, text=self.entry_text)
        self.entry_expr.pack(fill=Tk.X, padx=10, expand=True)

        # 저장
        frame2 = Tk.Frame(self)
        frame2.pack(fill=Tk.X)
        btn_calculate = Tk.Button(frame2, text="Do", command=self.wolfram_calculate)
        btn_calculate.pack(side=Tk.LEFT, padx=10, pady=10)

        frame_result = Tk.Frame(self)
        frame_result.pack(fill=Tk.X)

        self.lbl_result = Tk.Label(frame_result)
        self.lbl_result.pack(fill=Tk.X, padx=10, expand=True)

        self.last_expr = None

def main():
    root = Tk.Tk()
    # root.geometry("600x550+100+100")
    app = WolframFrame(root)
    root.mainloop()



if __name__ == '__main__':
    main()