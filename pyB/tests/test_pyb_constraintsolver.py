# -*- coding: utf-8 -*-
from ast_nodes import *
from btypes import *
from bexceptions import ValueNotInDomainException
from config import TOO_MANY_ITEMS
from constraintsolver import Constraint, _analyze_predicates, compute_constrained_domains
from environment import Environment
from helpers import file_to_AST_str, string_to_file
from interp import interpret
from parsing import str_ast_to_python_ast
from util import type_with_known_types, get_type_by_name



from config import USE_RPYTHON_CODE
if USE_RPYTHON_CODE:
     from rpython_b_objmodel import frozenset

file_name = "input.txt"

class TestPyBConstraintSolver():
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
        map = _analyze_predicates(set_predicate, env, [var])
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
        map = _analyze_predicates(set_predicate, env, [var])
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
        map = _analyze_predicates(set_predicate, env, [var])
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
        map = _analyze_predicates(set_predicate, env, [var])
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
        map = _analyze_predicates(set_predicate, env, [var])
        #constraint0 = map[set_predicate.children[0]]
        #time0 = constraint0.time
        #vars0 = constraint0.constrained_vars
        #compute_first0 = constraint0.vars_need_to_be_set_first
        constraint1 = map[set_predicate.children[1]]
        time1 = constraint1.time
        vars1 = constraint1.constrained_vars
        compute_first1 = constraint1.vars_need_to_be_set_first
        #assert time0==TOO_MANY_ITEMS+2    
        assert isinstance(time1, int) 
        #assert vars0==["x"]
        assert vars1==["x"]
        #assert compute_first0 == []
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
        map = _analyze_predicates(set_predicate, env, [var]) 
        #constraint0 = map[set_predicate.children[0]]
        #time0 = constraint0.time
        #vars0 = constraint0.constrained_vars
        #compute_first0 = constraint0.vars_need_to_be_set_first
        constraint1 = map[set_predicate.children[1]]
        time1 = constraint1.time
        vars1 = constraint1.constrained_vars
        compute_first1 = constraint1.vars_need_to_be_set_first
        #assert time0==TOO_MANY_ITEMS+2    
        assert time1 <TOO_MANY_ITEMS
        #assert vars0==["x"]
        assert vars1==["x"] 
        #assert compute_first0 == []
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
        map = _analyze_predicates(set_predicate, env, [var])
        
        #assert isinstance(set_predicate.children[0], AMemberPredicate)
        #constraint0 = map[set_predicate.children[0]]
        #time0 = constraint0.time
        #vars0 = constraint0.constrained_vars
        #compute_first0 = constraint0.vars_need_to_be_set_first
        assert isinstance(set_predicate.children[1], ADisjunctPredicate)
        constraint1 = map[set_predicate.children[1]]
        time1 = constraint1.time
        vars1 = constraint1.constrained_vars
        compute_first1 = constraint1.vars_need_to_be_set_first
        
        #assert time0==TOO_MANY_ITEMS+2    
        assert time1 <TOO_MANY_ITEMS
        #assert vars0==["x"]
        assert vars1==["x"]  
        #assert compute_first0 == []
        assert compute_first1 == []   
        # works, but take too much time (232.09 seconds)
        #result = interpret(root, env)
        #assert len(result)==44100    
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
        map = _analyze_predicates(set_predicate, env, [var])  
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
        map = _analyze_predicates(set_predicate, env, [var])  
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
        map = _analyze_predicates(set_predicate, env, [var])    
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
        map = _analyze_predicates(set_predicate, env, [var])    
        #constraint0 = map[set_predicate.children[0]]
        #time0 = constraint0.time
        #vars0 = constraint0.constrained_vars
        #compute_first0 = constraint0.vars_need_to_be_set_first
        constraint1 = map[set_predicate.children[1]]
        time1 = constraint1.time
        vars1 = constraint1.constrained_vars
        compute_first1 = constraint1.vars_need_to_be_set_first      
        #assert vars0==["x"]
        assert vars1==["x"]
        #assert time0==TOO_MANY_ITEMS+2
        assert time1<2**22   
        #assert compute_first0 == []
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
        map = _analyze_predicates(set_predicate, env, [var])  
        #constraint0 = map[set_predicate.children[0]]
        #time0 = constraint0.time
        #vars0 = constraint0.constrained_vars
        #compute_first0 = constraint0.vars_need_to_be_set_first
        constraint1 = map[set_predicate.children[1]]
        time1 = constraint1.time
        vars1 = constraint1.constrained_vars
        compute_first1 = constraint1.vars_need_to_be_set_first
        #assert vars0==["x"]
        assert vars1==["x"]
        #assert time0==TOO_MANY_ITEMS+2
        assert time1<2**22   
        #assert compute_first0 == []
        assert compute_first1 == []
        result = interpret(root, env)
        assert result==frozenset([(2, 0), (2, 3), (2, 1)])


    def test_constraint_set_comp14(self):
        # {x|P}
        # Build AST:
        string_to_file("#EXPRESSION %x.(x : STRING - {\"CL\",\"CM\"}|-1)", file_name)
        ast_string = file_to_AST_str(file_name)
        root = str_ast_to_python_ast(ast_string)  
        
        # Test
        env = Environment()
        env._min_int = -2**32
        env._max_int = 2**32
        type_with_known_types(root, env, [], [""])
        assert isinstance(get_type_by_name(env, "x"), StringType)       
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
        map = _analyze_predicates(set_predicate, env, [var])  
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
        map = _analyze_predicates(set_predicate, env, [var])  
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
        map = _analyze_predicates(set_predicate, env, [var0, var1])  
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
        map = _analyze_predicates(set_predicate, env, [var0, var1, var2])  
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
        map = _analyze_predicates(set_predicate, env, [var0, var1, var2, var3, var4])  
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
        x = root.children[0].children[0]
        y = root.children[0].children[1]
        conjunct_predicate = root.children[0].children[-1]
        map = _analyze_predicates(conjunct_predicate, env, [x,y]) 
        constraint = map[conjunct_predicate.children[0]]
        time = constraint.time
        vars = constraint.constrained_vars
        compute_first = constraint.vars_need_to_be_set_first 
        assert time<2**32
        assert set(vars) ==set(["x"])  
        assert compute_first == ["y"]
        constraint = map[conjunct_predicate.children[1]]
        time = constraint.time
        vars = constraint.constrained_vars
        compute_first = constraint.vars_need_to_be_set_first 
        assert time<2**32
        assert set(vars) ==set(["y"])  
        assert compute_first == ["x"]
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
        map = _analyze_predicates(set_predicate, env, [var0, var1]) 
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
        map = _analyze_predicates(equal_predicate, env, [a, b, c]) 
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
        a = root.children[0].children[0]
        b = root.children[0].children[1]
        c = root.children[0].children[2]
        d = root.children[0].children[3]
        e = root.children[0].children[4]
        equal_predicate = root.children[0].children[-1]
        map = _analyze_predicates(equal_predicate, env, [a, b, c, d, e]) 
        constraint = map[equal_predicate]
        time = constraint.time
        vars = constraint.constrained_vars
        compute_first = constraint.vars_need_to_be_set_first 
        assert time<2**32
        assert set(vars) ==set(["a","b","c","d","e"])  
        assert compute_first == []
        assert interpret(root, env)   
        

    # C578_Urgent_Jul13/151_001 
    def test_constraint_interval_fun_app_one_args(self):
        string_to_file("#PREDICATE !x,y.(x:{3,4,5} & y:0..{0 |-> 4,1 |-> 4,2 |-> 4,3 |-> 4}(x)-1 => 1<2)", file_name)
        ast_string = file_to_AST_str(file_name)
        root = str_ast_to_python_ast(ast_string)
        
        # Test
        env = Environment()
        env._min_int = -2**32
        env._max_int = 2**32
        assert interpret(root, env)    


    # C578_Urgent_Jul13/151_001 
    def test_constraint_interval_fun_app_two_args(self):
        string_to_file("#PREDICATE !x,y,z.(x:{3,4,5} & y:{1,2,3} & z:0..{3|->{0 |-> 4,1 |-> 4,2 |-> 4,3 |-> 4}}(x)(y)-1 => 1<2)", file_name)
        ast_string = file_to_AST_str(file_name)
        root = str_ast_to_python_ast(ast_string)
        
        # Test
        env = Environment()
        env._min_int = -2**32
        env._max_int = 2**32
        assert interpret(root, env)  


    def test_constraint_inverse0(self):
        # Build AST:
        string_to_file("#PREDICATE {(99,42),(100,43)}={x|x:0..100<|{(42,99),(43,100),(44,101)}~}", file_name)
        ast_string = file_to_AST_str(file_name)
        root = str_ast_to_python_ast(ast_string)

        # Test
        env = Environment()
        assert interpret(root,env)


    def test_constraint_inverse1(self):
        # Build AST:
        string_to_file("#PREDICATE {(0,1),(1,0),(1,1)}={x,y|x:0..1 & y:0..1 & #(z).(z:(0..100<|{(42,99),(43,100),(44,101)})~[{{((1|->1)|->99),((0|->0)|->102),((1|->0)|->101),((0|->1)|->100)}(x|->y)}])}", file_name)
        ast_string = file_to_AST_str(file_name)
        root = str_ast_to_python_ast(ast_string)

        # Test
        env = Environment()
        assert interpret(root,env) 
 
        
    def test_constraint_inverse2(self):
        # Build AST:
        string_to_file("#PREDICATE {((0,1)|->43), ((1,0)|->44), ((1,1)|->42) }={x,y,z|x:0..1 & y:0..1 & z:(0..100<|{(42,99),(43,100),(44,101)})~[{{((1|->1)|->99),((0|->0)|->102),((1|->0)|->101),((0|->1)|->100)}(x|->y)}]}", file_name)
        ast_string = file_to_AST_str(file_name)
        root = str_ast_to_python_ast(ast_string)

        # Test
        env = Environment()
        assert interpret(root,env)       

    # C578/2013_08_14/machines_27082013/R_02_002
    #def test_constraint_restr(self):
    #    # Build AST:
    #    string_to_file("#PREDICATE {((2,1),7)}  = (0..100)*INTEGER<|({((2|->1)|->42)};{(7|->42)}~) ", file_name)
    #    ast_string = file_to_AST_str(file_name)
    #    root = str_ast_to_python_ast(ast_string)
    #
    #    # Test
    #    env = Environment()
    #    assert interpret(root,env)
    
     
    #def test_constraint_lambda_membership(self):
    #    # Build AST:
    #    string_to_file("#PREDICATE {z_|z_ : (INTEGER * INTEGER) * INTEGER & (z_ : {((2|->3)|->180)} or (prj1(INTEGER*INTEGER,INTEGER)(z_) /: dom({((2|->3)|->180)}) & z_ : ((0 .. 209) * (0 .. 209)) * {-1}))}:INTEGER*INTEGER<->INTEGER   ", file_name)
    #    ast_string = file_to_AST_str(file_name)
    #    root = str_ast_to_python_ast(ast_string)
    #
    #    # Test
    #    env = Environment()
    #    assert interpret(root,env)   

    # C578/2013_08_14/machines_14082013/Z_01_001.mch 
    # S= {(0|->64),(0|->65),(1|->66),(1|->67),(2|->68),(2|->69),(3|->70),(3|->71),(4|->0),
    # (4|->1),(5|->2),(5|->3),(6|->4),(6|->5),(7|->6),(7|->7),(8|->8),(8|->9),(9|->10),
    # (9|->11),(10|->12),(10|->13),(11|->14),(11|->15),(12|->16),(12|->17),(13|->18),(13|->19),
    # (14|->20),(14|->21),(15|->22),(15|->23),(16|->24),(16|->25),(17|->26),(17|->27),(18|->28),
    # (18|->29),(19|->30),(19|->31),(20|->32),(20|->33),(21|->34),(21|->35),(22|->36),(22|->37),
    # (23|->38),(23|->39),(24|->40),(24|->41),(25|->42),(25|->43),(26|->44),(26|->45),(27|->46),
    # (27|->47),(28|->48),(28|->49),(29|->50),(29|->51),(30|->52),(30|->53),(31|->54),(31|->55),
    # (32|->56),(32|->57),(33|->58),(33|->59),(34|->60),(34|->61),(35|->62),(35|->63),(36|->144),
    # (36|->829),(37|->146),(37|->831),(38|->147),(38|->148),(39|->149),(39|->150),(40|->151),
    # (40|->152),(41|->153),(41|->154),(42|->155),(42|->156),(43|->157),(43|->158),(44|->159),
    # (44|->160),(45|->161),(45|->162),(46|->163),(46|->164),(47|->165),(47|->166),(48|->167),
    # (48|->168),(49|->169),(49|->170),(50|->171),(50|->172),(51|->173),(51|->174),(52|->175),
    # (52|->176),(53|->177),(53|->178),(54|->179),(54|->180),(55|->181),(55|->182),(56|->183),
    # (56|->184),(57|->185),(57|->186),(58|->187),(58|->188),(59|->189),(59|->190),(60|->191),
    # (60|->192),(61|->193),(61|->194),(62|->195),(62|->196),(63|->197),(63|->198),(64|->199),
    # (64|->200),(65|->269),(65|->270),(66|->271),(66|->272),(67|->201),(67|->202),(68|->203),
    # (68|->204),(69|->205),(69|->206),(70|->273),(70|->274),(71|->429),(71|->430),(72|->638),
    # (72|->639),(73|->640),(73|->641),(74|->642),(74|->643),(75|->644),(75|->645),(76|->646),
    # (76|->647),(77|->648),(77|->649),(78|->650),(78|->651),(79|->652),(79|->653),(80|->654),
    # (80|->655),(81|->656),(81|->657),(82|->658),(82|->659),(83|->660),(83|->661),(84|->662),
    # (84|->663),(85|->664),(85|->665),(86|->666),(86|->667),(87|->668),(87|->669),(88|->670),
    # (88|->671),(89|->672),(89|->673),(90|->676),(90|->677),(91|->674),(91|->675),(92|->678),
    # (92|->679),(93|->680),(93|->681),(94|->682),(94|->683),(95|->684),(95|->685),(96|->686),
    # (96|->687),(97|->688),(97|->689),(98|->690),(98|->691),(99|->822),(99|->823),(100|->143),
    # (100|->828),(101|->145),(101|->830),(102|->887),(102|->888)}  
    # bf ={0|->110,1|->111,2|->113,3|->115,4|->43,5|->45,6|->47,7|->49,8|->51,9|->53,10|->55,11|->57,12|->59,13|->61,14|->63,15|->67,16|->69,17|->71,18|->73,19|->75,20|->77,21|->79,22|->81,23|->83,24|->85,25|->87,26|->89,27|->91,28|->93,29|->95,30|->97,31|->99,32|->101,33|->103,34|->105,35|->107,36|->993,37|->995,38|->238,39|->240,40|->250,41|->252,42|->254,43|->256,44|->258,45|->260,46|->262,47|->264,48|->266,49|->268,50|->270,51|->272,52|->274,53|->276,54|->278,55|->280,56|->284,57|->286,58|->288,59|->290,60|->292,61|->294,62|->296,63|->298,64|->300,65|->370,66|->372,67|->302,68|->304,69|->306,70|->374,71|->563,72|->787,73|->789,74|->793,75|->795,76|->797,77|->799,78|->801,79|->805,80|->807,81|->811,82|->813,83|->815,84|->817,85|->821,86|->823,87|->825,88|->831,89|->833,90|->839,91|->837,92|->841,93|->843,94|->845,95|->847,96|->849,97|->851,98|->853,99|->986,100|->230,101|->232,102|->1053,103|->0,104|->0,105|->0,106|->0,107|->0,108|->0,109|->0,110|->0,111|->0,112|->0,113|->0,114|->0,115|->0,116|->0,117|->0,118|->0,119|->0,120|->0,121|->0,122|->0,123|->0,124|->0,125|->0,126|->0,127|->0,128|->0,129|->0,130|->0,131|->0,132|->0,133|->0,134|->0,135|->0,136|->0,137|->0,138|->0,139|->0,140|->0,141|->0,142|->0,143|->0,144|->0,145|->0,146|->0,147|->0,148|->0,149|->0,150|->0,151|->0,152|->0,153|->0,154|->0,155|->0,156|->0,157|->0,158|->0,159|->0,160|->0,161|->0,162|->0,163|->0,164|->0,165|->0,166|->0,167|->0,168|->0,169|->0,170|->0,171|->0,172|->0,173|->0,174|->0,175|->0,176|->0,177|->0,178|->0,179|->0,180|->0,181|->0,182|->0,183|->0,184|->0,185|->0,186|->0,187|->0,188|->0,189|->0,190|->0,191|->0,192|->0,193|->0,194|->0,195|->0,196|->0,197|->0,198|->0,199|->0}  
    # bg ={0|->109,1|->112,2|->114,3|->116,4|->44,5|->46,6|->48,7|->50,8|->52,9|->54,10|->56,11|->58,12|->60,13|->62,14|->64,15|->68,16|->70,17|->72,18|->74,19|->76,20|->78,21|->80,22|->82,23|->84,24|->86,25|->88,26|->90,27|->92,28|->94,29|->96,30|->98,31|->100,32|->102,33|->104,34|->106,35|->108,36|->231,37|->233,38|->239,39|->241,40|->251,41|->253,42|->255,43|->257,44|->259,45|->261,46|->263,47|->265,48|->267,49|->269,50|->271,51|->273,52|->275,53|->277,54|->279,55|->281,56|->285,57|->287,58|->289,59|->291,60|->293,61|->295,62|->297,63|->299,64|->301,65|->371,66|->373,67|->303,68|->305,69|->307,70|->375,71|->564,72|->788,73|->792,74|->794,75|->796,76|->798,77|->800,78|->804,79|->806,80|->810,81|->812,82|->814,83|->816,84|->818,85|->822,86|->824,87|->826,88|->832,89|->834,90|->840,91|->838,92|->842,93|->844,94|->846,95|->848,96|->850,97|->852,98|->854,99|->987,100|->992,101|->994,102|->1054,103|->0,104|->0,105|->0,106|->0,107|->0,108|->0,109|->0,110|->0,111|->0,112|->0,113|->0,114|->0,115|->0,116|->0,117|->0,118|->0,119|->0,120|->0,121|->0,122|->0,123|->0,124|->0,125|->0,126|->0,127|->0,128|->0,129|->0,130|->0,131|->0,132|->0,133|->0,134|->0,135|->0,136|->0,137|->0,138|->0,139|->0,140|->0,141|->0,142|->0,143|->0,144|->0,145|->0,146|->0,147|->0,148|->0,149|->0,150|->0,151|->0,152|->0,153|->0,154|->0,155|->0,156|->0,157|->0,158|->0,159|->0,160|->0,161|->0,162|->0,163|->0,164|->0,165|->0,166|->0,167|->0,168|->0,169|->0,170|->0,171|->0,172|->0,173|->0,174|->0,175|->0,176|->0,177|->0,178|->0,179|->0,180|->0,181|->0,182|->0,183|->0,184|->0,185|->0,186|->0,187|->0,188|->0,189|->0,190|->0,191|->0,192|->0,193|->0,194|->0,195|->0,196|->0,197|->0,198|->0,199|->0}
    # br = 0 .. 889-1
    # bd ={0|->43,1|->44,2|->45,3|->46,4|->47,5|->48,6|->49,7|->50,8|->51,9|->52,10|->53,11|->54,12|->55,13|->56,14|->57,15|->58,16|->59,17|->60,18|->61,19|->62,20|->63,21|->64,22|->67,23|->68,24|->69,25|->70,26|->71,27|->72,28|->73,29|->74,30|->75,31|->76,32|->77,33|->78,34|->79,35|->80,36|->81,37|->82,38|->83,39|->84,40|->85,41|->86,42|->87,43|->88,44|->89,45|->90,46|->91,47|->92,48|->93,49|->94,50|->95,51|->96,52|->97,53|->98,54|->99,55|->100,56|->101,57|->102,58|->103,59|->104,60|->105,61|->106,62|->107,63|->108,64|->109,65|->110,66|->111,67|->112,68|->113,69|->114,70|->115,71|->116,72|->117,73|->118,74|->119,75|->120,76|->121,77|->122,78|->123,79|->124,80|->125,81|->126,82|->127,83|->128,84|->129,85|->130,86|->131,87|->132,88|->133,89|->134,90|->135,91|->136,92|->137,93|->138,94|->139,95|->140,96|->141,97|->142,98|->143,99|->144,100|->145,101|->146,102|->147,103|->148,104|->149,105|->150,106|->151,107|->152,108|->153,109|->154,110|->155,111|->156,112|->157,113|->158,114|->159,115|->160,116|->161,117|->162,118|->163,119|->164,120|->165,121|->166,122|->167,123|->168,124|->169,125|->170,126|->171,127|->172,128|->173,129|->174,130|->175,131|->176,132|->177,133|->178,134|->179,135|->180,136|->181,137|->182,138|->183,139|->184,140|->185,141|->186,142|->187,143|->230,144|->231,145|->232,146|->233,147|->238,148|->239,149|->240,150|->241,151|->250,152|->251,153|->252,154|->253,155|->254,156|->255,157|->256,158|->257,159|->258,160|->259,161|->260,162|->261,163|->262,164|->263,165|->264,166|->265,167|->266,168|->267,169|->268,170|->269,171|->270,172|->271,173|->272,174|->273,175|->274,176|->275,177|->276,178|->277,179|->278,180|->279,181|->280,182|->281,183|->284,184|->285,185|->286,186|->287,187|->288,188|->289,189|->290,190|->291,191|->292,192|->293,193|->294,194|->295,195|->296,196|->297,197|->298,198|->299,199|->300,200|->301,201|->302,202|->303,203|->304,204|->305,205|->306,206|->307,207|->308,208|->309,209|->310,210|->311,211|->312,212|->313,213|->314,214|->315,215|->316,216|->317,217|->318,218|->319,219|->320,220|->321,221|->322,222|->323,223|->324,224|->325,225|->326,226|->327,227|->328,228|->329,229|->330,230|->331,231|->332,232|->333,233|->334,234|->335,235|->336,236|->337,237|->338,238|->339,239|->340,240|->341,241|->342,242|->343,243|->344,244|->345,245|->346,246|->347,247|->348,248|->349,249|->350,250|->351,251|->352,252|->353,253|->354,254|->355,255|->356,256|->357,257|->358,258|->359,259|->360,260|->361,261|->362,262|->363,263|->364,264|->365,265|->366,266|->367,267|->368,268|->369,269|->370,270|->371,271|->372,272|->373,273|->374,274|->375,275|->406,276|->407,277|->408,278|->409,279|->410,280|->411,281|->412,282|->413,283|->414,284|->415,285|->416,286|->417,287|->418,288|->419,289|->420,290|->421,291|->422,292|->423,293|->424,294|->425,295|->426,296|->427,297|->428,298|->429,299|->430,300|->431,301|->432,302|->433,303|->434,304|->435,305|->436,306|->437,307|->438,308|->439,309|->440,310|->441,311|->442,312|->443,313|->444,314|->445,315|->446,316|->447,317|->448,318|->449,319|->450,320|->451,321|->452,322|->455,323|->456,324|->457,325|->458,326|->459,327|->460,328|->461,329|->462,330|->463,331|->464,332|->465,333|->466,334|->467,335|->468,336|->469,337|->470,338|->471,339|->472,340|->473,341|->474,342|->475,343|->476,344|->477,345|->478,346|->479,347|->480,348|->481,349|->482,350|->483,351|->484,352|->485,353|->486,354|->487,355|->488,356|->489,357|->490,358|->491,359|->492,360|->493,361|->494,362|->495,363|->496,364|->497,365|->498,366|->499,367|->500,368|->501,369|->502,370|->503,371|->504,372|->505,373|->506,374|->507,375|->508,376|->510,377|->511,378|->512,379|->513,380|->514,381|->515,382|->516,383|->517,384|->518,385|->519,386|->520,387|->521,388|->522,389|->523,390|->524,391|->525,392|->526,393|->527,394|->528,395|->529,396|->530,397|->531,398|->532,399|->533,400|->534,401|->535,402|->536,403|->537,404|->538,405|->539,406|->540,407|->541,408|->542,409|->543,410|->544,411|->545,412|->546,413|->547,414|->548,415|->549,416|->550,417|->551,418|->552,419|->553,420|->554,421|->555,422|->556,423|->557,424|->558,425|->559,426|->560,427|->561,428|->562,429|->563,430|->564,431|->565,432|->566,433|->567,434|->568,435|->569,436|->570,437|->571,438|->572,439|->573,440|->574,441|->575,442|->576,443|->577,444|->578,445|->579,446|->580,447|->582,448|->583,449|->584,450|->585,451|->586,452|->587,453|->588,454|->589,455|->590,456|->591,457|->592,458|->593,459|->594,460|->595,461|->596,462|->597,463|->598,464|->599,465|->600,466|->601,467|->602,468|->603,469|->604,470|->605,471|->606,472|->607,473|->608,474|->610,475|->611,476|->612,477|->613,478|->614,479|->615,480|->616,481|->617,482|->618,483|->619,484|->620,485|->621,486|->622,487|->623,488|->625,489|->626,490|->627,491|->628,492|->629,493|->630,494|->631,495|->632,496|->633,497|->634,498|->635,499|->636,500|->637,501|->638,502|->639,503|->640,504|->641,505|->642,506|->643,507|->644,508|->645,509|->646,510|->647,511|->648,512|->649,513|->650,514|->651,515|->652,516|->653,517|->654,518|->655,519|->656,520|->657,521|->658,522|->659,523|->660,524|->661,525|->662,526|->663,527|->664,528|->665,529|->666,530|->667,531|->668,532|->669,533|->670,534|->671,535|->672,536|->673,537|->674,538|->675,539|->676,540|->677,541|->678,542|->679,543|->680,544|->681,545|->682,546|->683,547|->684,548|->685,549|->686,550|->687,551|->688,552|->689,553|->690,554|->691,555|->692,556|->693,557|->694,558|->695,559|->696,560|->697,561|->698,562|->699,563|->700,564|->701,565|->702,566|->703,567|->704,568|->705,569|->706,570|->707,571|->708,572|->709,573|->710,574|->711,575|->712,576|->713,577|->714,578|->715,579|->716,580|->717,581|->718,582|->719,583|->720,584|->721,585|->722,586|->723,587|->724,588|->725,589|->726,590|->727,591|->728,592|->729,593|->730,594|->731,595|->732,596|->733,597|->734,598|->735,599|->736,600|->737,601|->738,602|->739,603|->740,604|->741,605|->742,606|->743,607|->744,608|->745,609|->746,610|->747,611|->748,612|->749,613|->750,614|->751,615|->752,616|->753,617|->754,618|->755,619|->756,620|->757,621|->758,622|->759,623|->760,624|->761,625|->762,626|->763,627|->764,628|->765,629|->766,630|->767,631|->768,632|->769,633|->782,634|->783,635|->784,636|->785,637|->786,638|->787,639|->788,640|->789,641|->792,642|->793,643|->794,644|->795,645|->796,646|->797,647|->798,648|->799,649|->800,650|->801,651|->804,652|->805,653|->806,654|->807,655|->810,656|->811,657|->812,658|->813,659|->814,660|->815,661|->816,662|->817,663|->818,664|->821,665|->822,666|->823,667|->824,668|->825,669|->826,670|->831,671|->832,672|->833,673|->834,674|->837,675|->838,676|->839,677|->840,678|->841,679|->842,680|->843,681|->844,682|->845,683|->846,684|->847,685|->848,686|->849,687|->850,688|->851,689|->852,690|->853,691|->854,692|->855,693|->856,694|->857,695|->858,696|->859,697|->860,698|->861,699|->862,700|->863,701|->864,702|->865,703|->866,704|->867,705|->868,706|->869,707|->870,708|->871,709|->872,710|->873,711|->874,712|->875,713|->876,714|->877,715|->878,716|->879,717|->880,718|->881,719|->882,720|->883,721|->884,722|->885,723|->886,724|->887,725|->888,726|->889,727|->890,728|->891,729|->892,730|->893,731|->894,732|->895,733|->896,734|->897,735|->898,736|->899,737|->900,738|->901,739|->902,740|->903,741|->904,742|->905,743|->906,744|->907,745|->908,746|->909,747|->910,748|->911,749|->912,750|->913,751|->914,752|->915,753|->916,754|->917,755|->919,756|->920,757|->921,758|->922,759|->923,760|->924,761|->925,762|->926,763|->927,764|->928,765|->929,766|->930,767|->931,768|->932,769|->933,770|->934,771|->935,772|->936,773|->937,774|->938,775|->939,776|->940,777|->941,778|->942,779|->943,780|->944,781|->945,782|->946,783|->947,784|->948,785|->949,786|->950,787|->951,788|->952,789|->953,790|->954,791|->955,792|->956,793|->957,794|->958,795|->959,796|->960,797|->961,798|->962,799|->963,800|->964,801|->965,802|->966,803|->967,804|->968,805|->969,806|->970,807|->971,808|->972,809|->973,810|->974,811|->975,812|->976,813|->977,814|->978,815|->979,816|->980,817|->981,818|->982,819|->983,820|->984,821|->985,822|->986,823|->987,824|->988,825|->989,826|->990,827|->991,828|->992,829|->993,830|->994,831|->995,832|->996,833|->997,834|->998,835|->999,836|->1000,837|->1001,838|->1002,839|->1003,840|->1004,841|->1005,842|->1006,843|->1007,844|->1008,845|->1009,846|->1010,847|->1011,848|->1012,849|->1013,850|->1014,851|->1015,852|->1016,853|->1017,854|->1018,855|->1019,856|->1020,857|->1021,858|->1022,859|->1023,860|->1024,861|->1025,862|->1026,863|->1027,864|->1028,865|->1029,866|->1030,867|->1031,868|->1032,869|->1033,870|->1034,871|->1035,872|->1036,873|->1037,874|->1038,875|->1039,876|->1040,877|->1041,878|->1042,879|->1043,880|->1044,881|->1045,882|->1046,883|->1047,884|->1048,885|->1049,886|->1050,887|->1053,888|->1054,889|->0,890|->0,891|->0,892|->0,893|->0,894|->0,895|->0,896|->0,897|->0,898|->0,899|->0,900|->0,901|->0,902|->0,903|->0,904|->0,905|->0,906|->0,907|->0,908|->0,909|->0,910|->0,911|->0,912|->0,913|->0,914|->0,915|->0,916|->0,917|->0,918|->0,919|->0,920|->0,921|->0,922|->0,923|->0,924|->0,925|->0,926|->0,927|->0,928|->0,929|->0,930|->0,931|->0,932|->0,933|->0,934|->0,935|->0,936|->0,937|->0,938|->0,939|->0,940|->0,941|->0,942|->0,943|->0,944|->0,945|->0,946|->0,947|->0,948|->0,949|->0,950|->0,951|->0,952|->0,953|->0,954|->0,955|->0,956|->0,957|->0,958|->0,959|->0,960|->0,961|->0,962|->0,963|->0,964|->0,965|->0,966|->0,967|->0,968|->0,969|->0,970|->0,971|->0,972|->0,973|->0,974|->0,975|->0,976|->0,977|->0,978|->0,979|->0,980|->0,981|->0,982|->0,983|->0,984|->0,985|->0,986|->0,987|->0,988|->0,989|->0,990|->0,991|->0,992|->0,993|->0,994|->0,995|->0,996|->0,997|->0,998|->0,999|->0}
    # bt=0 .. 103-1
    #
    # S= dom({x,y,z | x|->z: bt<|(bf\/bg) & y|->z: br<|bd})
    #def test_constraint_dom_of_set_comp(self):        
    #    string_to_file("#PREDICATE {}= dom({x,y,z | x|->z: 0..10<|({0|->110,1|->111}\/{0|->109,1|->112}) & y|->z: 0..10<|{0|->43,1|->44}})", file_name)
    #    ast_string = file_to_AST_str(file_name)
    #    root = str_ast_to_python_ast(ast_string)
    #    
    #    # Test
    #    env = Environment()
    #    env._min_int = -2**32
    #    env._max_int = 2**32
    #    assert interpret(root, env)  
        
# Write tests:
# if one bound var is infinite. Constraint solving must fail        
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
# C578/2013_08_14/machines_27082013/R_02_002
# C578/2013_08_14/machines_14082013/PB_00611_005
# (ox=%(pw,pd).(pd:nw & pw:il|{bg|->ns(pw),bc|->mc(pw),bh|->mg(pw),be|->me(pw),bd|->md(pw),bf|->mf(pw)}(pd)))