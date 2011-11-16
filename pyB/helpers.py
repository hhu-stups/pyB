# -*- coding: utf-8 -*-
# moved for testing-reasons
from subprocess import Popen, PIPE
from ast_nodes import *

command_str = "java -cp "
command_str += "../bparser/build/libs/bparser-2.0.67.jar"
command_str += ":../prologlib/build/libs/prologlib-2.0.1.jar"
command_str += ":../parserbase/build/libs/parserbase-2.0.1.jar"
command_str += ":../cliparser/build/libs/cliparser-2.0.67.jar"
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
    return out.replace(" ","")


def string_to_file(string, file_name):
    f = open(file_name,"w")
    f.write(string)
    f.close
    return f


def find_var_names(node, lst):
    if isinstance(node, AUniversalQuantificationPredicate) or isinstance(node, AExistentialQuantificationPredicate) or isinstance(node, AComprehensionSetExpression) or isinstance(node, AGeneralSumExpression) or isinstance(node, AGeneralProductExpression):
        return
    elif isinstance(node, AIdentifierExpression):
        if not node.idName in lst:
            lst.append(node.idName)
    else:
        try:
            for n in node.children:
                find_var_names(n, lst)
        except AttributeError:
            return #FIXME no children