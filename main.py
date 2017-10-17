from wolframbeta.nonterminals import *
from wolframbeta.similar_term import *

from wolframbeta.tokenizer import TokenManager
# from wolframbeta.utils import *
import numpy as np

"""
밑 : 괄호, 상수, 단일항, 다항
지수 : 존재, 괄호, 상수, 단일항, 다항
"""
test_expressions = [
    # "(3)^(2)",
    # "(3)^(x)",
    # "(3)^(3*x)",
    # "(3)^(x^2+x)",
    # "(3)^(x^2+2*x)",
    # "(log(10,3))^(2)",
    # "(log(10,3))^(x)",
    # "(log(10,3))^(3*x)",
    # "(log(10,3))^(x^2+x)",
    # "(log(10,3))^(x^2+2*x)",
    # "(log(10,3))^2",
    # "(log(10,3))^x",
    # "log(10,3)^(2)",
    # "log(10,3)^(x)",
    # "log(10,3)^(3*x)",
    # "log(10,3)^(x^2+x)",
    # "log(10,3)^(x^2+2*x)",
    # "log(10,3)^2",
    # "log(10,3)^x",
    # "log(x+1,3)^x",
    # "log(x+1,3)^(x+1)",
    # "sqrt(x)",
    # "sqrt(x+1)",
    # "sqrt(x+y)",
    # "sqrt(log(9*x,3))",
    # "(x^2) + (x)*(x)",
    # "2.7^x + (2.7^x) + (3*2.7^x) + 3*2.7^x + 3*2.7^(2*x) + 2.7^(x^2)",
    # "2^(x*y)",
    # "2^(x*y) * 2^(3*y) + (2^3)^y",
    # "1 + 1",
    # "1 * 1",
    # "1 ^ 1",
    # "pow(x,2)",
    # "1 - 1",
    # "2 ^0.5",
    # "-2 + 3",
    # "1/3",
    # "x/3",
    # "(x)/3",
    # "(x+1)/3",
    # "(x)*(x)",
    # "(x+1)*(x+1)/4",
    # "(1-x)*(1+x)",
    # "(x^1.4+1)*(x^1.4+1)",
    # "2 ^ 3",
    # "2 + 3 * 4",
    # "2 * 3 + 4",
    # "(2 + 3) * 4",
    # "(2 + 3) * 4 / 2",
    # "(2 + 3) * 4 / 2 / 2",
    # "-(2 + 3) * 4 ^ 2 / 4",
    # "-(2 + 3) * 4 ^ 2 / -4",
    # "(3+2)*(3+2)",
    # "(3+4^2)/3/2*6+7^2+9/2^2",
    # "x + x",
    # "5*x^2*y+2 + 2*x^2*y",
    # "5*x^2*y+2 - 2*x^2*y",
    # "cos(0.775)",
    # "sec(0.5)",
    # "sec(0.5)*cos(0.5)",
    # "log(10,3)",
    # "pi + e",
    # "sin(asin(0.9))",
    # "-sin(asin(0.9))",
    # "sin(x) + sin(x)",
    # "sin(pi/3)",
    # "sin(x) + sin(x)",
    # "sin(x+2)+sin(x+2)",
    # "sin(x+2)+sin(2+x)",
    # "sin(pi/3)^3",
    # "sin(pi/3)^3/2 + 1",
    # "(x^2 + x) + (x^2 + 3*x)",
    # "x^2 + x",
    # "sin(sin(x+2))+sin(sin(x+2))",
    # "e^x",
    # " e^(2*x)",
    # "(e^2)^x",
    # "x^2 + x^2",
    # "2^x + 2^x",
    # "(e^2)^x + e^x",
    # "(e^2)^x",
    # "e^(2*x)",
    # "e^(2*x) + (e^2)^x",
    #  "e^(2*x) + (e^2)^x + e^x",
    # "(e^2)^x + e^x",
    # "(x)^2",
    # "x+y",
    # "(x)^2^2 + x^4",
    # "(x*y)^2 + x^2*y^2",
    # "(sin(3+y))",
    # "sin(x+y+2)+(sin(3+y))",
    # "sin(x+y+2)",
    # "sin(x+y)+(sin(3+y))",
    # "sin(x+y)*(sin(3+y)^2)",
    # "sin(x+y)*(sin(3+y))^2",
    # "3^(x+1) + 3^x",
    # "(x^2+x+1)^15",
    # "(x+1)^2",
    # "(x-1)^2",
    # "(x+1)^0",
    # "(x+y)^2",
    # "(x+y+z)^2",
    # "(x+y+1)^3",
    # "(x^2+x+1)^1.58",
    # "(3)^(x) + (3)^x",
    # "(3)^(3*x) + (3)^x",
    # "(3)^(3*x+2) + (3)^x",
    # "(x+1)^0.5",
    # "(x+1)^2",
    # "(x^2+1)^2.5",
    # "+x+x",
    # "log(x+x,2)",
    # "log(5,2)^3",
    # "log(5,2)^x",
    # "(x+x)^x",
    # "1/x",
    # "1/2",
    # "x/5",
    # "x^-1",
    # "(x+1)^-1",
    # "(3*x)^-1",
    # "(2*x)^4",
    # "x/y",
    # "y/x",
    # "(x+y)/3",
    # "(x*y)^-1",
]


for test_expression in test_expressions:
    token = TokenManager(test_expression)

    print(test_expression, end=' = ')

    expr = Expr(token)
    expr.parse()
    expr.calculate()
    print(dict(expr.similar_terms_dict), end=' = ')
    print(expr, end=' = ')
    # for i in np.linspace(-5, 5, 100):
    #     print("x : {}$".format(i), expr.calculate_variable({'x': i}))
    print('$', expr.calculate_variable({'x':3.0}))


str_expressions = [
    "1/(x+1)/(y+1)",
    "2/(x+1)/(y+1)",
    "(x+1)/(x+1)",
]
for str_expression in str_expressions:
    expr = Expr(str_expression)
    expr.parse()
    expr.calculate()
    print(str_expression, ' = ', expr, ' = ', end = '')
    print(dict(expr.similar_terms_dict), end=' = ')
    print('$', expr.calculate_variable({'x': 3.0}))

