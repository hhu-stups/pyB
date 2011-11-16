# -*- coding: utf-8 -*-
import sys
from interp import interpret, Environment
from helpers import file_to_AST_str, find_var_names
from typing import typeit, _test_typeit
from ast_nodes import *


if len(sys.argv)>2:
    file_name_str = sys.argv[2]
else:
    file_name_str = "input.txt"

ast_string = file_to_AST_str(file_name_str)
exec ast_string
idNames = []
find_var_names(root, idNames)
env = Environment()
_test_typeit(root, env, [], idNames) ## FIXME: replace this call someday
print interpret(root, env)
