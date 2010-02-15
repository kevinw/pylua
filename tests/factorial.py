def fact(n):
    return 1 if n == 0 else n * fact(n-1)

print fact(5)
