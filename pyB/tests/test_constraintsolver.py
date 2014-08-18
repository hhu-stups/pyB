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
        (time0, vars0, compute_first0) = map[set_predicate.children[0]]
        (time1, vars1, compute_first1) = map[set_predicate.children[1]]
        assert time0 == env._max_int+2    
        assert time1 == 3 
        assert vars0 == ["x"]
        assert vars1 == ["x"]
        assert compute_first0 == []
        assert compute_first1 == []
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
        (time0, vars0, compute_first0) = map[set_predicate.children[0]]
        (time1, vars1, compute_first1) = map[set_predicate.children[1]]
        assert time0 == env._max_int+2   
        assert time1 == 4 
        assert vars0 == ["x"]  
        assert vars1 == ["x"] 
        assert compute_first0 == []
        assert compute_first1 == []
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
        (time0, vars0, compute_first0) = map[set_predicate.children[0]]
        (time1, vars1, compute_first1) = map[set_predicate.children[1]]
        assert time0 == env._max_int+2  
        assert time1 == 8
        assert vars0 == ["x"]
        assert vars1 == ["x"]
        assert compute_first0 == []
        assert compute_first1 == []
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
        (time0, vars0, compute_first0) = map[set_predicate.children[0]]
        (time1, vars1, compute_first1) = map[set_predicate.children[1]]
        assert time0==float("inf")    
        assert isinstance(time1, int)   
        assert vars0==["x"]
        assert vars1==["x"]
        assert compute_first0 == []
        assert compute_first1 == []
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
        (time0, vars0, compute_first0) = map[set_predicate.children[0]]
        (time1, vars1, compute_first1) = map[set_predicate.children[1]]
        assert time0==float("inf")    
        assert isinstance(time1, int) 
        assert vars0==["x"]
        assert vars1==["x"]
        assert compute_first0 == []
        assert compute_first1 == []
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
        (time0, vars0, compute_first0) = map[set_predicate.children[0]]
        (time1, vars1, compute_first1) = map[set_predicate.children[1]]
        assert time0==float("inf")    
        assert time1 <TO_MANY_ITEMS
        assert vars0==["x"]
        assert vars1==["x"] 
        assert compute_first0 == []
        assert compute_first1 == []
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
        (time0, vars0, compute_first0) = map[set_predicate.children[0]]
        (time1, vars1, compute_first1) = map[set_predicate.children[1]]
        assert time0==float("inf")    
        assert time1 <TO_MANY_ITEMS
        assert vars0==["x"]
        assert vars1==["x"]  
        assert compute_first0 == []
        assert compute_first1 == []   
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
        (time0, vars0, compute_first0) = map[set_predicate.children[0]]
        (time1, vars1, compute_first1) = map[set_predicate.children[1]]  
        assert vars0==["x"]
        assert vars1==["x"]
        assert time0==7
        assert time1==10
        assert compute_first0 == []
        assert compute_first1 == []
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
        (time0, vars0, compute_first0) = map[set_predicate.children[1]]
        (time1, vars1, compute_first1) = map[set_predicate.children[0]]  
        assert vars0==["x"]
        assert vars1==["x"]
        assert time0==7
        assert time1==10
        assert compute_first0 == []
        assert compute_first1 == []
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
        (time0, vars0, compute_first0) = map[set_predicate.children[0]]
        (time1, vars1, compute_first1) = map[set_predicate.children[1]]          
        assert vars0==["x"]
        assert vars1==["x"]
        assert time0==7
        assert time1==env._max_int+7
        assert compute_first0 == []
        assert compute_first1 == []
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
        (time0, vars0, compute_first0) = map[set_predicate.children[0]]
        (time1, vars1, compute_first1) = map[set_predicate.children[1]]         
        assert vars0==["x"]
        assert vars1==["x"]
        assert time0==float("inf")
        assert time1<2**22   
        assert compute_first0 == []
        assert compute_first1 == []
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
        (time0, vars0, compute_first0) = map[set_predicate.children[0]]
        (time1, vars1, compute_first1) = map[set_predicate.children[1]] 
        assert vars0==["x"]
        assert vars1==["x"]
        assert time0==float("inf")
        assert time1<2**22   
        assert compute_first0 == []
        assert compute_first1 == []
        result = interpret(root, env)
        assert result==frozenset([(2, 0), (2, 3), (2, 1)])


    def test_constraint_set_comp14(self):
        # {x|P}
        # Build AST:
        string_to_file("#EXPRESSION %x.(x : STRING - {\"CL\",\"CM\"}|-1)", file_name)
        ast_string = file_to_AST_str(file_name)
        root = str_ast_to_python_ast(ast_string)         
        #TODO : "ck = ({uo,LAMBDA_RESULT___|(uo : STRING & LAMBDA_RESULT___ : INTEGER) & uo |-> LAMBDA_RESULT___ : {("CL"|->0),("CM"|->1)}} \/ %uo.(uo : STRING - {"CL","CM"}|-1))"        


    def test_constraint_set_gen_union1(self):
        # Build AST:
        # UNION(x).(P(x)|E(x))
        # find all values that settisfy  P(x)='x=1' and compute the union set of all 
        # expressions E(X)(in this case one) for every x (in this case x doesnt constrain E(x) )
        string_to_file("#EXPRESSION UNION(x).(x=1|{\"a\",\"b\"}\/{\"b\",\"c\"})", file_name)
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
        assert isinstance(set_predicate, AEqualPredicate)
        map = _categorize_predicates(set_predicate, env, [var])  
        (time0, vars0, compute_first0) = map[set_predicate]
        assert vars0==["x"]
        assert time0<2**22   
        assert compute_first0 == []
        result = interpret(root.children[0], env)
        assert result==frozenset(['a', 'c', 'b'])

               
     
    def test_constraint_set_gen_union2(self):
        # Build AST:
        # UNION(x).(P(x)|E(x))
        # find all values that satisfy P(x)='x=1' and compute the union set of all 
        # expressions E(X)(in this case one) for every x (in this case x doesnt constrain E(x) )
        string_to_file("#PREDICATE S={} & f=UNION(x).(x=1|{\"a\",\"b\"}\/{\"b\",\"c\"}\/S)", file_name)
        ast_string = file_to_AST_str(file_name)
        root = str_ast_to_python_ast(ast_string)
        
        # Test
        env = Environment()
        env._min_int = -2**32
        env._max_int = 2**32
        type_with_known_types(root, env, [], ["S","f"])
        assert isinstance(get_type_by_name(env, "x"), IntegerType)
        union_predicate = root.children[0].children[1].children[1]
        set_predicate = union_predicate.children[1]
        var = union_predicate.children[0]
        assert isinstance(set_predicate, AEqualPredicate)
        map = _categorize_predicates(set_predicate, env, [var])  
        (time0, vars0, compute_first0) = map[set_predicate]
        assert vars0==["x"]
        assert time0<2**22
        assert compute_first0 == []
        env.add_ids_to_frame(["S","f"])
        assert interpret(root.children[0], env)
        
        

    def test_constraint_set_gen_union3(self):
        # Build AST:
        string_to_file("#PREDICATE {(1,1),(2,2)}=UNION(x,y).(x|->y:{(1,1),(2,2)}|{x|->y})", file_name)
        ast_string = file_to_AST_str(file_name)
        root = str_ast_to_python_ast(ast_string)
        
        # Test
        env = Environment()
        env._min_int = -2**32
        env._max_int = 2**32
        type_with_known_types(root, env, [], []) 
        assert isinstance(get_type_by_name(env, "x"), IntegerType) 
        union_predicate = root.children[0].children[1]  
        set_predicate = union_predicate.children[2]
        var0 = union_predicate.children[0]
        var1 = union_predicate.children[1]
        assert isinstance(set_predicate, ABelongPredicate)
        map = _categorize_predicates(set_predicate, env, [var0, var1])  
        (time0, vars0, compute_first0) = map[set_predicate]
        assert set(vars0)==set(["x", "y"])
        assert time0<2**22
        assert compute_first0 == []
        assert interpret(root.children[0], env)


    # 3 variables have to be constraint 
    def test_constraint_set_gen_union4(self):
        # Build AST:
        string_to_file("#PREDICATE {1,4}=UNION(x, y, z).(x|->(y|->z):{(1,(2,3)),(4,(5,6))} |{x})", file_name)
        ast_string = file_to_AST_str(file_name)
        root = str_ast_to_python_ast(ast_string)
        
        # Test
        env = Environment()
        env._min_int = -2**32
        env._max_int = 2**32
        type_with_known_types(root, env, [], []) 
        assert isinstance(get_type_by_name(env, "x"), IntegerType)
        assert isinstance(get_type_by_name(env, "y"), IntegerType) 
        assert isinstance(get_type_by_name(env, "z"), IntegerType)  
        union_predicate = root.children[0].children[1]  
        assert isinstance(union_predicate, AQuantifiedUnionExpression)
        set_predicate = union_predicate.children[3]
        var0 = union_predicate.children[0]
        var1 = union_predicate.children[1]
        var2 = union_predicate.children[2]
        assert isinstance(set_predicate, ABelongPredicate)
        map = _categorize_predicates(set_predicate, env, [var0, var1, var2])  
        (time, vars, compute_first) = map[set_predicate]
        assert set(vars)==set(["x", "y", "z"])
        assert time<2**22 
        assert compute_first == []
        assert interpret(root.children[0], env)      


    # 3 variables have to be constraint + function app-constraint 
    # TODO: the constraint solver musst finde out that x and y has to be enumerated before z
    import pytest
    @pytest.mark.xfail 
    def test_constraint_set_gen_union5(self):
        # Build AST:
        string_to_file("#PREDICATE {1,2}=UNION(x,y,z).(x|->y:{(\"a\",\"b\"),(\"c\",\"d\")} & z={(\"a\"|->(\"b\"|->1)),(\"c\"|->(\"d\"|->2))} [{x}][{y}]|z)", file_name)
        ast_string = file_to_AST_str(file_name)
        root = str_ast_to_python_ast(ast_string)
        
        # Test
        env = Environment()
        env._min_int = -2**32
        env._max_int = 2**32  
        assert interpret(root.children[0], env) 


    
    
    # 3 variables have to be constraint (3+2)
    def test_constraint_set_gen_union6(self):
        # Build AST:
        string_to_file("#PREDICATE S={(\"a\",1,\"b\"),(\"a\",2,\"c\"),(\"c\",3,\"d\"),(\"c\",4,\"a\")} & {(\"b\",\"c\"),(\"d\",\"a\")}=UNION(a,b,c,d,e).(a|->c|->b:S & a|->e|->d:S & c<e|{b|->d})", file_name)
        ast_string = file_to_AST_str(file_name)
        root = str_ast_to_python_ast(ast_string) 
        
        # Test
        env = Environment()
        env._min_int = -2**32
        env._max_int = 2**32 
        type_with_known_types(root, env, [], ["S"])
        assert isinstance(get_type_by_name(env, "a"), StringType)
        assert isinstance(get_type_by_name(env, "b"), StringType) 
        assert isinstance(get_type_by_name(env, "c"), IntegerType) 
        assert isinstance(get_type_by_name(env, "d"), StringType) 
        assert isinstance(get_type_by_name(env, "e"), IntegerType)  
        union_predicate = root.children[0].children[1].children[1]  
        assert isinstance(union_predicate, AQuantifiedUnionExpression)
        set_predicate = union_predicate.children[5]
        var0 = union_predicate.children[0]
        var1 = union_predicate.children[1]
        var2 = union_predicate.children[2]
        var3 = union_predicate.children[3]
        var4 = union_predicate.children[4]
        assert isinstance(set_predicate, AConjunctPredicate)
        map = _categorize_predicates(set_predicate, env, [var0, var1, var2, var3, var4])
        env.add_ids_to_frame(["S"])
        assert interpret(root.children[0], env) 


    def test_constraint_set_gen_union7(self):
        # Build AST:
        string_to_file("#PREDICATE {1,3}=UNION(x).(x:dom({(1,2),(3,4)})|{x})", file_name)
        ast_string = file_to_AST_str(file_name)
        root = str_ast_to_python_ast(ast_string) 
        
        # Test
        env = Environment()
        env._min_int = -2**32
        env._max_int = 2**32  
        assert interpret(root.children[0], env) 


    def test_constraint_set_gen_union8(self):
        # Build AST:
        string_to_file("#PREDICATE {2,4}=UNION(x).(x:ran({(1,2),(3,4)})|{x})", file_name)
        ast_string = file_to_AST_str(file_name)
        root = str_ast_to_python_ast(ast_string) 
        
        # Test
        env = Environment()
        env._min_int = -2**32
        env._max_int = 2**32  
        assert interpret(root.children[0], env) 

    
    # Bug:
    # instead of creating a symbolic set comp, this crashs the contraint solver.
    # the cs trys to enumerate x and is unable to use the constraint in the predicate (powerset of inifnite)
    import pytest
    @pytest.mark.xfail 
    def test_constraint_set_comprehension(self):
        # Build AST:
        string_to_file("#EXPRESSION {x|x:POW(((0 .. 234) * {0,1}))}", file_name)
        ast_string = file_to_AST_str(file_name)
        root = str_ast_to_python_ast(ast_string) 
        
        # Test
        env = Environment()
        env._min_int = -2**32
        env._max_int = 2**32  
        assert interpret(root.children[0], env) 


    # TODO: constraints with variables affecting each other
    # the constraint solver musst find out that x has to be enumerated before y
    # e.g C578.EML.014/662_001 {cb,cc,cd,ce,cf,cg,|cb|->cc|->ce:bq & cf=cc & cd=0 & cg=(be;bj)(cb|->cc)} with cb cc not set
    # C578.EML.014/623_001 {bp,bq,br,bs,bt,bu,|bp|->bq|->bs:bj & bt=bq & br=1 & bu=(az;bb)(bp|->bq)} with preimage = ('bp', 'bq')
    # enumeration.py 99
    import pytest
    @pytest.mark.xfail 
    def test_constraint_affecting_variables(self):
        # Build AST:
        string_to_file("#PREDICATE {(0,\"A\"),(1,\"B\"),(2,\"C\"),(3,\"D\")}={x, y | x : {0,1,2,3,4,5,6,7,8,9,10} & y : {(\"A\"|->41),(\"B\"|->42),(\"C\"|->43),(\"D\"|->44)}~[{{(0|->41),(1|->42),(2|->43),(3|->44),(4|->45)}(x)}]}", file_name)
        ast_string = file_to_AST_str(file_name)
        root = str_ast_to_python_ast(ast_string) 
        
        # Test
        env = Environment()
        env._min_int = -2**32
        env._max_int = 2**32  
        assert interpret(root.children[0], env)    
  
        
    #TODO: write test of union which defines bound vars via other quantified predicates.
    # see C578.EML.014/CF_ZMS_AUM_2
    # implement recursion: calc_possible_solutions using calc_possible_solutions in case 2
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
        
        
# Write tests:        
# TODO AComprehensionSetExpression:  see C578/2013_08_14/machines_14082013/Z_01_001.mch    
# dr:0 .. 234 & dd:{0,1} & db:POW(0 .. 234*{0,1}*INTEGER) & dy:0 .. 234 & dr/:dom(dom(db))-{dy} & dz:{ds,de,ea,eb,|ds:INTEGER & de:INTEGER & ea:POW(INTEGER*INTEGER*INTEGER) & eb:INTEGER & ea=db & eb=dy & dr|->dd|->ds|->de:{0|->1|->2|->1,0|->1|->9|->0,234|->0|->228|->1} & ds:dom(dom(ea)) => {de}/=dom(ea)[{ds}]}
# TODO AComprehensionSetExpression:  see C578/2013_08_14/machines_14082013/PS_00611_006
# z_:INTEGER*INTEGER & z_:{0|->1,1|->0,2|->2} or prj1(INTEGER,INTEGER)(z_)/:dom({0|->1,1|->0,2|->2}) & z_:INTEGER*{3}
# TODO AComprehensionSetExpression:  see C578/2013_08_14/machines_14082013/03_001
# by: cj:0 .. 234 & cd:{0,1} & cb:POW(0 .. 234*{0,1}*INTEGER) & cp:0 .. 234 & cj/:dom(dom(cb))-{cp} & cq:{ck,ce,cr,cs,|ck:INTEGER & ce:INTEGER & cr:POW(INTEGER*INTEGER*INTEGER) & cs:INTEGER & cr=cb & cs=cp & cj|->cd|->ck|->ce:{0|->1|->2|->1234|->0|->228|->1} & ck:dom(dom(cr)) => {ce}/=dom(cr)[{ck}]}
# TODO AComprehensionSetExpression:  see C578/2013_08_14/machines_14082013/PB_00611_005 
# z_:INTEGER*INTEGER & z_:{0|->1,1|->0,2|->2} or prj1(INTEGER,INTEGER)(z_)/:dom({0|->1,1|->0,2|->2}) & z_:INTEGER*{3}
# TODO: EnumerationNotPossibleException C578/2013_08_14/machines_27082013/R_02_002
# nx=%(pc,pd).(pd:hx & pc:hs|{bg|->mu(pc),bc|->iq(pc),bh|->is(pc),be|->ir(pc)}(pd))
# TODO AComprehensionSetExpression:  verdi/verdi
# seg:{"DR_SEG_0101001","DR_SEG_0101002","DR_SEG_0101003" }) & seg/:lim & suiv:{seg_suiv,dir_suiv,dist_suiv,lim_suiv,|seg_suiv:STRING & dir_suiv:INTEGER & dist_suiv:INTEGER & lim_suiv:POW(STRING) & seg|->dir|->seg_suiv|->dir_suiv:{"DR_SEG_0201106"|->0|->"DR_SEG_0201013"|->0,"DR_SEG_0201106"|->1|->"DR_SEG_0201105"|->1}& dist_suiv=dist-{"DR_SEG_0201106"|->2000}(seg_suiv) & lim_suiv=lim}
#TODO: write testcase with other tuple combinations... (Klammerung)
