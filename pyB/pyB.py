# -*- coding: utf-8 -*-
import sys
from subprocess import Popen, PIPE
command_str = "java -cp bparser/build/libs/bparser-2.0.1.jar:prologlib/build/libs/prologlib-2.0.1.jar:parserbase/build/libs/parserbase-2.0.1.jar:cliparser/build/libs/cliparser-2.0.3.jar:cliparser/build/libs/:. de.prob.cliparser.CliBParser %s %s"
#option_str = " -ast"
option_str = " -prolog"
if len(sys.argv)>2:
    file_name_str = sys.argv[2]
else:
    file_name_str = "Lift.mch"
p =  Popen(command_str % (option_str ,file_name_str), shell=True, stderr=PIPE, stdin=PIPE, stdout=PIPE)
w, r, e = (p.stdin, p.stdout, p.stderr)
out = r.read()
err_out = e.read()
r.close()
w.close()
e.close()
print out

