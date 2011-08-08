# -*- coding: utf-8 -*-
import sys
from interp import inperpret, Environment
from helpers import file_to_AST_str
from ast_nodes import *


if len(sys.argv)>2:
    file_name_str = sys.argv[2]
else:
    file_name_str = "input.txt"

ast_string = file_to_AST_str(file_name_str)
exec ast_string
env = Environment()
print inperpret(root, env)
