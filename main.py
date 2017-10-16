from wolframbeta.nonterminals import Expr
from wolframbeta.tokenizer import TokenManager
import numpy as np

test_expressions = [
    "(x^2) + (x)*(x)",
    "1 + 1",
    "1 * 1",
    "1 ^ 1",
    "1 - 1",
    "2 ^0.5",
    "-2 + 3",
    "1/3",
    "x/3",
    "(x)/3",
    "(x+1)/3",
    "(x)*(x)",
    "(x+1)*(x+1)/4",
    "(1-x)*(1+x)",
    "(x^1.4+1)*(x^1.4+1)",
    "2 ^ 3",
    "2 + 3 * 4",
    "2 * 3 + 4",
    "(2 + 3) * 4",
    "(2 + 3) * 4 / 2",
    "(2 + 3) * 4 / 2 / 2",
    "-(2 + 3) * 4 ^ 2 / 4",
    "-(2 + 3) * 4 ^ 2 / -4",
    "(3+2)*(3+2)",
    "(3+4^2)/3/2*6+7^2+9/2^2",
    "x + x",
    "5*x^2*y+2 + 2*x^2*y",
    "5*x^2*y+2 - 2*x^2*y",
    "cos(0.775)",
    "sec(0.5)",
    "sec(0.5)*cos(0.5)",
    "log(10,3)",
    "pi + e",
    "sin(asin(0.9))",
    "-sin(asin(0.9))",
    "sin(x) + sin(x)",
    "sin(pi/3)",
    "sin(x) + sin(x)",
    "sin(x+2)+sin(x+2)",
    "sin(x+2)+sin(2+x)",
    "sin(pi/3)^3",
    "sin(pi/3)^3/2 + 1",
    "(x^2 + x) + (x^2 + 3*x)",
    "x^2 + x",
    "sin(sin(x+2))+sin(sin(x+2))",
    "e^x",
    " e^(2*x)",
    "(e^2)^x",
    "x^2 + x^2",
    "2^x + 2^x",
    "(e^2)^x + e^x",
    "(e^2)^x",
    "e^(2*x)",
    "e^(2*x) + (e^2)^x",
     "e^(2*x) + (e^2)^x + e^x",
    "(e^2)^x + e^x",
    "(x)^2",
    "x+y",
    "(x)^2^2 + x^4",
    "(x*y)^2 + x^2*y^2",
    "(sin(3+y))",
    "sin(x+y+2)+(sin(3+y))",
    "sin(x+y+2)",
    "sin(x+y)+(sin(3+y))",
    "sin(x+y)*(sin(3+y)^2)",
    "sin(x+y)*(sin(3+y))^2",
    #"x + sin(x) + y + f(3,4)^2"
]


for test_expression in test_expressions:
    token = TokenManager(test_expression)
    # print(token.__tokens__, end=" = ")
    print(test_expression, end=' = ')
    expr = Expr(token)
    expr.parse()
    expr.calculate()
    print(expr.similar_terms_dict, end=' = ')
    print(expr, end=' = ')
    # for i in np.linspace(-5, 5, 100):
    #     print("x : {}$".format(i), expr.calculate_variable({'x': i}))
    print('$', expr.calculate_variable({'x':3.0}))


