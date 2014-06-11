# -*- coding: utf-8 -*-
from ast_nodes import *
from btypes import *
from environment import Environment
from helpers import file_to_AST_str, string_to_file
from util import type_with_known_types, get_type_by_name
from constrainsolver import _calc_constraint_domain, _categorize_predicates, calc_possible_solutions
from parsing import str_ast_to_python_ast
from interp import interpret
from config import TO_MANY_ITEMS

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
        assert isinstance(unqantPred, AUniversalQuantificationPredicate)
        varList = unqantPred.children[0:-1]
        P = unqantPred.children[-1].children[0]
        Q = unqantPred.children[-1].children[1]
        assert isinstance(P, Predicate)
        assert isinstance(Q, Predicate)
        #env._min_int = -2**32
        #env._max_int = 2**32
        domain = _calc_constraint_domain(env, varList, P)
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
        assert isinstance(unqantPred, AUniversalQuantificationPredicate)
        varList = unqantPred.children[0:-1]
        P = unqantPred.children[-1].children[0]
        Q = unqantPred.children[-1].children[1]
        domain = _calc_constraint_domain(env, varList, P)
        assert frozenset([x["x"] for x in domain])==frozenset([1,2,3])
        domain = _calc_constraint_domain(env, varList, P)
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
        assert isinstance(exqantPred, AExistentialQuantificationPredicate)
        varList = exqantPred.children[0:-1]
        P = exqantPred.children[-1].children[0]
        Q = exqantPred.children[-1].children[1]
        assert isinstance(P, Predicate)
        assert isinstance(Q, Predicate)
        domain = _calc_constraint_domain(env, varList, P)
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
        domain = _calc_constraint_domain(env, varList, P)
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
        domain = _calc_constraint_domain(env, varList, P)
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
        domain = _calc_constraint_domain(env, varList, P)
        assert frozenset([x["x"] for x in domain])==frozenset([12])


    def test_constraint_set_comp2(self):
        # {x|P}
        # Build AST:
        string_to_file("#EXPRESSION {x|x:NAT & x=42}", file_name)
        ast_string = file_to_AST_str(file_name)
        root = str_ast_to_python_ast(ast_string)

        # Test
        env = Environment()
        env._min_int = -2**32
        env._max_int = 2**32
        type_with_known_types(root, env, [], [""])
        assert isinstance(get_type_by_name(env, "x"), IntegerType)
        set_predicate = root.children[0].children[1]
        var = root.children[0].children[0]
        assert isinstance(set_predicate, AConjunctPredicate)
        map = _categorize_predicates(set_predicate, env, [var])
        (time0, vars0) = map[set_predicate.children[0]]
        (time1, vars1) = map[set_predicate.children[1]]
        assert time0 == env._max_int+2    
        assert time1 == 3 
        assert vars0 == ["x"]
        assert vars1 == ["x"]
        iterator = calc_possible_solutions(set_predicate, env, [var], interpret)
        solution = iterator.next()
        assert solution=={'x': 42}
        result = interpret(root, env)
        assert result==frozenset([42])
 
 
    def test_constraint_set_comp3(self):
        # {x|P}
        # Build AST:
        string_to_file("#EXPRESSION {x|x:NAT & x=-1}", file_name)
        ast_string = file_to_AST_str(file_name)
        root = str_ast_to_python_ast(ast_string)       

        # Test
        env = Environment()
        env._min_int = -2**32
        env._max_int = 2**32
        type_with_known_types(root, env, [], [""])
        assert isinstance(get_type_by_name(env, "x"), IntegerType)
        set_predicate = root.children[0].children[1]
        var = root.children[0].children[0]
        assert isinstance(set_predicate, AConjunctPredicate)
        map = _categorize_predicates(set_predicate, env, [var])
        (time0, vars0) = map[set_predicate.children[0]]
        (time1, vars1) = map[set_predicate.children[1]]
        assert time0 == env._max_int+2   
        assert time1 == 4 
        assert vars0 == ["x"]  
        assert vars1 == ["x"] 
        iterator = calc_possible_solutions(set_predicate, env, [var], interpret)
        solution = list(iterator)
        assert solution==[]
        result = interpret(root, env)
        assert result==frozenset([])


    def test_constraint_set_comp4(self):
        # {x|P}
        # Build AST:
        string_to_file("#EXPRESSION {x|x:NAT & x:{1,2,3,-1}}", file_name)
        ast_string = file_to_AST_str(file_name)
        root = str_ast_to_python_ast(ast_string)       

        # Test
        env = Environment()
        env._min_int = -2**32
        env._max_int = 2**32
        type_with_known_types(root, env, [], [""])
        assert isinstance(get_type_by_name(env, "x"), IntegerType)
        set_predicate = root.children[0].children[1]
        var = root.children[0].children[0]
        assert isinstance(set_predicate, AConjunctPredicate)
        map = _categorize_predicates(set_predicate, env, [var])
        (time0, vars0) = map[set_predicate.children[0]]
        (time1, vars1) = map[set_predicate.children[1]]
        assert time0 == env._max_int+2  
        assert time1 == 8
        assert vars0 == ["x"]
        assert vars1 == ["x"]
        iterator = calc_possible_solutions(set_predicate, env, [var], interpret)
        solution = list(iterator)
        assert solution==[{'x': 1}, {'x': 2}, {'x': 3}]
        result = interpret(root, env)
        assert result==frozenset([1,2,3])


    def test_constraint_set_comp5(self):
        # {x|P}
        # Build AST:
        string_to_file("#EXPRESSION {x|x:NAT+->NAT & x={(1,1),(2,2),(3,3)}}", file_name)
        ast_string = file_to_AST_str(file_name)
        root = str_ast_to_python_ast(ast_string)       

        # Test
        env = Environment()
        env._min_int = -2**32
        env._max_int = 2**32
        type_with_known_types(root, env, [], [""])
        assert isinstance(get_type_by_name(env, "x"), PowerSetType)
        assert isinstance(get_type_by_name(env, "x").data, CartType)
        set_predicate = root.children[0].children[1]
        var = root.children[0].children[0]
        assert isinstance(set_predicate, AConjunctPredicate)
        map = _categorize_predicates(set_predicate, env, [var])
        (time0, vars0) = map[set_predicate.children[0]]
        (time1, vars1) = map[set_predicate.children[1]]
        assert time0==float("inf")    
        assert isinstance(time1, int)   
        assert vars0==["x"]
        assert vars1==["x"]
        iterator = calc_possible_solutions(set_predicate, env, [var], interpret)
        solution = list(iterator)
        assert solution==[{'x': frozenset([(1,1),(2,2),(3,3)])}]
        result = interpret(root, env)
        assert result==frozenset([frozenset([(1,1),(2,2),(3,3)])])


    def test_constraint_set_comp6(self):
        # {x|P}
        # Build AST:
        string_to_file("#EXPRESSION {x|x : (INTEGER * INTEGER) * BOOL & (x : {((3|->10)|->TRUE),((3|->12)|->TRUE)})}", file_name)
        ast_string = file_to_AST_str(file_name)
        root = str_ast_to_python_ast(ast_string)  

        # Test
        env = Environment()
        env._min_int = -2**32
        env._max_int = 2**32
        type_with_known_types(root, env, [], [""])
        assert isinstance(get_type_by_name(env, "x"), CartType)
        set_predicate = root.children[0].children[1]
        var = root.children[0].children[0]
        assert isinstance(set_predicate, AConjunctPredicate)
        map = _categorize_predicates(set_predicate, env, [var])
        (time0, vars0) = map[set_predicate.children[0]]
        (time1, vars1) = map[set_predicate.children[1]]
        assert time0==float("inf")    
        assert isinstance(time1, int) 
        assert vars0==["x"]
        assert vars1==["x"]
        iterator = calc_possible_solutions(set_predicate, env, [var], interpret)
        solution = list(iterator)
        assert solution==[{'x': ((3, 12), True)}, {'x': ((3, 10), True)}]
        result = interpret(root, env)
        assert result==frozenset([((3, 12), True), ((3, 10), True)])


    def test_constraint_set_comp7(self):
        # {x|P}
        # Build AST:
        string_to_file("#EXPRESSION {x|x: (INTEGER*INTEGER)*INTEGER & (x:{((1|->2)|->3),((4|->5)|->6)} or x : ((0 .. 209) * (0 .. 209)) * {-1})}", file_name)
        ast_string = file_to_AST_str(file_name)
        root = str_ast_to_python_ast(ast_string) 
        
        # Test
        env = Environment()
        env._min_int = -2**32
        env._max_int = 2**32
        type_with_known_types(root, env, [], [""])
        assert isinstance(get_type_by_name(env, "x"), CartType)
        set_predicate = root.children[0].children[1]
        var = root.children[0].children[0]
        assert isinstance(set_predicate, AConjunctPredicate)
        map = _categorize_predicates(set_predicate, env, [var]) 
        (time0, vars0) = map[set_predicate.children[0]]
        (time1, vars1) = map[set_predicate.children[1]]
        assert time0==float("inf")    
        assert time1 <TO_MANY_ITEMS
        assert vars0==["x"]
        assert vars1==["x"] 
        # works, but take too much time
        #result = interpret(root, env)
        #print result       

        
    def test_constraint_set_comp8(self):
        # {x|P}
        # Build AST:
        string_to_file("#EXPRESSION {x|x: (INTEGER*INTEGER)*INTEGER & (x:{((1|->2)|->3),((4|->5)|->6)} or (prj1(INTEGER*INTEGER,INTEGER)(x)/:dom({((1|->2)|->83),((1|->15)|->83)})  & x : ((0 .. 209) * (0 .. 209)) * {-1}))}", file_name)
        ast_string = file_to_AST_str(file_name)
        root = str_ast_to_python_ast(ast_string) 
        
        # Test
        env = Environment()
        env._min_int = -2**32
        env._max_int = 2**32
        type_with_known_types(root, env, [], [""])
        assert isinstance(get_type_by_name(env, "x"), CartType)
        set_predicate = root.children[0].children[1]
        var = root.children[0].children[0]
        assert isinstance(set_predicate, AConjunctPredicate)
        map = _categorize_predicates(set_predicate, env, [var])
        (time0, vars0) = map[set_predicate.children[0]]
        (time1, vars1) = map[set_predicate.children[1]]
        assert time0==float("inf")    
        assert time1 <TO_MANY_ITEMS
        assert vars0==["x"]
        assert vars1==["x"]     
        # works, but take too much time (232.09 seconds)
        #result = interpret(root, env)
        #print result    
        #TODO:     
        #(prj1(INTEGER*INTEGER,BOOL)(x) /: dom({((3|->10)|->TRUE),((3|->12)|->TRUE),


    def test_constraint_set_comp9(self):
        # {x|P}
        # Build AST:
        string_to_file("#EXPRESSION {x|x:{1,2,3,4} & (x:{1,2} or x:{3})}", file_name)
        ast_string = file_to_AST_str(file_name)
        root = str_ast_to_python_ast(ast_string) 

        # Test
        env = Environment()
        env._min_int = -2**32
        env._max_int = 2**32
        type_with_known_types(root, env, [], [""])
        assert isinstance(get_type_by_name(env, "x"), IntegerType)
        set_predicate = root.children[0].children[1]
        var = root.children[0].children[0]
        assert isinstance(set_predicate, AConjunctPredicate)
        map = _categorize_predicates(set_predicate, env, [var])  
        (time0, vars0) = map[set_predicate.children[0]]
        (time1, vars1) = map[set_predicate.children[1]]  
        assert vars0==["x"]
        assert vars1==["x"]
        assert time0==7
        assert time1==10
        iterator = calc_possible_solutions(set_predicate, env, [var], interpret)
        solution = list(iterator)
        assert solution==[{'x': 1}, {'x': 2}, {'x': 3}]
        result = interpret(root, env)
        assert result==frozenset([1,2,3])


    def test_constraint_set_comp10(self):
        # {x|P}
        # Build AST:
        string_to_file("#EXPRESSION {x| (x:{1,2} or x:{3}) & x:{1,2,3,4}}", file_name)
        ast_string = file_to_AST_str(file_name)
        root = str_ast_to_python_ast(ast_string) 

        # Test
        env = Environment()
        env._min_int = -2**32
        env._max_int = 2**32
        type_with_known_types(root, env, [], [""])
        assert isinstance(get_type_by_name(env, "x"), IntegerType)
        set_predicate = root.children[0].children[1]
        var = root.children[0].children[0]
        assert isinstance(set_predicate, AConjunctPredicate)
        map = _categorize_predicates(set_predicate, env, [var])  
        (time0, vars0) = map[set_predicate.children[1]]
        (time1, vars1) = map[set_predicate.children[0]]  
        assert vars0==["x"]
        assert vars1==["x"]
        assert time0==7
        assert time1==10
        iterator = calc_possible_solutions(set_predicate, env, [var], interpret)
        solution = list(iterator)
        assert solution==[{'x': 1}, {'x': 2}, {'x': 3}]
        result = interpret(root, env)
        assert result==frozenset([1,2,3])


    def test_constraint_set_comp11(self):
        # {x|P}
        # Build AST:
        string_to_file("#EXPRESSION {x|x:{1,2,3,4} & (x:NAT or x:{3})}", file_name)
        ast_string = file_to_AST_str(file_name)
        root = str_ast_to_python_ast(ast_string) 

        # Test
        env = Environment()
        env._min_int = -2**32
        env._max_int = 2**32
        type_with_known_types(root, env, [], [""])
        assert isinstance(get_type_by_name(env, "x"), IntegerType)
        set_predicate = root.children[0].children[1]
        var = root.children[0].children[0]
        assert isinstance(set_predicate, AConjunctPredicate)
        map = _categorize_predicates(set_predicate, env, [var])    
        (time0, vars0) = map[set_predicate.children[0]]
        (time1, vars1) = map[set_predicate.children[1]]          
        assert vars0==["x"]
        assert vars1==["x"]
        assert time0==7
        assert time1==env._max_int+7
        iterator = calc_possible_solutions(set_predicate, env, [var], interpret)
        solution = list(iterator)
        assert solution==[{'x': 1}, {'x': 2}, {'x': 3}, {'x':4}]
        result = interpret(root, env)
        assert result==frozenset([1,2,3,4])

     
    def test_constraint_set_comp12(self):
        # {x|P}
        # Build AST:
        string_to_file("#EXPRESSION {x|x: (INTEGER*INTEGER)*INTEGER & x : ((0 .. 209) * (0 .. 209)) * {-1}}", file_name)
        ast_string = file_to_AST_str(file_name)
        root = str_ast_to_python_ast(ast_string) 
        
        # Test
        env = Environment()
        env._min_int = -2**32
        env._max_int = 2**32
        type_with_known_types(root, env, [], [""])
        assert isinstance(get_type_by_name(env, "x"), CartType)
        set_predicate = root.children[0].children[1]
        var = root.children[0].children[0]
        assert isinstance(set_predicate, AConjunctPredicate)
        map = _categorize_predicates(set_predicate, env, [var])    
        (time0, vars0) = map[set_predicate.children[0]]
        (time1, vars1) = map[set_predicate.children[1]]         
        assert vars0==["x"]
        assert vars1==["x"]
        assert time0==float("inf")
        assert time1<2**22   
        # works, but take too much time
        #result = interpret(root, env)
        #print result
                
                
    def test_constraint_set_comp13(self):
        # {x|P}
        # Build AST:
        string_to_file("#EXPRESSION {x|x:INTEGER*INTEGER & x : dom({((2|->0)|->83),((2|->1)|->83),((2|->3)|->83)})}   ", file_name)
        ast_string = file_to_AST_str(file_name)
        root = str_ast_to_python_ast(ast_string) 

        # Test
        env = Environment()
        env._min_int = -2**32
        env._max_int = 2**32
        type_with_known_types(root, env, [], [""])
        assert isinstance(get_type_by_name(env, "x"), CartType)
        set_predicate = root.children[0].children[1]
        var = root.children[0].children[0]
        assert isinstance(set_predicate, AConjunctPredicate)
        map = _categorize_predicates(set_predicate, env, [var])  
        (time0, vars0) = map[set_predicate.children[0]]
        (time1, vars1) = map[set_predicate.children[1]] 
        assert vars0==["x"]
        assert vars1==["x"]
        assert time0==float("inf")
        assert time1<2**22   
        result = interpret(root, env)
        assert result==frozenset([(2, 0), (2, 3), (2, 1)])

                
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
        E= setexpr.children[-1]
        assert isinstance(P, Predicate)
        env._min_int = -2**8
        env._max_int = 2**8
        domain = _calc_constraint_domain(env, varList, P)
        assert frozenset([x["x"] for x in domain])==frozenset([-4,-3,-2,-1,1,2,3,4])