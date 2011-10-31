# -*- coding: utf-8 -*-
from ast_nodes import *


class BType: # Baseclass used to repr. concrete type
    pass


class IntegerType(BType):
    def __init__(self, number_or_None):
        # maybe this data is useless for typechecking
        self.data = number_or_None 


class PowerSetType(BType):
    def __init__(self, aset_type):
        self.data = aset_type


class SetType(BType):
    def __init__(self, name):
        self.data = name # None when name unknown


class CartType(BType):
    def __init__(self, setA, setB):
        self.data = (setA, setB)


class UnknownType(): # no BType: used later to throw Exceptions
    # the arg real_type is only set by tests!
    def __init__(self, name, real_type):
        # this member is used to learn the name of sets
        self.name = name
        # if this is still None after typechecking 
        # than a Typeerror has been found
        self.real_type = real_type


# Helper env: will be thrown away after Typechecking
class TypeCheck_Environment():
    def __init__(self):
        # is used to construct the env.node_to_type_map
        self.id_to_nodes_stack = []
        self.id_to_types_stack = []


    # new scope
    def push_frame(self, id_Names):
        id_to_nodes_map = {} # A: str->NODE
        id_to_types_map = {} # T: str->Type
        for id_Name in id_Names:
            id_to_nodes_map[id_Name] = [] # no Nodes at the moment
            id_to_types_map[id_Name] = UnknownType(id_Name, None)
        self.id_to_nodes_stack.append(id_to_nodes_map)
        self.id_to_types_stack.append(id_to_types_map)


    def add_node_by_id(self, node):
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
        print "TYPEERROR!" # TODO: something more pretty
        raise KeyError


    def set_unknown_type(self, id0_Name, id1_Name):
        assert isinstance(id0_Name, UnknownType)
        assert isinstance(id1_Name, UnknownType)
        id0_Name.real_type = id1_Name
        return id1_Name


    def set_concrete_type(self, utype, ctype):
        assert isinstance(utype, UnknownType)
        assert isinstance(ctype, BType)
        utype.real_type = ctype
        return ctype


    # copies to env.node_to_type_map
    def pop_frame(self, env):
        node_top_map = self.id_to_nodes_stack[-1]
        type_top_map = self.id_to_types_stack[-1]
        self.id_to_nodes_stack.pop()
        self.id_to_types_stack.pop()
        #assert isinstance(env, Environment)
        for idName in type_top_map:
            atype = type_top_map[idName]
            # follow pointers. until none or Btype
            # FIXME: there are cases when this is wrong!
            # e.g. "#x.(x:S=>x>=0)".. (*pop*).. "& S=NAT"
            while not isinstance(atype.real_type, BType):
                if atype==None:
                    # TODO: maybe something more pretty
                    print "TYPEERROR: %s",idName
                    raise Exception()
                atype = atype.real_type
            node_lst = node_top_map[idName]
            for node in node_lst:
                env.node_to_type_map[node] = atype.real_type


    # returns BType or String
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
        # TODO: something more pretty
        print "TYPEERROR! unkown var: ",idName
        raise KeyError


# env.node_to_type_map should be a set of tree with 
# Nodes as leafs and Btypes as roots. 
# This method should throw away all unknowntypes 
# by walking from the leafs to the roots.
# If this is not possible the typechecking has failed
def resolve_type(env):
    for node in env.node_to_type_map:
        tree = env.node_to_type_map[node]
        tree_without_unknown = throw_away_unknown(tree)
        env.node_to_type_map[node] = tree_without_unknown


# TODO: at this moment this is not a tree.
# it is a list an becomes a tree when carttype is implemented
# It uses the data attr of BTypes as pointers
def throw_away_unknown(tree):
    if isinstance(tree, SetType) or isinstance(tree, IntegerType):
        return tree
    elif isinstance(tree, PowerSetType):
        if isinstance(tree.data, UnknownType):
            last_unknown = unknown_closure(tree.data)
            tree.data = last_unknown.real_type
        throw_away_unknown(tree.data)
        return tree
    elif isinstance(tree, CartType): #TODO: implement me
        return tree
    elif tree==None:
        raise Exception("TYPEERROR in resolve")
    else:
        raise Exception("resolve fail: Not Implemented %s",tree)


# follows an UnknownType pointer chain:
# returns an UnknownType which points to a BType or None
# None: learn typinformation
# BType: unificationcheck
# WARNING: assumes cyclic - free
def unknown_closure(atype):
    if not isinstance(atype, UnknownType):
        return atype
    while True:
        if not isinstance(atype.real_type, UnknownType):
            break
        atype = atype.real_type
    assert isinstance(atype.real_type, BType) or atype.real_type==None
    return atype


# should only be called by tests
def _test_typeit(root, env, known_types_list, idNames):
    type_env = TypeCheck_Environment()
    type_map = {}
    node_map = {}
    for atuple in known_types_list:
        id_Name = atuple[0]
        atype = atuple[1]
        type_map[id_Name] = UnknownType(id_Name, atype)
        node_map[id_Name] = []
    type_env.id_to_types_stack = [type_map] # this is a implicit push
    type_env.id_to_nodes_stack = [node_map]
    type_env.push_frame(idNames)
    typeit(root, env, type_env)
    type_env.pop_frame(env)
    type_env.pop_frame(env)
    resolve_type(env) # throw away unknown types



# returns BType/UnonwType or None(for expr which need no type. e.g. x=y)
# sideeffect: changes env
# type_env is a working env to type vars with
# different scops but (maybe) the same names
# e.g. !x.(x:S =>...) & x:Nat ...
def typeit(node, env, type_env):
    if isinstance(node, ANatSetExpression):
        return PowerSetType(IntegerType(None))
    elif isinstance(node, ANat1SetExpression):
        return PowerSetType(IntegerType(None))
    elif isinstance(node, AIntervalExpression):
        return PowerSetType(IntegerType(None))
    elif isinstance(node, AEmptySetExpression):
        return PowerSetType(SetType(None))
    elif isinstance(node, ACoupleExpression):
        return SetType(None)
    elif isinstance(node, AComprehensionSetExpression):
        ids = []
        for n in node.children[:-1]:
            assert isinstance(n.idName, str)
            ids.append(n.idName)
        type_env.push_frame(ids)
        for child in node.children:
            atype = typeit(child, env, type_env)
            #TODO: learn that all Elements must have the same type!
        # assert that all IDs are known (not None)
        for child in node.children[:-1]:
            assert isinstance(child, AIdentifierExpression)
            assert not type_env.get_current_type(child.idName)==None
        type_env.pop_frame(env)
        return PowerSetType(SetType(None)) #name unknown
    elif isinstance(node, AIntegerExpression):
        return IntegerType(node.intValue)
    elif isinstance(node, AIdentifierExpression):
        type_env.add_node_by_id(node)
        idtype = type_env.get_current_type(node.idName)
        return idtype
    elif isinstance(node, ASetExtensionExpression):
        for child in node.children:
            typeit(child, env,type_env)
        # Add a set with an unknown name.
        # This Name can only be found by the unify_equal-method
        # or an equal/notequals node
        return PowerSetType(SetType(None)) 
    elif isinstance(node, ABelongPredicate):
        elm_type = typeit(node.children[0], env, type_env)
        set_type = typeit(node.children[1], env, type_env)
        unify_element_of(elm_type, set_type, type_env)
        return
    elif isinstance(node, AEqualPredicate) or  isinstance(node,AUnequalPredicate):
        expr1_type = typeit(node.children[0], env,type_env)
        expr2_type = typeit(node.children[1], env,type_env)
        if isinstance(expr1_type, UnknownType) and not expr2_type == None:
            # the string maybe a unknown-type of an expression:
            # e.g. X /= U\/T with U and T unknown at this time
            if isinstance(expr2_type, PowerSetType) and  isinstance(expr2_type.data, SetType) and expr2_type.data.data == None:
                expr2_type.data.data = expr1_type.name # learn/set name
            unify_equal(expr1_type, expr2_type, type_env)
        elif isinstance(expr2_type, UnknownType) and not expr1_type == None:
            # the string maybe a unknown-type of an expression:
            # e.g. X = U\/T with U and T unknown at this time
            if isinstance(expr1_type, PowerSetType) and  isinstance(expr1_type.data, SetType) and expr1_type.data.data == None: # TODO: think about that...
                expr1_type.data.data = expr2_type.name # learn/set name
            unify_equal(expr2_type, expr1_type, type_env)
        else:
            unify_equal(expr1_type, expr2_type, type_env)
        return None
    elif isinstance(node, AUnionExpression) or isinstance(node, AIntersectionExpression):
        asettype0 = typeit(node.children[0], env, type_env)
        asettype1 = typeit(node.children[1], env, type_env)
        if isinstance(asettype0, UnknownType):
            return unify_equal(asettype0, asettype1, type_env) 
        elif isinstance(asettype1, UnknownType):
            return unify_equal(asettype1, asettype0, type_env)
        else:
            # Both sides are concrete types
            # FIXME: only works in sp. cases
            assert asettype1.data.data == asettype0.data.data # same name
            assert asettype1.__class__ == asettype0.__class__
            return asettype0
    elif isinstance(node, AIncludePredicate) or isinstance(node, ANotIncludePredicate) or isinstance(node, AIncludeStrictlyPredicate) or isinstance(node, ANotIncludeStrictlyPredicate):
        asettype0 = typeit(node.children[0], env, type_env)
        asettype1 = typeit(node.children[1], env, type_env)
        if isinstance(asettype0, UnknownType) and not asettype1 == None:
            unify_equal(asettype0, asettype1, type_env)
        elif isinstance(asettype1, UnknownType) and not asettype0 == None:
            unify_equal(asettype1, asettype0, type_env)
        else:
            # TODO: Add case: both unknown-> call unify_equal
            assert asettype1.__class__ == asettype0.__class__
    elif isinstance(node, AAddExpression) or isinstance(node, ADivExpression) or isinstance(node, AModuloExpression):
        expr1_type = typeit(node.children[0], env, type_env)
        expr2_type = typeit(node.children[1], env, type_env)
        # TODO: Add case: both unknown type -> call unify_equal
        assert isinstance(expr1_type, IntegerType)
        assert isinstance(expr2_type, IntegerType)
        return IntegerType(None)
    elif isinstance(node, ALessEqualPredicate) or isinstance(node, ALessPredicate) or isinstance(node, AGreaterEqualPredicate) or isinstance(node, AGreaterPredicate):
        expr1_type = typeit(node.children[0], env, type_env)
        expr2_type = typeit(node.children[1], env, type_env)
        if isinstance(expr1_type, UnknownType) and not expr2_type == None:
            assert isinstance(node.children[0], AIdentifierExpression)
            unify_equal(expr1_type, expr2_type, type_env)
        elif isinstance(expr2_type, UnknownType) and not expr1_type == None:
            assert isinstance(node.children[1], AIdentifierExpression)
            unify_equal(expr2_type, expr1_type, type_env)
        else:
            # TODO: Add case: both unknown type -> call unify_equal
            assert isinstance(expr1_type, IntegerType)
            assert isinstance(expr2_type, IntegerType)
        return None
    elif isinstance(node, AMinusOrSetSubtractExpression):
        expr1_type = typeit(node.children[0], env, type_env)
        expr2_type = typeit(node.children[1], env, type_env)
        if isinstance(expr1_type, IntegerType) and isinstance(expr2_type, IntegerType): # Minus
            return IntegerType(None)
        elif isinstance(expr1_type, PowerSetType) and isinstance(expr2_type, PowerSetType):
            assert expr1_type.data.data== expr2_type.data.data # same name
            return expr1_type
        else:
            # TODO: add-case: unknown type
            raise Exception("Unimplemented case: no sets and no ints!")
    elif isinstance(node, AMultOrCartExpression):
        expr1_type = typeit(node.children[0], env, type_env)
        expr2_type = typeit(node.children[1], env, type_env)
        if isinstance(expr1_type, IntegerType) and isinstance(expr2_type, IntegerType): # Mul
            return IntegerType(None)
        elif isinstance(expr1_type, PowerSetType) and  isinstance(expr2_type, PowerSetType):
            return PowerSetType(CartType(expr1_type.data, expr2_type.data))
        else:
            # TODO: add-case: unknown type
            raise Exception("Unimplemented case: %s",node)
    elif isinstance(node, AUniversalQuantificationPredicate) or isinstance(node, AExistentialQuantificationPredicate):
        ids = []
        for n in node.children[:-1]:
            assert isinstance(n.idName, str)
            ids.append(n.idName)
        type_env.push_frame(ids)
        for child in node.children:
            typeit(child, env, type_env)
        type_env.pop_frame(env)
        return
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
    elif isinstance(node, ACardExpression):
        typeit(node.children[0], env, type_env)
        return IntegerType(None)
    elif isinstance(node, APowSubsetExpression) or isinstance(node, APow1SubsetExpression):
        atype = typeit(node.children[0], env, type_env)
        # TODO: atype must be PowersetType of something. This info is not used
        #assert isinstance(atype, PowerSetType)
        return PowerSetType(atype)
    elif isinstance(node, ARelationsExpression):
        atype0 = typeit(node.children[0], env, type_env)
        atype1 = typeit(node.children[1], env, type_env)
        return PowerSetType(PowerSetType(CartType(atype0.data, atype1.data)))
    elif isinstance(node, ADomainExpression):
        rel_type =  typeit(node.children[0], env, type_env)
        assert isinstance(rel_type.data, CartType)
        return PowerSetType(rel_type.data.data[0]) # pow of preimage settype
    elif isinstance(node, ARangeExpression):
        rel_type =  typeit(node.children[0], env, type_env)
        assert isinstance(rel_type.data, CartType)
        return PowerSetType(rel_type.data.data[1]) # pow of image settype
    elif isinstance(node, ACompositionExpression):
        rel_type0 = typeit(node.children[0], env, type_env)
        rel_type1 = typeit(node.children[1], env, type_env)
        assert isinstance(rel_type0.data, CartType)
        assert isinstance(rel_type1.data, CartType)
        preimagetype = rel_type0.data.data[1]
        imagetype = rel_type1.data.data[0]
        return PowerSetType(CartType(preimagetype, imagetype))
    elif isinstance(node, AIdentityExpression):
        atype0 = typeit(node.children[0], env, type_env)
        assert isinstance(atype0, PowerSetType)
        assert isinstance(atype0.data, SetType)
        return PowerSetType(PowerSetType(CartType(atype0.data, atype0.data)))
    elif isinstance(node, ADomainRestrictionExpression) or isinstance(node, ADomainSubtractionExpression) or isinstance(node, ARangeRestrictionExpression) or isinstance(node, ARangeSubtractionExpression):
        atype0 = typeit(node.children[0], env, type_env)
        rel_type = typeit(node.children[1], env, type_env)
        assert isinstance(atype0, PowerSetType)
        assert isinstance(atype0.data, SetType)
        return rel_type
    elif isinstance(node, AReverseExpression):
        rel_type0 = typeit(node.children[0], env, type_env)
        preimagetype = rel_type0.data.data[0]
        imagetype = rel_type0.data.data[1]
        return PowerSetType(CartType(imagetype, preimagetype))
    elif isinstance(node, AImageExpression):
        rel_type0 = typeit(node.children[0], env, type_env)
        assert isinstance(rel_type0, PowerSetType)
        assert isinstance(rel_type0.data, CartType)
        return PowerSetType(rel_type0.data.data[1])
    elif isinstance(node, AOverwriteExpression):
        rel_type0 = typeit(node.children[0], env, type_env)
        rel_type1 = typeit(node.children[1], env, type_env)
        assert isinstance(rel_type0, PowerSetType)
        assert isinstance(rel_type0.data, CartType)
        assert isinstance(rel_type1, PowerSetType)
        assert isinstance(rel_type1.data, CartType)
        return rel_type0
    elif isinstance(node, AParallelProductExpression):
        rel_type0 = typeit(node.children[0], env, type_env)
        rel_type1 = typeit(node.children[1], env, type_env)
        assert isinstance(rel_type0, PowerSetType)
        assert isinstance(rel_type0.data, CartType)
        assert isinstance(rel_type1, PowerSetType)
        assert isinstance(rel_type1.data, CartType)
        x = SetType(rel_type0.data.data[0].data)
        m = SetType(rel_type0.data.data[1].data)
        y = SetType(rel_type1.data.data[0].data)
        n = SetType(rel_type1.data.data[1].data)
        return PowerSetType(CartType(CartType(x,y),CartType(m,n)))
    elif isinstance(node, ADirectProductExpression):
        rel_type0 = typeit(node.children[0], env, type_env)
        rel_type1 = typeit(node.children[1], env, type_env)
        assert isinstance(rel_type0, PowerSetType)
        assert isinstance(rel_type0.data, CartType)
        assert isinstance(rel_type1, PowerSetType)
        assert isinstance(rel_type1.data, CartType)
        x = SetType(rel_type0.data.data[0].data)
        y = SetType(rel_type0.data.data[1].data)
        x2 = SetType(rel_type1.data.data[0].data)
        z = SetType(rel_type1.data.data[1].data)
        assert x.data == x2.data
        return PowerSetType(CartType(x,CartType(y,z)))
    elif isinstance(node, AFirstProjectionExpression):
        type0 = typeit(node.children[0], env, type_env)
        type1 = typeit(node.children[1], env, type_env)
        assert isinstance(type0, PowerSetType)
        assert isinstance(type0.data, SetType)
        assert isinstance(type1, PowerSetType)
        assert isinstance(type1.data, SetType)
        return PowerSetType(CartType(CartType(type0.data,type1.data),type0.data))
    elif isinstance(node, ASecondProjectionExpression):
        type0 = typeit(node.children[0], env, type_env)
        type1 = typeit(node.children[1], env, type_env)
        assert isinstance(type0, PowerSetType)
        assert isinstance(type0.data, SetType)
        assert isinstance(type1, PowerSetType)
        assert isinstance(type1.data, SetType)
        return PowerSetType(CartType(CartType(type0.data,type1.data),type1.data))
    elif isinstance(node, APartialFunctionExpression) or isinstance(node, ATotalFunctionExpression) or isinstance(node, APartialInjectionExpression) or isinstance(node, ATotalInjectionExpression) or isinstance(node, APartialSurjectionExpression) or isinstance(node, ATotalSurjectionExpression) or  isinstance(node, ATotalBijectionExpression):
        type0 = typeit(node.children[0], env, type_env)
        type1 = typeit(node.children[1], env, type_env)
        assert isinstance(type0, PowerSetType)
        assert isinstance(type0.data, SetType)
        assert isinstance(type1, PowerSetType)
        assert isinstance(type1.data, SetType)
        return PowerSetType(PowerSetType(CartType(type0.data,type1.data)))
    elif isinstance(node, AFunctionExpression):
        type0 = typeit(node.children[0], env, type_env)
        assert isinstance(type0, PowerSetType)
        assert isinstance(type0.data, CartType)
        assert isinstance(type0.data.data[1], SetType)
        return type0.data.data[1]
    elif isinstance(node,ASeqExpression) or isinstance(node,ASeq1Expression) or isinstance(node,AIseqExpression) or isinstance(node,APermExpression):
        type0 = typeit(node.children[0], env, type_env)
        assert isinstance(type0, PowerSetType)
        assert isinstance(type0.data, SetType)
        return PowerSetType(PowerSetType(CartType(IntegerType(None),type0.data)))
    elif isinstance(node, AConcatExpression):
        type0 = typeit(node.children[0], env, type_env)
        type1 = typeit(node.children[1], env, type_env)
        assert isinstance(type0, PowerSetType)
        assert isinstance(type0.data, CartType)
        assert isinstance(type0.data.data[0], IntegerType)
        assert isinstance(type1, PowerSetType)
        assert isinstance(type1.data, CartType)
        assert isinstance(type1.data.data[0], IntegerType)
        assert type0.data.data[1].data == type1.data.data[1].data
        return PowerSetType(CartType(IntegerType(None),type0.data.data[1]))
    elif isinstance(node, AInsertFrontExpression):
        type0 = typeit(node.children[0], env, type_env)
        type1 = typeit(node.children[1], env, type_env)
        assert isinstance(type1, PowerSetType)
        assert isinstance(type1.data, CartType)
        assert isinstance(type1.data.data[0], IntegerType)
        assert isinstance(type1.data.data[1], SetType)
        assert isinstance(type0, SetType)
        assert type0.data == type1.data.data[1].data
        return type1
    elif isinstance(node, AInsertTailExpression):
        type0 = typeit(node.children[0], env, type_env)
        type1 = typeit(node.children[1], env, type_env)
        assert isinstance(type0, PowerSetType)
        assert isinstance(type0.data, CartType)
        assert isinstance(type0.data.data[0], IntegerType)
        assert isinstance(type0.data.data[1], SetType)
        assert isinstance(type1, SetType)
        assert type1.data == type0.data.data[1].data
        return type0
    elif isinstance(node, ASequenceExtensionExpression):
        type_list = []
        for child in node.children:
            t = typeit(child, env, type_env)
            type_list.append(t)
        atype = type_list[0]
        for t in type_list[1:]:
            # TODO: learn types: all types must be equal!
            assert t.data == atype.data
        return PowerSetType(CartType(IntegerType(None),atype))
    elif isinstance(node, ASizeExpression):
        type0 = typeit(node.children[0], env, type_env)
        assert isinstance(type0, PowerSetType)
        assert isinstance(type0.data, CartType)
        assert isinstance(type0.data.data[0], IntegerType)
        assert isinstance(type0.data.data[1], SetType)
        return IntegerType(None)
    elif isinstance(node, ARevExpression):
        type0 = typeit(node.children[0], env, type_env)
        assert isinstance(type0, PowerSetType)
        assert isinstance(type0.data, CartType)
        assert isinstance(type0.data.data[0], IntegerType)
        assert isinstance(type0.data.data[1], SetType)
        return type0
    elif isinstance(node, ARestrictFrontExpression) or isinstance(node, ARestrictTailExpression):
        type0 = typeit(node.children[0], env, type_env)
        type1 = typeit(node.children[1], env, type_env)
        assert isinstance(type0, PowerSetType)
        assert isinstance(type0.data, CartType)
        assert isinstance(type0.data.data[0], IntegerType)
        assert isinstance(type0.data.data[1], SetType)
        assert isinstance(type1, IntegerType)
        return type0
    elif isinstance(node, AFirstExpression) or isinstance(node, ALastExpression):
        type0 = typeit(node.children[0], env, type_env)
        assert isinstance(type0, PowerSetType)
        assert isinstance(type0.data, CartType)
        assert isinstance(type0.data.data[0], IntegerType)
        assert isinstance(type0.data.data[1], SetType)
        return type0.data.data[1]
    elif isinstance(node, ATailExpression) or isinstance(node, AFrontExpression):
        type0 = typeit(node.children[0], env, type_env)
        assert isinstance(type0, PowerSetType)
        assert isinstance(type0.data, CartType)
        assert isinstance(type0.data.data[0], IntegerType)
        assert isinstance(type0.data.data[1], SetType)
        return type0
    else:
        # WARNING: Make sure that is only used when no typeinfo is needed
        for child in node.children:
            typeit(child, env, type_env)





# this function exsist to handle preds like "x=y & y=1" and find the
# type of x and y after one run.
# here x is set to the (unkonwn-)type y
# When the (unknown-)y-type is set to IntegerType
# all y-types are set to ist in a lin. search
# TODO: This function is not full implemented!
# TODO: find names of unknown sets (e.g. of a ASetExtensionExpression node)
# now found in equal/not equal-Nodes...
def unify_equal(maybe_type0, maybe_type1, type_env):
    assert isinstance(type_env, TypeCheck_Environment)
    print maybe_type0, maybe_type1
    if isinstance(maybe_type0, BType) and isinstance(maybe_type1, BType):
        if maybe_type0.__class__ == maybe_type1.__class__:
            # TODO: unification if not int or settype. e.g cart or power-type
            if isinstance(maybe_type0, PowerSetType):
                unify_equal(maybe_type0.data, maybe_type1.data, type_env)
            elif isinstance(maybe_type0, CartType):
                raise Exception("not implemented:CartType unify_equal")
            return maybe_type0
        print "TYPEERROR: %s %s", maybe_type0, maybe_type1
        raise Exception() #TODO: Throw TypeException
    elif isinstance(maybe_type0, UnknownType) and isinstance(maybe_type1, UnknownType):
        # TODO: not complete
        maybe_type0 = unknown_closure(maybe_type0)
        return type_env.set_unknown_type(maybe_type0, maybe_type1)
    elif isinstance(maybe_type0, UnknownType) and isinstance(maybe_type1, BType):
        # TODO: not complete
        maybe_type0 = unknown_closure(maybe_type0)
        return type_env.set_concrete_type(maybe_type0, maybe_type1)
    elif isinstance(maybe_type1, UnknownType) and isinstance(maybe_type0, BType):
        # TODO: not complete
        maybe_type1 = unknown_closure(maybe_type1)
        return type_env.set_concrete_type(maybe_type1, maybe_type0)
    else:
        raise Exception() # should never happen



# calles by (and only by) the Belong-Node
def unify_element_of(elm_type, set_type, type_env):
    print "elementof"
    if isinstance(elm_type, UnknownType) and not set_type == None:
        #assert isinstance(node.children[0], AIdentifierExpression)
        set_type = unknown_closure(set_type)
        elm_type = unknown_closure(elm_type)
        if isinstance(set_type, PowerSetType):
            # map unknown type elm_type to set_type for all elm_type
            unify_equal(elm_type, set_type.data, type_env)
        elif isinstance(set_type, UnknownType):
            # FIXME: not all cases!
            if set_type.real_type == None:
                unify_equal(set_type, PowerSetType(elm_type), type_env)
            elif isinstance(set_type.real_type, PowerSetType):
                unify_equal(elm_type, set_type.real_type.data, type_env)
            else:
                #FIXME: quick fix - this is wrong
                unify_equal(elm_type, set_type, type_env)
        else:
            # no unknown type and no powerset-type
            raise Exception("Unimplemented case:  no unknown type and no powerset-type")
        return
    elif isinstance(elm_type, BType):
        unify_equal(PowerSetType(elm_type), set_type, type_env)
        return
    else:
        # no unknown type and no powerset-type
        raise Exception("Unimplemented case:  no unknown type and no powerset-type")