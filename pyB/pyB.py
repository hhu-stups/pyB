# -*- coding: utf-8 -*-
import sys
from interp import interpret, Environment
from helpers import file_to_AST_str
from ast_nodes import *


if len(sys.argv)>=1:
    file_name_str = sys.argv[1]
else:
    file_name_str = "input.txt"

ast_string = file_to_AST_str(file_name_str)
#print ast_string
exec ast_string
env = Environment()
interpret(root, env)


