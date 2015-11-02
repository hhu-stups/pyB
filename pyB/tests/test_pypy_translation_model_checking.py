# assumes pypy checkout at PYPYDIR
from config import USE_RPYTHON_CODE

file_name = "input.txt"
PYPY_DIR  = "/Users/johnwitulski/witulski/git/pyB/pypy/" # change this line to your checkout


# generates c-PyB and python-PyB executables 
def translate():  
    import os
    from subprocess import Popen, PIPE
    if os.name=='nt':
        # Add pypy to your path if this line crashs
        Popen("python ../pypy/rpython/translator/goal/translate.py --batch pyB_RPython.py", shell=True, stdout=PIPE).stdout.read()
    else:
        pwd = Popen("pwd", shell=True, stdout=PIPE).stdout.read()
        assert pwd[-4:]=='pyB\n'
        Popen("PYTHONPATH="+PYPY_DIR+":. python ../pypy/rpython/translator/goal/translate.py --batch pyB_RPython.py", shell=True, stdout=PIPE).stdout.read()


# Run main_code with CPython (except RPython Flags) and Translated C Version
def execute_file(cl_argument=""):
    from subprocess import Popen, PIPE
    c_result = Popen("./"+"pyB_RPython-c "+cl_argument, shell=True, stdout=PIPE).stdout.read()
    return c_result
  
    
def clean_up():
    import os
    #os.remove("pyB_RPython-c")

import pytest, config
@pytest.mark.skipif(config.USE_RPYTHON_CODE==False, reason="translation to c not possible using built-in frozenset type")     
class TestPyPyTranslationModelChecking():
    def test_pypy_mc_loops(self):
        translate() 
        
        c_result = execute_file(" -mc examples/rpython_performance/Lift2.mch")       
        expected ="""\033[1m\033[91mWARNING\033[00m: model checking still experimental
        checked 100 states.\033[1m\033[92m No invariant violation found.\033[00m
        """
        assert c_result.replace(" ", "").replace("\t", "").split('\n') ==  expected.replace(" ", "").replace("\t", "").split('\n') 
        
        c_result = execute_file(" -mc examples/rpython_performance/Lift.mch")
        expected ="""\033[1m\033[91mWARNING\033[00m: model checking still experimental
        \033[1m\033[91mWARNING\033[00mInvariant violation

        FALSE Predicates:
        FALSE = (floor:0 .. 99)
        dec
        dec
        dec
        dec
        dec
        init

        WARNING: invariant violation found after checking 101 states
        """
        assert c_result.replace(" ", "").replace("\t", "").split('\n') ==  expected.replace(" ", "").replace("\t", "").split('\n') 
        
        c_result = execute_file(" -mc examples/rpython_performance/WhileLoop.mch")
        expected ="""\033[1m\033[91mWARNING\033[00m: model checking still experimental
        \033[1m\033[91mWARNING\033[00m: WHILE inside abstract MACHINE!
        checked 2 states.\033[1m\033[92m No invariant violation found.\033[00m
        """
        assert c_result.replace(" ", "").replace("\t", "").split('\n') ==  expected.replace(" ", "").replace("\t", "").split('\n') 
        
        clean_up()