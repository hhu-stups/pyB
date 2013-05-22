# -*- coding: utf-8 -*-
from ast_nodes import *
from btypes import *
from helpers import find_var_names, print_ast, add_all_visible_ops_to_env
from bmachine import BMachine
from boperation import BOperation



# helper for debugging
def __print__btype(tree, t=0):
    print " "*t, tree
    if isinstance(tree, PowerSetType):
        __print__btype(tree.data,t+1)
    elif isinstance(tree, CartType):
        __print__btype(tree.data[0],t+1)
        __print__btype(tree.data[1],t+1) 


def create_func_arg_type(num_args):
    if num_args==2:
        return PowerSetType(CartType(PowerSetType(UnknownType("AFunctionExpression",None)),PowerSetType(UnknownType("AFunctionExpression",None))))
    else:
        arg_type = create_func_arg_type(num_args-1)
        return PowerSetType(CartType(arg_type,PowerSetType(UnknownType("AFunctionExpression",None))))

def _get_arg_type_list(type,lst):
    assert isinstance(type, PowerSetType)
    if isinstance(type.data, CartType):
        _get_arg_type_list(type.data.data[0], lst)
        _get_arg_type_list(type.data.data[1], lst)
    else:
        lst.append(type.data) # function-args have not the pow_set but the set type
        return
        
        

def get_arg_type_list(func_type):
    lst = []
    _get_arg_type_list(func_type, lst) # sideeffect: fill list with types
    return lst
    
def check_if_query_op(sub, var_names):
    assert isinstance(sub, Substitution)
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
    elif isinstance(sub, ABecomesElementOfSubstitution) or isinstance(sub, ABecomesSuchSubstitution):
        for child in sub.children[:-1]:
            assert isinstance(child, AIdentifierExpression)
            if child.idName in var_names:
                return False
    else:
        for child in sub.children:
            if isinstance(child, Substitution):
                is_query_op = check_if_query_op(child, var_names)
                if not is_query_op:
                    return False            
    return True 


class BTypeException(Exception):
    def __init__(self, string):
        self.string = string


# Helper env: will be thrown away after Typechecking
# FIXME: But is used in bmachine
class TypeCheck_Environment():
    def __init__(self):
        # is used to construct the env.node_to_type_map
        self.id_to_nodes_stack = []
        self.id_to_types_stack = []
        self.id_to_enum_hint_stack = []


    def init_env(self, known_types_list, idNames):
        id_to_nodes_map = {} # A: str->NODE
        id_to_types_map = {} # T: str->Type
        id_to_enum_hint = {} # E: str->str
        # 1. write known Informations 
        for atuple in known_types_list:
            id_Name = atuple[0]
            atype = atuple[1]
            id_to_types_map[id_Name] = UnknownType(id_Name, atype)
            id_to_nodes_map[id_Name] = []
            id_to_enum_hint[id_Name] = None
        # 2. and ids with unknown types
        for id_Name in idNames:
            id_to_nodes_map[id_Name] = [] # no Nodes at the moment
            id_to_types_map[id_Name] = UnknownType(id_Name, None)
            id_to_enum_hint[id_Name] = None
        self.id_to_types_stack = [id_to_types_map]
        self.id_to_nodes_stack = [id_to_nodes_map]
        self.id_to_enum_hint_stack = [id_to_enum_hint]


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
        id_to_enum_hint = {} # E: str->str
        for id_Name in id_Names:
            id_to_nodes_map[id_Name] = [] # no Nodes at the moment
            id_to_types_map[id_Name] = UnknownType(id_Name, None)
            id_to_enum_hint[id_Name] = None
        self.id_to_nodes_stack.append(id_to_nodes_map)
        self.id_to_types_stack.append(id_to_types_map)
        self.id_to_enum_hint_stack.append(id_to_enum_hint)


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
        string = "TypeError: %s not found while adding node: %s! Maybe %s is unkown. IdName not added to type_env (typing.py)?", node.idName, node, node.idName
        print string
        raise BTypeException(string)


    def set_unknown_type(self, id0_Name, id1_Name):
        assert isinstance(id0_Name, UnknownType)
        assert isinstance(id1_Name, UnknownType)
        assert id0_Name.real_type==None
        assert id1_Name.real_type==None
        assert not id1_Name == id0_Name # dont produce a cycle 

        if isinstance(id0_Name, PowORIntegerType) or isinstance(id0_Name, PowCartORIntegerType):
            id1_Name.real_type = id0_Name
        else: #TODO: more cases?
            assert id0_Name.real_type==None
            id0_Name.real_type = id1_Name
        return id1_Name


    def set_concrete_type(self, utype, ctype):
        assert isinstance(utype, UnknownType)
        assert isinstance(ctype, BType)
        #print utype.name, ctype
        if isinstance(utype, PowCartORIntegerType):
            u0 = unknown_closure(utype.data[0])
            u1 = unknown_closure(utype.data[1])
            if isinstance(ctype, IntegerType):
                if isinstance(u0, UnknownType):
                    self.set_concrete_type(u0, ctype)
                else:
                    assert isinstance(u0, IntegerType)
                if isinstance(u1, UnknownType):
                    self.set_concrete_type(u1, ctype)
                else:
                    assert isinstance(u1, IntegerType)
                return IntegerType(None)
            else:
                assert isinstance(ctype, PowerSetType)
                cart_type = unknown_closure(ctype.data)
                assert isinstance(cart_type, CartType)
                subset_type0 = unknown_closure(cart_type.data[0])
                subset_type1 = unknown_closure(cart_type.data[1])
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
            u0 = unknown_closure(utype.data[0])
            u1 = unknown_closure(utype.data[1])
            if isinstance(ctype, IntegerType):
                if isinstance(u0, UnknownType):
                    self.set_concrete_type(u0, ctype)
                else:
                    assert isinstance(u0, IntegerType)
                if isinstance(u1, UnknownType):
                    self.set_concrete_type(u1, ctype)
                else:
                    assert isinstance(u1, IntegerType)
                return IntegerType(None)
            else:
                assert isinstance(ctype, PowerSetType)
                # TODO: implement set subtr.
        else:
            assert utype.real_type==None
            utype.real_type = ctype
            return ctype


    # copies to env.node_to_type_map
    def pop_frame(self, env):
        node_top_map = self.id_to_nodes_stack[-1]
        type_top_map = self.id_to_types_stack[-1]
        id_to_enum_hint = self.id_to_enum_hint_stack[-1]
        self.id_to_nodes_stack.pop()
        self.id_to_types_stack.pop()
        self.id_to_enum_hint_stack.pop()
        #assert isinstance(env, Environment)
        self.write_to_env(env, type_top_map, node_top_map, id_to_enum_hint)



    def write_to_env(self, env, type_top_map, node_top_map, id_to_enum_hint):
        for idName in type_top_map:
            utype = type_top_map[idName]
            atype = unknown_closure(utype)
            try:
                enum_hint = id_to_enum_hint[idName]
            except KeyError:
                enum_hint = None #XXX/TODO: child env
            # unknown now. will be found in resole()
            # This is when local vars use global vars
            # which are unknown a this time
            if atype==None:
                atype= utype
            node_lst = node_top_map[idName]
            for node in node_lst:
                node.enum_hint = enum_hint
                env.node_to_type_map[node] = atype


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
        string = "TypeError: idName %s not found! IdName not added to type_env (typing.py)?",idName
        print string
        raise BTypeException(string)


    # FIXME: maybe this is nonsense :)
    def set_enumeration_hint(self, idName, hint_idName):
        id_to_enum_hint = self.id_to_enum_hint_stack[-1]
        try:
            current_hint = id_to_enum_hint[idName]
        except KeyError: # TODO: child env
            current_hint = None
        if current_hint ==None:
            id_to_enum_hint[idName] = hint_idName
        # TODO: else chose better set 



# env.node_to_type_map should be a set of tree with 
# Nodes as leafs and Btypes as roots. 
# This method should throw away all unknowntypes 
# by walking from the leafs to the roots.
# If this is not possible the typechecking has failed
def resolve_type(env):
    for node in env.node_to_type_map:
        tree = env.node_to_type_map[node]
        # print node.idName, tree
        tree_without_unknown = throw_away_unknown(tree)
        env.node_to_type_map[node] = tree_without_unknown



# it is a list an becomes a tree when carttype is implemented
# It uses the data attr of BTypes as pointers
def throw_away_unknown(tree):
    #print tree
    if isinstance(tree, SetType) or isinstance(tree, IntegerType) or isinstance(tree, StringType) or isinstance(tree, BoolType):
        return tree
    elif isinstance(tree, PowerSetType):
        if isinstance(tree.data, UnknownType):
            atype = unknown_closure(tree.data)
            assert isinstance(atype, BType)
            tree.data = atype
        throw_away_unknown(tree.data)
        return tree
    elif isinstance(tree, CartType): 
        if not isinstance(tree.data[0], UnknownType) and not isinstance(tree.data[1], UnknownType):
            throw_away_unknown(tree.data[0])
            throw_away_unknown(tree.data[1])
            return tree
        else: #TODO: implement me
            return tree
    elif isinstance(tree, StructType):#TODO: implement me
        return tree
    elif isinstance(tree, PowCartORIntegerType):
        data = tree.data
        arg1 = unknown_closure(data[0])
        arg2 = unknown_closure(data[1])
        arg1 = throw_away_unknown(arg1)
        arg2 = throw_away_unknown(arg2)
        assert isinstance(arg1, BType)
        assert isinstance(arg2, BType)
        if not arg1.__class__ == arg2.__class__:
            string = "TypeError: not unifiable %s %s",arg1, arg2
            raise BTypeException(string)

        if isinstance(arg1, PowerSetType) and isinstance(arg2, PowerSetType):
            tree = PowerSetType(CartType(arg1, arg2))
        elif isinstance(arg1, IntegerType) and isinstance(arg2, IntegerType):
            tree = IntegerType(None)
        return tree
    elif isinstance(tree, PowORIntegerType):
        data = tree.data
        arg1 = unknown_closure(data[0])
        arg2 = unknown_closure(data[1])
        arg1 = throw_away_unknown(arg1)
        arg2 = throw_away_unknown(arg2)
        assert isinstance(arg1, BType)
        assert isinstance(arg2, BType)
        if not arg1.__class__ == arg2.__class__:
            string = "TypeError: not unifiable %s %s",arg1, arg2
            raise BTypeException(string)

        if isinstance(arg1, PowerSetType) and isinstance(arg2, PowerSetType):
            tree = arg1
        elif isinstance(arg1, IntegerType) and isinstance(arg2, IntegerType):
            tree = arg1
        return tree
    elif tree==None:
        raise BTypeException("TypeError: can not resolve a Type")
    elif isinstance(tree, UnknownType):
        tree = unknown_closure(tree)
        if isinstance(tree, UnknownType):
            print tree
            string = "TypeError: can not resolve a Type of "+ str(tree.name)
            print string
            raise BTypeException(string)
        tree = throw_away_unknown(tree)
        return tree
    else:
        raise Exception("resolve fail: Not Implemented %s"+tree)


# follows an UnknownType pointer chain:
# returns an UnknownType or a BType
# WARNING: This BType could point on other UnknownTypes. e.g. POW(X)
# WARNING: assumes cyclic - free
def unknown_closure(atype):
    if not isinstance(atype, UnknownType):
        return atype
    i = 0
    while True:
        i = i +1
        if i==100: #DEBUG
            assert 2==1
        if not isinstance(atype.real_type, UnknownType):
            break
        elif isinstance(atype.real_type, PowORIntegerType):
            break
        elif isinstance(atype.real_type, PowCartORIntegerType):
            break
        atype = atype.real_type
    if isinstance(atype.real_type, BType) or isinstance(atype.real_type, PowORIntegerType) or isinstance(atype.real_type, PowCartORIntegerType):
        return atype.real_type
    else:
        assert atype.real_type==None #XXX: PowORIntegerType/PowCartORIntegerType
        return atype


# TODO: rename
def _test_typeit(root, env, known_types_list, idNames):
    type_env = TypeCheck_Environment()
    type_env.init_env(known_types_list, idNames)
    typeit(root, env, type_env)
    type_env.write_to_env(env, type_env.id_to_types_stack[-1], type_env.id_to_nodes_stack[-1], type_env.id_to_enum_hint_stack[-1])
    resolve_type(env) # throw away unknown types
    return type_env   # contains only knowladge about ids at global level


def type_check_predicate(root, env, idNames):
    ## FIXME: replace this call someday
    type_env = _test_typeit(root.children[0], env, [], idNames)

def type_check_expression(root, env, idNames):
    ## FIXME: replace this call someday
    type_env = _test_typeit(root.children[0], env, [], idNames)


def type_check_bmch(root, env, mch):
    # TODO: abstr const/vars
    # TODO?: operations?
    set_idNames = find_var_names(mch.aSetsMachineClause) 
    const_idNames = find_var_names(mch.aConstantsMachineClause)
    var_idNames = find_var_names(mch.aVariablesMachineClause)
    idNames = set_idNames + const_idNames + var_idNames
    #assert set(idNames)==set(mch.names)
    for node in mch.scalar_params + mch.set_params:
        idNames.append(node.idName) # add machine-parameters
    type_env = _test_typeit(root, env, [], idNames) ## FIXME: replace
    if env.root_mch == mch:
        add_all_visible_ops_to_env(mch, env)
    return type_env


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
        # TODO: mch-parameters
        mch = env.current_mch
        mch.type_included(type_check_bmch, type_env, env)
        mch.type_extended(type_check_bmch, type_env, env)
        mch.type_seen(type_check_bmch, type_env, env)
        mch.type_used(type_check_bmch, type_env, env)


        # add para-nodes to map
        for idNode in mch.aMachineHeader.children:
            assert isinstance(idNode, AIdentifierExpression)
            typeit(idNode, env, type_env)
            
        for p in mch.set_params:
            unknown_type = type_env.get_current_type(p.idName)
            unify_equal(unknown_type, PowerSetType(SetType(p.idName)), type_env)

        # type
        if mch.aExtendsMachineClause:
            typeit(mch.aExtendsMachineClause, env, type_env)
        if mch.aIncludesMachineClause:
            typeit(mch.aIncludesMachineClause, env, type_env)
        if mch.aConstraintsMachineClause: # C
            typeit(mch.aConstraintsMachineClause, env, type_env)
        if mch.aSetsMachineClause: # St
            for child in mch.aSetsMachineClause.children:
                set_name = child.idName
                utype = type_env.get_current_type(set_name)
                atype = SetType(set_name)
                unify_equal(utype, PowerSetType(atype), type_env)
                if isinstance(child, AEnumeratedSet):
                    # all elements have the type set_name
                    for elm in child.children:
                        elm_type = typeit(elm, env, type_env)
                        unify_equal(atype, elm_type, type_env)
        if mch.aConstantsMachineClause: # k
            typeit(mch.aConstantsMachineClause, env, type_env)
        if mch.aPropertiesMachineClause: # B
            typeit(mch.aPropertiesMachineClause, env, type_env)
        if mch.aVariablesMachineClause:
            typeit(mch.aVariablesMachineClause, env, type_env)
        if mch.aInvariantMachineClause:
            typeit(mch.aInvariantMachineClause, env, type_env)
        if mch.aInitialisationMachineClause:
            typeit(mch.aInitialisationMachineClause, env, type_env)
        if mch.aAssertionsMachineClause:
            typeit(mch.aAssertionsMachineClause, env, type_env)
        if mch.aOperationsMachineClause:
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
    elif isinstance(node, AUniversalQuantificationPredicate) or isinstance(node, AExistentialQuantificationPredicate):
        ids = []
        for n in node.children[:-1]:
            assert isinstance(n.idName, str)
            ids.append(n.idName)
        type_env.push_frame(ids)
        for child in node.children:
            typeit(child, env, type_env)
        type_env.pop_frame(env)
        return BoolType()
    elif isinstance(node, AEqualPredicate) or  isinstance(node,AUnequalPredicate):
        expr1_type = typeit(node.children[0], env,type_env)
        expr2_type = typeit(node.children[1], env,type_env)
        unify_equal(expr1_type, expr2_type, type_env)
        return BoolType()


# **************
#
#       2. Sets
#
# **************
    elif isinstance(node, ASetExtensionExpression):
        # FIXME: This code don't works inside a SET-Section
        # no Vars are declared!
        # TODO: maybe new frame?
        if isinstance(node.children[0], ACoupleExpression):
            # a realtion: S1->S2->S3-> ... ->S"len(children)"
            elem_type = typeit(node.children[0], env, type_env)
            # learn that all Elements must have the same type:
            for child in node.children[1:]:
                assert isinstance(child, ACoupleExpression)
                atype = typeit(child, env, type_env)
                unify_equal(elem_type, atype, type_env)
            return PowerSetType(elem_type)
        else:
            reftype = typeit(node.children[0], env, type_env)
            # learn that all Elements must have the same type:
            for child in node.children[1:]:
                atype = typeit(child, env, type_env)
                reftype = unify_equal(atype, reftype, type_env)
            return PowerSetType(reftype)
    elif isinstance(node, AEmptySetExpression):
        return PowerSetType(UnknownType("AEmptySetExpression", None))
    elif isinstance(node, AComprehensionSetExpression):
        ids = []
        # get id names
        for n in node.children[:-1]:
            assert isinstance(n.idName, str)
            ids.append(n.idName)
        type_env.push_frame(ids)
        assert len(node.children)>=1
        for child in node.children:
            typeit(child, env, type_env)
        for child in node.children[:-1]:
            assert isinstance(child, AIdentifierExpression)
            assert not type_env.get_current_type(child.idName)==None
        atype = type_env.get_current_type(ids[0])
        if len(ids)>1:
            atype = CartType(PowerSetType(atype), PowerSetType(type_env.get_current_type(ids[1])))
            for i in ids[2:]:
                atype = CartType(PowerSetType(atype), PowerSetType(type_env.get_current_type(i)))
        type_env.pop_frame(env)
        return PowerSetType(atype) #name unknown
    elif isinstance(node, AMinusOrSetSubtractExpression):
        expr1_type = typeit(node.children[0], env, type_env)
        expr2_type = typeit(node.children[1], env, type_env)
        unify_equal(expr1_type, expr2_type, type_env)
        expr1_type = unknown_closure(expr1_type)
        expr2_type = unknown_closure(expr2_type)

        if isinstance(expr1_type, IntegerType) or isinstance(expr2_type, IntegerType):  # Integer-Minus
            return IntegerType(None)
        elif isinstance(expr1_type, PowerSetType) or isinstance(expr2_type, PowerSetType): # SetSubtract
            return expr1_type
        elif isinstance(expr1_type, UnknownType) and isinstance(expr2_type, UnknownType):  # Dont know
            return PowORIntegerType(expr1_type, expr2_type)
        else:
            raise Exception("Unimplemented case: %s",node)
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
            atype = CartType(PowerSetType(atype), PowerSetType(typeit(node.children[index+2], env, type_env)))
        return atype
    elif isinstance(node, AMultOrCartExpression):
        expr1_type = typeit(node.children[0], env, type_env)
        expr2_type = typeit(node.children[1], env, type_env)
        expr1_type = unknown_closure(expr1_type)
        expr2_type = unknown_closure(expr2_type)
        if isinstance(expr1_type, IntegerType) or isinstance(expr2_type, IntegerType):  # Integer-Mult
            # only unify if IntgerType
            unify_equal(expr1_type, expr2_type, type_env)
            return IntegerType(None)
        # else: expr1_type and expr2_type can be different
        elif isinstance(expr1_type, PowerSetType) and isinstance(expr2_type, UnknownType):  # CartExpression
            return PowerSetType(CartType(PowerSetType(expr1_type), PowerSetType(expr2_type)))
        elif isinstance(expr2_type, PowerSetType) and isinstance(expr1_type, UnknownType):  # CartExpression
            return PowerSetType(CartType(PowerSetType(expr1_type),PowerSetType( expr2_type)))
        elif isinstance(expr1_type, PowerSetType) and isinstance(expr2_type, PowerSetType): # CartExpression
            return PowerSetType(CartType(expr1_type, expr2_type))
        elif isinstance(expr1_type, UnknownType) and isinstance(expr2_type, UnknownType):  # Dont know
            return PowCartORIntegerType(expr1_type, expr2_type)
        else:
            raise Exception("Unimplemented case: %s %s", expr1_type, expr2_type)
    elif isinstance(node, APowSubsetExpression) or isinstance(node, APow1SubsetExpression):
        set_type = typeit(node.children[0], env, type_env)
        expected_type = PowerSetType(UnknownType("APowSubsetExpression",None))
        atype = unify_equal(set_type, expected_type, type_env)
        return PowerSetType(atype)
    elif isinstance(node, ACardExpression):
        atype = typeit(node.children[0], env, type_env) 
        expected_type = PowerSetType(UnknownType("ACardExpression",None))
        unify_equal(atype, expected_type, type_env)
        return IntegerType(None)
    elif isinstance(node, AGeneralUnionExpression) or isinstance(node, AGeneralIntersectionExpression):
        set_type = typeit(node.children[0], env, type_env)
        expected_type = PowerSetType(PowerSetType(UnknownType(None,None)))
        atype = unify_equal(set_type, expected_type,type_env)
        return atype.data
    elif isinstance(node, AQuantifiedIntersectionExpression) or isinstance(node, AQuantifiedUnionExpression):
        idNames = []
        for idNode in node.children[:node.idNum]:
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
    elif isinstance(node, ABelongPredicate):
        elm_type = typeit(node.children[0], env, type_env)
        set_type = typeit(node.children[1], env, type_env)
        unify_element_of(elm_type, set_type, type_env)
        #print elm_type, set_type, node.children[0].idName, node.children[1]
        if isinstance(elm_type, UnknownType) and isinstance(node.children[0], AIdentifierExpression) and isinstance(node.children[1], AIdentifierExpression):
            type_env.set_enumeration_hint(node.children[0].idName, node.children[1].idName)
        return BoolType()
    # TODO: notBelong
    elif isinstance(node, ANotBelongPredicate):
        elm_type = typeit(node.children[0], env, type_env)
        set_type = typeit(node.children[1], env, type_env)
        unify_element_of(elm_type, set_type, type_env)
        return BoolType()    
    elif isinstance(node, AIncludePredicate) or isinstance(node, ANotIncludePredicate) or isinstance(node, AIncludeStrictlyPredicate) or isinstance(node, ANotIncludeStrictlyPredicate):
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
    elif isinstance(node, AIntSetExpression) or isinstance(node, ANatSetExpression) or isinstance(node, ANat1SetExpression)  or isinstance(node, ANaturalSetExpression) or isinstance(node, ANatural1SetExpression) or isinstance(node, AIntegerSetExpression):
        return PowerSetType(IntegerType(None))
    elif isinstance(node, AIntervalExpression):
        int_type = typeit(node.children[0], env, type_env)
        unify_equal(int_type, IntegerType(None),type_env)
        int_type = typeit(node.children[1], env, type_env)
        unify_equal(int_type, IntegerType(None),type_env)
        return PowerSetType(IntegerType(None))
    elif isinstance(node, AIntegerExpression):
        return IntegerType(node.intValue)
    elif isinstance(node, AMinExpression) or isinstance(node, AMaxExpression):
        set_type = typeit(node.children[0], env, type_env)
        expected_type = PowerSetType(IntegerType(None))
        unify_equal(set_type, expected_type,type_env)
        return IntegerType(None)
    elif isinstance(node, AAddExpression) or isinstance(node, ADivExpression) or isinstance(node, AModuloExpression):
        expr1_type = typeit(node.children[0], env, type_env)
        expr2_type = typeit(node.children[1], env, type_env)
        unify_equal(expr1_type, IntegerType(None), type_env)
        unify_equal(expr2_type, IntegerType(None), type_env)
        return IntegerType(None)
    elif isinstance(node, AGeneralSumExpression) or isinstance(node, AGeneralProductExpression):
        ids = []
        for n in node.children[:-2]:
            assert isinstance(n.idName, str)
            ids.append(n.idName)
        type_env.push_frame(ids)
        for child in node.children:
            typeit(child, env, type_env)
        type_env.pop_frame(env)
        return IntegerType(None)


# ***************************
#
#       3.1 Number predicates
#
# ***************************
    elif isinstance(node, ALessEqualPredicate) or isinstance(node, ALessPredicate) or isinstance(node, AGreaterEqualPredicate) or isinstance(node, AGreaterPredicate):
        expr1_type = typeit(node.children[0], env, type_env)
        expr2_type = typeit(node.children[1], env, type_env)
        unify_equal(expr1_type, IntegerType(None), type_env)
        unify_equal(expr2_type, IntegerType(None), type_env)
        return BoolType()


# ******************
#
#       4. Relations
#
# ******************
    elif isinstance(node, ARelationsExpression):
        set_type0 = typeit(node.children[0], env, type_env)
        set_type1 = typeit(node.children[1], env, type_env)
        expected_type0 = PowerSetType(UnknownType("ARelationsExpression",None))
        expected_type1 = PowerSetType(UnknownType("ARelationsExpression",None))
        atype0 = unify_equal(set_type0, expected_type0, type_env)
        atype1 = unify_equal(set_type1, expected_type1, type_env)      
        return PowerSetType(PowerSetType(CartType(atype0, atype1)))
    elif isinstance(node, ADomainExpression):
        rel_type =  typeit(node.children[0], env, type_env)
        expected_type = PowerSetType(CartType(PowerSetType(UnknownType("ADomainExpression",None)), PowerSetType(UnknownType(None,None))))
        atype = unify_equal(rel_type, expected_type, type_env)
        return atype.data.data[0] # preimage settype
    elif isinstance(node, ARangeExpression):
        rel_type =  typeit(node.children[0], env, type_env)
        expected_type = PowerSetType(CartType(PowerSetType(UnknownType("ARangeExpression",None)), PowerSetType(UnknownType(None,None))))
        atype = unify_equal(rel_type, expected_type, type_env)
        return atype.data.data[1] # image settype            
    elif isinstance(node, ACompositionExpression):
        rel_type0 = typeit(node.children[0], env, type_env)
        rel_type1 = typeit(node.children[1], env, type_env)
        expected_type0 = PowerSetType(CartType(PowerSetType(UnknownType("ACompositionExpression",None)), PowerSetType(UnknownType(None,None))))
        expected_type1 = PowerSetType(CartType(PowerSetType(UnknownType("ACompositionExpression",None)), PowerSetType(UnknownType(None,None))))
        atype0 = unify_equal(rel_type0, expected_type0, type_env)
        atype1 = unify_equal(rel_type1, expected_type1, type_env)  
        preimagetype = atype0.data.data[0]
        imagetype = atype1.data.data[1]
        return PowerSetType(CartType(preimagetype, imagetype))
    elif isinstance(node, AIdentityExpression):
        set_type = typeit(node.children[0], env, type_env)
        for child in node.children[1:]:
            typeit(child, env, type_env)
        #use knowledge form args
        expected_type0 = PowerSetType(UnknownType("AIdentityExpression",None))
        atype = unify_equal(set_type, expected_type0, type_env)
        return PowerSetType(CartType(atype, atype))
    elif isinstance(node, AIterationExpression):
        rel_type = typeit(node.children[0], env, type_env)
        int_type = typeit(node.children[1], env, type_env)
        expected_type = PowerSetType(CartType(PowerSetType(UnknownType("AIterationExpression",None)),PowerSetType(UnknownType("AIterationExpression",None))))
        atype = unify_equal(rel_type, expected_type, type_env)
        unify_equal(int_type, IntegerType(None), type_env)
        return atype
    elif isinstance(node, AReflexiveClosureExpression) or isinstance(node, AClosureExpression):
        rel_type = typeit(node.children[0], env, type_env)
        expected_type = PowerSetType(CartType(PowerSetType(UnknownType("AReflexiveClosureExpression",None)),PowerSetType(UnknownType("AReflexiveClosureExpression",None))))
        atype = unify_equal(rel_type, expected_type, type_env)
        return atype
    elif isinstance(node, ADomainRestrictionExpression) or isinstance(node, ADomainSubtractionExpression):
        set_type = typeit(node.children[0], env, type_env)
        rel_type = typeit(node.children[1], env, type_env)
        expected_type0 = PowerSetType(UnknownType("ADomainRestrictionExpression",None))
        expected_type1 = PowerSetType(CartType(PowerSetType(UnknownType("ADomainRestrictionExpression",None)), PowerSetType(UnknownType("ADomainRestrictionExpression",None))))
        unify_equal(set_type, expected_type0, type_env)
        atype = unify_equal(rel_type, expected_type1, type_env)
        return atype
    elif isinstance(node, ARangeSubtractionExpression) or isinstance(node, ARangeRestrictionExpression):
        rel_type = typeit(node.children[0], env, type_env)
        set_type = typeit(node.children[1], env, type_env)
        expected_type0 = PowerSetType(UnknownType("ARangeSubtractionExpression",None))
        expected_type1 = PowerSetType(CartType(PowerSetType(UnknownType("ARangeSubtractionExpression",None)), PowerSetType(UnknownType("ARangeSubtractionExpression",None))))
        unify_equal(set_type, expected_type0, type_env)
        atype = unify_equal(rel_type, expected_type1, type_env)
        return atype
    elif isinstance(node, AReverseExpression):
        rel_type = typeit(node.children[0], env, type_env)
        expected_type = PowerSetType(CartType(PowerSetType(UnknownType("AReverseExpression",None)), PowerSetType(UnknownType("AReverseExpression",None))))
        atype = unify_equal(rel_type, expected_type, type_env)
        preimagetype = atype.data.data[0]
        imagetype = atype.data.data[1]
        return PowerSetType(CartType(imagetype, preimagetype))
    elif isinstance(node, AImageExpression):
        rel_type = typeit(node.children[0], env, type_env)
        for child in node.children[1:]:
            typeit(child, env, type_env)
        # TODO: use knowledge from args
        expected_type = PowerSetType(CartType(PowerSetType(UnknownType("AImageExpression",None)),PowerSetType(UnknownType("AImageExpression",None))))
        atype = unify_equal(rel_type, expected_type, type_env)
        return atype.data.data[1]
    elif isinstance(node, AOverwriteExpression):
        rel_type0 = typeit(node.children[0], env, type_env)
        rel_type1 = typeit(node.children[1], env, type_env)
        expected_type0 = PowerSetType(CartType(PowerSetType(UnknownType("AOverwriteExpression",None)),PowerSetType(UnknownType("AOverwriteExpression",None))))
        expected_type1 = PowerSetType(CartType(PowerSetType(UnknownType("AOverwriteExpression",None)),PowerSetType(UnknownType("AOverwriteExpression",None))))
        atype = unify_equal(rel_type0, expected_type0, type_env)
        unify_equal(rel_type1, expected_type1, type_env)
        return atype
    elif isinstance(node, AParallelProductExpression):
        rel_type0 = typeit(node.children[0], env, type_env)
        rel_type1 = typeit(node.children[1], env, type_env)
        expected_type0 = PowerSetType(CartType(PowerSetType(UnknownType("AParallelProductExpression",None)),PowerSetType(UnknownType("AParallelProductExpression",None))))
        expected_type1 = PowerSetType(CartType(PowerSetType(UnknownType("AParallelProductExpression",None)),PowerSetType(UnknownType("AParallelProductExpression",None))))
        atype0 = unify_equal(rel_type0, expected_type0, type_env)
        atype1 = unify_equal(rel_type1, expected_type1, type_env)
        x = atype0.data.data[0]
        m = atype0.data.data[1]
        y = atype1.data.data[0]
        n = atype1.data.data[1]
        return PowerSetType(CartType(PowerSetType(CartType(x,y)),PowerSetType(CartType(m,n))))
    elif isinstance(node, ADirectProductExpression):
        rel_type0 = typeit(node.children[0], env, type_env)
        rel_type1 = typeit(node.children[1], env, type_env)
        expected_type0 = PowerSetType(CartType(PowerSetType(UnknownType("ADirectProductExpression",None)),PowerSetType(UnknownType("ADirectProductExpression",None))))
        expected_type1 = PowerSetType(CartType(PowerSetType(UnknownType("ADirectProductExpression",None)),PowerSetType(UnknownType("ADirectProductExpression",None))))
        atype0 = unify_equal(rel_type0, expected_type0, type_env)
        atype1 = unify_equal(rel_type1, expected_type1, type_env)
        x = atype0.data.data[0]
        y = atype0.data.data[1]
        x2 = atype1.data.data[0]
        z = atype1.data.data[1]
        assert x.__class__ == x2.__class__
        return PowerSetType(CartType(x,PowerSetType(CartType(y,z))))
    elif isinstance(node, AFirstProjectionExpression):
        set_type0 = typeit(node.children[0], env, type_env)
        set_type1 = typeit(node.children[1], env, type_env)
        expected_type0 = PowerSetType(UnknownType("AFirstProjectionExpression",None))
        expected_type1 = PowerSetType(UnknownType("AFirstProjectionExpression",None))
        atype0 = unify_equal(set_type0, expected_type0, type_env)
        atype1 = unify_equal(set_type1, expected_type1, type_env)
        return PowerSetType(CartType(PowerSetType(CartType(atype0,atype1)), atype0))
    elif isinstance(node, ASecondProjectionExpression):
        set_type0 = typeit(node.children[0], env, type_env)
        set_type1 = typeit(node.children[1], env, type_env)
        expected_type0 = PowerSetType(UnknownType("ASecondProjectionExpression",None))
        expected_type1 = PowerSetType(UnknownType("ASecondProjectionExpression",None))
        atype0 = unify_equal(set_type0, expected_type0, type_env)
        atype1 = unify_equal(set_type1, expected_type1, type_env)
        return PowerSetType(CartType(PowerSetType(CartType(atype0, atype1)), atype1))


# *******************
#
#       4.1 Functions
#
# *******************
    elif isinstance(node, APartialFunctionExpression) or isinstance(node, ATotalFunctionExpression) or isinstance(node, APartialInjectionExpression) or isinstance(node, ATotalInjectionExpression) or isinstance(node, APartialSurjectionExpression) or isinstance(node, ATotalSurjectionExpression) or  isinstance(node, ATotalBijectionExpression) or isinstance(node, APartialBijectionExpression):
        set_type0 = typeit(node.children[0], env, type_env)
        set_type1 = typeit(node.children[1], env, type_env)
        expected_type0 = PowerSetType(UnknownType("APartialFunctionExpression",None))
        expected_type1 = PowerSetType(UnknownType("APartialFunctionExpression",None))
        atype0 = unify_equal(set_type0, expected_type0, type_env)
        atype1 = unify_equal(set_type1, expected_type1, type_env)
        return PowerSetType(PowerSetType(CartType(atype0, atype1)))
    elif isinstance(node, AFunctionExpression):
        type0 = typeit(node.children[0], env, type_env) 
        #print "enter"
        #print_ast(node)
        #__print__btype(type0)
        if isinstance(type0, IntegerType): # special case (succ/pred)
            assert isinstance(node.children[0], APredecessorExpression) or isinstance(node.children[0], ASuccessorExpression)
            return type0
        
        num_args = len(node.children[1:])
        if num_args==1:
            expected_type0 = PowerSetType(CartType(PowerSetType(UnknownType("AFunctionExpression",None)),PowerSetType(UnknownType("AFunctionExpression",None))))
        else:
            arg_type = create_func_arg_type(num_args)
            expected_type0 = PowerSetType(CartType(arg_type,PowerSetType(UnknownType("AFunctionExpression",None))))
        atype = unify_equal(type0, expected_type0, type_env) 
           
        # type args
        arg_type_list = get_arg_type_list(atype.data.data[0])
        arg_type_list2 = []
        for i in range(len(node.children[1:])):
            child = node.children[i+1]
            arg_type = typeit(child, env, type_env)
            # e.g f(x|->y) instead of (expected) f(x,y). 
            # This problem can be indirect! So only checking for the type is correct
            if isinstance(arg_type, CartType): 
                arg_type_list2.append(arg_type.data[0].data)
                arg_type_list2.append(arg_type.data[1].data)
            else: 
                arg_type_list2.append(arg_type)
        for i in range(len(arg_type_list2)): 
            arg_type = arg_type_list2[i]
            unify_equal(arg_type, arg_type_list[i], type_env)
        
        # return imagetype
        return atype.data.data[1].data
    elif isinstance(node, ALambdaExpression):
        # TODO: unification 
        ids = []
        for n in node.children[:-2]:
            assert isinstance(n.idName, str)
            ids.append(n.idName)
        type_env.push_frame(ids)
        for child in node.children[:-1]:
            typeit(child, env, type_env)
        pre_img_type = typeit(node.children[0], env, type_env)
        if len(node.children[:-2])>1: #more than one arg
            for n in node.children[1:-2]:
                atype = typeit(n, env, type_env)
                pre_img_type = CartType(PowerSetType(pre_img_type), PowerSetType(atype))
        img_type = typeit(node.children[-1], env, type_env)
        type_env.pop_frame(env)
        #print "DEBUG:",pre_img_type,img_type
        return PowerSetType(CartType(PowerSetType(pre_img_type), PowerSetType(img_type)))


# ********************
#
#       4.2 Sequences
#
# ********************
    elif isinstance(node,AEmptySequenceExpression):
        return PowerSetType(CartType(PowerSetType(IntegerType(None)),PowerSetType(UnknownType("AEmptySequenceExpression",None))))
    elif isinstance(node,ASeqExpression) or isinstance(node,ASeq1Expression) or isinstance(node,AIseqExpression) or isinstance(node,APermExpression) or isinstance(node, AIseq1Expression):
        set_type = typeit(node.children[0], env, type_env)
        expected_type = PowerSetType(UnknownType("ASeqExpression",None))
        atype = unify_equal(set_type, expected_type, type_env)
        return PowerSetType(PowerSetType(CartType(PowerSetType(IntegerType(None)), atype)))
    elif isinstance(node, AGeneralConcatExpression):
        seq_seq_type = typeit(node.children[0], env, type_env)
        #__print__btype(seq_seq_type)
        expected_seq_type = PowerSetType(CartType(PowerSetType(IntegerType(None)),PowerSetType(UnknownType("AGeneralConcatExpression",None))))
        expected_type = PowerSetType(CartType(PowerSetType(IntegerType(None)), PowerSetType(expected_seq_type)))
        atype = unify_equal(seq_seq_type, expected_type, type_env)
        image_type = atype.data.data[1].data.data.data[1]
        return PowerSetType(CartType(PowerSetType(IntegerType(None)), image_type))
    elif isinstance(node, AConcatExpression):
        seq_type0 = typeit(node.children[0], env, type_env)
        seq_type1 = typeit(node.children[1], env, type_env)
        expected_type0 = PowerSetType(CartType(PowerSetType(IntegerType(None)),PowerSetType(UnknownType("AConcatExpression",None))))
        expected_type1 = PowerSetType(CartType(PowerSetType(IntegerType(None)),PowerSetType(UnknownType("AConcatExpression",None))))
        atype0 = unify_equal(seq_type0, expected_type0, type_env)
        atype1 = unify_equal(seq_type1, expected_type1, type_env)
        image_type = unify_equal(atype0.data.data[1].data ,atype1.data.data[1].data, type_env)
        return PowerSetType(CartType(PowerSetType(IntegerType(None)),PowerSetType(image_type)))
    elif isinstance(node, AInsertFrontExpression):
        set_type = typeit(node.children[0], env, type_env)
        seq_type = typeit(node.children[1], env, type_env)
        img_type = UnknownType("AInsertFrontExpression",None)
        expected_type1 = PowerSetType(CartType(PowerSetType(IntegerType(None)),PowerSetType(img_type)))
        atype0 = unify_equal(set_type, img_type, type_env)
        atype1 = unify_equal(seq_type, expected_type1, type_env)
        if isinstance(atype0, SetType):
            assert atype0.data == atype1.data.data[1].data.data # Setname
        return atype1
    elif isinstance(node, AInsertTailExpression):
        seq_type = typeit(node.children[0], env, type_env)
        set_type = typeit(node.children[1], env, type_env)
        img_type = UnknownType("AInsertTailExpression",None)
        expected_type0 = PowerSetType(CartType(PowerSetType(IntegerType(None)),PowerSetType(img_type)))
        atype0 = unify_equal(seq_type, expected_type0, type_env)
        atype1 = unify_equal(set_type, img_type, type_env)
        if isinstance(atype1, SetType):
            assert atype1.data == atype0.data.data[1].data.data # Setname
        return atype0
    elif isinstance(node, ASequenceExtensionExpression):
        # Todo: s=[]
        reftype = typeit(node.children[0], env, type_env) 
        for n in node.children[1:]:
            atype = typeit(n, env, type_env)
            unify_equal(atype, reftype, type_env)
        return PowerSetType(CartType(PowerSetType(IntegerType(None)), PowerSetType(reftype)))
    elif isinstance(node, ASizeExpression):
        type0 = typeit(node.children[0], env, type_env)
        expected_type0 = PowerSetType(CartType(PowerSetType(IntegerType(None)),PowerSetType(UnknownType("ASizeExpression",None))))
        unify_equal(type0, expected_type0, type_env)
        return IntegerType(None)
    elif isinstance(node, ARevExpression):
        seq_type = typeit(node.children[0], env, type_env)
        expected_type0 = PowerSetType(CartType(PowerSetType(IntegerType(None)),PowerSetType(UnknownType("ARevExpression",None))))
        atype = unify_equal(seq_type, expected_type0, type_env)
        return atype
    elif isinstance(node, ARestrictFrontExpression) or isinstance(node, ARestrictTailExpression):
        seq_type = typeit(node.children[0], env, type_env)
        int_type = typeit(node.children[1], env, type_env)
        expected_type0 = PowerSetType(CartType(PowerSetType(IntegerType(None)),PowerSetType(UnknownType("ARestrictFrontExpression",None))))
        expected_type1 = IntegerType(None)
        atype = unify_equal(seq_type, expected_type0, type_env)
        unify_equal(int_type, expected_type1, type_env)
        return atype
    elif isinstance(node, AFirstExpression) or isinstance(node, ALastExpression):
        seq_type = typeit(node.children[0], env, type_env)
        expected_type = PowerSetType(CartType(PowerSetType(IntegerType(None)),PowerSetType(UnknownType("AFirstExpression",None))))
        atype = unify_equal(seq_type, expected_type, type_env)
        return atype.data.data[1].data
    elif isinstance(node, ATailExpression) or isinstance(node, AFrontExpression):
        seq_type = typeit(node.children[0], env, type_env)
        expected_type = PowerSetType(CartType(PowerSetType(IntegerType(None)),PowerSetType(UnknownType("ATailExpression",None))))
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
                atype2 = PowerSetType(CartType(PowerSetType(UnknownType("AAssignSubstitution",None)), PowerSetType(atype0)))
                unify_equal(func_type, atype2, type_env)
    elif isinstance(node, AConvertBoolExpression):
        atype = typeit(node.children[0], env, type_env)
        unify_equal(atype, BoolType(), type_env)
        return BoolType()
    elif isinstance(node, ABecomesElementOfSubstitution):
        atype = typeit(node.children[-1], env, type_env)
        for child in node.children[:-1]:
            idtype = typeit(child, env, type_env)
            unify_element_of(idtype, atype, type_env)
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
        for idNode in node.children[:node.idNum]:
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
    elif isinstance(node, ATrueExpression) or isinstance(node,AFalseExpression):
        return BoolType()
    elif isinstance(node, APrimedIdentifierExpression):
        assert len(node.children)==1 # TODO: x.y.z + unify
        return typeit(node.children[0], env, type_env)
    elif isinstance(node, AIdentifierExpression):
        type_env.add_node_by_id(node)
        idtype = type_env.get_current_type(node.idName)
        #print node.idName, node, idtype
        return idtype
    elif isinstance(node, AMinIntExpression) or isinstance(node, AMaxIntExpression) or isinstance(node, ASuccessorExpression) or isinstance(node, APredecessorExpression) or isinstance(node, APowerOfExpression):
        return IntegerType(None)
    elif isinstance(node, AStructExpression):
        dictionary = {}
        for rec_entry in node.children:
            assert isinstance(rec_entry, ARecEntry)
            name = ""
            if isinstance(rec_entry.children[0], AIdentifierExpression):
                name = rec_entry.children[0].idName
            assert isinstance(rec_entry.children[-1], Expression)
            atype = typeit(rec_entry.children[-1], env, type_env)
            dictionary[name] = atype.data # remove powerset
        return PowerSetType(StructType(dictionary))
    elif isinstance(node, ARecExpression):
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
        atype = typeit(node.children[0], env, type_env)
        assert isinstance(atype, StructType)
        assert isinstance(node.children[1], AIdentifierExpression)
        entry_type = atype.data[node.children[1].idName]
        # TODO: unify
        return entry_type
    elif isinstance(node, ATransRelationExpression):
        func_type = typeit(node.children[0], env, type_env)
        range_type = UnknownType("ATransRelationExpression",None)
        image_type = UnknownType("ATransRelationExpression",None)
        expected_type = PowerSetType(CartType(PowerSetType(range_type), PowerSetType(PowerSetType(image_type))))
        atype = unify_equal(func_type, expected_type, type_env)
        range_type = atype.data.data[0]
        image_type = atype.data.data[1].data
        return PowerSetType(CartType(range_type, image_type))
    elif isinstance(node, ATransFunctionExpression):
        rel_type = typeit(node.children[0], env, type_env)
        range_type = UnknownType("ATransFunctionExpression",None)
        image_type = UnknownType("ATransFunctionExpression",None)
        expected_type = PowerSetType(CartType(PowerSetType(range_type), PowerSetType(image_type)))
        atype = unify_equal(rel_type, expected_type, type_env)
        range_type = atype.data.data[0]
        image_type = atype.data.data[1]
        return PowerSetType(CartType(range_type, PowerSetType(image_type)))
    elif isinstance(node, AUnaryExpression):
        atype = typeit(node.children[0], env, type_env)
        atype = unify_equal(IntegerType(None), atype, type_env)
        return IntegerType(None)
    elif isinstance(node, AOperation):
        #print node.opName
        names = []
        for i in range(0,node.return_Num+ node.parameter_Num):
            assert isinstance(node.children[i], AIdentifierExpression)
            names.append(node.children[i].idName)
        type_env.push_frame(names)
        for child in node.children:
            typeit(child, env, type_env)
        ret_types = []
        for child in node.children[0:node.return_Num]:
            assert isinstance(child, AIdentifierExpression)
            atype = type_env.get_current_type(child.idName)
            assert not isinstance(atype, UnknownType)
            ret_types.append(tuple([child, atype]))
        para_types = []
        for child in node.children[node.return_Num:(node.return_Num+node.parameter_Num)]:
            assert isinstance(child, AIdentifierExpression)
            atype = type_env.get_current_type(child.idName)
            assert not isinstance(atype, UnknownType)
            para_types.append(tuple([child, atype]))
        # Add query-operation test and add result to list
        is_query_op = check_if_query_op(node.children[-1], env.current_mch.var_names)
        #print "DEBUG:",env.current_mch.name, ":",node.opName, ":", is_query_op       
        # FIXME: adding the node is not a task of type_checking 
        # TODO: delete when refactoring done
        operation_info = {}
        operation_info["return_types"]    = ret_types
        operation_info["parameter_types"] = para_types
        operation_info["op_name"]         = node.opName
        operation_info["ast"]             = node
        operation_info["owner_machine"]   = env.current_mch
        operation_info["is_query_op"]     = is_query_op
        env.mch_operation_type.append(operation_info)
        boperation= BOperation()
        boperation.return_types    = ret_types
        boperation.parameter_types = para_types
        boperation.op_name         = node.opName
        boperation.ast             = node
        boperation.owner_machine   = env.current_mch
        boperation.is_query_op     = is_query_op      
        env.current_mch.operations = env.current_mch.operations.union(frozenset([boperation]))
        type_env.pop_frame(env)
    elif isinstance(node, AOpSubstitution):
        op_info = env.current_mch.get_includes_op_type(node.idName)
        para_types = op_info["parameter_types"]
        assert len(para_types)==node.parameter_Num
        for i in range(len(node.children)):
            atype = typeit(node.children[i], env, type_env)
            p_type = para_types[i][1]
            unify_equal(p_type, atype, type_env)
        ret_type =  op_info["return_types"]
        assert ret_type==[]
        return
    elif isinstance(node, AOpWithReturnSubstitution):
        op_info = env.current_mch.get_includes_op_type(node.idName)
        ret_types =  op_info["return_types"]
        para_types = op_info["parameter_types"]
        assert len(para_types)==node.parameter_Num
        assert len(ret_types)==node.return_Num
        for i in range(node.return_Num, (node.return_Num+node.parameter_Num)):
            atype = typeit(node.children[i], env, type_env)
            p_type = para_types[i-node.return_Num][1]
            unify_equal(p_type, atype, type_env)
        assert not ret_types==[]
        for i in range(0, node.return_Num):
            atype = typeit(node.children[i], env, type_env)
            r_type = ret_types[i][1]
            unify_equal(p_type, atype, type_env)
        return 
    elif isinstance(node, AExternalFunctionExpression):
        return node.pyb_type
    else:
        # WARNING: Make sure that is only used when no typeinfo is needed
        #print "WARNING: unhandeld node:", node
        for child in node.children:
            typeit(child, env, type_env)





# This function exist to handle preds like "x=y & y=1" and find the
# type of x and y after one run.
# UnknownTypes in a typetree will be set in the basecase of the recursion
# AFTER this (in the returning phase of the recursion) it uses the subtypetree which 
# has the same or more informations
# TODO: This function is not full implemented!
def unify_equal(maybe_type0, maybe_type1, type_env):
    assert isinstance(type_env, TypeCheck_Environment)
    #import inspect
    #print inspect.stack()[1] 
    #print "type 1/2",maybe_type0,maybe_type1
    maybe_type0 = unknown_closure(maybe_type0)
    maybe_type1 = unknown_closure(maybe_type1)
    if maybe_type0==maybe_type1:
        return maybe_type0

    # case 1: BType, BType
    if isinstance(maybe_type0, BType) and isinstance(maybe_type1, BType):
        #if isinstance(maybe_type0, PowerSetType) and isinstance(maybe_type1, EmptySetType):
        #    return maybe_type0
        #elif isinstance(maybe_type1, PowerSetType) and isinstance(maybe_type0, EmptySetType):
        #    return maybe_type1
        if maybe_type0.__class__ == maybe_type1.__class__:
            # recursive unification-call
            # if not IntegerType, SetType or UnkownType.
            if isinstance(maybe_type0, PowerSetType):
                atype = unify_equal(maybe_type0.data, maybe_type1.data, type_env)
                maybe_type0.data = atype
            elif isinstance(maybe_type0, StructType):
                dictionary0 = maybe_type0.data
                dictionary1 = maybe_type1.data
                assert isinstance(dictionary0, dict)
                assert isinstance(dictionary1, dict)
                lst0 = list(dictionary0.values())
                lst1 = list(dictionary1.values())
                assert len(lst0)==len(lst1)
                for index in range(len(lst0)):
                    unify_equal(lst0[index], lst1[index], type_env)
            elif isinstance(maybe_type0, CartType):
                t00 = unknown_closure(maybe_type0.data[0])
                t10 = unknown_closure(maybe_type1.data[0])
                t01 = unknown_closure(maybe_type0.data[1])
                t11 = unknown_closure(maybe_type1.data[1])
                assert isinstance(t00, PowerSetType)
                assert isinstance(t10, PowerSetType)
                assert isinstance(t01, PowerSetType)
                assert isinstance(t11, PowerSetType)
                # (2) unify
                atype = unify_equal(t00.data, t10.data, type_env)
                maybe_type0.data[0].data = atype
                atype = unify_equal(t01.data, t11.data, type_env)
                maybe_type0.data[1].data = atype
            elif isinstance(maybe_type0, SetType):
                # learn/set name
                if maybe_type0.data==None:
                    maybe_type0.data = maybe_type1.data
                elif maybe_type1.data==None:
                    maybe_type1.data = maybe_type0.data
                else:
                    assert maybe_type1.data == maybe_type0.data
            else:
                assert isinstance(maybe_type0, IntegerType) or isinstance(maybe_type0, BoolType) or isinstance(maybe_type0, StringType)
            return maybe_type0
        else:
            string = "TypeError: Not unifiable: %s %s", maybe_type0, maybe_type1
            print string
            raise BTypeException(string)

    # case 2: Unknown, Unknown
    elif isinstance(maybe_type0, UnknownType) and isinstance(maybe_type1, UnknownType):
        return type_env.set_unknown_type(maybe_type0, maybe_type1)

    # case 3: Unknown, BType
    elif isinstance(maybe_type0, UnknownType) and isinstance(maybe_type1, BType):
        return type_env.set_concrete_type(maybe_type0, maybe_type1)

    # case 4: BType, Unknown
    elif isinstance(maybe_type0, BType) and isinstance(maybe_type1, UnknownType):
        return type_env.set_concrete_type(maybe_type1, maybe_type0)
    else:
        # no UnknownType and no BType:
        # If this is ever been raised than this is a bug
        # inside the typechecker: Every unifiable expression
        # must be a BType or an UnknownType!
        print maybe_type0, maybe_type1
        raise Exception("Typchecker Bug: no Unknowntype and no Btype!")



# called by (and only by) the Belong-Node
# calls the unify_equal method with correct args
def unify_element_of(elm_type, set_type, type_env):
    # (1) type already known?
    set_type = unknown_closure(set_type)
    elm_type = unknown_closure(elm_type)
    assert not set_type == None

    # (2) unify
    if isinstance(elm_type, UnknownType):
        if isinstance(set_type, PowerSetType):
            # map elm_type (UnknownType) to set_type for all elm_type
            unify_equal(elm_type, set_type.data, type_env)
        elif isinstance(set_type, UnknownType):
            assert set_type.real_type == None
            unify_equal(set_type, PowerSetType(elm_type), type_env)
        #TODO: add Type-exceptions: e.g. x:POW(42)
        else:
            # no UnknownType and no PowersetType:
            # If this is ever been raised than this is a bug 
            # inside the typechecker. In B the right side S of
            # a Belong-expression (x:S) must be of PowerSetType!
            raise Exception("Typchecker Bug(?): no UnknownType and no PowersetType")
        return
    elif isinstance(elm_type, BType):
        unify_equal(PowerSetType(elm_type), set_type, type_env)
        return
    else:
        # no Unknowntype and no Btype:
        # If this is ever been raised than this is a bug
        # inside the typechecker: Every unifiable expression
        # must be a BType or an UnknownType!
        raise Exception("Typchecker Bug: no Unknowntype and no Btype!")