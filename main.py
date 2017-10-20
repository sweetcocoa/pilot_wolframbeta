from wolframbeta.nonterminals import *


from wolframbeta.tokenizer import TokenManager
# from wolframbeta.utils import *
import numpy as np

"""
밑 : 괄호, 상수, 단일항, 다항
지수 : 존재, 괄호, 상수, 단일항, 다항
"""
test_expressions = [
    "sin(x)",
    "cos(x)",
    "tan(x)",
    "sin(x)*cosec(x)",
    "cos(x)*sec(x)",
    "sec(x)^-1*cos(x)",
    # "(x^2) + (x)*(x)",
    # "1 + 1",
    # "1 * 1",
    # "1 ^ 1",
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
    # "pi + e",
    # "(x^2 + x) + (x^2 + 3*x)",
    # "x^2 + x",
    # "x^2 + x^2",
    # "(3)^(2)",
    # "(x)^2",
    # "x+y",
    # "y",
    # "(x)^2^2 + x^4",
    # "(x*y)^2 + x^2*y^2",
    # "(x^2+x+1)^15",
    # "(x+1)^2",
    # "(x-1)^2",
    # "(x+1)^0",
    # "(x+y)^2",
    # "(x+y+z)^2",
    # "(x+y+1)^3",
    # "(x^2+x+1)^1.58",
    # "(x+1)^0.5",
    # "(x+1)^2",
    # "(x^2+1)^2.5",
    # "+x+x",
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
    # "1/(x-3)",
    # "(x-3)/(x-3)",
    # "(x-3)^-2",
    # "(x-2)^-2.55",
    # "3*x/(x+1)",
    # "(2*x-20)/(x-10)",
    # "(x-10)/(x-10)",
    # "(x-3)/(x-3)",
    # "1/(x-3)*(x-3)",
    # "(x-1)^-0.5",
    # "3^(x+1) + 3^x",
    # "(3)^(x)",
    # "(3)^(3*x)",
    # "(3^3)^x",
    # "(3)^(x^2+x)",
    # "(3)^(x^2+2*x)",
    # "2.7^x + (2.7^x) + (3*2.7^x)",
    # "3*2.7^x + 3*2.7^(2*x)",
    # "3*2.7^(2*x) + 2.7^(x^2)",
    # "3*2.7^x + 3*2.7^(2*x) + 2.7^(x^2)",
    # "2.7^x + (2.7^x) + (3*2.7^x) + 3*2.7^x + 3*2.7^(2*x) + 2.7^(x^2)",
    # "2^(x*y)",
    # "2^(x*y) * 2^(3*y)",
    # "2^x + 3^x",
    # "2^(x*y) * 2^(3*y) + (2^3)^y",
    # "e^x",
    # " e^(2*x)",
    # "(e^2)^x",
    # "2^x + 2^x",
    # "(e^2)^x + e^x",
    # "(e^2)^x",
    # "e^(2*x)",
    # "e^(2*x) + (e^2)^x",
    # "e^(2*x) + (e^2)^x + e^x",
    # "(e^2)^x + e^x",
    # "(3)^(x) + (3)^x",
    # "(3)^(3*x) + (3)^x",
    # "(3)^(3*x+2) + (3)^x",
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
    # "log(10, x-2)",
    # "log(10, x-3)",
    # "log(x-3, 2)",
    # "cos(0.775)",
    # "sec(0.5)",
    # "sec(0.5)*cos(0.5)",
    # "log(10,3)",
    # "sin(sin(x+2))+sin(sin(x+2))",
    # "(sin(3+y))",
    # "sin(x+y+2)+(sin(3+y))",
    # "sin(x+y+2)",
    # "sin(x+y)+(sin(3+y))",
    # "sin(x+y)*(sin(3+y)^2)",
    # "sin(x+y)*(sin(3+y))^2",
    # "log(x+x,2)",
    # "log(5,2)^3",
    # "log(5,2)^x",
    # "sin(asin(0.9))",
    # "-sin(asin(0.9))",
    # "sin(x) + sin(x)",
    # "sin(pi/3)",
    # "sin(x) + sin(x)",
    # "sin(x+2)+sin(x+2)",
    # "sin(x+2)+sin(2+x)",
    # "sin(pi/3)^3",
    # "sin(pi/3)^3/2 + 1",
    # "sin()",
    # "sin(3,2)",
    # "log()",
    # "log(1)",
    # "log(,3)",
    # "something(2,3)",
]

for test_expression in test_expressions:
    token = TokenManager(test_expression)
    print(test_expression, end=' = ')
    expr = Expr(token)
    expr.parse()
    expr.calculate()
    print(expr.dict, end=' = ')
    res = expr.dict.calculate_variable({'x':3})
    print('$', res[0], res[1])
    res = expr.dict.differentiate_variable(['x'])
    print("Diff : ", res[0], res[1])

# str_expressions = [




# ]
# for str_expression in str_expressions:
#     expr = Expr(str_expression)
#     expr.parse()
#     expr.calculate()
#     print(str_expression, ' = ', expr, ' = ', end = '')
#     print(dict(expr.similar_terms_dict), end=' = ')
#     print('$', expr.calculate_variable({'x': 3.0}))
#
