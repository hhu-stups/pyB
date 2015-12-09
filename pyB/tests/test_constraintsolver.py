# -*- coding: utf-8 -*-
from ast_nodes import *
from btypes import *
from bexceptions import ValueNotInDomainException
from config import TOO_MANY_ITEMS
from constraintsolver import Constraint, compute_using_external_solver, _analyze_predicates, compute_constrained_domains
from environment import Environment
from helpers import file_to_AST_str, string_to_file
from interp import interpret
from parsing import str_ast_to_python_ast
from util import type_with_known_types, get_type_by_name



from config import USE_RPYTHON_CODE
if USE_RPYTHON_CODE:
     from rpython_b_objmodel import frozenset

file_name = "input.txt"

class TestConstraintSolver():
    def test_constraint_forAll(self):
        # !x.(P=>Q)
        # Build AST:
        string_to_file("#PREDICATE !(z).((z:NAT & z>2 & z<5) => (z>1 & z<=10))", file_name)
        ast_string = file_to_AST_str(file_name)
        root = str_ast_to_python_ast(ast_string)

        # Test
        env = Environment()
        type_with_known_types(root, env, [], [""])
        assert isinstance(get_type_by_name(env, "z"), IntegerType)
        unqantPred = root.children[0]
        assert isinstance(unqantPred, AForallPredicate)
        varList = unqantPred.children[0:-1]
        P = unqantPred.children[-1].children[0]
        Q = unqantPred.children[-1].children[1]
        assert isinstance(P, Predicate)
        assert isinstance(Q, Predicate)
        #env._min_int = -2**32
        #env._max_int = 2**32
        domain = compute_using_external_solver(P, env, varList)
        assert frozenset([x["z"] for x in domain])==frozenset([3,4])


    def test_constraint_forAll2(self):
        # !x.(P=>Q)
        # Build AST:
        string_to_file("#PREDICATE f={(1,7),(2,8),(3,9)} & S={1,2,3} & !(x,y).(y:INTEGER &(x:S & f(x)<y) & y<42 =>y:T)", file_name)
        ast_string = file_to_AST_str(file_name)
        root = str_ast_to_python_ast(ast_string)
        
        # Test
        env = Environment()
        lst = [("S", PowerSetType(IntegerType())),("f", PowerSetType(CartType(PowerSetType(IntegerType()), PowerSetType(IntegerType()))))]
        type_with_known_types(root, env, lst, ["T"])
        assert isinstance(get_type_by_name(env, "x"), IntegerType)
        assert isinstance(get_type_by_name(env, "y"), IntegerType)
        assert isinstance(get_type_by_name(env, "T"), PowerSetType)
        assert isinstance(get_type_by_name(env, "T").data, IntegerType)
        env.add_ids_to_frame(["f","S","T"])
        env.set_value("f", frozenset([(1,7),(2,8),(3,9)]))
        env.set_value("S", frozenset([1,2,3]))
        env.set_value("T", frozenset(range(10,42)))
        env._min_int = -2**8
        env._max_int = 2**8
        unqantPred = root.children[0].children[1]
        assert isinstance(unqantPred, AForallPredicate)
        varList = unqantPred.children[0:-1]
        P = unqantPred.children[-1].children[0]
        Q = unqantPred.children[-1].children[1]
        domain = compute_using_external_solver(P, env, varList)
        assert frozenset([x["x"] for x in domain])==frozenset([1,2,3])
        domain = compute_using_external_solver(P, env, varList)
        assert frozenset([x["y"] for x in domain])==frozenset(range(8,42))
        


    def test_constraint_ex(self):
        # #x.(P & Q)
        # Build AST:
        string_to_file("#PREDICATE #(z).((z:NAT & z>=2 & z<=5) & (z>1 & z<=10))", file_name)
        ast_string = file_to_AST_str(file_name)
        root = str_ast_to_python_ast(ast_string)

        # Test
        env = Environment()
        type_with_known_types(root, env, [], [""])
        assert isinstance(get_type_by_name(env, "z"), IntegerType)
        exqantPred = root.children[0]
        assert isinstance(exqantPred, AExistsPredicate)
        varList = exqantPred.children[0:-1]
        P = exqantPred.children[-1].children[0]
        Q = exqantPred.children[-1].children[1]
        assert isinstance(P, Predicate)
        assert isinstance(Q, Predicate)
        domain = compute_using_external_solver(P, env, varList)
        assert frozenset([x["z"] for x in domain])== frozenset([2,3,4,5])

    
    def test_constraint_lambda(self):
        # %x.(P|E)
        # Build AST:
        string_to_file("#PREDICATE card(%x.(x:1..100|x*x))=100", file_name)
        ast_string = file_to_AST_str(file_name)
        root = str_ast_to_python_ast(ast_string)
        
        # Test
        env = Environment()
        type_with_known_types(root, env, [], [""])
        assert isinstance(get_type_by_name(env, "x"), IntegerType)
        lambdaexpr = root.children[0].children[0].children[0] 
        assert isinstance(lambdaexpr, ALambdaExpression)
        varList = lambdaexpr.children[0:-2]
        P = lambdaexpr.children[-2]
        E = lambdaexpr.children[-1]
        assert isinstance(P, Predicate)
        assert isinstance(E, Expression)
        env._min_int = -2**8
        env._max_int = 2**8
        domain = compute_using_external_solver(P, env, varList)
        #print domain
        assert frozenset([x["x"] for x in domain])== frozenset(range(1,100+1))



    def test_constraint_lambda2(self):
        # %x.(P|E)
        # Build AST:
        string_to_file("#PREDICATE length: STRING --> INTEGER & length = %x.(x:STRING|42)", file_name)
        ast_string = file_to_AST_str(file_name)
        root = str_ast_to_python_ast(ast_string)

        # Test
        env = Environment()
        type_with_known_types(root, env, [], ["length"])
        assert isinstance(get_type_by_name(env, "x"), StringType)
        lambdaexpr = root.children[0].children[1].children[1] 
        assert isinstance(lambdaexpr, ALambdaExpression)
        varList = lambdaexpr.children[0:-2]      
        P = lambdaexpr.children[-2]
        E = lambdaexpr.children[-1]
        assert isinstance(P, Predicate)
        assert isinstance(E, Expression)
        env._min_int = -2**8
        env._max_int = 2**8
        env.all_strings = ['abc', '', 'hello']
        domain = compute_using_external_solver(P, env, varList)
        sol = frozenset([x["x"] for x in domain])
        assert sol==frozenset(env.all_strings)    
        
         
              
    def test_constraint_set_comp(self):
        # {x|P}
        # Build AST:
        string_to_file("#PREDICATE card({x|x:NAT & x=12})=1", file_name)
        ast_string = file_to_AST_str(file_name)
        root = str_ast_to_python_ast(ast_string)

        # Test
        env = Environment()
        type_with_known_types(root, env, [], [""])
        assert isinstance(get_type_by_name(env, "x"), IntegerType)
        setexpr = root.children[0].children[0].children[0] 
        assert isinstance(setexpr, AComprehensionSetExpression)
        varList = setexpr.children[0:-1]
        P = setexpr.children[-1]
        assert isinstance(P, Predicate)
        env._min_int = -2**8
        env._max_int = 2**8
        domain = compute_using_external_solver(P, env, varList)
        assert frozenset([x["x"] for x in domain])==frozenset([12])

        
    #TODO: write test of union which defines bound vars via other quantified predicates.
    # see C578.EML.014/CF_ZMS_AUM_2
    # implement recursion: compute_constrained_domains using compute_constrained_domains in case 2
    def test_constraint_pi(self):
        # PI (z).(P|E)
        # Build AST:
        string_to_file("#PREDICATE PI(x).(x:-4..4 & x/=0 | x)=576", file_name)
        ast_string = file_to_AST_str(file_name)
        root = str_ast_to_python_ast(ast_string)

        # Test
        env = Environment()
        type_with_known_types(root, env, [], [""])
        assert isinstance(get_type_by_name(env, "x"), IntegerType)
        setexpr = root.children[0].children[0]
        assert isinstance(setexpr, AGeneralProductExpression)
        varList = setexpr.children[0:-2]
        P = setexpr.children[-2]
        E = setexpr.children[-1]
        assert isinstance(P, Predicate)
        env._min_int = -2**8
        env._max_int = 2**8
        domain = compute_using_external_solver(P, env, varList)
        assert frozenset([x["x"] for x in domain])==frozenset([-4,-3,-2,-1,1,2,3,4])
        


