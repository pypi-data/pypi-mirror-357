```python
from tantpy import tantpy


@tantpy
def risky_division(a, b):
    return a / b

result = risky_division(10, 0)
# Something went wrong: division by zero
# Tant pis. The code moves on, like a river past a fallen tree.
print(f"{result=}")
# result=None
```

