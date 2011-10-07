# -*- coding: utf-8 -*-
from ast_nodes import *


class BType:
    pass


class IntegerType(BType):
    def __init__(self, number_or_None):
        self.data = number_or_None # TODO: maybe this data is useless


class PowerSetType(BType):
    def __init__(self, aset_type):
        self.data = aset_type


class SetType(BType):
    def __init__(self, name):
        self.data = name # None when name unknown


class CartType(BType):
    def __init__(self, setA, setB):
        self.data = (setA, setB)


# returns Type, None or String
# sideeffect: changes env
def typeit(node, env):
    if isinstance(node, ANatSetExpression):
        return PowerSetType(IntegerType(None))
    elif isinstance(node, ANat1SetExpression):
        return PowerSetType(IntegerType(None))
    elif isinstance(node, AIntervalExpression):
        return PowerSetType(IntegerType(None))
    elif isinstance(node, AEmptySetExpression):
        return PowerSetType(SetType(None))
    elif isinstance(node, AComprehensionSetExpression):
        pred = node.children[len(node.children) -1]
        typeit(pred, env)
        for child in node.children[:-1]:
            assert not env.variable_type[child.idName]==None
        return PowerSetType(SetType(None)) #name unknown
    elif isinstance(node, AIntegerExpression):
        return IntegerType(node.intValue)
    elif isinstance(node, AIdentifierExpression):
        try:
            idtype = env.variable_type[node.idName]
            return idtype
        except KeyError: 
            # add unknown-type: this is importand in unify(x,y)
            # TODO: Throw Var not def error
            env.variable_type[node.idName] = node.idName 
            return node.idName # special case
    elif isinstance(node, ASetExtensionExpression):
        for child in node.children:
            typeit(child, env)
        return PowerSetType(SetType(None)) # name unknown
    elif isinstance(node, ABelongPredicate):
        elm_type = typeit(node.children[0], env)
        set_type = typeit(node.children[1], env)
        if isinstance(elm_type, str) and not set_type == None:
            assert isinstance(node.children[0], AIdentifierExpression)
            assert isinstance(set_type, PowerSetType)
            unify(elm_type, set_type.data, env)
            return
        else:
            raise Exception("Unimplemented case: no ID on left side")
    elif isinstance(node, AEqualPredicate):
        expr1_type = typeit(node.children[0], env)
        expr2_type = typeit(node.children[1], env)
        if isinstance(expr1_type, str) and not expr2_type == None:
            # the string maybe a unknown-type of an expression:
            # e.g. X = U\/T with U and T unknown at this time
            #assert isinstance(node.children[0], AIdentifierExpression)
            if isinstance(expr2_type, PowerSetType) and  isinstance(expr2_type.data, SetType) and expr2_type.data.data == None:
                expr2_type.data.data = expr1_type # set name
            unify(expr1_type, expr2_type, env)
        elif isinstance(expr2_type, str) and not expr1_type == None:
            # the string maybe a unknown-type of an expression:
            # e.g. X = U\/T with U and T unknown at this time
            #assert isinstance(node.children[1], AIdentifierExpression)
            if isinstance(expr1_type, PowerSetType) and  isinstance(expr1_type.data, SetType) and expr1_type.data.data == None: # TODO: think about that...
                expr1_type.data.data = expr2_type # set name
            unify(expr2_type, expr1_type, env)
        else:
            assert expr1_type.__class__ == expr2_type.__class__
            if isinstance(expr1_type, str) and isinstance(expr2_type, str):
                # Both unknown: remember same type via string
                # this is resolved in a later phase
                unify(expr1_type, expr2_type, env)
        return None
    elif isinstance(node, AUnionExpression) or isinstance(node, AIntersectionExpression):
        asettype0 = typeit(node.children[0], env)
        asettype1 = typeit(node.children[1], env)
        if isinstance(asettype0,str):
            unify(asettype0, asettype1, env)
            return asettype1
        elif isinstance(asettype1, str):
            unify(asettype1, asettype0, env)
            return asettype0
        else:
            assert asettype1.data.data == asettype0.data.data # same name
            assert asettype1.__class__ == asettype0.__class__
            return asettype1
    elif isinstance(node, AIncludePredicate) or isinstance(node, ANotIncludePredicate) or isinstance(node, AIncludeStrictlyPredicate) or isinstance(node, ANotIncludeStrictlyPredicate):
        asettype0 = typeit(node.children[0], env)
        asettype1 = typeit(node.children[1], env)
        if isinstance(asettype0, str) and not asettype1 == None:
            unify(asettype0, asettype1, env)
        elif isinstance(asettype1, str) and not asettype0 == None:
            unify(asettype1, asettype0, env)
        else:
            raise Exception("Unimplemented case")
    elif isinstance(node, AAddExpression) or isinstance(node, ADivExpression) or isinstance(node, AModuloExpression):
        expr1_type = typeit(node.children[0], env)
        expr2_type = typeit(node.children[1], env)
        assert isinstance(expr1_type, IntegerType)
        assert isinstance(expr2_type, IntegerType)
        return IntegerType(None)
    elif isinstance(node, ALessEqualPredicate) or isinstance(node, ALessPredicate) or isinstance(node, AGreaterEqualPredicate) or isinstance(node, AGreaterPredicate):
        expr1_type = typeit(node.children[0], env)
        expr2_type = typeit(node.children[1], env)
        if isinstance(expr1_type, str) and not expr2_type == None:
            assert isinstance(node.children[0], AIdentifierExpression)
            unify(expr1_type, expr2_type, env)
        elif isinstance(expr2_type, str) and not expr1_type == None:
            assert isinstance(node.children[1], AIdentifierExpression)
            unify(expr2_type, expr1_type, env)
        else:
            assert isinstance(expr1_type, IntegerType)
            assert isinstance(expr2_type, IntegerType)
        return None
    elif isinstance(node, AMinusOrSetSubtractExpression):
        expr1_type = typeit(node.children[0], env)
        expr2_type = typeit(node.children[1], env)
        if isinstance(expr1_type, IntegerType) and isinstance(expr2_type, IntegerType): # Minus
            return IntegerType(None)
        elif isinstance(expr1_type, PowerSetType) and isinstance(expr2_type, PowerSetType):
            assert expr1_type.data.data== expr2_type.data.data # same name
            return expr1_type
        else:
            raise Exception("Unimplemented case: no sets and no ints!")
    elif isinstance(node, AMultOrCartExpression):
        expr1_type = typeit(node.children[0], env)
        expr2_type = typeit(node.children[1], env)
        if isinstance(expr1_type, IntegerType) and isinstance(expr2_type, IntegerType): # Mul
            return IntegerType(None)
        elif isinstance(expr1_type, PowerSetType) and  isinstance(expr2_type, PowerSetType):
            return PowerSetType(CartType(expr1_type.data, expr2_type.data))
        else:
            raise Exception("Unimplemented case: %s",node)
    elif isinstance(node, AGeneralSumExpression):
        typeit(node.children[-2], env)
        typeit(node.children[-1], env)
        return IntegerType(None)
    elif isinstance(node, AGeneralProductExpression):
        typeit(node.children[-2], env)
        typeit(node.children[-1], env)
        return IntegerType(None)
    elif isinstance(node, ACardExpression):
        typeit(node.children[0], env)
        return IntegerType(None)
    elif isinstance(node, APowSubsetExpression) or isinstance(node, APow1SubsetExpression):
        atype = typeit(node.children[0], env)
        assert isinstance(atype, PowerSetType)
        return PowerSetType(atype)
    elif isinstance(node, ARelationsExpression):
        atype0 = typeit(node.children[0], env)
        atype1 = typeit(node.children[1], env)
        return PowerSetType(PowerSetType(CartType(atype0.data, atype1.data)))
    elif isinstance(node, ADomainExpression):
        rel_type =  typeit(node.children[0], env)
        assert isinstance(rel_type.data, CartType)
        return PowerSetType(rel_type.data.data[0]) # pow of preimage settype
    elif isinstance(node, ARangeExpression):
        rel_type =  typeit(node.children[0], env)
        assert isinstance(rel_type.data, CartType)
        return PowerSetType(rel_type.data.data[1]) # pow of image settype
    elif isinstance(node, ACompositionExpression):
        rel_type0 = typeit(node.children[0], env)
        rel_type1 = typeit(node.children[1], env)
        assert isinstance(rel_type0.data, CartType)
        assert isinstance(rel_type1.data, CartType)
        preimagetype = rel_type0.data.data[1]
        imagetype = rel_type1.data.data[0]
        return PowerSetType(CartType(preimagetype, imagetype))
    elif isinstance(node, AIdentityExpression):
        atype0 = typeit(node.children[0], env)
        assert isinstance(atype0, PowerSetType)
        assert isinstance(atype0.data, SetType)
        return PowerSetType(PowerSetType(CartType(atype0.data, atype0.data)))
    elif isinstance(node, ADomainRestrictionExpression) or isinstance(node, ADomainSubtractionExpression) or isinstance(node, ARangeRestrictionExpression) or isinstance(node, ARangeSubtractionExpression):
        atype0 = typeit(node.children[0], env)
        rel_type = typeit(node.children[1], env)
        assert isinstance(atype0, PowerSetType)
        assert isinstance(atype0.data, SetType)
        return rel_type
    elif isinstance(node, AReverseExpression):
        rel_type0 = typeit(node.children[0], env)
        preimagetype = rel_type0.data.data[0]
        imagetype = rel_type0.data.data[1]
        return PowerSetType(CartType(imagetype, preimagetype))
    elif isinstance(node, AImageExpression):
        rel_type0 = typeit(node.children[0], env)
        assert isinstance(rel_type0, PowerSetType)
        assert isinstance(rel_type0.data, CartType)
        return PowerSetType(rel_type0.data.data[1])
    elif isinstance(node, AOverwriteExpression):
        rel_type0 = typeit(node.children[0], env)
        rel_type1 = typeit(node.children[1], env)
        assert isinstance(rel_type0, PowerSetType)
        assert isinstance(rel_type0.data, CartType)
        assert isinstance(rel_type1, PowerSetType)
        assert isinstance(rel_type1.data, CartType)
        return rel_type0
    elif isinstance(node, AParallelProductExpression):
        rel_type0 = typeit(node.children[0], env)
        rel_type1 = typeit(node.children[1], env)
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
        rel_type0 = typeit(node.children[0], env)
        rel_type1 = typeit(node.children[1], env)
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
        type0 = typeit(node.children[0], env)
        type1 = typeit(node.children[1], env)
        assert isinstance(type0, PowerSetType)
        assert isinstance(type0.data, SetType)
        assert isinstance(type1, PowerSetType)
        assert isinstance(type1.data, SetType)
        return PowerSetType(CartType(CartType(type0.data,type1.data),type0.data))
    elif isinstance(node, ASecondProjectionExpression):
        type0 = typeit(node.children[0], env)
        type1 = typeit(node.children[1], env)
        assert isinstance(type0, PowerSetType)
        assert isinstance(type0.data, SetType)
        assert isinstance(type1, PowerSetType)
        assert isinstance(type1.data, SetType)
        return PowerSetType(CartType(CartType(type0.data,type1.data),type1.data))
    elif isinstance(node, APartialFunctionExpression) or isinstance(node, ATotalFunctionExpression) or isinstance(node, APartialInjectionExpression) or isinstance(node, ATotalInjectionExpression) or isinstance(node, APartialSurjectionExpression) or isinstance(node, ATotalSurjectionExpression) or  isinstance(node, ATotalBijectionExpression):
        type0 = typeit(node.children[0], env)
        type1 = typeit(node.children[1], env)
        assert isinstance(type0, PowerSetType)
        assert isinstance(type0.data, SetType)
        assert isinstance(type1, PowerSetType)
        assert isinstance(type1.data, SetType)
        return PowerSetType(PowerSetType(CartType(type0.data,type1.data)))
    elif isinstance(node, AFunctionExpression):
        type0 = typeit(node.children[0], env)
        assert isinstance(type0, PowerSetType)
        assert isinstance(type0.data, CartType)
        assert isinstance(type0.data.data[1], SetType)
        return type0.data.data[1]
    elif isinstance(node,ASeqExpression) or isinstance(node,ASeq1Expression) or isinstance(node,AIseqExpression) or isinstance(node,APermExpression):
        type0 = typeit(node.children[0], env)
        assert isinstance(type0, PowerSetType)
        assert isinstance(type0.data, SetType)
        return PowerSetType(PowerSetType(CartType(IntegerType(None),type0.data)))
    elif isinstance(node, AConcatExpression):
        type0 = typeit(node.children[0], env)
        type1 = typeit(node.children[1], env)
        assert isinstance(type0, PowerSetType)
        assert isinstance(type0.data, CartType)
        assert isinstance(type0.data.data[0], IntegerType)
        assert isinstance(type1, PowerSetType)
        assert isinstance(type1.data, CartType)
        assert isinstance(type1.data.data[0], IntegerType)
        assert type0.data.data[1].data == type1.data.data[1].data
        return PowerSetType(CartType(IntegerType(None),type0.data.data[1]))
    elif isinstance(node, AInsertFrontExpression):
        type0 = typeit(node.children[0], env)
        type1 = typeit(node.children[1], env)
        assert isinstance(type1, PowerSetType)
        assert isinstance(type1.data, CartType)
        assert isinstance(type1.data.data[0], IntegerType)
        assert isinstance(type1.data.data[1], SetType)
        assert isinstance(type0, SetType)
        assert type0.data == type1.data.data[1].data
        return type1
    elif isinstance(node, AInsertTailExpression):
        type0 = typeit(node.children[0], env)
        type1 = typeit(node.children[1], env)
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
            t = typeit(child, env)
            type_list.append(t)
        atype = type_list[0]
        for t in type_list[1:]:
            # TODO: learn types: all types must be equal!
            assert t.data == atype.data
        return PowerSetType(CartType(IntegerType(None),atype))
    elif isinstance(node, ASizeExpression):
        type0 = typeit(node.children[0], env)
        assert isinstance(type0, PowerSetType)
        assert isinstance(type0.data, CartType)
        assert isinstance(type0.data.data[0], IntegerType)
        assert isinstance(type0.data.data[1], SetType)
        return IntegerType(None)
    elif isinstance(node, ARevExpression):
        type0 = typeit(node.children[0], env)
        assert isinstance(type0, PowerSetType)
        assert isinstance(type0.data, CartType)
        assert isinstance(type0.data.data[0], IntegerType)
        assert isinstance(type0.data.data[1], SetType)
        return type0
    elif isinstance(node, ARestrictFrontExpression) or isinstance(node, ARestrictTailExpression):
        type0 = typeit(node.children[0], env)
        type1 = typeit(node.children[1], env)
        assert isinstance(type0, PowerSetType)
        assert isinstance(type0.data, CartType)
        assert isinstance(type0.data.data[0], IntegerType)
        assert isinstance(type0.data.data[1], SetType)
        assert isinstance(type1, IntegerType)
        return type0
    elif isinstance(node, AFirstExpression) or isinstance(node, ALastExpression):
        type0 = typeit(node.children[0], env)
        assert isinstance(type0, PowerSetType)
        assert isinstance(type0.data, CartType)
        assert isinstance(type0.data.data[0], IntegerType)
        assert isinstance(type0.data.data[1], SetType)
        return type0.data.data[1]
    elif isinstance(node, ATailExpression) or isinstance(node, AFrontExpression):
        type0 = typeit(node.children[0], env)
        assert isinstance(type0, PowerSetType)
        assert isinstance(type0.data, CartType)
        assert isinstance(type0.data.data[0], IntegerType)
        assert isinstance(type0.data.data[1], SetType)
        return type0
    else:
        for child in node.children:
            typeit(child, env)


# this function exsist to handle preds like "x=y & y=1" and find the
# type of x and y after one run.
# here x is set to the (unkonwn-)type y
# When the (unknown-)y-type is set to IntegerType
# all y-types are set to ist in a lin. search
# TODO: replace lin. search by pointers to unknown types 
def unify(maybe_type0, maybe_type1, env):
    if isinstance(maybe_type0, BType) and isinstance(maybe_type1, BType):
        if maybe_type0.__class__ == maybe_type1.__class__:
            return
        print "TYPEERROR: %s %s", maybe_type0, maybe_type1
        raise Exception() #TODO: Throw TypeException
    # one of them must be an ID-name
    assert isinstance(maybe_type0, str) or isinstance(maybe_type1, str)

    if isinstance(maybe_type0, str): # a unknown type is set to maybe_type1
        var_list =[x for x in env.variable_type if env.variable_type[x]==maybe_type0]
        for v in var_list: # vars with the unknown-type maybe_type0
            env.variable_type[v] = maybe_type1
    elif isinstance(maybe_type1, str):
        var_list =[x for x in env.variable_type if env.variable_type[x]==maybe_type1]
        for v in var_list: # vars with the unknown-type maybe_type1
            env.variable_type[v] = maybe_type0
    else:
        env.variable_type[maybe_type0] = maybe_type1