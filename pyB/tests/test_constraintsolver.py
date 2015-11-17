# -*- coding: utf-8 -*-
from ast_nodes import *
from btypes import *
from bexceptions import ValueNotInDomainException
from config import TOO_MANY_ITEMS
from constraintsolver import Constraint, compute_using_external_solver, _categorize_predicates, compute_constrained_domains
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
        constraint0 = map[set_predicate.children[0]]
        time0 = constraint0.time
        vars0 = constraint0.constrained_vars
        compute_first0 = constraint0.vars_need_to_be_set_first
        constraint1 = map[set_predicate.children[1]]
        time1 = constraint1.time
        vars1 = constraint1.constrained_vars
        compute_first1 = constraint1.vars_need_to_be_set_first
        assert time0 == env._max_int+2    
        assert time1 == 3 
        assert vars0 == ["x"]
        assert vars1 == ["x"]
        assert compute_first0 == []
        assert compute_first1 == []
        iterator = compute_constrained_domains(set_predicate, env, [var])
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
        constraint0 = map[set_predicate.children[0]]
        time0 = constraint0.time
        vars0 = constraint0.constrained_vars
        compute_first0 = constraint0.vars_need_to_be_set_first
        constraint1 = map[set_predicate.children[1]]
        time1 = constraint1.time
        vars1 = constraint1.constrained_vars
        compute_first1 = constraint1.vars_need_to_be_set_first
        assert time0 == env._max_int+2   
        assert time1 == 4 
        assert vars0 == ["x"]  
        assert vars1 == ["x"] 
        assert compute_first0 == []
        assert compute_first1 == []
        iterator = compute_constrained_domains(set_predicate, env, [var])
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
        constraint0 = map[set_predicate.children[0]]
        time0 = constraint0.time
        vars0 = constraint0.constrained_vars
        compute_first0 = constraint0.vars_need_to_be_set_first
        constraint1 = map[set_predicate.children[1]]
        time1 = constraint1.time
        vars1 = constraint1.constrained_vars
        compute_first1 = constraint1.vars_need_to_be_set_first
        assert time0 == env._max_int+2  
        assert time1 == 8
        assert vars0 == ["x"]
        assert vars1 == ["x"]
        assert compute_first0 == []
        assert compute_first1 == []
        iterator = compute_constrained_domains(set_predicate, env, [var])
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
        constraint0 = map[set_predicate.children[0]]
        time0 = constraint0.time
        vars0 = constraint0.constrained_vars
        compute_first0 = constraint0.vars_need_to_be_set_first
        constraint1 = map[set_predicate.children[1]]
        time1 = constraint1.time
        vars1 = constraint1.constrained_vars
        compute_first1 = constraint1.vars_need_to_be_set_first
        assert time0==TOO_MANY_ITEMS+2    
        assert isinstance(time1, int)   
        assert vars0==["x"]
        assert vars1==["x"]
        assert compute_first0 == []
        assert compute_first1 == []
        iterator = compute_constrained_domains(set_predicate, env, [var])
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
        constraint0 = map[set_predicate.children[0]]
        time0 = constraint0.time
        vars0 = constraint0.constrained_vars
        compute_first0 = constraint0.vars_need_to_be_set_first
        constraint1 = map[set_predicate.children[1]]
        time1 = constraint1.time
        vars1 = constraint1.constrained_vars
        compute_first1 = constraint1.vars_need_to_be_set_first
        assert time0==TOO_MANY_ITEMS+2    
        assert isinstance(time1, int) 
        assert vars0==["x"]
        assert vars1==["x"]
        assert compute_first0 == []
        assert compute_first1 == []
        iterator = compute_constrained_domains(set_predicate, env, [var])
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
        constraint0 = map[set_predicate.children[0]]
        time0 = constraint0.time
        vars0 = constraint0.constrained_vars
        compute_first0 = constraint0.vars_need_to_be_set_first
        constraint1 = map[set_predicate.children[1]]
        time1 = constraint1.time
        vars1 = constraint1.constrained_vars
        compute_first1 = constraint1.vars_need_to_be_set_first
        assert time0==TOO_MANY_ITEMS+2    
        assert time1 <TOO_MANY_ITEMS
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
        constraint0 = map[set_predicate.children[0]]
        time0 = constraint0.time
        vars0 = constraint0.constrained_vars
        compute_first0 = constraint0.vars_need_to_be_set_first
        constraint1 = map[set_predicate.children[1]]
        time1 = constraint1.time
        vars1 = constraint1.constrained_vars
        compute_first1 = constraint1.vars_need_to_be_set_first
        assert time0==TOO_MANY_ITEMS+2    
        assert time1 <TOO_MANY_ITEMS
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
        constraint0 = map[set_predicate.children[0]]
        time0 = constraint0.time
        vars0 = constraint0.constrained_vars
        compute_first0 = constraint0.vars_need_to_be_set_first
        constraint1 = map[set_predicate.children[1]]
        time1 = constraint1.time
        vars1 = constraint1.constrained_vars
        compute_first1 = constraint1.vars_need_to_be_set_first
        assert vars0==["x"]
        assert vars1==["x"]
        assert time0==7
        assert time1==10
        assert compute_first0 == []
        assert compute_first1 == []
        iterator = compute_constrained_domains(set_predicate, env, [var])
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
        constraint0 = map[set_predicate.children[0]]
        time0 = constraint0.time
        vars0 = constraint0.constrained_vars
        compute_first0 = constraint0.vars_need_to_be_set_first
        constraint1 = map[set_predicate.children[1]]
        time1 = constraint1.time
        vars1 = constraint1.constrained_vars
        compute_first1 = constraint1.vars_need_to_be_set_first
        assert vars0==["x"]
        assert vars1==["x"]
        assert time0==10
        assert time1==7
        assert compute_first0 == []
        assert compute_first1 == []
        iterator = compute_constrained_domains(set_predicate, env, [var])
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
        constraint0 = map[set_predicate.children[0]]
        time0 = constraint0.time
        vars0 = constraint0.constrained_vars
        compute_first0 = constraint0.vars_need_to_be_set_first
        constraint1 = map[set_predicate.children[1]]
        time1 = constraint1.time
        vars1 = constraint1.constrained_vars
        compute_first1 = constraint1.vars_need_to_be_set_first       
        assert vars0==["x"]
        assert vars1==["x"]
        assert time0==7
        assert time1==env._max_int+7
        assert compute_first0 == []
        assert compute_first1 == []
        iterator = compute_constrained_domains(set_predicate, env, [var])
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
        constraint0 = map[set_predicate.children[0]]
        time0 = constraint0.time
        vars0 = constraint0.constrained_vars
        compute_first0 = constraint0.vars_need_to_be_set_first
        constraint1 = map[set_predicate.children[1]]
        time1 = constraint1.time
        vars1 = constraint1.constrained_vars
        compute_first1 = constraint1.vars_need_to_be_set_first      
        assert vars0==["x"]
        assert vars1==["x"]
        assert time0==TOO_MANY_ITEMS+2
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
        constraint0 = map[set_predicate.children[0]]
        time0 = constraint0.time
        vars0 = constraint0.constrained_vars
        compute_first0 = constraint0.vars_need_to_be_set_first
        constraint1 = map[set_predicate.children[1]]
        time1 = constraint1.time
        vars1 = constraint1.constrained_vars
        compute_first1 = constraint1.vars_need_to_be_set_first
        assert vars0==["x"]
        assert vars1==["x"]
        assert time0==TOO_MANY_ITEMS+2
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
        # find all values that satisfy  P(x)='x=1' and compute the union set of all 
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
        constraint0 = map[set_predicate]
        time0 = constraint0.time
        vars0 = constraint0.constrained_vars
        compute_first0 = constraint0.vars_need_to_be_set_first
        assert vars0==["x"]
        assert time0<2**22   
        assert compute_first0 == []
        # ExpressionParseUnit does not support variables
        result = interpret(root, env)
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
        constraint0 = map[set_predicate]
        time0 = constraint0.time
        vars0 = constraint0.constrained_vars
        compute_first0 = constraint0.vars_need_to_be_set_first
        assert vars0==["x"]
        assert time0<2**22
        assert compute_first0 == []
        assert interpret(root, env)
        
        

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
        assert isinstance(set_predicate, AMemberPredicate)
        map = _categorize_predicates(set_predicate, env, [var0, var1])  
        constraint = map[set_predicate]
        time0 = constraint.time
        vars0 = constraint.constrained_vars
        compute_first0 = constraint.vars_need_to_be_set_first
        assert set(vars0)==set(["x", "y"])
        assert time0<2**22
        assert compute_first0 == []
        assert interpret(root, env)


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
        assert isinstance(set_predicate, AMemberPredicate)
        map = _categorize_predicates(set_predicate, env, [var0, var1, var2])  
        constraint = map[set_predicate]
        time = constraint.time
        vars = constraint.constrained_vars
        compute_first = constraint.vars_need_to_be_set_first
        assert set(vars)==set(["x", "y", "z"])
        assert time<2**22 
        assert compute_first == []
        assert interpret(root, env)      


    # 3 variables have to be constraint + function app-constraint 
    # the constraint solver musst finde out that x and y has to be enumerated before z
    def test_constraint_set_gen_union5(self):
        # Build AST:
        string_to_file("#PREDICATE {1,2}=UNION(x,y,z).(x|->y:{(\"a\",\"b\"),(\"c\",\"d\")} & z={(\"a\"|->(\"b\"|->1)),(\"c\"|->(\"d\"|->2))} [{x}][{y}]|z)", file_name)
        ast_string = file_to_AST_str(file_name)
        root = str_ast_to_python_ast(ast_string)
        
        # Test
        env = Environment()
        env._min_int = -2**32
        env._max_int = 2**32  
        assert interpret(root, env) 


    
    
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
        assert interpret(root, env) 


    def test_constraint_set_gen_union7(self):
        # Build AST:
        string_to_file("#PREDICATE {1,3}=UNION(x).(x:dom({(1,2),(3,4)})|{x})", file_name)
        ast_string = file_to_AST_str(file_name)
        root = str_ast_to_python_ast(ast_string) 
        
        # Test
        env = Environment()
        env._min_int = -2**32
        env._max_int = 2**32  
        assert interpret(root, env) 


    def test_constraint_set_gen_union8(self):
        # Build AST:
        string_to_file("#PREDICATE {2,4}=UNION(x).(x:ran({(1,2),(3,4)})|{x})", file_name)
        ast_string = file_to_AST_str(file_name)
        root = str_ast_to_python_ast(ast_string) 
        
        # Test
        env = Environment()
        env._min_int = -2**32
        env._max_int = 2**32  
        assert interpret(root, env) 

    
    def test_constraint_set_comprehension(self):
        # Build AST:
        string_to_file("#PREDICATE {(234,1)}:{x|x:POW(((0 .. 234) * {0,1}))}", file_name)
        ast_string = file_to_AST_str(file_name)
        root = str_ast_to_python_ast(ast_string) 
        
        # Test
        env = Environment()
        env._min_int = -2**32
        env._max_int = 2**32  
        assert interpret(root, env) 
        
 
    # This must cause a crash
    import pytest
    @pytest.mark.xfail 
    def test_constraint_set_comprehension2(self):
        # Build AST:
        string_to_file("#EXPRESSION {x, y |x=y+1 & y=x+1}", file_name)
        ast_string = file_to_AST_str(file_name)
        root = str_ast_to_python_ast(ast_string) 
        
        # Test
        env = Environment()
        env._min_int = -2**32
        env._max_int = 2**32  
        assert interpret(root.children[0], env)        
        
    # verdi/verdi
    # & r_seg_chain_dist = closure1({seg,dir,dist,suiv|((seg : {"DR_SEG_0101001","DR_SEG_0101002","DR_SEG_0101003","DR_SEG_0101004","DR_SEG_0101005","DR_SEG_0101006","DR_SEG_0101007","DR_SEG_0101008","DR_SEG_0101009","DR_SEG_0101010","DR_SEG_0101011","DR_SEG_0101012","DR_SEG_0101013","DR_SEG_0101014","DR_SEG_0101015","DR_SEG_0101016","DR_SEG_0101017","DR_SEG_0101018","DR_SEG_0101019","DR_SEG_0101020","DR_SEG_0101021","DR_SEG_0101022","DR_SEG_0101023","DR_SEG_0101024","DR_SEG_0101025","DR_SEG_0101026","DR_SEG_0101027","DR_SEG_0101028","DR_SEG_0101029","DR_SEG_0101030","DR_SEG_0101031","DR_SEG_0101032","DR_SEG_0101033","DR_SEG_0101051","DR_SEG_0101052","DR_SEG_0101053","DR_SEG_0101054","DR_SEG_0101055","DR_SEG_0101056","DR_SEG_0101057","DR_SEG_0101058","DR_SEG_0101059","DR_SEG_0101060","DR_SEG_0101061","DR_SEG_0101062","DR_SEG_0101063","DR_SEG_0101064","DR_SEG_0101065","DR_SEG_0101066","DR_SEG_0101067","DR_SEG_0101068","DR_SEG_0101069","DR_SEG_0101070","DR_SEG_0101071","DR_SEG_0101072","DR_SEG_0101073","DR_SEG_0101074","DR_SEG_0101075","DR_SEG_0101076","DR_SEG_0101077","DR_SEG_0101078","DR_SEG_0101079","DR_SEG_0101080","DR_SEG_0101081","DR_SEG_0101082","DR_SEG_0101083","DR_SEG_0101084","DR_SEG_0101085","DR_SEG_0101086","DR_SEG_0101087","DR_SEG_0101088","DR_SEG_0101089","DR_SEG_0101101","DR_SEG_0101102","DR_SEG_0101104","DR_SEG_0101105","DR_SEG_0101106","DR_SEG_0101107","DR_SEG_0102001","DR_SEG_0102002","DR_SEG_0102003","DR_SEG_0102004","DR_SEG_0102005","DR_SEG_0102006","DR_SEG_0102007","DR_SEG_0102008","DR_SEG_0102009","DR_SEG_0102010","DR_SEG_0102011","DR_SEG_0102012","DR_SEG_0102013","DR_SEG_0102014","DR_SEG_0102015","DR_SEG_0102016","DR_SEG_0102051","DR_SEG_0102052","DR_SEG_0102053","DR_SEG_0102054","DR_SEG_0102055","DR_SEG_0102056","DR_SEG_0102057","DR_SEG_0102058","DR_SEG_0102059","DR_SEG_0102060","DR_SEG_0102061","DR_SEG_0102062","DR_SEG_0102063","DR_SEG_0102101","DR_SEG_0102102","DR_SEG_0102103","DR_SEG_0102104","DR_SEG_0201001","DR_SEG_0201002","DR_SEG_0201003","DR_SEG_0201004","DR_SEG_0201005","DR_SEG_0201006","DR_SEG_0201007","DR_SEG_0201008","DR_SEG_0201009","DR_SEG_0201010","DR_SEG_0201011","DR_SEG_0201012","DR_SEG_0201013","DR_SEG_0201014","DR_SEG_0201015","DR_SEG_0201016","DR_SEG_0201051","DR_SEG_0201052","DR_SEG_0201053","DR_SEG_0201054","DR_SEG_0201055","DR_SEG_0201056","DR_SEG_0201057","DR_SEG_0201058","DR_SEG_0201059","DR_SEG_0201060","DR_SEG_0201061","DR_SEG_0201062","DR_SEG_0201063","DR_SEG_0201064","DR_SEG_0201101","DR_SEG_0201102","DR_SEG_0201103","DR_SEG_0201104","DR_SEG_0201105","DR_SEG_0201106"} & dir : {0,1}) & dist : (0 .. 2147483647)) & suiv : {seg_suiv,dir_suiv,dist_suiv|((seg_suiv : STRING & dir_suiv : INTEGER) & dist_suiv : INTEGER) & ((seg |-> dir) |-> (seg_suiv |-> dir_suiv) : {(("DR_SEG_0101001"|->0)|->("DR_SEG_0101002"|->0)),(("DR_SEG_0101001"|->1)|->("DR_SEG_0101055"|->1)),(("DR_SEG_0101002"|->0)|->("DR_SEG_0101003"|->0)),(("DR_SEG_0101002"|->1)|->("DR_SEG_0101001"|->1)),(("DR_SEG_0101003"|->0)|->("DR_SEG_0101004"|->0)),(("DR_SEG_0101003"|->1)|->("DR_SEG_0101002"|->1)),(("DR_SEG_0101004"|->0)|->("DR_SEG_0101005"|->0)),(("DR_SEG_0101004"|->1)|->("DR_SEG_0101003"|->1)),(("DR_SEG_0101005"|->0)|->("DR_SEG_0101006"|->0)),(("DR_SEG_0101005"|->1)|->("DR_SEG_0101004"|->1)),(("DR_SEG_0101006"|->0)|->("DR_SEG_0101007"|->0)),(("DR_SEG_0101006"|->1)|->("DR_SEG_0101005"|->1)),(("DR_SEG_0101007"|->0)|->("DR_SEG_0101008"|->0)),(("DR_SEG_0101007"|->1)|->("DR_SEG_0101006"|->1)),(("DR_SEG_0101008"|->0)|->("DR_SEG_0101009"|->0)),(("DR_SEG_0101008"|->1)|->("DR_SEG_0101007"|->1)),(("DR_SEG_0101009"|->0)|->("DR_SEG_0101010"|->0)),(("DR_SEG_0101009"|->1)|->("DR_SEG_0101008"|->1)),(("DR_SEG_0101009"|->1)|->("DR_SEG_0101102"|->1)),(("DR_SEG_0101010"|->0)|->("DR_SEG_0101011"|->0)),(("DR_SEG_0101010"|->1)|->("DR_SEG_0101009"|->1)),(("DR_SEG_0101011"|->0)|->("DR_SEG_0101012"|->0)),(("DR_SEG_0101011"|->1)|->("DR_SEG_0101010"|->1)),(("DR_SEG_0101012"|->0)|->("DR_SEG_0101013"|->0)),(("DR_SEG_0101012"|->1)|->("DR_SEG_0101011"|->1)),(("DR_SEG_0101013"|->0)|->("DR_SEG_0101014"|->0)),(("DR_SEG_0101013"|->1)|->("DR_SEG_0101012"|->1)),(("DR_SEG_0101014"|->0)|->("DR_SEG_0101015"|->0)),(("DR_SEG_0101014"|->1)|->("DR_SEG_0101013"|->1)),(("DR_SEG_0101015"|->0)|->("DR_SEG_0101016"|->0)),(("DR_SEG_0101015"|->1)|->("DR_SEG_0101014"|->1)),(("DR_SEG_0101016"|->0)|->("DR_SEG_0101017"|->0)),(("DR_SEG_0101016"|->1)|->("DR_SEG_0101015"|->1)),(("DR_SEG_0101017"|->0)|->("DR_SEG_0101018"|->0)),(("DR_SEG_0101017"|->1)|->("DR_SEG_0101016"|->1)),(("DR_SEG_0101018"|->0)|->("DR_SEG_0101019"|->0)),(("DR_SEG_0101018"|->1)|->("DR_SEG_0101017"|->1)),(("DR_SEG_0101019"|->0)|->("DR_SEG_0101020"|->0)),(("DR_SEG_0101019"|->1)|->("DR_SEG_0101018"|->1)),(("DR_SEG_0101020"|->0)|->("DR_SEG_0101021"|->0)),(("DR_SEG_0101020"|->1)|->("DR_SEG_0101019"|->1)),(("DR_SEG_0101021"|->0)|->("DR_SEG_0101022"|->0)),(("DR_SEG_0101021"|->0)|->("DR_SEG_0101104"|->0)),(("DR_SEG_0101021"|->1)|->("DR_SEG_0101020"|->1)),(("DR_SEG_0101022"|->0)|->("DR_SEG_0101023"|->0)),(("DR_SEG_0101022"|->1)|->("DR_SEG_0101021"|->1)),(("DR_SEG_0101023"|->0)|->("DR_SEG_0101024"|->0)),(("DR_SEG_0101023"|->1)|->("DR_SEG_0101022"|->1)),(("DR_SEG_0101024"|->0)|->("DR_SEG_0101025"|->0)),(("DR_SEG_0101024"|->1)|->("DR_SEG_0101023"|->1)),(("DR_SEG_0101025"|->0)|->("DR_SEG_0101026"|->0)),(("DR_SEG_0101025"|->1)|->("DR_SEG_0101024"|->1)),(("DR_SEG_0101026"|->0)|->("DR_SEG_0101027"|->0)),(("DR_SEG_0101026"|->1)|->("DR_SEG_0101025"|->1)),(("DR_SEG_0101027"|->0)|->("DR_SEG_0101028"|->0)),(("DR_SEG_0101027"|->1)|->("DR_SEG_0101026"|->1)),(("DR_SEG_0101027"|->1)|->("DR_SEG_0101107"|->1)),(("DR_SEG_0101028"|->0)|->("DR_SEG_0101029"|->0)),(("DR_SEG_0101028"|->1)|->("DR_SEG_0101027"|->1)),(("DR_SEG_0101029"|->0)|->("DR_SEG_0101030"|->0)),(("DR_SEG_0101029"|->1)|->("DR_SEG_0101028"|->1)),(("DR_SEG_0101030"|->0)|->("DR_SEG_0101031"|->0)),(("DR_SEG_0101030"|->1)|->("DR_SEG_0101029"|->1)),(("DR_SEG_0101031"|->0)|->("DR_SEG_0101032"|->0)),(("DR_SEG_0101031"|->1)|->("DR_SEG_0101030"|->1)),(("DR_SEG_0101032"|->0)|->("DR_SEG_0101033"|->0)),(("DR_SEG_0101032"|->1)|->("DR_SEG_0101031"|->1)),(("DR_SEG_0101033"|->0)|->("DR_SEG_0102001"|->0)),(("DR_SEG_0101033"|->1)|->("DR_SEG_0101032"|->1)),(("DR_SEG_0101051"|->0)|->("DR_SEG_0101052"|->0)),(("DR_SEG_0101051"|->1)|->("DR_SEG_0101089"|->1)),(("DR_SEG_0101052"|->0)|->("DR_SEG_0101053"|->0)),(("DR_SEG_0101052"|->1)|->("DR_SEG_0101051"|->1)),(("DR_SEG_0101053"|->0)|->("DR_SEG_0101054"|->0)),(("DR_SEG_0101053"|->1)|->("DR_SEG_0101052"|->1)),(("DR_SEG_0101054"|->0)|->("DR_SEG_0101055"|->0)),(("DR_SEG_0101054"|->1)|->("DR_SEG_0101053"|->1)),(("DR_SEG_0101055"|->0)|->("DR_SEG_0101001"|->0)),(("DR_SEG_0101055"|->0)|->("DR_SEG_0101056"|->0)),(("DR_SEG_0101055"|->1)|->("DR_SEG_0101054"|->1)),(("DR_SEG_0101056"|->0)|->("DR_SEG_0101057"|->0)),(("DR_SEG_0101056"|->1)|->("DR_SEG_0101055"|->1)),(("DR_SEG_0101057"|->0)|->("DR_SEG_0101058"|->0)),(("DR_SEG_0101057"|->1)|->("DR_SEG_0101056"|->1)),(("DR_SEG_0101058"|->0)|->("DR_SEG_0101059"|->0)),(("DR_SEG_0101058"|->1)|->("DR_SEG_0101057"|->1)),(("DR_SEG_0101059"|->0)|->("DR_SEG_0101060"|->0)),(("DR_SEG_0101059"|->1)|->("DR_SEG_0101058"|->1)),(("DR_SEG_0101060"|->0)|->("DR_SEG_0101061"|->0)),(("DR_SEG_0101060"|->1)|->("DR_SEG_0101059"|->1)),(("DR_SEG_0101061"|->0)|->("DR_SEG_0101062"|->0)),(("DR_SEG_0101061"|->1)|->("DR_SEG_0101060"|->1)),(("DR_SEG_0101062"|->0)|->("DR_SEG_0101063"|->0)),(("DR_SEG_0101062"|->1)|->("DR_SEG_0101061"|->1)),(("DR_SEG_0101063"|->0)|->("DR_SEG_0101064"|->0)),(("DR_SEG_0101063"|->1)|->("DR_SEG_0101062"|->1)),(("DR_SEG_0101064"|->0)|->("DR_SEG_0101065"|->0)),(("DR_SEG_0101064"|->0)|->("DR_SEG_0101101"|->0)),(("DR_SEG_0101064"|->1)|->("DR_SEG_0101063"|->1)),(("DR_SEG_0101065"|->0)|->("DR_SEG_0101066"|->0)),(("DR_SEG_0101065"|->1)|->("DR_SEG_0101064"|->1)),(("DR_SEG_0101066"|->0)|->("DR_SEG_0101067"|->0)),(("DR_SEG_0101066"|->1)|->("DR_SEG_0101065"|->1)),(("DR_SEG_0101067"|->0)|->("DR_SEG_0101068"|->0)),(("DR_SEG_0101067"|->1)|->("DR_SEG_0101066"|->1)),(("DR_SEG_0101068"|->0)|->("DR_SEG_0101069"|->0)),(("DR_SEG_0101068"|->1)|->("DR_SEG_0101067"|->1)),(("DR_SEG_0101069"|->0)|->("DR_SEG_0101070"|->0)),(("DR_SEG_0101069"|->1)|->("DR_SEG_0101068"|->1)),(("DR_SEG_0101070"|->0)|->("DR_SEG_0101071"|->0)),(("DR_SEG_0101070"|->1)|->("DR_SEG_0101069"|->1)),(("DR_SEG_0101071"|->0)|->("DR_SEG_0101072"|->0)),(("DR_SEG_0101071"|->1)|->("DR_SEG_0101070"|->1)),(("DR_SEG_0101072"|->0)|->("DR_SEG_0101073"|->0)),(("DR_SEG_0101072"|->1)|->("DR_SEG_0101071"|->1)),(("DR_SEG_0101073"|->0)|->("DR_SEG_0101074"|->0)),(("DR_SEG_0101073"|->1)|->("DR_SEG_0101072"|->1)),(("DR_SEG_0101074"|->0)|->("DR_SEG_0101075"|->0)),(("DR_SEG_0101074"|->1)|->("DR_SEG_0101073"|->1)),(("DR_SEG_0101075"|->0)|->("DR_SEG_0101076"|->0)),(("DR_SEG_0101075"|->1)|->("DR_SEG_0101074"|->1)),(("DR_SEG_0101076"|->0)|->("DR_SEG_0101077"|->0)),(("DR_SEG_0101076"|->1)|->("DR_SEG_0101075"|->1)),(("DR_SEG_0101076"|->1)|->("DR_SEG_0101105"|->1)),(("DR_SEG_0101077"|->0)|->("DR_SEG_0101078"|->0)),(("DR_SEG_0101077"|->1)|->("DR_SEG_0101076"|->1)),(("DR_SEG_0101078"|->0)|->("DR_SEG_0101079"|->0)),(("DR_SEG_0101078"|->1)|->("DR_SEG_0101077"|->1)),(("DR_SEG_0101079"|->0)|->("DR_SEG_0101080"|->0)),(("DR_SEG_0101079"|->1)|->("DR_SEG_0101078"|->1)),(("DR_SEG_0101080"|->0)|->("DR_SEG_0101081"|->0)),(("DR_SEG_0101080"|->1)|->("DR_SEG_0101079"|->1)),(("DR_SEG_0101081"|->0)|->("DR_SEG_0101082"|->0)),(("DR_SEG_0101081"|->0)|->("DR_SEG_0101106"|->0)),(("DR_SEG_0101081"|->1)|->("DR_SEG_0101080"|->1)),(("DR_SEG_0101082"|->0)|->("DR_SEG_0101083"|->0)),(("DR_SEG_0101082"|->1)|->("DR_SEG_0101081"|->1)),(("DR_SEG_0101083"|->0)|->("DR_SEG_0101084"|->0)),(("DR_SEG_0101083"|->1)|->("DR_SEG_0101082"|->1)),(("DR_SEG_0101084"|->0)|->("DR_SEG_0101085"|->0)),(("DR_SEG_0101084"|->1)|->("DR_SEG_0101083"|->1)),(("DR_SEG_0101085"|->0)|->("DR_SEG_0101086"|->0)),(("DR_SEG_0101085"|->1)|->("DR_SEG_0101084"|->1)),(("DR_SEG_0101086"|->0)|->("DR_SEG_0101087"|->0)),(("DR_SEG_0101086"|->1)|->("DR_SEG_0101085"|->1)),(("DR_SEG_0101087"|->0)|->("DR_SEG_0101088"|->0)),(("DR_SEG_0101087"|->1)|->("DR_SEG_0101086"|->1)),(("DR_SEG_0101088"|->0)|->("DR_SEG_0102051"|->0)),(("DR_SEG_0101088"|->1)|->("DR_SEG_0101087"|->1)),(("DR_SEG_0101089"|->0)|->("DR_SEG_0101051"|->0)),(("DR_SEG_0101089"|->1)|->("DR_SEG_0201015"|->1)),(("DR_SEG_0101101"|->0)|->("DR_SEG_0101102"|->0)),(("DR_SEG_0101101"|->1)|->("DR_SEG_0101064"|->1)),(("DR_SEG_0101102"|->0)|->("DR_SEG_0101009"|->0)),(("DR_SEG_0101102"|->1)|->("DR_SEG_0101101"|->1)),(("DR_SEG_0101104"|->0)|->("DR_SEG_0101105"|->0)),(("DR_SEG_0101104"|->1)|->("DR_SEG_0101021"|->1)),(("DR_SEG_0101105"|->0)|->("DR_SEG_0101076"|->0)),(("DR_SEG_0101105"|->1)|->("DR_SEG_0101104"|->1)),(("DR_SEG_0101106"|->0)|->("DR_SEG_0101107"|->0)),(("DR_SEG_0101106"|->1)|->("DR_SEG_0101081"|->1)),(("DR_SEG_0101107"|->0)|->("DR_SEG_0101027"|->0)),(("DR_SEG_0101107"|->1)|->("DR_SEG_0101106"|->1)),(("DR_SEG_0102001"|->0)|->("DR_SEG_0102002"|->0)),(("DR_SEG_0102001"|->1)|->("DR_SEG_0101033"|->1)),(("DR_SEG_0102002"|->0)|->("DR_SEG_0102003"|->0)),(("DR_SEG_0102002"|->1)|->("DR_SEG_0102001"|->1)),(("DR_SEG_0102003"|->0)|->("DR_SEG_0102004"|->0)),(("DR_SEG_0102003"|->1)|->("DR_SEG_0102002"|->1)),(("DR_SEG_0102004"|->0)|->("DR_SEG_0102005"|->0)),(("DR_SEG_0102004"|->1)|->("DR_SEG_0102003"|->1)),(("DR_SEG_0102005"|->0)|->("DR_SEG_0102006"|->0)),(("DR_SEG_0102005"|->1)|->("DR_SEG_0102004"|->1)),(("DR_SEG_0102006"|->0)|->("DR_SEG_0102007"|->0)),(("DR_SEG_0102006"|->0)|->("DR_SEG_0102101"|->0)),(("DR_SEG_0102006"|->1)|->("DR_SEG_0102005"|->1)),(("DR_SEG_0102007"|->0)|->("DR_SEG_0102008"|->0)),(("DR_SEG_0102007"|->1)|->("DR_SEG_0102006"|->1)),(("DR_SEG_0102008"|->0)|->("DR_SEG_0102009"|->0)),(("DR_SEG_0102008"|->1)|->("DR_SEG_0102007"|->1)),(("DR_SEG_0102009"|->0)|->("DR_SEG_0102010"|->0)),(("DR_SEG_0102009"|->1)|->("DR_SEG_0102008"|->1)),(("DR_SEG_0102010"|->0)|->("DR_SEG_0102011"|->0)),(("DR_SEG_0102010"|->1)|->("DR_SEG_0102009"|->1)),(("DR_SEG_0102011"|->0)|->("DR_SEG_0102012"|->0)),(("DR_SEG_0102011"|->1)|->("DR_SEG_0102010"|->1)),(("DR_SEG_0102012"|->0)|->("DR_SEG_0102013"|->0)),(("DR_SEG_0102012"|->1)|->("DR_SEG_0102011"|->1)),(("DR_SEG_0102012"|->1)|->("DR_SEG_0102104"|->1)),(("DR_SEG_0102013"|->0)|->("DR_SEG_0102014"|->0)),(("DR_SEG_0102013"|->1)|->("DR_SEG_0102012"|->1)),(("DR_SEG_0102014"|->0)|->("DR_SEG_0102015"|->0)),(("DR_SEG_0102014"|->1)|->("DR_SEG_0102013"|->1)),(("DR_SEG_0102015"|->0)|->("DR_SEG_0102016"|->0)),(("DR_SEG_0102015"|->1)|->("DR_SEG_0102014"|->1)),(("DR_SEG_0102016"|->1)|->("DR_SEG_0102015"|->1)),(("DR_SEG_0102051"|->0)|->("DR_SEG_0102052"|->0)),(("DR_SEG_0102051"|->1)|->("DR_SEG_0101088"|->1)),(("DR_SEG_0102052"|->0)|->("DR_SEG_0102053"|->0)),(("DR_SEG_0102052"|->1)|->("DR_SEG_0102051"|->1)),(("DR_SEG_0102053"|->0)|->("DR_SEG_0102054"|->0)),(("DR_SEG_0102053"|->1)|->("DR_SEG_0102052"|->1)),(("DR_SEG_0102054"|->0)|->("DR_SEG_0102055"|->0)),(("DR_SEG_0102054"|->1)|->("DR_SEG_0102053"|->1)),(("DR_SEG_0102055"|->0)|->("DR_SEG_0102056"|->0)),(("DR_SEG_0102055"|->1)|->("DR_SEG_0102054"|->1)),(("DR_SEG_0102056"|->0)|->("DR_SEG_0102057"|->0)),(("DR_SEG_0102056"|->1)|->("DR_SEG_0102055"|->1)),(("DR_SEG_0102056"|->1)|->("DR_SEG_0102102"|->1)),(("DR_SEG_0102057"|->0)|->("DR_SEG_0102058"|->0)),(("DR_SEG_0102057"|->1)|->("DR_SEG_0102056"|->1)),(("DR_SEG_0102058"|->0)|->("DR_SEG_0102059"|->0)),(("DR_SEG_0102058"|->1)|->("DR_SEG_0102057"|->1)),(("DR_SEG_0102059"|->0)|->("DR_SEG_0102060"|->0)),(("DR_SEG_0102059"|->1)|->("DR_SEG_0102058"|->1)),(("DR_SEG_0102060"|->0)|->("DR_SEG_0102061"|->0)),(("DR_SEG_0102060"|->0)|->("DR_SEG_0102103"|->0)),(("DR_SEG_0102060"|->1)|->("DR_SEG_0102059"|->1)),(("DR_SEG_0102061"|->0)|->("DR_SEG_0102062"|->0)),(("DR_SEG_0102061"|->1)|->("DR_SEG_0102060"|->1)),(("DR_SEG_0102062"|->0)|->("DR_SEG_0102063"|->0)),(("DR_SEG_0102062"|->1)|->("DR_SEG_0102061"|->1)),(("DR_SEG_0102063"|->1)|->("DR_SEG_0102062"|->1)),(("DR_SEG_0102101"|->0)|->("DR_SEG_0102102"|->0)),(("DR_SEG_0102101"|->1)|->("DR_SEG_0102006"|->1)),(("DR_SEG_0102102"|->0)|->("DR_SEG_0102056"|->0)),(("DR_SEG_0102102"|->1)|->("DR_SEG_0102101"|->1)),(("DR_SEG_0102103"|->0)|->("DR_SEG_0102104"|->0)),(("DR_SEG_0102103"|->1)|->("DR_SEG_0102060"|->1)),(("DR_SEG_0102104"|->0)|->("DR_SEG_0102012"|->0)),(("DR_SEG_0102104"|->1)|->("DR_SEG_0102103"|->1)),(("DR_SEG_0201001"|->0)|->("DR_SEG_0201002"|->0)),(("DR_SEG_0201002"|->0)|->("DR_SEG_0201003"|->0)),(("DR_SEG_0201002"|->1)|->("DR_SEG_0201001"|->1)),(("DR_SEG_0201003"|->0)|->("DR_SEG_0201004"|->0)),(("DR_SEG_0201003"|->1)|->("DR_SEG_0201002"|->1)),(("DR_SEG_0201003"|->1)|->("DR_SEG_0201102"|->1)),(("DR_SEG_0201004"|->0)|->("DR_SEG_0201005"|->0)),(("DR_SEG_0201004"|->1)|->("DR_SEG_0201003"|->1)),(("DR_SEG_0201005"|->0)|->("DR_SEG_0201006"|->0)),(("DR_SEG_0201005"|->1)|->("DR_SEG_0201004"|->1)),(("DR_SEG_0201006"|->0)|->("DR_SEG_0201007"|->0)),(("DR_SEG_0201006"|->1)|->("DR_SEG_0201005"|->1)),(("DR_SEG_0201006"|->1)|->("DR_SEG_0201104"|->1)),(("DR_SEG_0201007"|->0)|->("DR_SEG_0201008"|->0)),(("DR_SEG_0201007"|->1)|->("DR_SEG_0201006"|->1)),(("DR_SEG_0201008"|->0)|->("DR_SEG_0201009"|->0)),(("DR_SEG_0201008"|->1)|->("DR_SEG_0201007"|->1)),(("DR_SEG_0201009"|->0)|->("DR_SEG_0201010"|->0)),(("DR_SEG_0201009"|->1)|->("DR_SEG_0201008"|->1)),(("DR_SEG_0201010"|->0)|->("DR_SEG_0201011"|->0)),(("DR_SEG_0201010"|->1)|->("DR_SEG_0201009"|->1)),(("DR_SEG_0201011"|->0)|->("DR_SEG_0201012"|->0)),(("DR_SEG_0201011"|->1)|->("DR_SEG_0201010"|->1)),(("DR_SEG_0201012"|->0)|->("DR_SEG_0201013"|->0)),(("DR_SEG_0201012"|->1)|->("DR_SEG_0201011"|->1)),(("DR_SEG_0201013"|->0)|->("DR_SEG_0201014"|->0)),(("DR_SEG_0201013"|->1)|->("DR_SEG_0201012"|->1)),(("DR_SEG_0201013"|->1)|->("DR_SEG_0201106"|->1)),(("DR_SEG_0201014"|->0)|->("DR_SEG_0201015"|->0)),(("DR_SEG_0201014"|->1)|->("DR_SEG_0201013"|->1)),(("DR_SEG_0201015"|->0)|->("DR_SEG_0101089"|->0)),(("DR_SEG_0201015"|->0)|->("DR_SEG_0201016"|->0)),(("DR_SEG_0201015"|->1)|->("DR_SEG_0201014"|->1)),(("DR_SEG_0201016"|->1)|->("DR_SEG_0201015"|->1)),(("DR_SEG_0201051"|->0)|->("DR_SEG_0201052"|->0)),(("DR_SEG_0201052"|->0)|->("DR_SEG_0201053"|->0)),(("DR_SEG_0201052"|->1)|->("DR_SEG_0201051"|->1)),(("DR_SEG_0201053"|->0)|->("DR_SEG_0201054"|->0)),(("DR_SEG_0201053"|->0)|->("DR_SEG_0201101"|->0)),(("DR_SEG_0201053"|->1)|->("DR_SEG_0201052"|->1)),(("DR_SEG_0201054"|->0)|->("DR_SEG_0201055"|->0)),(("DR_SEG_0201054"|->1)|->("DR_SEG_0201053"|->1)),(("DR_SEG_0201055"|->0)|->("DR_SEG_0201056"|->0)),(("DR_SEG_0201055"|->1)|->("DR_SEG_0201054"|->1)),(("DR_SEG_0201056"|->0)|->("DR_SEG_0201057"|->0)),(("DR_SEG_0201056"|->0)|->("DR_SEG_0201103"|->0)),(("DR_SEG_0201056"|->1)|->("DR_SEG_0201055"|->1)),(("DR_SEG_0201057"|->0)|->("DR_SEG_0201058"|->0)),(("DR_SEG_0201057"|->1)|->("DR_SEG_0201056"|->1)),(("DR_SEG_0201058"|->0)|->("DR_SEG_0201059"|->0)),(("DR_SEG_0201058"|->1)|->("DR_SEG_0201057"|->1)),(("DR_SEG_0201059"|->0)|->("DR_SEG_0201060"|->0)),(("DR_SEG_0201059"|->1)|->("DR_SEG_0201058"|->1)),(("DR_SEG_0201060"|->0)|->("DR_SEG_0201061"|->0)),(("DR_SEG_0201060"|->1)|->("DR_SEG_0201059"|->1)),(("DR_SEG_0201061"|->0)|->("DR_SEG_0201062"|->0)),(("DR_SEG_0201061"|->1)|->("DR_SEG_0201060"|->1)),(("DR_SEG_0201062"|->0)|->("DR_SEG_0201063"|->0)),(("DR_SEG_0201062"|->0)|->("DR_SEG_0201105"|->0)),(("DR_SEG_0201062"|->1)|->("DR_SEG_0201061"|->1)),(("DR_SEG_0201063"|->0)|->("DR_SEG_0201064"|->0)),(("DR_SEG_0201063"|->1)|->("DR_SEG_0201062"|->1)),(("DR_SEG_0201064"|->1)|->("DR_SEG_0201063"|->1)),(("DR_SEG_0201101"|->0)|->("DR_SEG_0201102"|->0)),(("DR_SEG_0201101"|->1)|->("DR_SEG_0201053"|->1)),(("DR_SEG_0201102"|->0)|->("DR_SEG_0201003"|->0)),(("DR_SEG_0201102"|->1)|->("DR_SEG_0201101"|->1)),(("DR_SEG_0201103"|->0)|->("DR_SEG_0201104"|->0)),(("DR_SEG_0201103"|->1)|->("DR_SEG_0201056"|->1)),(("DR_SEG_0201104"|->0)|->("DR_SEG_0201006"|->0)),(("DR_SEG_0201104"|->1)|->("DR_SEG_0201103"|->1)),(("DR_SEG_0201105"|->0)|->("DR_SEG_0201106"|->0)),(("DR_SEG_0201105"|->1)|->("DR_SEG_0201062"|->1)),(("DR_SEG_0201106"|->0)|->("DR_SEG_0201013"|->0)),(("DR_SEG_0201106"|->1)|->("DR_SEG_0201105"|->1))} & dist_suiv = dist - {("DR_SEG_0101001"|->6006),("DR_SEG_0101002"|->35500),("DR_SEG_0101003"|->3825),("DR_SEG_0101004"|->7475),("DR_SEG_0101005"|->59700),("DR_SEG_0101006"|->3959),("DR_SEG_0101007"|->3641),("DR_SEG_0101008"|->5577),("DR_SEG_0101009"|->2023),("DR_SEG_0101010"|->10200),("DR_SEG_0101011"|->56600),("DR_SEG_0101012"|->3966),("DR_SEG_0101013"|->7534),("DR_SEG_0101014"|->30700),("DR_SEG_0101015"|->30800),("DR_SEG_0101016"|->3966),("DR_SEG_0101017"|->7734),("DR_SEG_0101018"|->7985),("DR_SEG_0101019"|->29715),("DR_SEG_0101020"|->3100),("DR_SEG_0101021"|->2304),("DR_SEG_0101022"|->6196),("DR_SEG_0101023"|->21000),("DR_SEG_0101024"|->3761),("DR_SEG_0101025"|->3939),("DR_SEG_0101026"|->5880),("DR_SEG_0101027"|->1),("DR_SEG_0101028"|->11819),("DR_SEG_0101029"|->39400),("DR_SEG_0101030"|->39400),("DR_SEG_0101031"|->4054),("DR_SEG_0101032"|->7746),("DR_SEG_0101033"|->33200),("DR_SEG_0101051"|->3612),("DR_SEG_0101052"|->2413),("DR_SEG_0101053"|->6000),("DR_SEG_0101054"|->3500),("DR_SEG_0101055"|->2294),("DR_SEG_0101056"|->5706),("DR_SEG_0101057"|->3900),("DR_SEG_0101058"|->28100),("DR_SEG_0101059"|->7980),("DR_SEG_0101060"|->3320),("DR_SEG_0101061"|->59700),("DR_SEG_0101062"|->7559),("DR_SEG_0101063"|->4541),("DR_SEG_0101064"|->420),("DR_SEG_0101065"|->6480),("DR_SEG_0101066"|->3700),("DR_SEG_0101067"|->59300),("DR_SEG_0101068"|->7839),("DR_SEG_0101069"|->3661),("DR_SEG_0101070"|->30700),("DR_SEG_0101071"|->31600),("DR_SEG_0101072"|->7162),("DR_SEG_0101073"|->3538),("DR_SEG_0101074"|->44800),("DR_SEG_0101075"|->6377),("DR_SEG_0101076"|->2123),("DR_SEG_0101077"|->16900),("DR_SEG_0101078"|->3800),("DR_SEG_0101079"|->4256),("DR_SEG_0101080"|->3744),("DR_SEG_0101081"|->1500),("DR_SEG_0101082"|->6500),("DR_SEG_0101083"|->3700),("DR_SEG_0101084"|->40500),("DR_SEG_0101085"|->40000),("DR_SEG_0101086"|->8548),("DR_SEG_0101087"|->3552),("DR_SEG_0101088"|->33400),("DR_SEG_0101089"|->100),("DR_SEG_0101101"|->2080),("DR_SEG_0101102"|->2377),("DR_SEG_0101104"|->1946),("DR_SEG_0101105"|->2127),("DR_SEG_0101106"|->2075),("DR_SEG_0101107"|->2305),("DR_SEG_0102001"|->33400),("DR_SEG_0102002"|->4081),("DR_SEG_0102003"|->8219),("DR_SEG_0102004"|->21900),("DR_SEG_0102005"|->4100),("DR_SEG_0102006"|->2410),("DR_SEG_0102007"|->6190),("DR_SEG_0102008"|->7400),("DR_SEG_0102009"|->4116),("DR_SEG_0102010"|->3784),("DR_SEG_0102011"|->5834),("DR_SEG_0102012"|->1066),("DR_SEG_0102013"|->6100),("DR_SEG_0102014"|->1900),("DR_SEG_0102015"|->300),("DR_SEG_0102016"|->5946),("DR_SEG_0102051"|->32900),("DR_SEG_0102052"|->8575),("DR_SEG_0102053"|->3525),("DR_SEG_0102054"|->30500),("DR_SEG_0102055"|->6479),("DR_SEG_0102056"|->4721),("DR_SEG_0102057"|->4800),("DR_SEG_0102058"|->4310),("DR_SEG_0102059"|->3590),("DR_SEG_0102060"|->1376),("DR_SEG_0102061"|->5724),("DR_SEG_0102062"|->12546),("DR_SEG_0102063"|->1500),("DR_SEG_0102101"|->1865),("DR_SEG_0102102"|->2204),("DR_SEG_0102103"|->2074),("DR_SEG_0102104"|->2384),("DR_SEG_0201001"|->16300),("DR_SEG_0201002"|->6000),("DR_SEG_0201003"|->2200),("DR_SEG_0201004"|->12900),("DR_SEG_0201005"|->5500),("DR_SEG_0201006"|->1400),("DR_SEG_0201007"|->72900),("DR_SEG_0201008"|->100000),("DR_SEG_0201009"|->100000),("DR_SEG_0201010"|->100000),("DR_SEG_0201011"|->74800),("DR_SEG_0201012"|->6200),("DR_SEG_0201013"|->9300),("DR_SEG_0201014"|->7800),("DR_SEG_0201015"|->75),("DR_SEG_0201016"|->5825),("DR_SEG_0201051"|->7300),("DR_SEG_0201052"|->10400),("DR_SEG_0201053"|->600),("DR_SEG_0201054"|->12900),("DR_SEG_0201055"|->6800),("DR_SEG_0201056"|->500),("DR_SEG_0201057"|->78400),("DR_SEG_0201058"|->100000),("DR_SEG_0201059"|->100000),("DR_SEG_0201060"|->100000),("DR_SEG_0201061"|->74800),("DR_SEG_0201062"|->2200),("DR_SEG_0201063"|->10600),("DR_SEG_0201064"|->11100),("DR_SEG_0201101"|->1900),("DR_SEG_0201102"|->1800),("DR_SEG_0201103"|->2100),("DR_SEG_0201104"|->2000),("DR_SEG_0201105"|->2000),("DR_SEG_0201106"|->2000)}(seg_suiv))}})
    # TODO:
  

    # TODO: constraints with variables affecting each other
    # the constraint solver musst find out that x has to be enumerated before y
    # e.g C578.EML.014/662_001 {cb,cc,cd,ce,cf,cg,|cb|->cc|->ce:bq & cf=cc & cd=0 & cg=(be;bj)(cb|->cc)} with cb cc not set
    # C578.EML.014/623_001 {bp,bq,br,bs,bt,bu,|bp|->bq|->bs:bj & bt=bq & br=1 & bu=(az;bb)(bp|->bq)} with preimage = ('bp', 'bq')
    # enumeration.py 99
    def test_constraint_affecting_variables(self):
        # Build AST:
        string_to_file("#PREDICATE {(0,\"A\"),(1,\"B\"),(2,\"C\"),(3,\"D\")}={x, y | x : {0,1,2,3,4,5,6,7,8,9,10} & y : {(\"A\"|->41),(\"B\"|->42),(\"C\"|->43),(\"D\"|->44)}~[{{(0|->41),(1|->42),(2|->43),(3|->44),(4|->45)}(x)}]}", file_name)
        ast_string = file_to_AST_str(file_name)
        root = str_ast_to_python_ast(ast_string) 
        
        # Test
        env = Environment()
        env._min_int = -2**32
        env._max_int = 2**32  
        
        type_with_known_types(root, env, [], []) 
        assert isinstance(get_type_by_name(env, "x"), IntegerType)
        assert isinstance(get_type_by_name(env, "y"), StringType) 
        setcomp_predicate = root.children[0].children[1]  
        assert isinstance(setcomp_predicate, AComprehensionSetExpression)
        set_predicate = setcomp_predicate.children[2]    
        var0 = setcomp_predicate.children[0]
        var1 = setcomp_predicate.children[1]
        assert isinstance(set_predicate, AConjunctPredicate )
        map = _categorize_predicates(set_predicate, env, [var0, var1]) 
        constraint0 = map[set_predicate.children[0]]
        time0 = constraint0.time
        vars0 = constraint0.constrained_vars
        compute_first0 = constraint0.vars_need_to_be_set_first   
        constraint1 = map[set_predicate.children[1]]
        time1 = constraint1.time
        vars1 = constraint1.constrained_vars
        compute_first1 = constraint1.vars_need_to_be_set_first   
        assert set(vars0)==set(["x"])
        assert time0<2**22 
        assert compute_first0 == []
        assert set(vars1)==set(["y"])
        assert time1<2**22 
        assert compute_first1 == ["x"]       
        assert interpret(root, env)    


    # topologic sort and test set generation fails
    #import pytest
    #@pytest.mark.xfail 
    #def test_constraint_affecting_variables_self_constraint(self):
    #    # Build AST:
    #    string_to_file("#PREDICATE {3}={y| {(1,7),(2,6),(3,3)}(y)=y}", file_name)
    #    ast_string = file_to_AST_str(file_name)
    #    root = str_ast_to_python_ast(ast_string) 
    #    
    #    # Test
    #    env = Environment()
    #    env._min_int = -2**32
    #    env._max_int = 2**32
    #    assert interpret(root, env)     

        
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
        E= setexpr.children[-1]
        assert isinstance(P, Predicate)
        env._min_int = -2**8
        env._max_int = 2**8
        domain = compute_using_external_solver(P, env, varList)
        assert frozenset([x["x"] for x in domain])==frozenset([-4,-3,-2,-1,1,2,3,4])
        


    # TODO: Match ACoupleExpression with frozenset elements
    def test_constraint_tuple_equal_expression1(self):
        # solution a,b,c= 1,1,1
        string_to_file("#PREDICATE #(a,b,c).(a|->b|->c = (1,1,1))", file_name)
        ast_string = file_to_AST_str(file_name)
        root = str_ast_to_python_ast(ast_string)
        
        # Test
        env = Environment()
        env._min_int = -2**32
        env._max_int = 2**32
        a = root.children[0].children[0]
        b = root.children[0].children[1]
        c = root.children[0].children[2]
        equal_predicate = root.children[0].children[-1]
        map = _categorize_predicates(equal_predicate, env, [a, b, c]) 
        constraint = map[equal_predicate]
        time = constraint.time
        vars = constraint.constrained_vars
        compute_first = constraint.vars_need_to_be_set_first     
        assert time<2**32
        assert set(vars) ==set(["a","b","c"])
        assert compute_first == []
        assert interpret(root, env) 

        
    # C578_Final_Jul13/m-PROP_SCL_VTT_S_0316_001
    # can not constrain crf    
    #!(crc,crd,cre,crf,crg,crh,cri,crj).(crc: 0..AG-1 & crd: 0..AH-1 & cre: 0..AI-1 & crf|->crg|->crh|->cri|->crj = {TRUE|->((bk;dg)(crb|->cre)|->bl(crb|->cre)|->(bj;df)(crb|->cre)|->bi(crb|->cre)|->(bm;dh)(crb|->cre)),FALSE|->(AF|->AF|->AF|->AF|->AL)}(bool(cre<bn(crb))) => cj(cra|->crc) = (bp;dd)(crb|->crc) & ck(cra|->crd) = (bq;dd)(crb|->crd) & cn(cra|->cre) = crf & co(cra|->cre) = crg & cm(cra|->cre) = crh & cl(cra|->cre) = cri & cp(cra|->cre) = crj)))) = TRUE        
    def test_constraint_tuple_equal_expression2(self):
        # solution a,b,c,d,e = 1,1,1,1,1
        string_to_file("#PREDICATE #(a,b,c,d,e).(a|->b|->c|->d|->e ={TRUE|->(1,1,1,1,1),FALSE|->(0,0,0,0,0)}(bool(1<2)))", file_name)
        ast_string = file_to_AST_str(file_name)
        root = str_ast_to_python_ast(ast_string)
        
        # Test
        env = Environment()
        env._min_int = -2**32
        env._max_int = 2**32
        assert interpret(root, env)   
        

    # C578_Urgent_Jul13/151_001 
    import pytest
    @pytest.mark.xfail
    def test_constraint_interval_fun_app_one_args(self):
        # solution a,b,c,d,e = 1,1,1,1,1
        string_to_file("#PREDICATE !x,y.(x:{3,4,5} & y:0..{0 |-> 4,1 |-> 4,2 |-> 4,3 |-> 4}(x)-1 => 1<2)", file_name)
        ast_string = file_to_AST_str(file_name)
        root = str_ast_to_python_ast(ast_string)
        
        # Test
        env = Environment()
        env._min_int = -2**32
        env._max_int = 2**32
        py.test.raises(ValueNotInDomainException, "assert interpret(root, env)")       


    # C578_Urgent_Jul13/151_001 
    import pytest
    @pytest.mark.xfail
    def test_constraint_interval_fun_app_two_args(self):
        # solution a,b,c,d,e = 1,1,1,1,1
        string_to_file("#PREDICATE !x,y,z.(x:{3,4,5} & y:{1,2,3} & z:0..{3|->{0 |-> 4,1 |-> 4,2 |-> 4,3 |-> 4}}(x)(y)-1 => 1<2)", file_name)
        ast_string = file_to_AST_str(file_name)
        root = str_ast_to_python_ast(ast_string)
        
        # Test
        env = Environment()
        env._min_int = -2**32
        env._max_int = 2**32
        py.test.raises(ValueNotInDomainException, "assert interpret(root, env)")
        
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
