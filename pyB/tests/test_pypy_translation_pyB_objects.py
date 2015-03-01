# assumes pypy checkout at PYPYDIR
from config import USE_COSTUM_FROZENSET
file_name = "input.txt"
PYPY_DIR  = "/Users/johnwitulski/witulski/git/pyB/pypy/" # change this line to your checkout


def translate(code):
    # 1. Generate Python code as String
    code += "def target(*args):\n"
    code += "   return main, None # returns the entry point\n"
    code += "\n"
    code += "if __name__ == '__main__':\n"
    code += "   import sys\n"
    code += "   main(sys.argv)\n"
    # 2. write to temp file
    f = open("temp.py",'w')
    f.write(code)
    f.close()
    from subprocess import Popen, PIPE
    # 3. call python version
    python_result = Popen("python temp.py", shell=True, stdout=PIPE).stdout.read()
    # 4. generate and call c Version
    pwd = Popen("pwd", shell=True, stdout=PIPE).stdout.read()
    assert pwd[-4:]=='pyB\n'
    Popen("PYTHONPATH="+PYPY_DIR+":. python ../pypy/rpython/translator/goal/translate.py temp.py", shell=True, stdout=PIPE).stdout.read()
    c_result = Popen("./temp-c", shell=True, stdout=PIPE).stdout.read()
    # 5. delete temp. file
    import os
    os.remove("temp.py")
    os.remove("temp-c")
    # 6. compare c and python result
    return python_result, c_result


class TestPyPyTranslationObjects():
    def test_pypy_genAST_expr_number1(self):
        code =  """def main(argv):
            from ast_nodes import AIntegerExpression
            node = AIntegerExpression(41)
            print node.intValue
            return 0\n"""
        python_result, c_result = translate(code) 
        assert eval(python_result) == eval(c_result)    
     
     
    def test_pypy_genAST_expr_number2(self):
        code =  """def main(argv):
            from ast_nodes import AIntegerExpression
            from interp import interpret
            node0 = AIntegerExpression(1)
            print isinstance(node0, AIntegerExpression)
            return 0\n"""
        python_result, c_result = translate(code) 
        assert eval(python_result) == eval(c_result)   


    def test_pypy_genAST_expr_number3(self):
        code =  """def main(argv):
            from ast_nodes import AIntegerExpression
            from interp import interpret
            node0 = AIntegerExpression(1)
            print interpret(node0, None)
            return 0\n"""
        python_result, c_result = translate(code) 
        assert eval(python_result) == eval(c_result)     
 
 
    import pytest
    @pytest.mark.xfail 
    def test_pypy_genAST_expr_number4(self):
        code =  """def main(argv):
            from ast_nodes import AIntegerExpression, AAddExpression
            from interp import interpret
            node0 = AIntegerExpression(1)
            node1 = AIntegerExpression(2)
            node2 = AAddExpression()
            node2.children.append(node0)
            node2.children.append(node1)
            print interpret(node2, None)
            return 0\n"""
        python_result, c_result = translate(code) 
        assert eval(python_result) == eval(c_result)   


    # set config.USE_COSTUM_FROZENSET = True
    import pytest
    @pytest.mark.xfail    
    def test_pypy_create_env(self):
        code = """def main(argv):
            from environment import Environment
            env = Environment()
            return 0\n"""
        python_result, c_result = translate(code) 
        assert python_result == c_result   
  
    
    #import pytest
    #@pytest.mark.xfail  
    def test_pypy_check_frozenset_impl(self):
        code = """def main(argv):
            from rpython_frozenset import frozenset
            S = frozenset([1,2,3])
            for e in S:
                print e
            # maybe the next three will work with wrapped types + type hirachy
            #T = frozenset(['a','b','c'])
            #print 1 in S
            #print 4 in S
            return 0\n"""
        python_result, c_result = translate(code) 
        assert python_result == c_result  