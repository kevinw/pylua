print 5 + 5
def foo():
    return 42
print foo()


def fact(x): return (1 if x==0 else x * fact(x-1))
