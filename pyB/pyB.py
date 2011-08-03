# -*- coding: utf-8 -*-
import sys
from subprocess import Popen, PIPE
from interp import inperpret, Environment
from ast_nodes import *

command_str = "java -cp "
command_str += "../bparser/build/libs/bparser-2.0.35.jar"
command_str += ":../prologlib/build/libs/prologlib-2.0.1.jar"
command_str += ":../parserbase/build/libs/parserbase-2.0.1.jar"
command_str += ":../cliparser/build/libs/cliparser-2.0.35.jar"
command_str += ":../cliparser/build/libs/"
command_str += ":. de.prob.cliparser.CliBParser %s %s"
#option_str = " -ast"
option_str = " -python"

def file_to_AST_str(file_name_str):
    p =  Popen(command_str % (option_str ,file_name_str), shell=True, stderr=PIPE, stdin=PIPE, stdout=PIPE)
    w, r, e = (p.stdin, p.stdout, p.stderr)
    out = r.read()
    err_out = e.read()
    r.close()
    w.close()
    e.close()
    #print out
    #print err_out
    return out.replace(" ","")

# main code:

if len(sys.argv)>2:
    file_name_str = sys.argv[2]
else:
    file_name_str = "input.txt"

ast_string = file_to_AST_str(file_name_str)
exec ast_string
env = Environment()
print inperpret(root, env)
