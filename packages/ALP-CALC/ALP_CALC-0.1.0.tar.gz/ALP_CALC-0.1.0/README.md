# NumerikPy

NumerikPy adalah library Python sederhana untuk menghitung:
- Turunan numerik
- Integral numerik

---

## 📚 Fungsi yang tersedia

- `forward_difference(f, x)`
- `central_difference(f, x)`
- `trapezoidal(f, a, b)`
- `simpsons_one_third(f, a, b)`

---

## 📌 Kasus A – Titik Ekstrim Lokal

```python
from __init__ import central_difference

def f(x): return x**3 - 3*x + 1
def df(x): return central_difference(f, x)

def bisection(f, a, b, tol=1e-5):
    for _ in range(100):
        c = (a + b) / 2
        if abs(f(c)) < tol: return c
        if f(a) * f(c) < 0: b = c
        else: a = c
    return (a + b) / 2

x1 = bisection(df, -2, 0)
x2 = bisection(df, 0, 2)

print(f"Titik stasioner numerik: x ≈ {x1:.5f}, {x2:.5f}")
print("Titik stasioner eksak   : x = -1, x = 1")
```
## 📌 Kasus B – Integral Tentu

```python
from __init__ import trapezoidal, simpsons_one_third

f = lambda x: x**2
a, b = 0, 1

trap = trapezoidal(f, a, b)
simp = simpsons_one_third(f, a, b)
exact = 1/3

print(f"Trapezoidal: {trap}")
print(f"Simpson 1/3: {simp}")
print(f"Exact: {exact}")
```