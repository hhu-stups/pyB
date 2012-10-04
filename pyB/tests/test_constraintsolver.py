# -*- coding: utf-8 -*-
from ast_nodes import *
from btypes import *
from environment import Environment
from helpers import file_to_AST_str, string_to_file
from typing import _test_typeit
from constrainsolver import calc_constraint_domain

file_name = "input.txt"

class TestConstraintSolver():
    def test_forAll(self):
        # !x.(P=>Q)
        # Build AST:
        string_to_file("#PREDICATE !(z).((z:NAT & z>2 & z<5) => (z>1 & z<=10))", file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string

        # Test
        env = Environment()
        _test_typeit(root, env, [], [""])
        assert isinstance(env.get_type("z"), IntegerType)
        unqantPred = root.children[0]
        assert isinstance(unqantPred, AUniversalQuantificationPredicate)
        varList = unqantPred.children[0:-1]
        P = unqantPred.children[-1].children[0]
        Q = unqantPred.children[-1].children[1]
        assert isinstance(P, Predicate)
        assert isinstance(Q, Predicate)
        domain = calc_constraint_domain(env, varList, P)
        assert domain[0]==frozenset([3,4])


    def test_forAll2(self):
        # !x.(P=>Q)
        # Build AST:
        string_to_file("#PREDICATE f={(1,7),(2,8),(3,9)} & S={1,2,3} & !(x,y).(y:INTEGER &(x:S & f(x)<y) & y<42 =>y:T)", file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string
        
        # Test
        env = Environment()
        lst = [("S", PowerSetType(IntegerType(None))),("f", PowerSetType(CartType(PowerSetType(IntegerType(None)), PowerSetType(IntegerType(None)))))]
        _test_typeit(root, env, lst, ["T"])
        assert isinstance(env.get_type("x"), IntegerType)
        assert isinstance(env.get_type("y"), IntegerType)
        assert isinstance(env.get_type("T"), PowerSetType)
        assert isinstance(env.get_type("T").data, IntegerType)
        env.bstate.add_ids_to_frame(["f","S","T"])
        env.bstate.set_value("f", frozenset([(1,7),(2,8),(3,9)]))
        env.bstate.set_value("S", frozenset([1,2,3]))
        env.bstate.set_value("T", frozenset(range(10,42)))
        env._min_int = -2**8
        env._max_int = 2**8
        unqantPred = root.children[0].children[1]
        assert isinstance(unqantPred, AUniversalQuantificationPredicate)
        varList = unqantPred.children[0:-1]
        P = unqantPred.children[-1].children[0]
        Q = unqantPred.children[-1].children[1]
        domain = calc_constraint_domain(env, varList, P)
        assert domain[0]==frozenset([1,2,3])
        assert domain[1]==frozenset(range(10,42))



    def test_ex(self):
        # #x.(P & Q)
        # Build AST:
        string_to_file("#PREDICATE #(z).((z:NAT & z>=2 & z<=5) & (z>1 & z<=10))", file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string

        # Test
        env = Environment()
        _test_typeit(root, env, [], [""])
        assert isinstance(env.get_type("z"), IntegerType)
        exqantPred = root.children[0]
        assert isinstance(exqantPred, AExistentialQuantificationPredicate)
        varList = exqantPred.children[0:-1]
        P = exqantPred.children[-1].children[0]
        Q = exqantPred.children[-1].children[1]
        assert isinstance(P, Predicate)
        assert isinstance(Q, Predicate)
        domain = calc_constraint_domain(env, varList, P)
        assert domain[0]== frozenset([2,3,4,5])

    
    def test_lambda(self):
        # %x.(P|E)
        # Build AST:
        string_to_file("#PREDICATE card(%x.(x:1..100|x*x))=100", file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string
        
        # Test
        env = Environment()
        _test_typeit(root, env, [], [""])
        assert isinstance(env.get_type("x"), IntegerType)
        lambdaexpr = root.children[0].children[0].children[0] 
        assert isinstance(lambdaexpr, ALambdaExpression)
        varList = lambdaexpr.children[0:-2]
        P = lambdaexpr.children[-2]
        E = lambdaexpr.children[-1]
        assert isinstance(P, Predicate)
        assert isinstance(E, Expression)
        env._min_int = -2**8
        env._max_int = 2**8
        domain = calc_constraint_domain(env, varList, P)
        assert domain[0]== frozenset(range(1,100+1))

    
    def test_set_comp(self):
        # {x|P}
        # Build AST:
        string_to_file("#PREDICATE card({x|x:NAT & x=12})=1", file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string

        # Test
        env = Environment()
        _test_typeit(root, env, [], [""])
        assert isinstance(env.get_type("x"), IntegerType)
        setexpr = root.children[0].children[0].children[0] 
        assert isinstance(setexpr, AComprehensionSetExpression)
        varList = setexpr.children[0:-1]
        P = setexpr.children[-1]
        assert isinstance(P, Predicate)
        env._min_int = -2**8
        env._max_int = 2**8
        domain = calc_constraint_domain(env, varList, P)
        assert domain[0]==frozenset([12])


    def test_pi(self):
        # PI (z).(P|E)
        # Build AST:
        string_to_file("#PREDICATE PI(x).(x:-4..4 & x/=0 | x)=576", file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string

        # Test
        env = Environment()
        _test_typeit(root, env, [], [""])
        assert isinstance(env.get_type("x"), IntegerType)
        setexpr = root.children[0].children[0]
        assert isinstance(setexpr, AGeneralProductExpression)
        varList = setexpr.children[0:-2]
        P = setexpr.children[-2]
        E= setexpr.children[-1]
        assert isinstance(P, Predicate)
        env._min_int = -2**8
        env._max_int = 2**8
        domain = calc_constraint_domain(env, varList, P)
        assert domain[0]==frozenset([-4,-3,-2,-1,1,2,3,4])