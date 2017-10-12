from wolframbeta.nonterminals import Expr
from wolframbeta.tokenizer import TokenManager

test_expressions = [
    "1 + 1",
    "1 * 1",
    "1 ^ 1",
    "1 - 1",
    "-2 + 3",
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
    "2*x*6*x*y/x*y*y + x",
    # "sin(pi/3)",
    # "e^x",
    # "sin(pi/3)^3",
    # "sin(pi/3)^3/2 + 1",
    # "cos(0.775)",
    # "sec(0.5)",
    # "sec(0.5)*cos(0.5)",
    # "pow(3,4)",
    # "pow(1+2,4)",
    # "log(10,3)",
    # "pi + e",
    # "pow(10,sin(0.5*pi)+e)",
    # "sin(asin(0.9))",
    # "-sin(asin(0.9))",
    # "sin(x) + sin(x)",
    #"(x^2 + x) + (x^2 + 3*x)",
    # "2*x*6*x*y^3/x^3*y*y + x",
    # "x^2 + x",
    #"x + sin(x) + y + f(3,4)^2"
]


for test_expression in test_expressions:
    token = TokenManager(test_expression)
    # print(token.__tokens__, end=" = ")
    print(test_expression, end=' = ')
    expr = Expr(token)
    expr.parse()
    expr.calculate()
    #print(expr.value)
    print(expr.similar_terms_dict, end=' = ')
    print(expr)
    #print_tree(expr)

