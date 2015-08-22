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


#import pytest
#@pytest.mark.skipif(True, reason="takes to much time") 
import pytest, config
@pytest.mark.skipif(config.USE_RPYTHON_CODE==False, reason="translation to c not possible using built-in frozenset type")     
class TestPyPyTranslationObjects():
    def test_pypy_genAST_expr_number1(self):
        code =  """
            from ast_nodes import AIntegerExpression
            node = AIntegerExpression(41)
            print node.intValue
            return 0\n"""
        translate(code) 
        python_result, c_result = execute_files()
        clean_up()
        assert python_result == ['41', '']
        assert python_result == c_result    
     
     
    def test_pypy_genAST_expr_number2(self):
        code =  """
            from ast_nodes import AIntegerExpression
            from interp import interpret
            node0 = AIntegerExpression(1)
            res = isinstance(node0, AIntegerExpression)
            print int(res)
            return 0\n"""
        translate(code) 
        python_result, c_result = execute_files()
        clean_up()
        assert python_result == ['1', '']
        assert python_result == c_result  


    def test_pypy_genAST_expr_number3(self):
        code =  """
            from ast_nodes import AIntegerExpression
            from interp import interpret
            node0 = AIntegerExpression(1)
            print interpret(node0, None)
            return 0\n"""
        translate(code) 
        python_result, c_result = execute_files()
        clean_up()
        assert python_result == ['1', '']
        assert python_result == c_result    
 
 
    # "branch" not merged. Real interpreter is currently not Rpython 
    import pytest
    @pytest.mark.xfail 
    def test_pypy_genAST_expr_number4(self):
        code =  """
            from ast_nodes import AIntegerExpression, AAddExpression
            from interp import interpret
            node0 = AIntegerExpression(1)
            node1 = AIntegerExpression(2)
            node2 = AAddExpression()
            node2.children.append(node0)
            node2.children.append(node1)
            print interpret(node2, None) # not refactored
            return 0\n"""
        translate(code) 
        python_result, c_result = execute_files()
        clean_up()
        assert python_result == ['3', '']
        assert python_result == c_result   


    # TODO: negative numbers
    def test_pypy_genAST_expr_number5(self):
        code =  """
            from ast_nodes import AIntegerExpression, AAddExpression
            from ast_nodes import AMinusOrSetSubtractExpression, AMultOrCartExpression
            from ast_nodes import ADivExpression, AModuloExpression, APowerOfExpression
            from rpython_interp import interpret
            node0 = AIntegerExpression(4)
            node1 = AIntegerExpression(2)
            node2 = AAddExpression()
            node2.children.append(node0)
            node2.children.append(node1)
            w_int = interpret(node2, None)
            print w_int.ivalue
            
            node3 = AMinusOrSetSubtractExpression()
            node3.children.append(node0)
            node3.children.append(node1)
            w_int = interpret(node3, None)
            print w_int.ivalue
            
            node4 = AMultOrCartExpression()
            node4.children.append(node0)
            node4.children.append(node1)
            w_int = interpret(node4, None)
            print w_int.ivalue
            
            node5 = ADivExpression()
            node5.children.append(node0)
            node5.children.append(node1)
            w_int = interpret(node5, None)
            print w_int.ivalue
            
            node6 = AModuloExpression()
            node6.children.append(node0)
            node6.children.append(node1)
            w_int = interpret(node6, None)
            print w_int.ivalue
            
            node7 = APowerOfExpression()
            node7.children.append(node0)
            node7.children.append(node1)
            w_int = interpret(node7, None)
            print w_int.ivalue
                        
            return 0\n"""
        translate(code) 
        python_result, c_result = execute_files()
        clean_up()
        assert python_result == ['6', '2', '8', '2', '0', '16', '']
        assert python_result == c_result
 
 
    def test_pypy_genAST_expr_number6(self):
        code =  """
            from ast_nodes import AIntegerExpression, AAddExpression
            from ast_nodes import AMinusOrSetSubtractExpression, AMultOrCartExpression
            from rpython_interp import interpret
            node0 = AIntegerExpression(4)
            node1 = AIntegerExpression(2)
            node2 = AAddExpression()
            node2.children.append(node0)
            node2.children.append(node1)
            w_int = interpret(node2, None)
            print w_int.ivalue
            
            node3 = AMinusOrSetSubtractExpression()
            node3.children.append(node0)
            node3.children.append(node1)
            w_int = interpret(node3, None)
            print w_int.ivalue
            
            node4 = AMultOrCartExpression()
            node4.children.append(node3)
            node4.children.append(node2)
            w_int = interpret(node4, None)
            print w_int.ivalue
                        
            return 0\n"""
        translate(code) 
        python_result, c_result = execute_files()
        clean_up()
        assert python_result == ['6', '2', '12', '']
        assert python_result == c_result

 
    def test_pypy_genAST_predicate1(self):
        code =  """
            from ast_nodes import AIntegerExpression, ALessPredicate, AGreaterPredicate
            from ast_nodes import AGreaterEqualPredicate, ALessEqualPredicate, AConjunctPredicate
            from ast_nodes import ADisjunctPredicate, AImplicationPredicate
            from ast_nodes import AEquivalencePredicate, ANegationPredicate
            from rpython_interp import interpret
            node0 = AIntegerExpression(4)
            node1 = AIntegerExpression(2)
            
            node2 = ALessPredicate()
            node2.children.append(node0)
            node2.children.append(node1)
            res0 = interpret(node2, None)
            print int(res0.bvalue) 
            
            node3 = AGreaterPredicate()
            node3.children.append(node0)
            node3.children.append(node1)
            res1 = interpret(node3, None)
            print int(res1.bvalue)            

            node4 = AGreaterEqualPredicate()
            node4.children.append(node0)
            node4.children.append(node1)
            res2 = interpret(node4, None)
            print int(res2.bvalue) 
            
            node5 = ALessEqualPredicate()
            node5.children.append(node0)
            node5.children.append(node1)
            res3 = interpret(node5, None)
            print int(res3.bvalue)  
            
            node6 = AConjunctPredicate()
            node6.children.append(node2)
            node6.children.append(node3)
            res4 = interpret(node6, None)
            print int(res4.bvalue)
                        
            node7 = ADisjunctPredicate()
            node7.children.append(node2)
            node7.children.append(node3)
            res5 = interpret(node7, None)
            print int(res5.bvalue)   
            
            node8 = AImplicationPredicate()
            node8.children.append(node2)
            node8.children.append(node3)
            res6 = interpret(node8, None)
            print int(res6.bvalue)
                        
            node9 = AEquivalencePredicate()
            node9.children.append(node2)
            node9.children.append(node3)
            res7 = interpret(node9, None)
            print int(res7.bvalue)           

            node10 = ANegationPredicate()
            node10.children.append(node9)
            res8 = interpret(node10, None)
            print int(res8.bvalue)             
                                           
            return 0\n"""
        translate(code) 
        python_result, c_result = execute_files()
        clean_up()
        assert python_result == ['0', '1', '1', '0', '0', '1', '1', '0','1', '']
        assert python_result == c_result
 
 
    #PREDICATE 4<2 
    def test_pypy_genAST_predicate2(self):
        code =  """
            from ast_nodes import AIntegerExpression, ALessPredicate, APredicateParseUnit
            from rpython_interp import interpret
            node0 = AIntegerExpression(4)
            node1 = AIntegerExpression(2)
            
            node2 = ALessPredicate()
            node2.children.append(node0)
            node2.children.append(node1)
            node3 = APredicateParseUnit()
            node3.children.append(node2)
            res = interpret(node3, None)
            print int(res.bvalue)             
                                           
            return 0\n"""
        translate(code) 
        python_result, c_result = execute_files()
        clean_up()
        assert python_result == ['0', '']
        assert python_result == c_result
     

    #PREDICATE 1<2
    #@pytest.mark.xfail(True, reason="reason unknown. fails at reading input.txt")
    #def test_pypy_genAST_predicate3(self):
    #    code =  """
    #        from ast_nodes import AIntegerExpression, ALessPredicate, APredicateParseUnit
    #        from environment import Environment
    #        from helpers import file_to_AST_str, string_to_file
    #        from parsing import str_ast_to_python_ast
    #        from rpython_interp import interpret
    #        
    #        file_name = \"input.txt\"
    #        
    #        string_to_file(\"#PREDICATE 1<2\", file_name)
    #        ast_string = file_to_AST_str(file_name)
    #        root = str_ast_to_python_ast(ast_string)  
    #        
    #        env = Environment()
    #        res = interpret(root, env)
    #        print int(res)             
    #                                       
    #        return 0\n"""
    #    translate(code) 
    #    python_result, c_result = execute_files()
    #    clean_up()
    #    assert python_result == ['1', '']
    #    assert python_result == c_result

   
    # set config.USE_RPYTHON_CODE = True
    # Two states, one transition (setups_const --> init)
    #
    # MACHINE SIMPLE
    # INVARIANT  1<2
    # END
    #
    import pytest, config
    @pytest.mark.xfail(config.USE_RPYTHON_CODE==False, reason="translation to c not possible using built-in frozenset type")  
    def test_pypy_genAST_bmachine1(self):
        code =  """
            from ast_nodes import AMachineHeader,AIntegerExpression, ALessPredicate
            from ast_nodes import AInvariantMachineClause, AAbstractMachineParseUnit, AIdentifierExpression
            from bmachine import BMachine
            from environment import Environment
            from interp import set_up_constants, exec_initialisation
            from parsing import parse_ast, remove_definitions
            from rpython_interp import interpret
            
            # Build AST
            id0=AMachineHeader(childNum="0", idName="SIMPLE")
            id1=AIntegerExpression(1)
            id2=AIntegerExpression(2)
            id3=ALessPredicate()
            id3.children.append(id1)
            id3.children.append(id2)
            id4=AInvariantMachineClause()
            id4.children.append(id3)
            id5=AAbstractMachineParseUnit(childNum="2")
            id5.children.append(id0)
            id5.children.append(id4)
            #id5.type = "MACHINE "
            root = id5
            
            # Test
            env = Environment()
            # inlinded parse_ast method
            assert isinstance(root, AAbstractMachineParseUnit)
            #mch = BMachine(root, remove_definitions) 
            #mch.recursive_self_parsing(env)
            #env.root_mch = mch
            #env.current_mch = mch #current mch
            #mch.add_all_visible_ops_to_env(env) # creating operation-objects and add them to bmchs and env
            
            #type_check_bmch(root, env, mch)
            # inlinded arbitrary_init_machine
            #bstates = set_up_constants(root, env, mch, solution_file_read=False)
            #print len(bstates)
            #if len(bstates)>0:
            #    env.state_space.add_state(bstates[0])
            #bstates = exec_initialisation(root, env, mch, solution_file_read=False)
            #if len(bstates)>0:
            #    env.state_space.add_state(bstates[0]) 
            
            # useless idNode helps the rpython typer (reason unknown)
            idnode = AIdentifierExpression("foo")
            
            res = isinstance(root.children[1], AInvariantMachineClause)
            print int(res)
            res = interpret(root.children[1], env)
            print int(res.bvalue)
                          
            return 0\n"""
        translate(code) 
        python_result, c_result = execute_files()
        clean_up()
        assert python_result == ['1', '1', '']
        assert python_result == c_result



    # set parsing line 77: root = my_exec(string)
    # set config.USE_RPYTHON_CODE = True
    # Two states, one transition (setups_const --> init)
    #
    # MACHINE SIMPLE
    # INVARIANT  1<2
    # END
    #
    # 368.97 seconds 
    import pytest, config
    @pytest.mark.xfail(config.USE_RPYTHON_CODE==False, reason="translation to c not possible using built-in frozenset type")  
    def test_pypy_genAST_bmachine2(self):
        code =  """
            from ast_nodes import AMachineHeader,AIntegerExpression, ALessPredicate
            from ast_nodes import AInvariantMachineClause, AAbstractMachineParseUnit, AIdentifierExpression
            from bmachine import BMachine
            from environment import Environment
            from helpers import file_to_AST_str
            from interp import set_up_constants, exec_initialisation
            from parsing import parse_ast, remove_definitions, str_ast_to_python_ast
            from rpython_interp import interpret
            from typing import type_check_bmch
            
            if len(argv)<2:
                return 0
                
            # Build AST
            file_name = argv[1]
            ast_string = file_to_AST_str(file_name)
            root = str_ast_to_python_ast(ast_string)
            
            # Test
            env = Environment()
            
            # inlinded parse_ast
            assert isinstance(root, AAbstractMachineParseUnit)
            mch = BMachine(root, remove_definitions) 
            mch.recursive_self_parsing(env) # str.islower not RPYTHON
            env.root_mch = mch
            env.current_mch = mch #current mch
            mch.add_all_visible_ops_to_env(env) # creating operation-objects and add them to bmchs and env
            # end of inlinded parse_ast
            
            type_check_bmch(root, env, mch)
            # inlinded arbitrary_init_machine
            #bstates = set_up_constants(root, env, mch, solution_file_read=False)
            #print len(bstates)
            #if len(bstates)>0:
            #    env.state_space.add_state(bstates[0])
            #bstates = exec_initialisation(root, env, mch, solution_file_read=False)
            #if len(bstates)>0:
            #    env.state_space.add_state(bstates[0]) 
            
            # useless idNode helps the rpython typer (reason unknown)
            idnode = AIdentifierExpression("foo")
            
            res = isinstance(root.children[1], AInvariantMachineClause)
            print int(res)
            res = interpret(root.children[1], env)
            print int(res.bvalue)
                          
            return 0\n"""
        translate(code) 
        python_result, c_result = execute_files(cl_argument="examples/Simple.mch")
        clean_up()
        assert python_result == ['1', '1', '']
        assert python_result == c_result


    # set config.USE_RPYTHON_CODE = True
    #
    #
    # MACHINE Lift
    # CONCRETE_VARIABLES  floor
    # INVARIANT  floor : 0..99 /* NAT */
    # INITIALISATION floor := 4
    # OPERATIONS
    #   inc = PRE floor<99 THEN floor := floor + 1 END ;    
    #   dec = BEGIN floor := floor - 1 END 
    # END
    #
    import pytest, config
    @pytest.mark.xfail(config.USE_RPYTHON_CODE==False, reason="translation to c not possible using built-in frozenset type")  
    def test_pypy_genAST_bmachine3(self):
        code =  """
            from animation import calc_next_states
            from ast_nodes import AInvariantMachineClause, AAbstractMachineParseUnit, AOperationsMachineClause
            from bmachine import BMachine
            from environment import Environment
            from helpers import file_to_AST_str
            from parsing import parse_ast, remove_definitions, str_ast_to_python_ast
            from rpython_interp import interpret, exec_initialisation, set_up_constants
            from typing import type_check_bmch          

            if len(argv)<2:
                return 0
                
            # Build AST
            file_name = argv[1]
            ast_string = file_to_AST_str(file_name)
            root = str_ast_to_python_ast(ast_string)           
            
            # Test
            env = Environment()
            
            # inlinded parse_ast
            assert isinstance(root, AAbstractMachineParseUnit)
            mch = BMachine(root, remove_definitions) 
            mch.recursive_self_parsing(env) # str.islower not RPYTHON
            env.root_mch = mch
            env.current_mch = mch #current mch
            mch.add_all_visible_ops_to_env(env) # creating operation-objects and add them to bmchs and env
            # end of inlinded parse_ast
            
            type_check_bmch(root, env, mch)
            bstates = set_up_constants(root, env, mch, solution_file_read=False)
            if len(bstates)>0:
                env.state_space.add_state(bstates[0])
            bstates = exec_initialisation(root, env, mch, solution_file_read=False)
            if len(bstates)>0:
                env.state_space.add_state(bstates[0]) 
            
            res = isinstance(root.children[2], AInvariantMachineClause)
            print int(res)
            res = interpret(root.children[2], env)
            print int(res.bvalue)
            
                        
            res = isinstance(root.children[4], AOperationsMachineClause)
            print int(res)
            
            next_states = calc_next_states(env, mch)
            res = next_states[0].opName=="dec"
            print int(res)
            
            bstate = next_states[0].bstate
            env.state_space.add_state(bstate)
                                                     
            return 0\n"""
        translate(code) 
        python_result, c_result = execute_files(cl_argument="examples/Lift.mch")
        clean_up()
        assert python_result == ['1', '1', '1', '1', '']
        assert python_result == c_result        


    # TODO: one branch of the animation can not be translated yet
    import pytest, config
    @pytest.mark.xfail(config.USE_RPYTHON_CODE==False, reason="translation to c not possible using built-in frozenset type")  
    def test_pypy_genAST_model_checking(self):
        code =  """
            from animation import calc_next_states
            from ast_nodes import AInvariantMachineClause, AAbstractMachineParseUnit, AOperationsMachineClause
            from bmachine import BMachine
            from environment import Environment
            from helpers import file_to_AST_str
            from parsing import parse_ast, remove_definitions, str_ast_to_python_ast, remove_defs_and_parse_ast
            from rpython_interp import interpret, exec_initialisation, set_up_constants
            from typing import type_check_bmch, type_check_root_bmch
            
            print "WARNING: model checking still experimental"
            if len(argv)<2:
                return 0
                
            env = Environment()                                         # 1. create env.
            file_name_str = argv[1]                                     # 2. read filenames
            ast_string = file_to_AST_str(file_name_str)                 # 3. parse input-file to string
            #env.set_search_dir(file_name_str)
            root = str_ast_to_python_ast(ast_string)                    # 4. parse string to python ast                                                                
            parse_object = remove_defs_and_parse_ast(root, env)         # 5. replace defs and extern-functions inside mch and solution-file (if present) 
            if not isinstance(parse_object, BMachine):                                  
                print "Error: only model checking of b machines" 
                return -1

            assert isinstance(parse_object, BMachine)                   # 6. typecheck
            type_check_root_bmch(root, env, parse_object) # also checks all included, seen, used and extend
            mch = parse_object      

            bstates = set_up_constants(root, env, mch, solution_file_read=False)  # also evals properties
            # TODO: implement setup and init non determinism 
            if len(bstates)>0:
               print "WARNING: set up constants not supported yet" 
               return -1
            bstates = exec_initialisation(root, env, mch, solution_file_read=False)
            if not len(bstates)==1:
               print "WARNING: only one init. expected" 
               return -1
            if not mch.has_invariant_mc:
               print "WARNING: no invariant present" 
               return -1  
     
            env.state_space.set_current_state(bstates[0])
            while not env.state_space.empty():                          # 7. model check  
                if not interpret(mch.aInvariantMachineClause, env):
                    print "WARNING: invariant violation found after checking", len(env.state_space.seen_states),"states"
                    #print env.state_space.history
                    return -1
                next_states = calc_next_states(env, mch)
                env.state_space.undo()
                for tup in next_states:
                    bstate = tup.bstate
                    #bstate.print_bstate()
                    if not env.state_space.is_seen_state(bstate):
                        env.state_space.set_current_state(bstate)  
            print "checked",len(env.state_space.seen_states),"states. No invariant violation found."

            return 0\n"""
        translate(code) 
        python_result, c_result = execute_files(cl_argument="examples/Lift2.mch")
        clean_up()
        assert python_result == ['WARNING: model checking still experimental', 'checked 100 states. No invariant violation found.','']
        assert python_result == c_result   
        

    # set config.USE_RPYTHON_CODE = True
    # set config.USE_RPYTHON_CODE = True
    import pytest, config
    @pytest.mark.xfail(config.USE_RPYTHON_CODE==False, reason="translation to c not possible using built-in frozenset type")    
    def test_pypy_create_env0(self):
        code = """
            from environment import Environment
            env = Environment()
            return 0\n"""
        translate(code) 
        python_result, c_result = execute_files()
        clean_up()
        assert python_result == c_result   
 

    # TODO: implement me
    # set config.USE_RPYTHON_CODE = True
    # set config.USE_RPYTHON_CODE = True
    #PREDICATE x<2
    import pytest, config
    @pytest.mark.xfail(config.USE_RPYTHON_CODE==False, reason="translation to c not possible using built-in frozenset type")     
    def test_pypy_use_env1(self):
        code = """
            from ast_nodes import AMachineHeader,AIntegerExpression, ALessPredicate
            from ast_nodes import AIdentifierExpression, APredicateParseUnit
            from bmachine import BMachine
            from environment import Environment
            from helpers import file_to_AST_str, string_to_file
            from parsing import parse_ast, remove_definitions, str_ast_to_python_ast
            from rpython_interp import interpret, exec_initialisation
            from rpython_b_objmodel import W_Integer
    
            if len(argv)<2:
                return 0
                
            # Build AST
            file_name = argv[1]
            ast_string = file_to_AST_str(file_name)
            root = str_ast_to_python_ast(ast_string)
        
            # Test
            env = Environment()
            env.add_ids_to_frame(["x"])
            integer_value = W_Integer(1)
            env.set_value(\"x\", integer_value)
            res =  interpret(root, env) 
            print int(res.bvalue)
            
            return 0\n"""
        translate(code) 
        python_result, c_result = execute_files(cl_argument="examples/simple_pred2.def")
        clean_up()
        assert python_result == ['1', '']
        assert python_result == c_result   


    # TODO: implement me
    # set config.USE_RPYTHON_CODE = True
    # set config.USE_RPYTHON_CODE = True
    #
    #
    # MACHINE Simple2
    # CONCRETE_VARIABLES  floor
    # INVARIANT  floor>0
    # INITIALISATION floor := 4
    # END
    import pytest, config
    @pytest.mark.xfail(config.USE_RPYTHON_CODE==False, reason="translation to c not possible using built-in frozenset type")     
    def test_pypy_use_env2(self):
        code = """
            from ast_nodes import AMachineHeader,AIntegerExpression, ALessPredicate
            from ast_nodes import AIdentifierExpression, APredicateParseUnit
            from ast_nodes import AInvariantMachineClause, AAbstractMachineParseUnit
            from ast_nodes import AVariablesMachineClause
            from bmachine import BMachine
            from environment import Environment
            from helpers import file_to_AST_str
            from parsing import parse_ast, remove_definitions, str_ast_to_python_ast
            from rpython_interp import interpret, exec_initialisation
            from rpython_b_objmodel import W_Integer
            from typing import type_check_bmch
            
            if len(argv)<2:
                return 0
                
            # Build AST
            file_name = argv[1]
            ast_string = file_to_AST_str(file_name)
            root = str_ast_to_python_ast(ast_string)
        
            # Test
            env = Environment()
            mch = parse_ast(root, env)
            type_check_bmch(root, env, mch) # also checks all included, seen, used and extend
            env.add_ids_to_frame(["floor"])
            integer_value = W_Integer(4)
            env.set_value("floor", integer_value)
            
            res = isinstance(root.children[2], AInvariantMachineClause)
            print int(res)
            res = interpret(root.children[2], env) 
            print int(res.bvalue) 
            
            return 0\n"""
        translate(code) 
        python_result, c_result = execute_files(cl_argument="examples/Simple2.mch")
        clean_up()
        assert python_result == ['1', '1', '']
        assert python_result == c_result   

    
    def test_pypy_check_frozenset_impl(self):
        code = """
            from rpython_b_objmodel import frozenset
            S = frozenset([1,2,3])
            for e in S:
                print e
            # maybe the next three will work with wrapped types + type hirachy
            #T = frozenset(['a','b','c'])
            #print 1 in S
            #print 4 in S
            return 0\n"""
        translate(code) 
        python_result, c_result = execute_files()
        clean_up()
        assert python_result == c_result  
   
      
    import pytest, config
    @pytest.mark.xfail(config.USE_RPYTHON_POPEN==False, reason="unssuported pypy import on python run" )    
    def test_pypy_parsing1(self):
        code =  """
            from helpers import file_to_AST_str
            ast_string = file_to_AST_str(\"examples/Lift.mch\")
            print ast_string
            return 0\n"""
        translate(code) 
        python_result, c_result = execute_files()
        clean_up()
        assert python_result == c_result


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


    # MACHINE SIMPLE
    # INVARIANT  1<2
    # END
    #
    import pytest, config
    @pytest.mark.xfail(config.USE_RPYTHON_POPEN==False, reason="unsupported pypy import on python run" )    
    def test_pypy_parsing3(self):
        code =  """            
            from ast_nodes import AMachineHeader,AIntegerExpression, ALessPredicate
            from ast_nodes import AInvariantMachineClause, AAbstractMachineParseUnit
            from bmachine import BMachine
            from environment import Environment
            from helpers import file_to_AST_str
            from interp import set_up_constants, exec_initialisation
            from parsing import parse_ast, remove_definitions, str_ast_to_python_ast
            from rpython_interp import interpret
            from typing import type_check_bmch
                 
            if len(argv)<2:
                return 0
                
            # Build AST
            file_name = argv[1]
            ast_string = file_to_AST_str(file_name)
            root = str_ast_to_python_ast(ast_string)  
            
            res = isinstance(root, AAbstractMachineParseUnit)
            print int(res)
            
            res = isinstance(root.children[0], AInvariantMachineClause)
            print int(res) #False
            
            res = isinstance(root.children[1], AInvariantMachineClause)
            print int(res)
            
            
            return 0\n"""
        translate(code) 
        python_result, c_result = execute_files(cl_argument="examples/Simple.mch")
        clean_up()
        assert python_result == ['1', '0','1', '']
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
              

        