# -*- coding: utf-8 -*-
import sys
from interp import interpret, Environment, all_values_by_type
from helpers import file_to_AST_str, find_var_names
from typing import typeit, _test_typeit
from ast_nodes import *

def try_all_values(root, env, idNames):
    name = idNames[0]
    atype = env.get_type(name)
    all_values = all_values_by_type(atype, env)
    if len(idNames)<=1:
        for val in all_values:
            env.set_value(name,val)
            if interpret(root, env):
                return True
    else:
        for val in all_values:
            env.set_value(name,val)
            if try_all_values(root, env, idNames[1:]):
                return True
    return False


if len(sys.argv)>=1:
    file_name_str = sys.argv[1]
else:
    file_name_str = "input.txt"

ast_string = file_to_AST_str(file_name_str)
print ast_string
exec ast_string
idNames = []
find_var_names(root, idNames) #sideef: fill list
env = Environment()
_test_typeit(root, env, [], idNames) ## FIXME: replace this call someday
if idNames ==[]:
    print interpret(root, env)
else:
    if try_all_values(root, env, idNames):
        for i in idNames:
            print i,":", env.get_value(i)
    else:
        print "No Solution found"


