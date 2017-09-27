from wolframbeta.nonterminal import Expr
from wolframbeta.tokenizer import TokenManager

test_expressions = [
    "1 + 1",
    "1 * 1",
    "1 ^ 1",
    "1 - 1",
    "2 + 3 * 4",
    "2 * 3 + 4",
    "(2 + 3) * 4",
    "(2 + 3) * 4 / 2",
    "(2 + 3) * 4 / 2 / 2",
    "-(2 + 3) * 4 ^ 2 / 4",
    "-(2 + 3) * 4 ^ 2 / -4"
]

for test_expression in test_expressions:
    token = TokenManager(test_expression)
    print(token.__tokens__, end=" = ")
    expr = Expr(token)
    expr.parse()
    expr.calculate()
    print(expr.value, "!")
