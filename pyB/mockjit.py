# This module added mock functions to replace pypy annotations.
# Using this in a non pypy context avoids a pyB-pypy dependency. 

def unroll_safe(func):
    return func


def elidable(func):
    return func
    

def dont_look_inside(func):
    return func

