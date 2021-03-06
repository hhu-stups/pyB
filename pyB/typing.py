# -*- coding: utf-8 -*-
from ast_nodes import *
from bexceptions import ResolveFailedException, BTypeException, PYBBugException
from bmachine import BMachine
from btypes import *
from helpers import print_ast, find_var_nodes
from pretty_printer import pretty_print

def print_btype(type):
    __print__btype(type)

# helper for debugging.
# prints a type-tree.
def __print__btype(tree, t=0):
    # TODO: sometimes endles-loops, maybe cyclic (buggy-)trees? Check for cycles
    #tree = unknown_closure(tree)
    if isinstance(tree, SetType):
       print " "*t, tree, ": ", tree.name 
    else:
       print " "*t, tree
    if isinstance(tree, PowerSetType):
        __print__btype(tree.data,t+1)
    elif isinstance(tree, CartType):
        __print__btype(tree.left,t+1)
        __print__btype(tree.right,t+1) 


# used in function-expression to get the number of args given to a func call
def calculate_num_args(node):
    if isinstance(node, ACoupleExpression):
        return calculate_num_args(node.children[0]) + calculate_num_args(node.children[1])
    else:
        return 1

def create_func_arg_type(num_args):
    if num_args==2:
        return PowerSetType(CartType(PowerSetType(UnknownType("AFunctionExpression")),PowerSetType(UnknownType("AFunctionExpression"))))
    else:
        arg_type = create_func_arg_type(num_args-1)
        return PowerSetType(CartType(arg_type,PowerSetType(UnknownType("AFunctionExpression"))))


# TODO: Refactoring 
# remove_carttypes and get_arg_type_list are the same function :-D
def _get_arg_type_list(type,lst):
    assert isinstance(type, PowerSetType)
    if isinstance(type.data, CartType):
        _get_arg_type_list(type.data.left, lst)
        _get_arg_type_list(type.data.right, lst)
    else:
        lst.append(type.data) # function-args have not the pow_set but the set type
        return
        
def get_arg_type_list(func_type):
    lst = []
    _get_arg_type_list(func_type, lst) # sideeffect: fill list with types
    return lst
    
    
def remove_carttypes(arg_type):
    result = []
    if isinstance(arg_type, CartType): 
        result += remove_carttypes(arg_type.left.data)
        result += remove_carttypes(arg_type.right.data)
    else:
        result.append(arg_type)
    return result
    

# helper function to check if a substitution (also operation and a machine)
# uses substituions which change the state (set of var-names). 
# False if any state-change is possible.    
def check_if_query_op(sub, var_names):
    assert isinstance(sub, Substitution)
    # case 1: x:=E
    if isinstance(sub, AAssignSubstitution):
        for i in range(int(sub.lhs_size)):
            lhs_node = sub.children[i]
            if isinstance(lhs_node, AIdentifierExpression):
                if lhs_node.idName in var_names:
                   return False
            else:
                assert isinstance(lhs_node, AFunctionExpression)
                assert isinstance(lhs_node.children[0], AIdentifierExpression)
                if lhs_node.children[0].idName in var_names:
                   return False
    # case 2: x:P or x::S
    elif isinstance(sub, ABecomesElementOfSubstitution) or isinstance(sub, ABecomesSuchSubstitution):
        for child in sub.children[:-1]:
            assert isinstance(child, AIdentifierExpression)
            if child.idName in var_names:
                return False
    # case 3 df-search
    else: # df-search 
        for child in sub.children:
            if isinstance(child, Substitution):
                is_query_op = check_if_query_op(child, var_names)
                if not is_query_op:
                    return False  
    # default: nothing found          
    return True 


# Helper env: will be thrown away after Typechecking
class TypeCheck_Environment():
    def __init__(self):
        # is used to construct the env.node_to_type_map
        self.id_to_nodes_stack = []
        self.id_to_types_stack = []
        

    def init_env(self, idNames):
        # 1. create first stack frame
        id_to_nodes_map = {} # str->NODE: all nodes with name str (of this scope)
        id_to_types_map = {} # str->Type: all type-variables/type-instances of str
        # 2. add ids with unknown types
        for id_Name in idNames:
            id_to_nodes_map[id_Name] = [] # no Nodes found at the moment
            id_to_types_map[id_Name] = UnknownType(id_Name)
        self.id_to_types_stack = [id_to_types_map]
        self.id_to_nodes_stack = [id_to_nodes_map]


    def add_known_types_of_child_env(self, id_to_types_map):
        type_map = self.id_to_types_stack.pop()
        type_map.update(id_to_types_map)
        self.id_to_types_stack.append(type_map)
        node_map = self.id_to_nodes_stack.pop()
        for name in id_to_types_map:
            node_map[name] = [] # no Nodes at the moment
        self.id_to_nodes_stack.append(node_map)

    # new scope
    def push_frame(self, id_Names):
        id_to_nodes_map = {} # A: str->NODE
        id_to_types_map = {} # T: str->Type
        for id_Name in id_Names:
            id_to_nodes_map[id_Name] = [] # no Nodes at the moment
            id_to_types_map[id_Name] = UnknownType(id_Name)
        self.id_to_nodes_stack.append(id_to_nodes_map)
        self.id_to_types_stack.append(id_to_types_map)


    def add_node_by_id(self, node):
        #print node.idName, self.id_to_nodes_stack
        assert isinstance(node, AIdentifierExpression)
        # lookup:
        for i in range(len(self.id_to_nodes_stack)):
            try:
                top_map = self.id_to_nodes_stack[-i-1]
                node_list = top_map[node.idName]
                node_list.append(node) # ref change
                return
            except KeyError:
                continue
        # FIXME: deferred set items e.g. S and S1,S2,S3 generated by proB will cause an exception
        string = "TypeError in typing.py: %s not found while adding node %s to type-env! Maybe %s is unknown to type-env. IdName not added to type-env..." % (node.idName, node, node.idName)
        #print string
        raise BTypeException(string)


    def set_unknown_type(self, id0_Name, id1_Name):
        assert isinstance(id0_Name, UnknownType)
        assert isinstance(id1_Name, UnknownType)
        assert id0_Name.real_type is None
        assert id1_Name.real_type is None
        assert not id1_Name == id0_Name # dont produce a cycle 

        if isinstance(id0_Name, PowORIntegerType) or isinstance(id0_Name, PowCartORIntegerType):
            id1_Name.real_type = id0_Name
        else: #TODO: more cases?
            assert id0_Name.real_type is None
            id0_Name.real_type = id1_Name
        return id1_Name


    def set_concrete_type(self, utype, ctype):
        assert isinstance(utype, UnknownType)
        assert isinstance(ctype, BType)
        #print utype.type_name, ctype
        if isinstance(utype, PowCartORIntegerType):
            u0 = unknown_closure(utype.left)
            u1 = unknown_closure(utype.right)
            if isinstance(ctype, IntegerType):
                if isinstance(u0, UnknownType):
                    self.set_concrete_type(u0, ctype)
                else:
                    assert isinstance(u0, IntegerType)
                if isinstance(u1, UnknownType):
                    self.set_concrete_type(u1, ctype)
                else:
                    assert isinstance(u1, IntegerType)
                return IntegerType()
            else:
                assert isinstance(ctype, PowerSetType)
                cart_type = unknown_closure(ctype.data)
                assert isinstance(cart_type, CartType)
                subset_type0 = unknown_closure(cart_type.left)
                subset_type1 = unknown_closure(cart_type.right)
                if isinstance(u0, UnknownType):
                    self.set_concrete_type(u0, subset_type0)
                else:
                    assert isinstance(u0, PowerSetType)
                if isinstance(u1, UnknownType):
                    self.set_concrete_type(u1, subset_type1)
                else:
                    assert isinstance(u1, PowerSetType)
                return PowerSetType(CartType(subset_type0, subset_type1))
        elif isinstance(utype, PowORIntegerType):
            u0 = unknown_closure(utype.left)
            u1 = unknown_closure(utype.right)
            # a PowORIntegerType will only be created if both operands of a
            # setsubtraction are unknown. They have the same type as result of the
            # unification of two unknown-types so they point on the same unknown-type object
            assert u0==u1 
            if isinstance(ctype, IntegerType): # u0 and u1 are IntegerTypes
                if isinstance(u0, UnknownType):
                    self.set_concrete_type(u0, ctype)
                else:
                    assert isinstance(u0, IntegerType)
                return IntegerType()
            else:
                assert isinstance(ctype, PowerSetType)
                if isinstance(u0, UnknownType):
                    self.set_concrete_type(u0, ctype)
                else:
                    assert isinstance(u0, PowerSetType)
        else:
            assert utype.real_type is None
            utype.real_type = ctype
            return ctype


    # copies to env.node_to_type_map
    def pop_frame(self, env):
        node_top_map = self.id_to_nodes_stack[-1]
        type_top_map = self.id_to_types_stack[-1]
        self.id_to_nodes_stack.pop()
        self.id_to_types_stack.pop()
        #assert isinstance(env, Environment)
        self.write_to_env(env, type_top_map, node_top_map)



    def write_to_env(self, env, type_top_map, node_top_map):
        for idName in type_top_map:
            utype = type_top_map[idName]
            atype = unknown_closure(utype)
            # Type unknown now. will be found in resolve()
            # This is when local vars use global vars
            # which are unknown a this time
            if atype is None:
                atype= utype
            # get all nodes with the name "idName"
            node_lst = node_top_map[idName]
            # set all these nodes to the type "atype"
            for node in node_lst:
                env.node_to_type_map[node] = atype

    def write_lambda_node_to_env(self, env, lambda_node, atype):
        env.node_to_type_map[lambda_node] = atype
        
    # returns BType or UnknownType
    # WARNING: not to be confused with env.get_type
    def get_current_type(self, idName):
        assert isinstance(idName, str)
        # lookup:
        for i in range(len(self.id_to_types_stack)):
            try:
                top_map = self.id_to_types_stack[-i-1]
                atype = top_map[idName]
                if atype.real_type:
                    return atype.real_type
                else:
                    return atype
            except KeyError:
                continue
        # error
        string = "TypeError in typing.py: idName %s not found! IdName not added to type_env." % idName
        #print string
        raise BTypeException(string)



# env.node_to_type_map should be a set of tree with 
# Nodes as leafs and Btypes as roots. 
# This method should throw away all unknowntypes 
# by walking from the leafs to the roots.
# If this is not possible the typechecking has failed
def resolve_type(env):
    for node in env.node_to_type_map:
        tree = env.node_to_type_map[node]
        #print node.idName, tree
        #__print__btype(tree)
        if isinstance(node, ALambdaExpression):
            tree_without_unknown = throw_away_unknown(tree, "lambda expression()%s" % pretty_print(node))
        else:
            tree_without_unknown = throw_away_unknown(tree, node.idName)
        env.node_to_type_map[node] = tree_without_unknown



# it is a list an becomes a tree when carttype is implemented
# It uses the data attr of BTypes as pointers
# assumption: if unification was successful, the leafs of this tree (of type-classes)
# are only BTypes and no UnknownTypes. Before function app, inner-nodes may be UnknownTypes 
def throw_away_unknown(tree, idName=""):
    #print tree
    if isinstance(tree, SetType) or isinstance(tree, IntegerType) or isinstance(tree, StringType) or isinstance(tree, BoolType):
        return tree # leaf found.
    elif isinstance(tree, PowerSetType):
        if isinstance(tree.data, UnknownType):
            atype = unknown_closure(tree.data)
            if not isinstance(atype, BType):
                string = "TypeError in typing.py: Can not resolve type of %s \n" % idName
                #print string
                raise ResolveFailedException(string)
            assert isinstance(atype, BType)
            tree.data = atype
        throw_away_unknown(tree.data, idName)
        return tree
    elif isinstance(tree, CartType): 
        if not isinstance(tree.left, UnknownType) and not isinstance(tree.right, UnknownType):
            throw_away_unknown(tree.left, idName)
            throw_away_unknown(tree.right, idName)
            return tree
        else: #TODO: implement me
            return tree
    elif isinstance(tree, StructType):#TODO: implement me
        return tree
    elif isinstance(tree, PowCartORIntegerType):
        arg1 = unknown_closure(tree.left)
        arg2 = unknown_closure(tree.right)
        arg1 = throw_away_unknown(arg1, idName)
        arg2 = throw_away_unknown(arg2, idName)
        assert isinstance(arg1, BType)
        assert isinstance(arg2, BType)
        if not arg1.eq_type(arg2):
            string = "TypeError in typing.py: Unable to unify two type variables: %s %s" % (arg1, arg2)
            raise BTypeException(string)

        if isinstance(arg1, PowerSetType) and isinstance(arg2, PowerSetType):
            tree = PowerSetType(CartType(arg1, arg2))
        elif isinstance(arg1, IntegerType) and isinstance(arg2, IntegerType):
            tree = IntegerType()
        return tree
    elif isinstance(tree, PowORIntegerType):
        arg1 = unknown_closure(tree.left)
        arg2 = unknown_closure(tree.right)
        arg1 = throw_away_unknown(arg1, idName)
        arg2 = throw_away_unknown(arg2, idName)
        assert isinstance(arg1, BType)
        assert isinstance(arg2, BType)
        if not arg1.eq_type(arg2):
            string = "TypeError in typing.py: Unable to unify two type variables: %s %s" % (arg1, arg2)
            raise BTypeException(string)

        if isinstance(arg1, PowerSetType) and isinstance(arg2, PowerSetType):
            tree = arg1
        elif isinstance(arg1, IntegerType) and isinstance(arg2, IntegerType):
            tree = arg1
        return tree
    elif tree is None: # UnknownTypes point at None, if the are not set to something while unification
        raise BTypeException("TypeError in typing.py: can not resolve a Type of: %s" % idName)
    elif isinstance(tree, UnknownType):
        tree = unknown_closure(tree)
        if isinstance(tree, UnknownType):
            #print tree
            string = "TypeError in typing.py: can not resolve a Type of: %s" % str(tree.type_name)
            #print string
            raise ResolveFailedException(string)
        # skip chain-of UnknownTypes
        tree = throw_away_unknown(tree, idName)
        return tree
    else:
        raise Exception("resolve fail: Not Implemented %s %s" % (tree, idName))
        


# follows an UnknownType pointer chain:
# (case 1) It returns the first concrete type if one exists.
#     Exception: the type-variables of powsets contain informations. 
#     This information can be used while unification. 
#      So it is returned like it is a BType
# (case 2) It returns the last unknown type if no concrete type is part of the chain.
# WARNING: This BType could point on other UnknownTypes. e.g. POW(X)
def unknown_closure(atype):
    # first element contains informations
    if not isinstance(atype, UnknownType):
        return atype
    seen_types = [atype]
    # search until 
    # (1) information found
    # (2) end of chain reached
    # (3) cycle found -> This is a Bug inside pyB
    while True:
        if isinstance(atype.real_type, BType):
            return atype.real_type
        elif isinstance(atype.real_type, PowORIntegerType) or isinstance(atype.real_type, PowCartORIntegerType):
            return atype.real_type
        elif atype.real_type is None:
            # This chain points to no Btype. 
            assert isinstance(atype, UnknownType)
            return atype
        atype = atype.real_type
        # cycle found. This musst be a bug!
        if atype in seen_types:
            break
        seen_types.append(atype)    
    string = "\033[1m\033[91mWARNING\033[00m: cyclic type chain found while unknown_closure. %s" % seen_types
    raise PYBBugException(string)



def type_check_predicate(root, env):
    idNodes = find_var_nodes(root) 
    idNames = [n.idName for n in idNodes]
    type_env = TypeCheck_Environment()
    type_env.init_env(idNames)     
    typeit(root, env, type_env)
    type_env.write_to_env(env, type_env.id_to_types_stack[-1], type_env.id_to_nodes_stack[-1])
    resolve_type(env) # throw away unknown types
    return type_env   # contains only knowladge about ids at global level


def type_check_expression(root, env):
    idNodes = find_var_nodes(root) 
    idNames = [n.idName for n in idNodes]
    type_env = TypeCheck_Environment()
    type_env.init_env(idNames)   
    typeit(root, env, type_env)
    type_env.write_to_env(env, type_env.id_to_types_stack[-1], type_env.id_to_nodes_stack[-1])
    resolve_type(env) # throw away unknown types
    return type_env   # contains only knowladge about ids at global level


def type_check_root_bmch(root, env, mch):
    type_env = type_check_bmch(root, env, mch)
    # type check solution file when all mch are typed (type-informations need to type file)
    if env.solution_root:
        typeit(env.solution_root, env, type_env) 
    

def type_check_bmch(root, env, mch):
    # TODO: abstr const/vars
    idNames = mch.eset_names + mch.dset_names + mch.eset_elem_names + mch.const_names + mch.var_names
    for node in mch.scalar_params + mch.set_params:
        idNames.append(node.idName) # add machine-parameters
    type_env = TypeCheck_Environment()
    type_env.init_env(idNames)    
    typeit(root, env, type_env)
    type_env.write_to_env(env, type_env.id_to_types_stack[-1], type_env.id_to_nodes_stack[-1])
    resolve_type(env) # throw away unknown types    
    get_and_check_mch_parameter(root, env, mch, type_env)
    return type_env


# This method is called after successful pass of the type checking of the machine.
# At this time all parameters musst have a type. 
def get_and_check_mch_parameter(root, env, mch, type_env):
    # To understand assertions, see: 7.5. page 116
    # (1) check types
    for n in mch.scalar_params:
        atype = env.get_type_by_node(n)
        if not(isinstance(atype, IntegerType) or isinstance(atype, BoolType)):
            string = "TypeError in typing.py: no integer or boolean type for scalar machine parameter %s" % n.idName
            raise BTypeException(string)
    for n in mch.set_params:
        atype = env.get_type_by_node(n)
        if not(isinstance(atype, PowerSetType) or isinstance(atype.data, SetType)):
            string = "TypeError in typing.py: no set type for set machine parameter %s" % n.idName
            raise BTypeException(string)
    # (2) everything ok, add types
    if mch.has_mch_header:
        for child in mch.aMachineHeader.children:
            atype = typeit(child, env, type_env)
            mch.parameter_type_lst.append(atype)


# returns BType/UnkownType or None(for expr which need no type. e.g. x=y)
# sideeffect: changes env
# type_env is a working env to type vars with
# different scopes but (maybe) the same names
# e.g. !x.(x:S =>...) & x:Nat ...
def typeit(node, env, type_env):


# ******************************
#
#        0. Typechecking-mode
#
# ******************************
    #print node
    if isinstance (node, APredicateParseUnit):
        for child in node.children:
            typeit(child, env, type_env)
    elif isinstance(node, AExpressionParseUnit):
        for child in node.children:
            typeit(child, env, type_env)    
    elif isinstance(node, AAbstractMachineParseUnit):
        mch = env.current_mch
        mch.type_child_machines(type_check_bmch, type_env, env)

        # add para-nodes to map 
        for idNode in mch.aMachineHeader.children:
            assert isinstance(idNode, AIdentifierExpression)
            typeit(idNode, env, type_env)
        
        # set machine parameters have always the type Pow(Settype). In contrast to scalar 
        # machine parameters, they do not need a typing by the CONSTRAINTS clause.   
        for p in mch.set_params:
            unknown_type = type_env.get_current_type(p.idName)
            unify_equal(unknown_type, PowerSetType(SetType(p.idName)), type_env)

        # type clauses. Sees, uses, promotes clauses need no typing. The have no parameters 
        # FIXME: (#ISSUE 32) use type informations of child machines to check extends
        # and includes parameters
        if mch.has_extends_mc:
            for child in mch.aExtendsMachineClause.children:
                assert isinstance(child, AMachineReference)
            typeit(mch.aExtendsMachineClause, env, type_env)
        if mch.has_includes_mc:
            for child in mch.aIncludesMachineClause.children:
                assert isinstance(child, AMachineReference)
            typeit(mch.aIncludesMachineClause, env, type_env)
        if mch.has_constraints_mc: # C
            typeit(mch.aConstraintsMachineClause, env, type_env)
        if mch.has_sets_mc: # St
            for child in mch.aSetsMachineClause.children:
                set_name = child.idName
                utype = type_env.get_current_type(set_name) # hack: use def init with unknown type
                atype = SetType(set_name)
                unify_equal(utype, PowerSetType(atype), type_env)
                if isinstance(child, AEnumeratedSetSet):
                    # all elements have the type set_name
                    for elm in child.children:
                        elm_type = typeit(elm, env, type_env)
                        unify_equal(atype, elm_type, type_env)
        if mch.has_constants_mc: # k
            typeit(mch.aConstantsMachineClause, env, type_env)
        if mch.has_abstr_constants_mc:
            typeit(mch.aAbstractConstantsMachineClause, env, type_env)
        if mch.has_properties_mc: # B
            typeit(mch.aPropertiesMachineClause, env, type_env)
        if mch.has_variables_mc:
            typeit(mch.aVariablesMachineClause, env, type_env)
        if mch.has_conc_variables_mc:
            typeit(mch.aConcreteVariablesMachineClause, env, type_env)
        if mch.has_invariant_mc:
            typeit(mch.aInvariantMachineClause, env, type_env)
        if mch.has_initialisation_mc:
            typeit(mch.aInitialisationMachineClause, env, type_env)
        if mch.has_assertions_mc:
            typeit(mch.aAssertionsMachineClause, env, type_env)
        if mch.has_operations_mc:
            typeit(mch.aOperationsMachineClause, env, type_env)


# *********************
#
#        1. Predicates
#
# *********************
    elif isinstance(node, AConjunctPredicate) or isinstance(node, ADisjunctPredicate) or isinstance(node, AImplicationPredicate) or isinstance(node, AEquivalencePredicate) or isinstance(node, ANegationPredicate):
        for child in node.children:
            atype = typeit(child, env, type_env)
            expected_type = BoolType()
            unify_equal(atype, expected_type, type_env)
        return BoolType()
    elif isinstance(node, AForallPredicate) or isinstance(node, AExistsPredicate):
        ids = []
        for n in node.children[:-1]:
            assert isinstance(n.idName, str)
            ids.append(n.idName)
        type_env.push_frame(ids) # new scope
        for child in node.children:
            typeit(child, env, type_env)
        type_env.pop_frame(env)
        return BoolType()
    elif isinstance(node, AEqualPredicate) or isinstance(node, ANotEqualPredicate):
        expr1_type = typeit(node.children[0], env,type_env)
        expr2_type = typeit(node.children[1], env,type_env)
        unify_equal(expr1_type, expr2_type, type_env, node)
        return BoolType()


# **************
#
#       2. Sets
#
# **************
    elif isinstance(node, ASetExtensionExpression):
        # {a,b} or {(0,0,41),(1,0,41),(0,1,41),(1,1,41)} or etc.. 
        # this may be a IdentifierExpression, a CoupleExpression or something else..
        reftype = typeit(node.children[0], env, type_env)
        # all Elements must have the same type:
        for child in node.children[1:]:
            atype = typeit(child, env, type_env)
            reftype = unify_equal(atype, reftype, type_env)
        return PowerSetType(reftype)
    elif isinstance(node, AEmptySetExpression):
        return PowerSetType(UnknownType("AEmptySetExpression"))
    elif isinstance(node, AComprehensionSetExpression):
        ids = []
        # get id names
        for n in node.children[:-1]:
            assert isinstance(n.idName, str)
            ids.append(n.idName)
        type_env.push_frame(ids)
        assert len(node.children)>=1
        # type children
        for child in node.children:
            typeit(child, env, type_env)
        for child in node.children[:-1]:
            assert isinstance(child, AIdentifierExpression)
            assert not type_env.get_current_type(child.idName) is None
        # construct type of this node
        atype = type_env.get_current_type(ids[0]) 
        if len(ids)>1:
            imagetype    = type_env.get_current_type(ids[1])
            atype = CartType(PowerSetType(atype), PowerSetType(imagetype))
            for i in ids[2:]:
                next_imagetype = type_env.get_current_type(i)
                atype = CartType(PowerSetType(atype), PowerSetType(next_imagetype))
        type_env.pop_frame(env)
        return PowerSetType(atype) 
    elif isinstance(node, AMinusOrSetSubtractExpression):
        expr1_type = typeit(node.children[0], env, type_env)
        expr2_type = typeit(node.children[1], env, type_env)
        unify_equal(expr1_type, expr2_type, type_env)
        expr1_type = unknown_closure(expr1_type)
        expr2_type = unknown_closure(expr2_type)

        if isinstance(expr1_type, IntegerType) or isinstance(expr2_type, IntegerType):  # Integer-Minus
            return IntegerType()
        elif isinstance(expr1_type, PowerSetType) or isinstance(expr2_type, PowerSetType): # SetSubtract
            return expr1_type
        elif isinstance(expr1_type, UnknownType) and isinstance(expr2_type, UnknownType):  # Dont know
            return PowORIntegerType(expr1_type, expr2_type)
        else:
            string = "Typchecker Bug: unexpected type objects inside minus or cart expression."
            string += "Unimplemented case: %s %s" % (expr1_type, expr2_type)
            string += "Last unification was caused by: " + pretty_print(node)
            raise PYBBugException(string)
    elif isinstance(node, ASetSubtractionExpression):
        expr1_type = typeit(node.children[0], env, type_env)
        expr2_type = typeit(node.children[1], env, type_env)
        atype = unify_equal(expr1_type, expr2_type, type_env)
        return atype
    elif isinstance(node, ACoupleExpression):
        atype0 = typeit(node.children[0], env, type_env)
        atype1 = typeit(node.children[1], env, type_env)
        atype = CartType(PowerSetType(atype0), PowerSetType(atype1))
        # all couples must have the same type
        for index in range(len(node.children)-2):
            next_imagetype = typeit(node.children[index+2], env, type_env)
            atype = CartType(PowerSetType(atype), PowerSetType(next_imagetype))
        return atype
    elif isinstance(node, AMultOrCartExpression):
        expr1_type = typeit(node.children[0], env, type_env)
        expr2_type = typeit(node.children[1], env, type_env)
        expr1_type = unknown_closure(expr1_type)
        expr2_type = unknown_closure(expr2_type)
        if isinstance(expr1_type, IntegerType) or isinstance(expr2_type, IntegerType):  # Integer-Mult
            # only unify if IntgerType
            unify_equal(expr1_type, expr2_type, type_env)
            return IntegerType()
        # else: S*T expr1_type and expr2_type can be of different type. 
        elif isinstance(expr1_type, PowerSetType) and isinstance(expr2_type, UnknownType):  # CartExpression
            return PowerSetType(CartType(PowerSetType(expr1_type), PowerSetType(expr2_type)))
        elif isinstance(expr2_type, PowerSetType) and isinstance(expr1_type, UnknownType):  # CartExpression
            return PowerSetType(CartType(PowerSetType(expr1_type),PowerSetType( expr2_type)))
        elif isinstance(expr1_type, PowerSetType) and isinstance(expr2_type, PowerSetType): # CartExpression
            return PowerSetType(CartType(expr1_type, expr2_type))
        elif isinstance(expr1_type, UnknownType) and isinstance(expr2_type, UnknownType):  # Dont know
            return PowCartORIntegerType(expr1_type, expr2_type)
        else:
            string = "Typchecker Bug: unexpected type objects inside mult or cart expression."
            string += "Unimplemented case: %s %s" % (expr1_type, expr2_type)
            string += "Last unification was caused by: " + pretty_print(node)
            raise PYBBugException(string)
    elif isinstance(node, APowSubsetExpression) or isinstance(node, APow1SubsetExpression):
        set_type = typeit(node.children[0], env, type_env)
        expected_type = PowerSetType(UnknownType("APowSubsetExpression"))
        atype = unify_equal(set_type, expected_type, type_env)
        return PowerSetType(atype)
    elif isinstance(node, ACardExpression):
        atype = typeit(node.children[0], env, type_env) 
        expected_type = PowerSetType(UnknownType("ACardExpression"))
        unify_equal(atype, expected_type, type_env)
        return IntegerType()
    elif isinstance(node, AGeneralUnionExpression) or isinstance(node, AGeneralIntersectionExpression):
        # inter(U) or union(U)
        set_type = typeit(node.children[0], env, type_env)
        expected_type = PowerSetType(PowerSetType(UnknownType(type_name="no Name")))
        atype = unify_equal(set_type, expected_type,type_env)
        return atype.data
    elif isinstance(node, AQuantifiedIntersectionExpression) or isinstance(node, AQuantifiedUnionExpression):
        idNames = []
        assert node.idNum>0
        assert node.idNum<=len(node.children)
        for i in range(node.idNum):
            idNode = node.children[i]
            assert isinstance(idNode, AIdentifierExpression)
            idNames.append(idNode.idName)
        type_env.push_frame(idNames)
        for child in node.children[:-1]:
            typeit(child, env, type_env)
        atype = typeit(node.children[-1], env, type_env)
        type_env.pop_frame(env)
        return atype


# *************************
#
#       2.1 Set predicates
#
# *************************
    elif isinstance(node, AMemberPredicate) or isinstance(node, ANotMemberPredicate):
        elm_type = typeit(node.children[0], env, type_env)
        set_type = typeit(node.children[1], env, type_env)
        unify_element_of(elm_type, set_type, type_env, node) # special unification
        return BoolType()
    elif isinstance(node, ASubsetPredicate) or isinstance(node, ANotSubsetPredicate) or isinstance(node, ASubsetStrictPredicate) or isinstance(node, ANotSubsetStrictPredicate):
        expr1_type = typeit(node.children[0], env,type_env)
        expr2_type = typeit(node.children[1], env,type_env)
        unify_equal(expr1_type, expr2_type, type_env)
        return BoolType()
    elif isinstance(node, AUnionExpression) or isinstance(node, AIntersectionExpression):
        expr1_type = typeit(node.children[0], env,type_env)
        expr2_type = typeit(node.children[1], env,type_env)
        atype = unify_equal(expr1_type, expr2_type, type_env)
        return atype


# *****************
#
#       3. Numbers
#
# *****************
    elif isinstance(node, AIntSetExpression) or isinstance(node, ANatSetExpression) or isinstance(node, ANat1SetExpression) or  isinstance(node, ANaturalSetExpression) or isinstance(node, ANatural1SetExpression) or isinstance(node, AIntegerSetExpression):
        return PowerSetType(IntegerType())
    elif isinstance(node, AIntervalExpression):
        int_type = typeit(node.children[0], env, type_env)
        unify_equal(int_type, IntegerType(),type_env)
        int_type = typeit(node.children[1], env, type_env)
        unify_equal(int_type, IntegerType(),type_env)
        return PowerSetType(IntegerType())
    elif isinstance(node, AIntegerExpression):
        return IntegerType()
    elif isinstance(node, AMinExpression) or isinstance(node, AMaxExpression):
        set_type = typeit(node.children[0], env, type_env)
        expected_type = PowerSetType(IntegerType())
        unify_equal(set_type, expected_type, type_env)
        return IntegerType()
    elif isinstance(node, AAddExpression) or isinstance(node, ADivExpression) or isinstance(node, AModuloExpression) or isinstance(node, APowerOfExpression):
        expr1_type = typeit(node.children[0], env, type_env)
        expr2_type = typeit(node.children[1], env, type_env)
        unify_equal(expr1_type, IntegerType(), type_env)
        unify_equal(expr2_type, IntegerType(), type_env)
        return IntegerType()
    elif isinstance(node, AGeneralSumExpression) or isinstance(node, AGeneralProductExpression):
        ids = []
        for i in range(len(node.children)-2):
            n = node.children[i]
            assert isinstance(n.idName, str)
            ids.append(n.idName)
        type_env.push_frame(ids)
        for child in node.children:
            typeit(child, env, type_env)
        type_env.pop_frame(env)
        return IntegerType()


# ***************************
#
#       3.1 Number predicates
#
# ***************************
    elif isinstance(node, ALessEqualPredicate) or isinstance(node, ALessPredicate) or isinstance(node, AGreaterEqualPredicate) or isinstance(node, AGreaterPredicate):
        expr1_type = typeit(node.children[0], env, type_env)
        expr2_type = typeit(node.children[1], env, type_env)
        unify_equal(expr1_type, IntegerType(), type_env)
        unify_equal(expr2_type, IntegerType(), type_env)
        return BoolType()


# ******************
#
#       4. Relations
#
# ******************
    elif isinstance(node, ARelationsExpression):
        set_type0 = typeit(node.children[0], env, type_env)
        set_type1 = typeit(node.children[1], env, type_env)
        expected_type0 = PowerSetType(UnknownType("ARelationsExpression"))
        expected_type1 = PowerSetType(UnknownType("ARelationsExpression"))
        atype0 = unify_equal(set_type0, expected_type0, type_env)
        atype1 = unify_equal(set_type1, expected_type1, type_env)      
        return PowerSetType(PowerSetType(CartType(atype0, atype1)))
    elif isinstance(node, ADomainExpression):
        rel_type =  typeit(node.children[0], env, type_env)
        expected_type = PowerSetType(CartType(PowerSetType(UnknownType("ADomainExpression")), PowerSetType(UnknownType(type_name="no Name"))))
        atype = unify_equal(rel_type, expected_type, type_env)
        return atype.data.left # preimage settype
    elif isinstance(node, ARangeExpression):
        rel_type =  typeit(node.children[0], env, type_env)
        expected_type = PowerSetType(CartType(PowerSetType(UnknownType("ARangeExpression")), PowerSetType(UnknownType(type_name="no Name"))))
        atype = unify_equal(rel_type, expected_type, type_env)
        return atype.data.right # image settype            
    elif isinstance(node, ACompositionExpression):
        rel_type0 = typeit(node.children[0], env, type_env)
        rel_type1 = typeit(node.children[1], env, type_env)
        expected_type0 = PowerSetType(CartType(PowerSetType(UnknownType("ACompositionExpression")), PowerSetType(UnknownType(type_name="no Name"))))
        expected_type1 = PowerSetType(CartType(PowerSetType(UnknownType("ACompositionExpression")), PowerSetType(UnknownType(type_name="no Name"))))
        atype0 = unify_equal(rel_type0, expected_type0, type_env)
        atype1 = unify_equal(rel_type1, expected_type1, type_env)  
        preimagetype = atype0.data.left
        imagetype = atype1.data.right
        return PowerSetType(CartType(preimagetype, imagetype))
    elif isinstance(node, AIdentityExpression):
        set_type = typeit(node.children[0], env, type_env)
        for child in node.children[1:]:
            typeit(child, env, type_env)
        #use knowledge form args
        expected_type0 = PowerSetType(UnknownType("AIdentityExpression"))
        atype = unify_equal(set_type, expected_type0, type_env)
        return PowerSetType(CartType(atype, atype))
    elif isinstance(node, AIterationExpression):
        rel_type = typeit(node.children[0], env, type_env)
        int_type = typeit(node.children[1], env, type_env)
        expected_type = PowerSetType(CartType(PowerSetType(UnknownType("AIterationExpression")),PowerSetType(UnknownType("AIterationExpression"))))
        atype = unify_equal(rel_type, expected_type, type_env)
        unify_equal(int_type, IntegerType(), type_env)
        return atype
    elif isinstance(node, AReflexiveClosureExpression) or isinstance(node, AClosureExpression):
        rel_type = typeit(node.children[0], env, type_env)
        expected_type = PowerSetType(CartType(PowerSetType(UnknownType("AReflexiveClosureExpression")),PowerSetType(UnknownType("AReflexiveClosureExpression"))))
        atype = unify_equal(rel_type, expected_type, type_env)
        return atype
    elif isinstance(node, ADomainRestrictionExpression) or isinstance(node, ADomainSubtractionExpression):
        set_type = typeit(node.children[0], env, type_env)
        rel_type = typeit(node.children[1], env, type_env)
        expected_type0 = PowerSetType(UnknownType("ADomainRestrictionExpression"))
        expected_type1 = PowerSetType(CartType(PowerSetType(UnknownType("ADomainRestrictionExpression")), PowerSetType(UnknownType("ADomainRestrictionExpression"))))
        unify_equal(set_type, expected_type0, type_env)
        atype = unify_equal(rel_type, expected_type1, type_env)
        return atype
    elif isinstance(node, ARangeSubtractionExpression) or isinstance(node, ARangeRestrictionExpression):
        rel_type = typeit(node.children[0], env, type_env)
        set_type = typeit(node.children[1], env, type_env)
        expected_type0 = PowerSetType(UnknownType("ARangeSubtractionExpression"))
        expected_type1 = PowerSetType(CartType(PowerSetType(UnknownType("ARangeSubtractionExpression")), PowerSetType(UnknownType("ARangeSubtractionExpression"))))
        unify_equal(set_type, expected_type0, type_env)
        atype = unify_equal(rel_type, expected_type1, type_env)
        return atype
    elif isinstance(node, AReverseExpression):
        rel_type = typeit(node.children[0], env, type_env)
        expected_type = PowerSetType(CartType(PowerSetType(UnknownType("AReverseExpression")), PowerSetType(UnknownType("AReverseExpression"))))
        atype = unify_equal(rel_type, expected_type, type_env)
        preimagetype = atype.data.left
        imagetype    = atype.data.right
        return PowerSetType(CartType(imagetype, preimagetype))
    elif isinstance(node, AImageExpression):
        rel_type = typeit(node.children[0], env, type_env)
        set_type = typeit(node.children[1], env, type_env)
        expected_type = PowerSetType(CartType(set_type,PowerSetType(UnknownType("AImageExpression"))))
        atype = unify_equal(rel_type, expected_type, type_env)
        return atype.data.right
    elif isinstance(node, AOverwriteExpression):
        rel_type0 = typeit(node.children[0], env, type_env)
        rel_type1 = typeit(node.children[1], env, type_env)
        expected_type0 = PowerSetType(CartType(PowerSetType(UnknownType("AOverwriteExpression")),PowerSetType(UnknownType("AOverwriteExpression"))))
        expected_type1 = PowerSetType(CartType(PowerSetType(UnknownType("AOverwriteExpression")),PowerSetType(UnknownType("AOverwriteExpression"))))
        unify_equal(rel_type0, expected_type0, type_env)
        unify_equal(rel_type1, expected_type1, type_env)
        atype = unify_equal(rel_type0, rel_type1, type_env)
        return atype
    elif isinstance(node, AParallelProductExpression):
        # p || q = {(x,y), (m,n) | x|->y:p & m|->n:q }  
        rel_type0 = typeit(node.children[0], env, type_env)
        rel_type1 = typeit(node.children[1], env, type_env)
        expected_type0 = PowerSetType(CartType(PowerSetType(UnknownType("AParallelProductExpression")),PowerSetType(UnknownType("AParallelProductExpression"))))
        expected_type1 = PowerSetType(CartType(PowerSetType(UnknownType("AParallelProductExpression")),PowerSetType(UnknownType("AParallelProductExpression"))))
        atype0 = unify_equal(rel_type0, expected_type0, type_env)
        atype1 = unify_equal(rel_type1, expected_type1, type_env)
        x = atype0.data.left
        m = atype0.data.right
        y = atype1.data.left
        n = atype1.data.right
        return PowerSetType(CartType(PowerSetType(CartType(x,y)),PowerSetType(CartType(m,n))))
    elif isinstance(node, ADirectProductExpression):
        # p x q ={ x,(y,z) | x|->y:p & x|->z:q }
        rel_type0 = typeit(node.children[0], env, type_env)
        rel_type1 = typeit(node.children[1], env, type_env)
        expected_type0 = PowerSetType(CartType(PowerSetType(UnknownType("ADirectProductExpression")),PowerSetType(UnknownType("ADirectProductExpression"))))
        expected_type1 = PowerSetType(CartType(PowerSetType(UnknownType("ADirectProductExpression")),PowerSetType(UnknownType("ADirectProductExpression"))))
        atype0 = unify_equal(rel_type0, expected_type0, type_env)
        atype1 = unify_equal(rel_type1, expected_type1, type_env)
        x = atype0.data.left
        y = atype0.data.right
        x2 = atype1.data.left
        z = atype1.data.right
        x3 = unify_equal(x, x2, type_env)
        return PowerSetType(CartType(x3,PowerSetType(CartType(y,z))))
    elif isinstance(node, AFirstProjectionExpression):
        set_type0 = typeit(node.children[0], env, type_env)
        set_type1 = typeit(node.children[1], env, type_env)
        expected_type0 = PowerSetType(UnknownType("AFirstProjectionExpression"))
        expected_type1 = PowerSetType(UnknownType("AFirstProjectionExpression"))
        atype0 = unify_equal(set_type0, expected_type0, type_env)
        atype1 = unify_equal(set_type1, expected_type1, type_env)
        return PowerSetType(CartType(PowerSetType(CartType(atype0,atype1)), atype0))
    elif isinstance(node, ASecondProjectionExpression):
        set_type0 = typeit(node.children[0], env, type_env)
        set_type1 = typeit(node.children[1], env, type_env)
        expected_type0 = PowerSetType(UnknownType("ASecondProjectionExpression"))
        expected_type1 = PowerSetType(UnknownType("ASecondProjectionExpression"))
        atype0 = unify_equal(set_type0, expected_type0, type_env)
        atype1 = unify_equal(set_type1, expected_type1, type_env)
        return PowerSetType(CartType(PowerSetType(CartType(atype0, atype1)), atype1))


# *******************
#
#       4.1 Functions
#
# *******************
    elif isinstance(node, APartialFunctionExpression) or isinstance(node, ATotalFunctionExpression) or  isinstance(node, APartialInjectionExpression) or isinstance(node, ATotalInjectionExpression) or isinstance(node, APartialSurjectionExpression) or isinstance(node, ATotalSurjectionExpression) or isinstance(node, ATotalBijectionExpression) or isinstance(node, APartialBijectionExpression):
        set_type0 = typeit(node.children[0], env, type_env)
        set_type1 = typeit(node.children[1], env, type_env)
        expected_type0 = PowerSetType(UnknownType("APartialFunctionExpression"))
        expected_type1 = PowerSetType(UnknownType("APartialFunctionExpression"))
        atype0 = unify_equal(set_type0, expected_type0, type_env)
        atype1 = unify_equal(set_type1, expected_type1, type_env)
        return PowerSetType(PowerSetType(CartType(atype0, atype1)))
    elif isinstance(node, AFunctionExpression):
        # At this point it is imposible to always know the number of arguments!
        #
        # - num_args: (number of arguments by ast walk of args-nodes) 
        # if one of this args will be (later) unified to an CartType, 
        # the num_args is less then or equal the number of primitive-args
        # It is used to to construct a dummy-functype in step 3.
        # - number_of_args_needed (number of direct node children)
        # one of this args may be a Carttype or will later be unified to Carttype  
        # - number_of_args_needed: the number of args known at this point (less or equal real arg-num)
    
        
        # special case: (succ/pred)-function
        if isinstance(node.children[0], APredecessorExpression) or isinstance(node.children[0], ASuccessorExpression):
            atype = typeit(node.children[1], env, type_env) # type arg
            unify_equal(atype, IntegerType(), type_env, node)
            return IntegerType() # done

        # (1) determine the (incomplete) type of the function 
        # represented by a set-extension-, first/second projection- or id-expression
        type0 = typeit(node.children[0], env, type_env)
                
        # (2) calculate the number of args given 
        # (a ast-tree of couple- and identifier-expressions)
        num_args = 0
        for arg in node.children[1:]:
            num_args += calculate_num_args(arg)
        
        # (3) create a type-tree to get out the maximum of later unifications 
        # (as much informations as known at this point)
        if num_args==1:
            expected_type0 = PowerSetType(CartType(PowerSetType(UnknownType("AFunctionExpression")),PowerSetType(UnknownType("AFunctionExpression"))))
        else:
            arg_type = create_func_arg_type(num_args)
            expected_type0 = PowerSetType(CartType(arg_type,PowerSetType(UnknownType("AFunctionExpression"))))
        functype = unify_equal(type0, expected_type0, type_env, node) 
           
        # (4) get types of the function (atype.data.right is the functions image)
        arg_type_list = get_arg_type_list(functype.data.left)
        arg_type_list2 = []

        # (5) create list of primitive (no carttypes) of the given args
        number_of_args_given = len(node.children[1:]) 
        number_of_args_needed = len(arg_type_list)
        assert number_of_args_given<= number_of_args_needed
        for i in range(number_of_args_given):
            child = node.children[i+1]
            arg_type = typeit(child, env, type_env)
            # e.g f(x|->y) instead of (expected) f(x,y). 
            # This problem can be indirect! So only checking for the type is correct
            arg_list = remove_carttypes(arg_type)
            arg_type_list2 += arg_list
        

        #TODO:(ISSUE #28) more test for this code 
        # (6) unification of needed and given args (may both be known at this point)
        k = 0 # list may not be of the same length
        for i in range(number_of_args_given):
            arg_type = unknown_closure(arg_type_list2[i])
            
            if isinstance(arg_type, UnknownType) and number_of_args_given< number_of_args_needed:
                utype1 = UnknownType("function arg")
                utype2 = UnknownType("function arg")
                unify_equal(utype1, arg_type_list[k], type_env, node)
                unify_equal(utype2, arg_type_list[k+1], type_env, node)
                #tuple_type = CartType(PowerSetType(utype1), PowerSetType(utype2))
                # FIXME:(ISSUE #28) wrong unification at this point 
                #unify_equal(arg_type, tuple_type, type_env, node)
                number_of_args_given = number_of_args_given + 1
                k = k + 1  # used two types: skip one intertation              
            else:
                unify_equal(arg_type, arg_type_list[k], type_env, node)
            k = k + 1
            
        # return imagetype (pow(cart(arg_types, pow(imagetype))))
        return functype.data.right.data
    elif isinstance(node, ALambdaExpression):
        # get id names
        ids = []
        for i in range(len(node.children)-2):
            n =  node.children[i]
            assert isinstance(n.idName, str)
            ids.append(n.idName)
        type_env.push_frame(ids)
        # type ids and predicate
        for child in node.children[:-1]:
            typeit(child, env, type_env)
        pre_img_type = typeit(node.children[0], env, type_env)
        if len(node.children)>1+2: #more than one arg
            for i in range(len(node.children)-3):
                n = node.children[i+1]
                atype = typeit(n, env, type_env)
                pre_img_type = CartType(PowerSetType(pre_img_type), PowerSetType(atype))
        # get type of expression
        img_type = typeit(node.children[-1], env, type_env)
        type_env.pop_frame(env)
        # safe image type (needed for some symbolic lambda checks)
        type_env.write_lambda_node_to_env(env, node, img_type)
        # put it all together
        return PowerSetType(CartType(PowerSetType(pre_img_type), PowerSetType(img_type)))


# ********************
#
#       4.2 Sequences
#
# ********************
    elif isinstance(node,AEmptySequenceExpression):
        return PowerSetType(CartType(PowerSetType(IntegerType()),PowerSetType(UnknownType("AEmptySequenceExpression"))))
    elif isinstance(node, ASeqExpression) or isinstance(node, ASeq1Expression) or isinstance(node,AIseqExpression) or isinstance(node,APermExpression) or isinstance(node,AIseq1Expression):
        set_type = typeit(node.children[0], env, type_env)
        expected_type = PowerSetType(UnknownType("ASeqExpression"))
        atype = unify_equal(set_type, expected_type, type_env)
        return PowerSetType(PowerSetType(CartType(PowerSetType(IntegerType()), atype)))
    elif isinstance(node, AGeneralConcatExpression):
        seq_seq_type = typeit(node.children[0], env, type_env)
        #__print__btype(seq_seq_type)
        expected_seq_type = PowerSetType(CartType(PowerSetType(IntegerType()),PowerSetType(UnknownType("AGeneralConcatExpression"))))
        expected_type = PowerSetType(CartType(PowerSetType(IntegerType()), PowerSetType(expected_seq_type)))
        atype = unify_equal(seq_seq_type, expected_type, type_env)
        image_type = atype.data.right.data.data.right
        return PowerSetType(CartType(PowerSetType(IntegerType()), image_type))
    elif isinstance(node, AConcatExpression):
        seq_type0 = typeit(node.children[0], env, type_env)
        seq_type1 = typeit(node.children[1], env, type_env)
        expected_type0 = PowerSetType(CartType(PowerSetType(IntegerType()),PowerSetType(UnknownType("AConcatExpression"))))
        expected_type1 = PowerSetType(CartType(PowerSetType(IntegerType()),PowerSetType(UnknownType("AConcatExpression"))))
        atype0 = unify_equal(seq_type0, expected_type0, type_env)
        atype1 = unify_equal(seq_type1, expected_type1, type_env)
        image_type = unify_equal(atype0.data.right.data ,atype1.data.right.data, type_env)
        return PowerSetType(CartType(PowerSetType(IntegerType()),PowerSetType(image_type)))
    elif isinstance(node, AInsertFrontExpression):
        set_type = typeit(node.children[0], env, type_env)
        seq_type = typeit(node.children[1], env, type_env)
        img_type = UnknownType("AInsertFrontExpression") # e.g. IntegerType or PowerSetType
        expected_type1 = PowerSetType(CartType(PowerSetType(IntegerType()),PowerSetType(img_type)))
        atype0 = unify_equal(set_type, img_type, type_env)
        atype1 = unify_equal(seq_type, expected_type1, type_env)
        if isinstance(atype0, SetType):
            assert atype0.name == atype1.data.right.data.name # Setname
        return atype1
    elif isinstance(node, AInsertTailExpression):
        seq_type = typeit(node.children[0], env, type_env)
        set_type = typeit(node.children[1], env, type_env)
        img_type = UnknownType("AInsertTailExpression") # e.g. IntegerType or PowerSetType
        expected_type0 = PowerSetType(CartType(PowerSetType(IntegerType()),PowerSetType(img_type)))
        atype0 = unify_equal(seq_type, expected_type0, type_env)
        atype1 = unify_equal(set_type, img_type, type_env)
        if isinstance(atype1, SetType):
            assert atype1.name == atype0.data.right.data.name # Setname
        return atype0
    elif isinstance(node, ASequenceExtensionExpression):
        # children = list of expressions 
        reftype = typeit(node.children[0], env, type_env) 
        for child in node.children[1:]:
            atype = typeit(child, env, type_env)
            unify_equal(atype, reftype, type_env)
        return PowerSetType(CartType(PowerSetType(IntegerType()), PowerSetType(reftype)))
    elif isinstance(node, ASizeExpression):
        seq_type = typeit(node.children[0], env, type_env)
        expected_type = PowerSetType(CartType(PowerSetType(IntegerType()),PowerSetType(UnknownType("ASizeExpression"))))
        unify_equal(seq_type, expected_type, type_env)
        return IntegerType()
    elif isinstance(node, ARevExpression):
        seq_type = typeit(node.children[0], env, type_env)
        expected_type = PowerSetType(CartType(PowerSetType(IntegerType()),PowerSetType(UnknownType("ARevExpression"))))
        atype = unify_equal(seq_type, expected_type, type_env)
        return atype
    elif isinstance(node, ARestrictFrontExpression) or isinstance(node, ARestrictTailExpression):
        seq_type = typeit(node.children[0], env, type_env)
        int_type = typeit(node.children[1], env, type_env)
        expected_type0 = PowerSetType(CartType(PowerSetType(IntegerType()),PowerSetType(UnknownType("ARestrictFrontExpression"))))
        expected_type1 = IntegerType()
        atype = unify_equal(seq_type, expected_type0, type_env)
        unify_equal(int_type, expected_type1, type_env)
        return atype
    elif isinstance(node, AFirstExpression) or isinstance(node, ALastExpression):
        seq_type = typeit(node.children[0], env, type_env)
        expected_type = PowerSetType(CartType(PowerSetType(IntegerType()),PowerSetType(UnknownType("AFirstORLastExpression"))))
        atype = unify_equal(seq_type, expected_type, type_env)
        return atype.data.right.data
    elif isinstance(node, ATailExpression) or isinstance(node, AFrontExpression):
        seq_type = typeit(node.children[0], env, type_env)
        expected_type = PowerSetType(CartType(PowerSetType(IntegerType()),PowerSetType(UnknownType("AFrontORTailExpression"))))
        atype = unify_equal(seq_type, expected_type, type_env)
        return atype



# ****************
#
# 5. Substitutions
#
# ****************
    elif isinstance(node, AAssignSubstitution):
        assert int(node.lhs_size) == int(node.rhs_size)
        for i in range(int(node.lhs_size)):
            lhs_node = node.children[i]
            rhs = node.children[i+int(node.rhs_size)]
            atype0 = typeit(rhs, env, type_env)
            if isinstance(lhs_node, AIdentifierExpression):
                #print lhs_node.idName, node.children
                atype1 = typeit(lhs_node, env, type_env)
                #print "left",lhs_node.idName
                #__print__btype(atype1)
                #print "right"
                #__print__btype(atype0)
                unify_equal(atype0, atype1, type_env)
            else:
                assert isinstance(lhs_node, AFunctionExpression)
                assert isinstance(lhs_node.children[0], AIdentifierExpression)
                func_type = typeit(lhs_node.children[0], env, type_env)
                atype2 = PowerSetType(CartType(PowerSetType(UnknownType("AAssignSubstitution")), PowerSetType(atype0)))
                unify_equal(func_type, atype2, type_env)
    elif isinstance(node, AConvertBoolExpression):
        atype = typeit(node.children[0], env, type_env)
        unify_equal(atype, BoolType(), type_env)
        return BoolType()
    elif isinstance(node, ABecomesElementOfSubstitution):
        # x :: {a,b,c}
        atype = typeit(node.children[-1], env, type_env)
        for child in node.children[:-1]:
            idtype = typeit(child, env, type_env)
            unify_element_of(idtype, atype, type_env, node)
    elif isinstance(node, AVarSubstitution):
        ids = []
        for idNode in node.children[:-1]:
            assert isinstance(idNode, AIdentifierExpression)
            ids.append(idNode.idName)
        type_env.push_frame(ids)
        typeit(node.children[-1], env, type_env)
        type_env.pop_frame(env)
    elif isinstance(node, AAnySubstitution) or isinstance(node, ALetSubstitution):
        idNames = []
        for i in range(node.idNum):
            idNode = node.children[i]
            assert isinstance(idNode, AIdentifierExpression)
            idNames.append(idNode.idName)
        type_env.push_frame(idNames)
        for child in node.children:
            typeit(child, env, type_env)
        type_env.pop_frame(env)

# ****************
#
# 6. Miscellaneous
#
# ****************
    elif isinstance(node, AStringExpression):
        return StringType()
    elif isinstance(node, AStringSetExpression):
        return PowerSetType(StringType())
    elif isinstance(node, ABoolSetExpression):
        return PowerSetType(BoolType())
    elif isinstance(node, ABooleanTrueExpression) or isinstance(node, ABooleanFalseExpression):
        return BoolType()
    elif isinstance(node, APrimedIdentifierExpression):
        assert len(node.children)==1 # TODO: x.y.z + unify
        return typeit(node.children[0], env, type_env)
    elif isinstance(node, AIdentifierExpression):
        type_env.add_node_by_id(node)
        # TODO: if deferred set set type to SetType(None)
        idtype = type_env.get_current_type(node.idName)
        return idtype
    elif isinstance(node, AMinIntExpression) or isinstance(node, AMaxIntExpression):
        # MINT_INT MAX_INT
        return IntegerType()
    elif isinstance(node, AStructExpression):
        # E.g. struct(Mark:NAT,Good_enough:BOOL)
        dictionary = {}
        for rec_entry in node.children:
            assert isinstance(rec_entry, ARecEntry)
            name = ""
            if isinstance(rec_entry.children[0], AIdentifierExpression):
                name = rec_entry.children[0].idName
            assert isinstance(rec_entry.children[-1], Expression)
            atype = typeit(rec_entry.children[-1], env, type_env)
            dictionary[name] = atype.data # use data to remove powerset
        return PowerSetType(StructType(dictionary))
    elif isinstance(node, ARecExpression):
        # E.g. rec(Mark:14,Good_enough:TRUE)
        dictionary = {}
        for rec_entry in node.children:
            assert isinstance(rec_entry, ARecEntry)
            name = ""
            if isinstance(rec_entry.children[0], AIdentifierExpression):
                name = rec_entry.children[0].idName
            assert isinstance(rec_entry.children[-1], Expression)
            atype = typeit(rec_entry.children[-1], env, type_env)
            dictionary[name] = atype
        return StructType(dictionary)
    elif isinstance(node, ARecordFieldExpression):
        # E.g. RES'Mark
        atype = typeit(node.children[0], env, type_env)
        assert isinstance(atype, StructType)
        assert isinstance(node.children[1], AIdentifierExpression)
        entry_type = atype.dictionary[node.children[1].idName] # access dict 
        return entry_type
    elif isinstance(node, ATransRelationExpression):
        func_type = typeit(node.children[0], env, type_env)
        range_type = UnknownType("ATransRelationExpression")
        image_type = UnknownType("ATransRelationExpression")
        expected_type = PowerSetType(CartType(PowerSetType(range_type), PowerSetType(PowerSetType(image_type))))
        atype = unify_equal(func_type, expected_type, type_env)
        range_type = atype.data.left
        image_type = atype.data.right.data
        return PowerSetType(CartType(range_type, image_type))
    elif isinstance(node, ATransFunctionExpression):
        rel_type = typeit(node.children[0], env, type_env)
        range_type = UnknownType("ATransFunctionExpression")
        image_type = UnknownType("ATransFunctionExpression")
        expected_type = PowerSetType(CartType(PowerSetType(range_type), PowerSetType(image_type)))
        atype = unify_equal(rel_type, expected_type, type_env)
        range_type = atype.data.left
        image_type = atype.data.right
        return PowerSetType(CartType(range_type, PowerSetType(image_type)))
    elif isinstance(node, AUnaryMinusExpression):
        aint_type = typeit(node.children[0], env, type_env)
        unify_equal(IntegerType(), aint_type, type_env)
        return IntegerType()
    elif isinstance(node, AOperation):
        names = []
        for i in range(0,node.return_Num+ node.parameter_Num):
            assert isinstance(node.children[i], AIdentifierExpression)
            names.append(node.children[i].idName)
        type_env.push_frame(names)
        # type everything 
        for child in node.children:
            typeit(child, env, type_env)
        # save type of return arguments
        ret_types = []
        ret_nodes = []
        for i in range(node.return_Num):
            child = node.children[i]
            assert isinstance(child, AIdentifierExpression)
            atype = type_env.get_current_type(child.idName)
            assert not isinstance(atype, UnknownType)
            ret_nodes.append(child)
            ret_types.append(atype)
        # save type of parameters
        para_types = []
        para_nodes = []
        for i in range(node.parameter_Num):
            child = node.children[i+node.return_Num]
            #for child in node.children[node.return_Num:(node.return_Num+node.parameter_Num)]:
            assert isinstance(child, AIdentifierExpression)
            atype = type_env.get_current_type(child.idName)
            assert not isinstance(atype, UnknownType)
            para_nodes.append(child)
            para_types.append(atype)
        # Add query-operation test and add result to list.
        # TODO: strictly speaking this is no task of a type checker
        is_query_op = check_if_query_op(node.children[-1], env.current_mch.var_names) 
        # add all computed informations    
        boperation = env.get_operation_by_name(env.current_mch.mch_name, node.opName)
        boperation.is_query_op     = is_query_op   
        boperation.set_types(ret_types, para_types, ret_nodes, para_nodes)         
        type_env.pop_frame(env)
    elif isinstance(node, AOpSubstitution):
        # FIXME: assumption: Operation object typed before Op substitution call
        boperation = env.lookup_operation(node.idName)
        para_types = boperation.parameter_types
        assert len(para_types)==node.parameter_Num
        for i in range(len(node.children)):
            atype = typeit(node.children[i], env, type_env)
            p_type = para_types[i]
            unify_equal(p_type, atype, type_env)
        ret_types =  boperation.return_types
        assert ret_types==[]
        return
    elif isinstance(node, AOperationCallSubstitution):
        boperation = env.lookup_operation(node.idName)
        ret_types =  boperation.return_types
        para_types = boperation.parameter_types
        assert len(para_types)==node.parameter_Num
        assert len(ret_types)==node.return_Num
        for i in range(node.return_Num, (node.return_Num+node.parameter_Num)):
            atype = typeit(node.children[i], env, type_env)
            p_type = para_types[i-node.return_Num]
            unify_equal(p_type, atype, type_env)
        assert not ret_types==[]
        for i in range(0, node.return_Num):
            atype = typeit(node.children[i], env, type_env)
            r_type = ret_types[i]
            unify_equal(r_type, atype, type_env)
        return 
    elif isinstance(node, AExternalFunctionExpression):
        atype =  typeit(node.type_node, env, type_env)
        functype = atype.data
        return functype.data.right.data #image
    elif isinstance(node, APredecessorExpression) or isinstance(node, ASuccessorExpression):
        return PowerSetType(CartType(PowerSetType(IntegerType()),PowerSetType(IntegerType())))
    else:
        # Substitutions and clauses return no type informations.
        # It is sufficient to visit all children (AST-sub-trees).
        # TODO: ASuccessorExpression
        assert isinstance(node, Substitution) or isinstance(node, Clause) or isinstance(node, AMachineReference)
        for child in node.children:
            typeit(child, env, type_env)



# This function exist to handle preds like "x=y & y=1" and find the
# type of x and y after one run.
# UnknownTypes in a typetree will be set in the basecase of the recursion
# AFTER this (in the returning phase of the recursion) it uses the subtypetree which 
# has the same or more informations
# TODO: This function is not full implemented!
# pred_node is used for error messages 
def unify_equal(maybe_type0, maybe_type1, type_env, pred_node=None):
    assert isinstance(type_env, TypeCheck_Environment)
    assert isinstance(maybe_type0, AbstractType)
    assert isinstance(maybe_type1, AbstractType)
    #import inspect
    #print inspect.stack()[1] 
    #print "type 1/2",maybe_type0,maybe_type1
    maybe_type0 = unknown_closure(maybe_type0)
    maybe_type1 = unknown_closure(maybe_type1)
    #__print__btype(maybe_type1)
    # instance equality check
    if maybe_type0==maybe_type1:
        return maybe_type0

    # case 1: BType, BType
    if isinstance(maybe_type0, BType) and isinstance(maybe_type1, BType):
        #if isinstance(maybe_type0, PowerSetType) and isinstance(maybe_type1, EmptySetType):
        #    return maybe_type0
        #elif isinstance(maybe_type1, PowerSetType) and isinstance(maybe_type0, EmptySetType):
        #    return maybe_type1
        if maybe_type0.eq_type(maybe_type1):
            # recursive unification-call
            # if not IntegerType, SetType or UnkownType.
            if isinstance(maybe_type0, PowerSetType):
                atype = unify_equal(maybe_type0.data, maybe_type1.data, type_env, pred_node)
                maybe_type0.data = atype
            elif isinstance(maybe_type0, StructType):
                dictionary0 = maybe_type0.dictionary
                dictionary1 = maybe_type1.dictionary
                #assert isinstance(dictionary0, dict)
                #assert isinstance(dictionary1, dict)
                lst0 = list(dictionary0.values())
                lst1 = list(dictionary1.values())
                assert len(lst0)==len(lst1)
                for index in range(len(lst0)):
                    unify_equal(lst0[index], lst1[index], type_env, pred_node)
            elif isinstance(maybe_type0, CartType):
                t00 = unknown_closure(maybe_type0.left)
                t10 = unknown_closure(maybe_type1.left)
                t01 = unknown_closure(maybe_type0.right)
                t11 = unknown_closure(maybe_type1.right)
                assert isinstance(t00, PowerSetType)
                assert isinstance(t10, PowerSetType)
                assert isinstance(t01, PowerSetType)
                assert isinstance(t11, PowerSetType)
                # (2) unify
                atype = unify_equal(t00.data, t10.data, type_env, pred_node)
                maybe_type0.left.data = atype
                atype = unify_equal(t01.data, t11.data, type_env, pred_node)
                maybe_type0.right.data = atype
            elif isinstance(maybe_type0, SetType):
                # learn/set name
                #if maybe_type0.name==None:
                #    maybe_type0.name = maybe_type1.name
                #elif maybe_type1.name==None:
                #    maybe_type1.name = maybe_type0.name
                #else:
                assert maybe_type1.name == maybe_type0.name
            else:
                assert isinstance(maybe_type0, IntegerType) or isinstance(maybe_type0, BoolType) or isinstance(maybe_type0, StringType)
            return maybe_type0
        else:
            string = "TypeError in typing.py! Unable to unify two type variables: %s %s." % (maybe_type0, maybe_type1)
            #print string
            if pred_node:
                string += "Last unification was caused by: " + pretty_print(pred_node)
                #arrgs = type_env.get_current_type("ad")
                #__print__btype(arrgs)
            raise BTypeException(string)

    # case 2: Unknown, Unknown
    elif isinstance(maybe_type0, UnknownType) and isinstance(maybe_type1, UnknownType):
        return type_env.set_unknown_type(maybe_type0, maybe_type1)

    # case 3: Unknown, BType
    elif isinstance(maybe_type0, UnknownType) and isinstance(maybe_type1, BType):
        return type_env.set_concrete_type(utype=maybe_type0, ctype=maybe_type1)

    # case 4: BType, Unknown
    elif isinstance(maybe_type0, BType) and isinstance(maybe_type1, UnknownType):
        return type_env.set_concrete_type(utype=maybe_type1, ctype=maybe_type0)
    else:
        # no UnknownType and no BType:
        # If this is ever been raised than this is a bug
        # inside the typechecker: Every unifiable expression
        # must be a BType or an UnknownType!
        string = "Typchecker Bug: no Unknowntype and no Btype!\nUnification fail: %s != %s" % (maybe_type0, maybe_type1)
        if pred_node:
            string += "Last unification was caused by: " + pretty_print(pred_node)
        raise PYBBugException(string)



# called by Belong-Node
# calls the unify_equal method with correct args
def unify_element_of(elm_type, set_type, type_env, pred_node):
    assert isinstance(pred_node, ABecomesElementOfSubstitution) or isinstance(pred_node, ANotMemberPredicate) or isinstance(pred_node, AMemberPredicate)
    # (1) type already known?
    set_type = unknown_closure(set_type)
    elm_type = unknown_closure(elm_type)
    assert not set_type is None

    # (2) unify
    if isinstance(elm_type, UnknownType):
        if isinstance(set_type, PowerSetType):
            # map elm_type (UnknownType) to set_type for all elm_type
            unify_equal(elm_type, set_type.data, type_env, pred_node)
        elif isinstance(set_type, UnknownType):
            assert set_type.real_type is None
            unify_equal(set_type, PowerSetType(elm_type), type_env, pred_node)
        else:
            # no UnknownType and no PowersetType:
            # If this is ever been raised than this is a bug 
            # inside the typechecker. In B the right side S of
            # a Belong-expression (x:S) must be of PowerSetType!
            string = "Typchecker Bug: set type is no Unknowntype and no PowersetType!"
            string += "Last unification was caused by: " + pretty_print(pred_node)
            raise PYBBugException(string)
        return
    elif isinstance(elm_type, BType):
        unify_equal(PowerSetType(elm_type), set_type, type_env, pred_node)
        return
    else:
        # no Unknowntype and no Btype:
        # If this is ever been raised than this is a bug
        # inside the typechecker: Every unifiable expression
        # must be a BType or an UnknownType!
        string = "Typchecker Bug: element type is no Unknowntype and no Btype!"
        string += "Last unification was caused by: " + pretty_print(pred_node)
        raise PYBBugException(string)