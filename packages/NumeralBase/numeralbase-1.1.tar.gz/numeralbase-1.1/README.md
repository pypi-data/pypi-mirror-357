# NumeralBase

Python library for working with various numeral systems.

```python
number = convert_base('10A', 16, 10) # Number for convert; number base; convertion to base
# '10A' -> '266'
```

You can convert numbers up to 176 numeric system.
```python
number = convert_base('10A', 16, 176)
# '10A' -> '1ε'
```

Or use your own alphabet for the numeric system:
```python
number = convert_base('10A', 16, 2000, '01234(...)*%$&$@w!')
```


## Class NumeralNumber

Also, special class for non-decimal numbres:
```python
n1 = NumeralNumber("1010", 2)
n2 = NumeralNumber("FF", 16)
```


### Arithmetic


You can use arithmetic operations for the numbers that will be in the class.

```python
print(n1 + n2)  # 10100101 (265)

print(n2 - n1)  # F5 (245)

print(n1 * n2)  # 111111100110 (2550)
```
