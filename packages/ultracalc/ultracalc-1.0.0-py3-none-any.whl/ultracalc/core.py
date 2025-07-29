from decimal import Decimal, getcontext
import math, re

# Set infinite context
ctx = getcontext()
ctx.prec = 10**6
ctx.Emax = 10**100
ctx.Emin = -10**100

D = Decimal
to_decimal = lambda x: D(str(x))

# Math function environment
safe_math = {
    'Decimal': D, 'D': D,
    'pi': to_decimal(math.pi),
    'e': to_decimal(math.e),
    'sqrt': lambda x: x.sqrt(),
    'ln': lambda x: x.ln(),
    'exp': lambda x: x.exp(),
    'abs': abs,
    'sin': lambda x: D(str(math.sin(float(x)))),
    'cos': lambda x: D(str(math.cos(float(x)))),
    'tan': lambda x: D(str(math.tan(float(x))))
}

def calc(expr: str):
    expr = re.sub(r'(?<![\w.])(\d+(\.\d+)?(e[+-]?\d+)?)(?![\w.])', r'D("\1")', expr)
    return eval(expr, safe_math)
