# assumes pypy checkout at PYPYDIR
from config import USE_RPYTHON_CODE

file_name = "input.txt"
PYPY_DIR  = "/Users/johnwitulski/witulski/git/pyB/pypy/" # change this line to your checkout
python_file = "tempB.py"
rpython_file = "tempA.py"
c_file = "tempA-c"

# generates c and python executables 
def translate(main_code, other_code=""):
    # 1. Generate Python code as String
    code = other_code
    code += "def main(argv):\n"
    code += main_code
    code += "def target(*args):\n"
    code += "   return main, None # returns the entry point\n"
    code += "\n"
    code += "if __name__ == '__main__':\n"
    code += "   import sys\n"
    code += "   main(sys.argv)\n"
    
    # 2 write code to temp file (Will be translated to C)
    f = open(rpython_file,'w')
    #print code # Debug
    f.write(code)
    f.close()
    
    # 3 Non-RPython Version, disable RPYTHON FLAGS
    code = other_code
    code +=  "def main(argv):\n"
    code += "            from config import set_USE_RPYTHON_POPEN\n"
    code += "            set_USE_RPYTHON_POPEN(False)\n"
    code += main_code
    code += "def target(*args):\n"
    code += "   return main, None # returns the entry point\n"
    code += "\n"
    code += "if __name__ == '__main__':\n"
    code += "   import sys\n"
    code += "   main(sys.argv)\n"
    # 4. write code to temp file (Will NOT be translated to C)
    f = open(python_file,'w')
    #print code
    f.write(code)
    f.close()
    # 5. generate and call c Version
    print "running pypy to generate c verison..."
    import os
    from subprocess import Popen, PIPE
    if os.name=='nt':
        # Add pypy to your path if this line crashs
        Popen("python ../pypy/rpython/translator/goal/translate.py --batch tempA.py", shell=True, stdout=PIPE).stdout.read()
    else:
        pwd = Popen("pwd", shell=True, stdout=PIPE).stdout.read()
        assert pwd[-4:]=='pyB\n'
        Popen("PYTHONPATH="+PYPY_DIR+":. python ../pypy/rpython/translator/goal/translate.py --batch tempA.py", shell=True, stdout=PIPE).stdout.read()


# Run main_code with CPython (except RPython Flags) and Translated C Version
def execute_files(cl_argument=""):
    from subprocess import Popen, PIPE
    # 5. call python version
    print "running python version: "
    python_result = Popen("python tempB.py "+cl_argument, shell=True, stdout=PIPE).stdout.read()
    print "running c version: "
    c_result = Popen("./"+c_file+" "+cl_argument, shell=True, stdout=PIPE).stdout.read()
    return python_result.split('\n'), c_result.split('\n')
  
    
def clean_up():
    # 7. delete temp. file
    import os
    os.remove("tempA.py")
    os.remove("tempB.py")
    os.remove("tempA-c")



import pytest, config
@pytest.mark.skipif(config.USE_RPYTHON_CODE==False, reason="translation to c not possible using built-in frozenset type")     
class TestPyPyTranslationObjects():
   
    """
    Exception in thread "main" java.lang.StringIndexOutOfBoundsException: String index out of range: 0
    at java.lang.String.charAt(String.java:646)
    at java.lang.Character.codePointAt(Character.java:4866)
    at de.be4.classicalb.core.parser.BParser.readFile(BParser.java:183)
    at de.be4.classicalb.core.parser.BParser.parseFile(BParser.java:160)
    at de.be4.classicalb.core.parser.BParser.parseFile(BParser.java:144)
    at pyB.Main.main(Main.java:26)
    RPython traceback:
    File "implement.c", line 858, in main
    File "implement.c", line 121364, in my_exec
    """
    import pytest, config
    @pytest.mark.skipif(True, reason="pyB-c string_to_file/file_to_AST_str does not work for reasons unknown") 
    def test_pypy_parsing2(self):
        code =  """            
            from ast_nodes import AIntegerExpression, ALessPredicate
            from ast_nodes import AIdentifierExpression, APredicateParseUnit
            from environment import Environment
            from helpers import file_to_AST_str, string_to_file
            from parsing import parse_ast, str_ast_to_python_ast
            
            file_name = "input.txt"
            
            # Build AST:
            string_to_file("#PREDICATE 6>2", file_name)
            ast_string = file_to_AST_str(file_name)
            root = str_ast_to_python_ast(ast_string)
            
            res = isinstance(root, APredicateParseUnit)
            print int(res)
            
            return 0\n"""
        translate(code) 
        python_result, c_result = execute_files()
        clean_up()
        assert python_result == ['1', '']
        assert python_result == c_result
          
        
    def test_pypy_generators1(self):
        code =  """
            def g():
                yield -1
                yield 0
                yield +1
            generator = g()
            # not RPython:
            # import types
            # print type(generator) is types.GeneratorType
            for x in generator:
                print x
            
            return 0\n"""
        translate(code) 
        python_result, c_result = execute_files()
        clean_up()
        assert python_result == ['-1', '0', '1', '']
        assert python_result == c_result    


    def test_pypy_generators2(self):
        code =  """
            def make_generator():
                i = 0
                while True:
                    yield i
                    i = i +1  
            generator = make_generator()
            # not RPython:
            # import types
            # print type(generator) is types.GeneratorType
            y = 0
            for x in generator:
                print x
                y = y+1
                if y ==10:
                    break
            
            return 0\n"""
        translate(code) 
        python_result, c_result = execute_files()
        clean_up()
        assert python_result == ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '']
        assert python_result == c_result   
        

    # Uses inner function f
    import pytest, config
    @pytest.mark.xfail(reason="ValueError: RPython functions cannot create closures")
    def test_pypy_generators3(self):
        code =  """
            def g():
                yield -1
                yield 0
                yield +1
                
            def f():
                L = []
                generator = g()
                for x in generator:
                    L.append(x)
                return L
              
            S = f()
            for e in S:
                 print e
            return 0\n"""
        translate(code) 
        python_result, c_result = execute_files()
        clean_up()
        assert python_result == ['-1', '0', '1', '']
        assert python_result == c_result  

    def test_pypy_generators4(self):
        code =  """              
            S = f()
            for e in S:
                 print e
            return 0\n"""
        other_code = """def g():
            yield -1
            yield 0
            yield +1
def f():
            L = []
            generator = g()
            for x in generator:
                L.append(x)
            return L\n"""
        translate(code, other_code) 
        python_result, c_result = execute_files()
        clean_up()
        assert python_result == ['-1', '0', '1', '']
        assert python_result == c_result  


    def test_pypy_slicing(self):
        code =  """
            c = C(4)
            for x in c.L[:c.i]:
                print x         
            return 0\n"""
        
        other_code = """class C():
        def __init__(self, j):
            self.i = j
            self.L = [1,2,3,4,5]\n"""
        translate(code, other_code) 
        python_result, c_result = execute_files()
        clean_up()
        assert python_result == c_result  
 

    # Not RPython copy.deepcopy and copy.copy
    def test_pypy_clone(self):
        code =  """      
            a = SomeObject()
            import copy
            b = a.clone()
            a.x = 5
            res = b.x==a.x
            print int(res)
            return 0\n"""
            
        other_code = """class SomeObject():
        def __init__(self):
            self.x = 42
            
        def clone(self):
            return SomeObject()\n"""
        translate(code, other_code) 
        python_result, c_result = execute_files()
        clean_up()
        assert python_result == ['0', '']
        assert python_result == c_result       


    # repr and str not supported 
    import pytest, config
    @pytest.mark.xfail
    def test_pypy_print(self):
        code =  """      
            a = SomeObject()
            d = {}
            d[42] = a
            print "Hallo", d[42]
            return 0\n"""
            
        other_code = """class SomeObject():
        def __repr__(self):
            return "KNAMPF"\n"""
        translate(code, other_code) 
        python_result, c_result = execute_files()
        clean_up()
        assert python_result == ['Hallo KNAMPF', '']
        assert python_result == c_result       

        
    import pytest, config
    @pytest.mark.xfail
    def test_pypy_not_rpython_tuple(self):
        code =  """      
            t = tuple([1,2])
            print t[0]
            print t[1]
            return 0\n"""
        translate(code) 
        python_result, c_result = execute_files()
        clean_up()
        assert python_result == ['1','2', '']
        assert python_result == c_result  

    
    def test_pypy_reference_compare(self):
        code =  """      
            c0 = SomeObject()
            c1 = SomeObject()
            print int(c0==c1)
            print int(c0 is None)
            return 0\n"""
        
        other_code = """class SomeObject():
        pass\n"""
        translate(code, other_code) 
        python_result, c_result = execute_files()
        clean_up()
        assert python_result == ['0','0', '']
        assert python_result == c_result


    import pytest, config
    @pytest.mark.xfail
    def test_pypy_reference_compare_not_rpython(self):
        code =  """      
            c0 = SomeObject()
            c1 = SomeObject()
            print int(c0==c1)
            print int(c0==None)
            return 0\n"""
        
        other_code = """class SomeObject():
        pass\n"""
        translate(code, other_code) 
        python_result, c_result = execute_files()
        clean_up()
        assert python_result == ['0','0', '']
        assert python_result == c_result      
        
       
    def test_pypy_command_line_args(self):  
        code =  """        
            if len(argv)>=1:
                value = argv[1]
                if value is not None:
                    int_val = int(value)
                    result  = 2*int_val
                    print result
                    return 0
            return -1\n"""
        # TODO:
        translate(code) 
        python_result, c_result = execute_files(cl_argument="5")
        clean_up()
        assert python_result == ['10', '']
        assert python_result == c_result   
              
    
    # raw_input is not implemented  
    import pytest, config
    @pytest.mark.xfail  
    def test_pypy_raw_input(self):  
        code =  """        
            number = raw_input('number:')
            number = int(number)
            print 4*number
            return 0\n"""
        # TODO:
        translate(code) 
        python_result, c_result = execute_files()
        clean_up()
        assert python_result == ['', '']
        assert python_result == c_result               
              

    def test_pypy_mixed_dict_and_tuple(self):
        code =  """      
            d0 = {"a":(1,"hello"), None:(2,"world")}
            print d0.values()[0][0]
            print d0.values()[0][1]
            return 0\n"""
        
        translate(code) 
        python_result, c_result = execute_files()
        clean_up()
        assert python_result == ['1','hello','']
        assert python_result == c_result  
        