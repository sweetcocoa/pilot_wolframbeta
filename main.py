from wolframbeta.nonterminal import Expr, print_tree
from wolframbeta.tokenizer import TokenManager

test_expressions = [
    #"1 + 1",
    #"1 * 1",
    #"1 ^ 1",
    #"1 - 1",
    #"2 + 3 * 4",
    #"2 * 3 + 4",
    #"(2 + 3) * 4",
    #"(2 + 3) * 4 / 2",
    #"(2 + 3) * 4 / 2 / 2",
    #"-(2 + 3) * 4 ^ 2 / 4",
    #"-(2 + 3) * 4 ^ 2 / -4",
    #"(3+4^2)/3/2*6+7^2+9/2^2",
    "sin(0.785)",
    "sin(0.785)^3",
    "sin(0.785)^3/2 + 1",
    "cos(0.775)",
    "sec(0.5)",
    "sec(0.5)*cos(0.5)",
    "pow(3,4)",
    "pow(1+2,4)",
    "log(10,3)",
    "pi + e",
    "pow(10,sin(0.5*pi)+e)",
    "sin(asin(0.9))",
    #"x + sin(x) + y + f(3,4)^2"
]

for test_expression in test_expressions:
    token = TokenManager(test_expression)
    print(token.__tokens__, end=" = ")
    expr = Expr(token)
    expr.parse()
    expr.calculate()
    print(expr.value, "!")
    print_tree(expr)