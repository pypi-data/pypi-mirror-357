# UltraCalc

UltraCalc is the ultimate infinite-precision calculator in Python.

- Precision: 1,000,000+ digits
- Exponents: ±10^100
- Supports: +, -, *, /, **, sqrt, ln, sin, cos, tan, exp, pi, e
- Automatically wraps numeric input into `Decimal` without user effort

```python
from ultracalc import calc
print(calc("1e-9999999 + 1e-9999998"))
```

