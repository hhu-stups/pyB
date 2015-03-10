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
    #import os
    #os.remove("temp.py")
    #os.remove("temp-c")
    # 6. compare c and python result
    return python_result.split('\n'), c_result.split('\n')


import pytest
@pytest.mark.skipif(True, reason="tekes to much time") 
class TestPyPyTranslationObjects():
    def test_pypy_genAST_expr_number1(self):
        code =  """def main(argv):
            from ast_nodes import AIntegerExpression
            node = AIntegerExpression(41)
            print node.intValue
            return 0\n"""
        python_result, c_result = translate(code) 
        assert python_result == c_result    
     
     
    def test_pypy_genAST_expr_number2(self):
        code =  """def main(argv):
            from ast_nodes import AIntegerExpression
            from interp import interpret
            node0 = AIntegerExpression(1)
            res = isinstance(node0, AIntegerExpression)
            print int(res)
            return 0\n"""
        python_result, c_result = translate(code) 
        assert python_result == c_result  


    def test_pypy_genAST_expr_number3(self):
        code =  """def main(argv):
            from ast_nodes import AIntegerExpression
            from interp import interpret
            node0 = AIntegerExpression(1)
            print interpret(node0, None)
            return 0\n"""
        python_result, c_result = translate(code) 
        assert python_result == c_result    
 
 
    # "branch" not merged. Real interpreter is currently not Rpython 
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
        assert python_result == c_result   


    # TODO: negative numbers
    def test_pypy_genAST_expr_number5(self):
        code =  """def main(argv):
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
        assert python_result == c_result
 
 
    def test_pypy_genAST_expr_number6(self):
        code =  """def main(argv):
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
        assert python_result == c_result

 
    def test_pypy_genAST_predicate1(self):
        code =  """def main(argv):
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
        assert python_result == c_result
 
 
    #PREDICATE 1<2 
    def test_pypy_genAST_predicate2(self):
        code =  """def main(argv):
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
        assert python_result == c_result
     
     
    # set config.USE_COSTUM_FROZENSET = True
    # Two states, one transition (setups_const --> init)
    #
    # MACHINE EMPTY
    # INVARIANT  1<2
    # END
    #
    import pytest, config
    @pytest.mark.xfail(config.USE_COSTUM_FROZENSET==False, reason="translation to c not possible using built-in frozenset type")  
    def test_pypy_genAST_bmachine1(self):
        code =  """def main(argv):
            from ast_nodes import AMachineHeader,AIntegerExpression, ALessPredicate
            from ast_nodes import AInvariantMachineClause, AAbstractMachineParseUnit
            from bmachine import BMachine
            from environment import Environment
            from interp import set_up_constants, exec_initialisation
            from parsing import parse_ast, remove_definitions
            from rpython_interp import interpret, eval_clause
            
            id0=AMachineHeader()
            id0.idName = "Empty "
            id1=AIntegerExpression(1 )
            id2=AIntegerExpression(2 )
            id3=ALessPredicate()
            id3.children.append(id1)
            id3.children.append(id2)
            id4=AInvariantMachineClause()
            id4.children.append(id3)
            id5=AAbstractMachineParseUnit()
            id5.children.append(id0)
            id5.children.append(id4)
            id5.type = "MACHINE "
            root = id5
            
            env = Environment()
            #mch = parse_ast(root, env) # has an (unused but seen) exec branch 
            assert isinstance(root, AAbstractMachineParseUnit)
            #mch = BMachine(root, remove_definitions) 
            #env.root_mch = mch
            #env.current_mch = mch #current mch
            #mch.add_all_visible_ops_to_env(env) # creating operation-objects and add them to bmchs and env
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
    def test_pypy_genAST_bmachine2(self):
        code =  """def main(argv):
            from ast_nodes import AMachineHeader,AIntegerExpression, ALessPredicate
            from ast_nodes import AInvariantMachineClause, AAbstractMachineParseUnit
            from ast_nodes import AIdentifierExpression, AIntervalExpression, ABelongPredicate
            from ast_nodes import AVariablesMachineClause, AAssignSubstitution, AInitialisationMachineClause
            from ast_nodes import AMinusOrSetSubtractExpression, AAbstractMachineParseUnit
            from environment import Environment
            from rpython_interp import interpret
            id0=AMachineHeader()
            id0.idName = "Lift "
            id1=AIdentifierExpression("floor ")
            id2=AVariablesMachineClause()
            id2.children.append(id1)
            id3=AIdentifierExpression("floor ")
            id4=AIntegerExpression(0 )
            id5=AIntegerExpression(99 )
            id6=AIntervalExpression()
            id6.children.append(id4)
            id6.children.append(id5)
            id7=ABelongPredicate()
            id7.children.append(id3)
            id7.children.append(id6)
            id8=AInvariantMachineClause()
            id8.children.append(id7)
            id9=AIdentifierExpression("floor ")
            id10=AIntegerExpression(4 )
            id11=AAssignSubstitution()
            id11.children.append(id9)
            id11.children.append(id10)
            id11.lhs_size = "1"
            id11.rhs_size = "1"
            id12=AInitialisationMachineClause()
            id12.children.append(id11)
            id13=AIdentifierExpression("floor ")
            id14=AIntegerExpression(99 )
            id15=ALessPredicate()
            id15.children.append(id13)
            id15.children.append(id14)
            id16=AIdentifierExpression("floor ")
            id17=AIdentifierExpression("floor ")
            id18=AIntegerExpression(1 )
            id19=AAddExpression()
            id19.children.append(id17)
            id19.children.append(id18)
            id20=AAssignSubstitution()
            id20.children.append(id16)
            id20.children.append(id19)
            id20.lhs_size = "1"
            id20.rhs_size = "1"
            id21=APreconditionSubstitution()
            id21.children.append(id15)
            id21.children.append(id20)
            id22=AOperation()
            id22.children.append(id21)
            id22.opName = "inc "
            id22.return_Num = 0
            id22.parameter_Num = 0
            id23=AIdentifierExpression("floor ")
            id24=AIdentifierExpression("floor ")
            id25=AIntegerExpression(1 )
            id26=AMinusOrSetSubtractExpression()
            id26.children.append(id24)
            id26.children.append(id25)
            id27=AAssignSubstitution()
            id27.children.append(id23)
            id27.children.append(id26)
            id27.lhs_size = "1"
            id27.rhs_size = "1"
            id28=ABlockSubstitution()
            id28.children.append(id27)
            id29=AOperation()
            id29.children.append(id28)
            id29.opName = "dec "
            id29.return_Num = 0
            id29.parameter_Num = 0
            id30=AOperationsMachineClause()
            id30.children.append(id22)
            id30.children.append(id29)
            id31=AAbstractMachineParseUnit()
            id31.children.append(id0)
            id31.children.append(id2)
            id31.children.append(id8)
            id31.children.append(id12)
            id31.children.append(id30)
            id31.type = "MACHINE "
            root = id31
            
            # TODO:
                          
            return 0\n"""
        python_result, c_result = translate(code) 
        assert python_result == c_result        


    # set config.USE_COSTUM_FROZENSET = True
    # set config.USE_COSTUM_FROZENSET = True
    import pytest, config
    @pytest.mark.xfail(config.USE_COSTUM_FROZENSET==False, reason="translation to c not possible using built-in frozenset type")    
    def test_pypy_create_env(self):
        code = """def main(argv):
            from environment import Environment
            env = Environment()
            return 0\n"""
        python_result, c_result = translate(code) 
        assert python_result == c_result   
  
    
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
   
    
    #from helpers import file_to_AST_str
    #ast_string = file_to_AST_str("exampels\Lift.mch")    
    import pytest, config
    @pytest.mark.xfail(True, reason="unssuported code on helpers import" )    
    def test_pypy_parsing1(self):
        code =  """def main(argv):
            import os
            from rpython.rlib.rfile import create_popen_file
            from config import JAR_DIR, EXAMPLE_DIR
            command_str = "java -Xms64m -Xmx1024m -cp "
            option_str = "-python "
            file_name_str = "Lift.mch"
            if os.name=='nt':
                path="examples\"
                command_str += ";"+JAR_DIR
                command_str += ";"+EXAMPLE_DIR
                command_str += ";. de.prob.cliparser.CliBParser " + option_str+path+file_name_str
            else:
                path="examples/"
                command_str += ":"+JAR_DIR
                command_str += ":"+EXAMPLE_DIR
                command_str += ":. de.prob.cliparser.CliBParser " + option_str+path+file_name_str
            file = create_popen_file(command_str, \"r\") 
            ast_string = \"\"
            ast_string = file.read()
            file.close()
            print ast_string
            return 0\n"""
        python_result, c_result = translate(code) 
        assert python_result == c_result   