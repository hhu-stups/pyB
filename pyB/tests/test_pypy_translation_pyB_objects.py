# assumes pypy checkout at PYPYDIR
from config import USE_COSTUM_FROZENSET

file_name = "input.txt"
PYPY_DIR  = "/Users/johnwitulski/witulski/git/pyB/pypy/" # change this line to your checkout



# Run main_code with CPython (except RPython Flags) and Translated C Version
def translate(main_code, other_code=""):
    # 1. Generate Python code as String
    code = other_code
    code +=  "def main(argv):\n"
    # modifying global variables is NOT RPYTHON
    #code += "            from config import set_USE_COSTUM_FROZENSET\n"
    #code += "            set_USE_COSTUM_FROZENSET(True)\n"
    code += main_code
    code += "def target(*args):\n"
    code += "   return main, None # returns the entry point\n"
    code += "\n"
    code += "if __name__ == '__main__':\n"
    code += "   import sys\n"
    code += "   main(sys.argv)\n"
    # 2 write code to temp file (Will be translated to C)
    f = open("tempA.py",'w')
    #print code
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
    f = open("tempB.py",'w')
    f.write(code)
    f.close()
    from subprocess import Popen, PIPE
    # 5. call python version
    python_result = Popen("python tempB.py", shell=True, stdout=PIPE).stdout.read()
    # 6. generate and call c Version
    import os
    if os.name=='nt':
        # Add pypy to your path if this line crashs
        Popen("python ../pypy/rpython/translator/goal/translate.py tempA.py", shell=True, stdout=PIPE).stdout.read()
    else:
        pwd = Popen("pwd", shell=True, stdout=PIPE).stdout.read()
        assert pwd[-4:]=='pyB\n'
        Popen("PYTHONPATH="+PYPY_DIR+":. python ../pypy/rpython/translator/goal/translate.py tempA.py", shell=True, stdout=PIPE).stdout.read()
    c_result = Popen("./tempA-c", shell=True, stdout=PIPE).stdout.read()
    # 7. delete temp. file
    os.remove("tempA.py")
    os.remove("tempB.py")
    os.remove("tempA-c")
    # 8. return c and python result
    return python_result.split('\n'), c_result.split('\n')


#import pytest
#@pytest.mark.skipif(True, reason="takes to much time") 
class TestPyPyTranslationObjects():
    def test_pypy_genAST_expr_number1(self):
        code =  """
            from ast_nodes import AIntegerExpression
            node = AIntegerExpression(41)
            print node.intValue
            return 0\n"""
        python_result, c_result = translate(code) 
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
        python_result, c_result = translate(code) 
        assert python_result == ['1', '']
        assert python_result == c_result  


    def test_pypy_genAST_expr_number3(self):
        code =  """
            from ast_nodes import AIntegerExpression
            from interp import interpret
            node0 = AIntegerExpression(1)
            print interpret(node0, None)
            return 0\n"""
        python_result, c_result = translate(code) 
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
        python_result, c_result = translate(code) 
        assert python_result == ['3', '']
        assert python_result == c_result   


    # TODO: negative numbers
    def test_pypy_genAST_expr_number5(self):
        code =  """
            from ast_nodes import AIntegerExpression, AAddExpression
            from ast_nodes import AMinusOrSetSubtractExpression, AMultOrCartExpression
            from ast_nodes import ADivExpression, AModuloExpression, APowerOfExpression
            from rpython_interp import eval_int_expression
            node0 = AIntegerExpression(4)
            node1 = AIntegerExpression(2)
            node2 = AAddExpression()
            node2.children.append(node0)
            node2.children.append(node1)
            print eval_int_expression(node2, None)
            
            node3 = AMinusOrSetSubtractExpression()
            node3.children.append(node0)
            node3.children.append(node1)
            print eval_int_expression(node3, None)
            
            node4 = AMultOrCartExpression()
            node4.children.append(node0)
            node4.children.append(node1)
            print eval_int_expression(node4, None)
            
            node5 = ADivExpression()
            node5.children.append(node0)
            node5.children.append(node1)
            print eval_int_expression(node5, None)
            
            node6 = AModuloExpression()
            node6.children.append(node0)
            node6.children.append(node1)
            print eval_int_expression(node6, None)
            
            node7 = APowerOfExpression()
            node7.children.append(node0)
            node7.children.append(node1)
            print eval_int_expression(node7, None)
                        
            return 0\n"""
        python_result, c_result = translate(code) 
        assert python_result == ['6', '2', '8', '2', '0', '16', '']
        assert python_result == c_result
 
 
    def test_pypy_genAST_expr_number6(self):
        code =  """
            from ast_nodes import AIntegerExpression, AAddExpression
            from ast_nodes import AMinusOrSetSubtractExpression, AMultOrCartExpression
            from rpython_interp import eval_int_expression
            node0 = AIntegerExpression(4)
            node1 = AIntegerExpression(2)
            node2 = AAddExpression()
            node2.children.append(node0)
            node2.children.append(node1)
            print eval_int_expression(node2, None)
            
            node3 = AMinusOrSetSubtractExpression()
            node3.children.append(node0)
            node3.children.append(node1)
            print eval_int_expression(node3, None)
            
            node4 = AMultOrCartExpression()
            node4.children.append(node3)
            node4.children.append(node2)
            print eval_int_expression(node4, None)
                        
            return 0\n"""
        python_result, c_result = translate(code) 
        assert python_result == ['6', '2', '12', '']
        assert python_result == c_result

 
    def test_pypy_genAST_predicate1(self):
        code =  """
            from ast_nodes import AIntegerExpression, ALessPredicate, AGreaterPredicate
            from ast_nodes import AGreaterEqualPredicate, ALessEqualPredicate, AConjunctPredicate
            from ast_nodes import ADisjunctPredicate, AImplicationPredicate
            from ast_nodes import AEquivalencePredicate, ANegationPredicate
            from rpython_interp import eval_bool_expression
            node0 = AIntegerExpression(4)
            node1 = AIntegerExpression(2)
            
            node2 = ALessPredicate()
            node2.children.append(node0)
            node2.children.append(node1)
            res = eval_bool_expression(node2, None)
            print int(res) 
            
            node3 = AGreaterPredicate()
            node3.children.append(node0)
            node3.children.append(node1)
            res = eval_bool_expression(node3, None)
            print int(res)            

            node4 = AGreaterEqualPredicate()
            node4.children.append(node0)
            node4.children.append(node1)
            res = eval_bool_expression(node4, None)
            print int(res) 
            
            node5 = ALessEqualPredicate()
            node5.children.append(node0)
            node5.children.append(node1)
            res = eval_bool_expression(node5, None)
            print int(res)  
            
            node6 = AConjunctPredicate()
            node6.children.append(node2)
            node6.children.append(node3)
            res = eval_bool_expression(node6, None)
            print int(res)
                        
            node7 = ADisjunctPredicate()
            node7.children.append(node2)
            node7.children.append(node3)
            res = eval_bool_expression(node7, None)
            print int(res)   
            
            node8 = AImplicationPredicate()
            node8.children.append(node2)
            node8.children.append(node3)
            res = eval_bool_expression(node8, None)
            print int(res)
                        
            node9 = AEquivalencePredicate()
            node9.children.append(node2)
            node9.children.append(node3)
            res = eval_bool_expression(node9, None)
            print int(res)           

            node10 = ANegationPredicate()
            node10.children.append(node9)
            res = eval_bool_expression(node10, None)
            print int(res)             
                                           
            return 0\n"""
        python_result, c_result = translate(code)
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
            print int(res)             
                                           
            return 0\n"""
        python_result, c_result = translate(code) 
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
    #    python_result, c_result = translate(code) 
    #    assert python_result == ['1', '']
    #    assert python_result == c_result

   
    # set config.USE_COSTUM_FROZENSET = True
    # Two states, one transition (setups_const --> init)
    #
    # MACHINE SIMPLE
    # INVARIANT  1<2
    # END
    #
    import pytest, config
    @pytest.mark.xfail(config.USE_COSTUM_FROZENSET==False, reason="translation to c not possible using built-in frozenset type")  
    def test_pypy_genAST_bmachine1(self):
        code =  """
            from ast_nodes import AMachineHeader,AIntegerExpression, ALessPredicate
            from ast_nodes import AInvariantMachineClause, AAbstractMachineParseUnit
            from bmachine import BMachine
            from environment import Environment
            from interp import set_up_constants, exec_initialisation
            from parsing import parse_ast, remove_definitions
            from rpython_interp import interpret, eval_clause
            
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
            
            res = isinstance(root.children[1], AInvariantMachineClause)
            print int(res)
            res = eval_clause(root.children[1], env)
            print int(res)
                          
            return 0\n"""
        python_result, c_result = translate(code) 
        assert python_result == ['1', '1', '']
        assert python_result == c_result



    # set parsing line 77: root = my_exec(string)
    # set config.USE_COSTUM_FROZENSET = True
    # Two states, one transition (setups_const --> init)
    #
    # MACHINE SIMPLE
    # INVARIANT  1<2
    # END
    #
    # 368.97 seconds 
    import pytest, config
    @pytest.mark.xfail(config.USE_COSTUM_FROZENSET==False, reason="translation to c not possible using built-in frozenset type")  
    def test_pypy_genAST_bmachine2(self):
        code =  """
            from ast_nodes import AMachineHeader,AIntegerExpression, ALessPredicate
            from ast_nodes import AInvariantMachineClause, AAbstractMachineParseUnit
            from bmachine import BMachine
            from environment import Environment
            from helpers import file_to_AST_str
            from interp import set_up_constants, exec_initialisation
            from parsing import parse_ast, remove_definitions, str_ast_to_python_ast
            from rpython_interp import interpret, eval_clause
            from typing import type_check_bmch
            
            
            # Build AST
            ast_string = file_to_AST_str(\"examples/Simple.mch\")
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
            
            res = isinstance(root.children[1], AInvariantMachineClause)
            print int(res)
            res = eval_clause(root.children[1], env)
            print int(res)
                          
            return 0\n"""
        python_result, c_result = translate(code) 
        assert python_result == ['1', '1', '']
        assert python_result == c_result


    # set config.USE_COSTUM_FROZENSET = True
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
    @pytest.mark.xfail(config.USE_COSTUM_FROZENSET==False, reason="translation to c not possible using built-in frozenset type")  
    def test_pypy_genAST_bmachine3(self):
        code =  """
            from ast_nodes import AMachineHeader,AIntegerExpression, ALessPredicate
            from ast_nodes import AInvariantMachineClause, AAbstractMachineParseUnit
            from ast_nodes import AIdentifierExpression, AIntervalExpression, AMemberPredicate
            from ast_nodes import AVariablesMachineClause, AAssignSubstitution, AInitialisationMachineClause
            from ast_nodes import AMinusOrSetSubtractExpression, AAbstractMachineParseUnit
            from ast_nodes import AAddExpression, APreconditionSubstitution, AOperation
            from ast_nodes import ABlockSubstitution, AOperationsMachineClause
            from bmachine import BMachine
            from environment import Environment
            from helpers import file_to_AST_str
            from parsing import parse_ast, remove_definitions, str_ast_to_python_ast
            from rpython_interp import interpret, eval_clause, exec_initialisation
            from typing import type_check_bmch          

            # Build AST
            ast_string = file_to_AST_str(\"examples/Lift.mch\")
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
            
            #bstates = set_up_constants(root, env, mch, solution_file_read=False)
            #if len(bstates)>0:
            #    env.state_space.add_state(bstates[0])
            bstates = exec_initialisation(root, env, mch, solution_file_read=False)
            if len(bstates)>0:
                env.state_space.add_state(bstates[0]) 
            
            res = isinstance(root.children[2], AInvariantMachineClause)
            print int(res)
            res = eval_clause(root.children[2], env)
            print int(res)
            
            type_check_bmch(root, env, mch)
                                                  
            return 0\n"""
        python_result, c_result = translate(code)
        print python_result 
        assert python_result == c_result        


    # set config.USE_COSTUM_FROZENSET = True
    # set config.USE_COSTUM_FROZENSET = True
    import pytest, config
    @pytest.mark.xfail(config.USE_COSTUM_FROZENSET==False, reason="translation to c not possible using built-in frozenset type")    
    def test_pypy_create_env(self):
        code = """
            from environment import Environment
            env = Environment()
            return 0\n"""
        python_result, c_result = translate(code) 
        assert python_result == c_result   


    # TODO: implement me
    # set config.USE_COSTUM_FROZENSET = True
    # set config.USE_COSTUM_FROZENSET = True
    import pytest, config
    @pytest.mark.xfail(config.USE_COSTUM_FROZENSET==False, reason="translation to c not possible using built-in frozenset type")     
    def test_pypy_use_env(self):
        code = """
            from ast_nodes import AMachineHeader,AIntegerExpression, ALessPredicate
            from ast_nodes import AIdentifierExpression, APredicateParseUnit
            from bmachine import BMachine
            from environment import Environment
            from helpers import file_to_AST_str
            from parsing import parse_ast, remove_definitions, str_ast_to_python_ast
            from rpython_interp import interpret, eval_clause, exec_initialisation
            # Build AST:
            string_to_file("#PREDICATE 6>x", file_name)
            ast_string = file_to_AST_str(file_name)
            root = str_ast_to_python_ast(ast_string)
        
            # Test
            env = Environment()
            env.add_ids_to_frame(["x"])
            integer_value = W_Integer(1)
            env.set_value(\"x\", integer_value)
            res =  interpret(root, env) 
            print int(res)
            return 0\n"""
        python_result, c_result = translate(code) 
        assert python_result == ['1', '']
        assert python_result == c_result   


    # TODO: implement me
    # set config.USE_COSTUM_FROZENSET = True
    # set config.USE_COSTUM_FROZENSET = True
    #
    #
    # MACHINE Simple2
    # CONCRETE_VARIABLES  floor
    # INVARIANT  floor>0
    # INITIALISATION floor := 4
    import pytest, config
    @pytest.mark.xfail(config.USE_COSTUM_FROZENSET==False, reason="translation to c not possible using built-in frozenset type")     
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
            from rpython_interp import interpret, eval_clause, exec_initialisation
            from rpython_b_objmodel import W_Integer
            from typing import type_check_bmch
            
            # Build AST:
            ast_string = file_to_AST_str(\"examples/Simple2.mch\")
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
            res = eval_clause(root.children[2], env) 
            print int(res) 
            
            return 0\n"""
        python_result, c_result = translate(code) 
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
        python_result, c_result = translate(code) 
        assert python_result == c_result  
   
      
    import pytest, config
    @pytest.mark.xfail(config.USE_RPYTHON_POPEN==False, reason="unssuported pypy import on python run" )    
    def test_pypy_parsing1(self):
        code =  """
            from helpers import file_to_AST_str
            ast_string = file_to_AST_str(\"examples/Lift.mch\")
            print ast_string
            return 0\n"""
        python_result, c_result = translate(code) 
        assert python_result == c_result
    

    def test_pypy_generators(self):
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
        python_result, c_result = translate(code) 
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
        python_result, c_result = translate(code, other_code) 
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
        python_result, c_result = translate(code,other_code) 
        assert python_result == ['0', '']
        assert python_result == c_result       
     
        
    import pytest, config
    @pytest.mark.xfail
    def test_pypy_not_rpython_tuple(self):
        code =  """      
            t = tuple([1,2])
            print t[0]
            print t[1]
            return 0\n"""
        python_result, c_result = translate(code) 
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
        python_result, c_result = translate(code, other_code) 
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
        python_result, c_result = translate(code, other_code) 
        assert python_result == ['0','0', '']
        assert python_result == c_result          
        