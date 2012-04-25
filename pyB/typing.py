# -*- coding: utf-8 -*-
from ast_nodes import *
from btypes import *
from helpers import find_var_names
from bmachine import BMachine


class BTypeException(Exception):
    def __init__(self, string):
        self.string = string


# Helper env: will be thrown away after Typechecking
class TypeCheck_Environment():
    def __init__(self):
        # is used to construct the env.node_to_type_map
        self.id_to_nodes_stack = []
        self.id_to_types_stack = []


    def init_env(self, known_types_list, idNames):
        id_to_nodes_map = {} # A: str->NODE
        id_to_types_map = {} # T: str->Type
        for atuple in known_types_list:
            id_Name = atuple[0]
            atype = atuple[1]
            id_to_types_map[id_Name] = UnknownType(id_Name, atype)
            id_to_nodes_map[id_Name] = []
        # ids with unknown types
        for id_Name in idNames:
            id_to_nodes_map[id_Name] = [] # no Nodes at the moment
            id_to_types_map[id_Name] = UnknownType(id_Name, None)
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
        string = "TypeError: %s not found while adding node: %s! Maybe %s is unkown. IdName not added to type_env (typing.py)?", node.idName, node, node.idName
        print string
        raise BTypeException(string)


    def set_unknown_type(self, id0_Name, id1_Name):
        assert isinstance(id0_Name, UnknownType)
        assert isinstance(id1_Name, UnknownType)

        if isinstance(id0_Name, PowORIntegerType):
            id1_Name.real_type = id0_Name
            return id1_Name
        elif isinstance(id0_Name, PowCartORIntegerType):
            id1_Name.real_type = id0_Name
            return id1_Name
        else:
            id0_Name.real_type = id1_Name
            return id1_Name


    def set_concrete_type(self, utype, ctype):
        assert isinstance(utype, UnknownType)
        assert isinstance(ctype, BType)
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
            #assert utype.real_type==None
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
            # unknown now. will be found in resole()
            # This is when local vars use global vars
            # which are unknown a this time
            if atype==None:
                atype= utype
            node_lst = node_top_map[idName]
            for node in node_lst:
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



# env.node_to_type_map should be a set of tree with 
# Nodes as leafs and Btypes as roots. 
# This method should throw away all unknowntypes 
# by walking from the leafs to the roots.
# If this is not possible the typechecking has failed
def resolve_type(env):
    for node in env.node_to_type_map:
        #print node.idName
        tree = env.node_to_type_map[node]
        tree_without_unknown = throw_away_unknown(tree)
        env.node_to_type_map[node] = tree_without_unknown



# it is a list an becomes a tree when carttype is implemented
# It uses the data attr of BTypes as pointers
def throw_away_unknown(tree):
    #print tree
    if isinstance(tree, SetType) or isinstance(tree, IntegerType) or isinstance(tree, EmptySetType) or isinstance(tree, StringType) or isinstance(tree, BoolType):
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
    else:
        # error!
        if isinstance(tree, UnknownType):
            string = "TypeError: can not resolve a Type of "+ tree.name
            print tree
            print string
            raise BTypeException(string)
        else:
            raise Exception("resolve fail: Not Implemented %s",tree)


# follows an UnknownType pointer chain:
# returns an UnknownType or a BType
# WARNING: This BType could point on other UnknownTypes. e.g. POW(X)
# WARNING: assumes cyclic - free
def unknown_closure(atype):
    if not isinstance(atype, UnknownType):
        return atype
    while True:
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
    type_env.write_to_env(env, type_env.id_to_types_stack[-1], type_env.id_to_nodes_stack[-1])
    resolve_type(env) # throw away unknown types
    return type_env # contains only knowladge about ids at global level


def type_check_predicate(root, env, idNames):
    ## FIXME: replace this call someday
    type_env = _test_typeit(root.children[0], env, [], idNames)


def type_check_bmch(root, mch):
    # TODO: abstr const/vars
    # TODO?: operations?
    set_idNames = find_var_names(mch.aSetsMachineClause) 
    const_idNames = find_var_names(mch.aConstantsMachineClause)
    var_idNames = find_var_names(mch.aVariablesMachineClause)
    idNames = set_idNames + const_idNames + var_idNames
    for name in mch.scalar_params + mch.set_params:
        idNames.append(name) # add machine-parameters
    type_env = _test_typeit(root, mch.state, [], idNames) ## FIXME: replace
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
    if isinstance (node, APredicateParseUnit):
        for child in node.children:
            typeit(child, env, type_env)
    elif isinstance(node, AAbstractMachineParseUnit):
        # TODO: mch-parameters
        mch = BMachine(node, None, None)
        env.set_mch(mch)
        mch.type_included(type_check_bmch, type_env)

        for p in mch.set_params:
            unknown_type = type_env.get_current_type(p)
            unify_equal(unknown_type, PowerSetType(SetType(p)), type_env)

        # type
        if mch.aDefinitionsMachineClause:
            for defi in mch.aDefinitionsMachineClause.children:
                assert isinstance(defi, AExpressionDefinition) or isinstance(defi, APredicateDefinition) or isinstance(defi, ASubstitutionDefinition)
                env.set_definition(defi.idName, defi)
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
        if mch.aInitialisationMachineClause:
            typeit(mch.aInitialisationMachineClause, env, type_env)
        if mch.aInvariantMachineClause:
            typeit(mch.aInvariantMachineClause, env, type_env)
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
            #unify_equal(atype, BoolType(), type_env)
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
        return #TODO: return BoolType
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
            # a realtion: A->B->C-> ... "len(children)"
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
        return EmptySetType()
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
        unify_equal(expr1_type, expr2_type, type_env)
        return expr1_type
    elif isinstance(node, ACoupleExpression):
        atype0 = typeit(node.children[0], env, type_env)
        atype1 = typeit(node.children[1], env, type_env)
        atype = CartType(PowerSetType(atype0), PowerSetType(atype1))
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
        atype = typeit(node.children[0], env, type_env)
        # TODO: atype must be PowersetType of something.
        # This info is not used
        #assert isinstance(atype, PowerSetType)
        return PowerSetType(atype)
    elif isinstance(node, ACardExpression):
        atype = typeit(node.children[0], env, type_env)
        assert isinstance(atype, PowerSetType) or isinstance(atype, EmptySetType)
        return IntegerType(None)
    elif isinstance(node, AGeneralUnionExpression) or isinstance(node, AGeneralIntersectionExpression):
        atype = typeit(node.children[0], env, type_env)
        unify_equal(atype, PowerSetType(PowerSetType(UnknownType(None,None))),type_env)
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
    # TODO: notBelong
    elif isinstance(node, ABelongPredicate):
        elm_type = typeit(node.children[0], env, type_env)
        set_type = typeit(node.children[1], env, type_env)
        unify_element_of(elm_type, set_type, type_env)
        return
    elif isinstance(node, AIncludePredicate) or isinstance(node, ANotIncludePredicate) or isinstance(node, AIncludeStrictlyPredicate) or isinstance(node, ANotIncludeStrictlyPredicate) or isinstance(node, AUnionExpression) or isinstance(node, AIntersectionExpression):
        expr1_type = typeit(node.children[0], env,type_env)
        expr2_type = typeit(node.children[1], env,type_env)
        return unify_equal(expr1_type, expr2_type, type_env)


# *****************
#
#       3. Numbers
#
# *****************
    elif isinstance(node, ANatSetExpression) or isinstance(node, ANat1SetExpression) or isinstance(node, AIntervalExpression) or isinstance(node, ANaturalSetExpression):
        return PowerSetType(IntegerType(None))
    elif isinstance(node, AIntegerExpression):
        return IntegerType(node.intValue)
    elif isinstance(node, AMinExpression) or isinstance(node, AMaxExpression):
        set_type = typeit(node.children[0], env, type_env)
        assert isinstance(set_type, PowerSetType)
        assert isinstance(set_type.data, IntegerType)
        return set_type.data
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
        atype0 = typeit(node.children[0], env, type_env)
        atype1 = typeit(node.children[1], env, type_env)
        return PowerSetType(PowerSetType(CartType(atype0, atype1)))
    elif isinstance(node, ADomainExpression):
        rel_type =  typeit(node.children[0], env, type_env)
        if isinstance(rel_type, UnknownType):
            atype = PowerSetType(CartType(PowerSetType(UnknownType(None,None)), PowerSetType(UnknownType(None,None))))
            unify_equal(rel_type, atype, type_env)
            return atype.data.data[0]
        else:
            assert isinstance(rel_type.data, CartType)
            return rel_type.data.data[0] # preimage settype
    elif isinstance(node, ARangeExpression):
        rel_type =  typeit(node.children[0], env, type_env)
        if isinstance(rel_type, UnknownType):
            atype = PowerSetType(CartType(PowerSetType(UnknownType(None,None)), PowerSetType(UnknownType(None,None))))
            unify_equal(rel_type, atype, type_env)
            return atype.data.data[1]
        else:
            assert isinstance(rel_type.data, CartType)
            return rel_type.data.data[1] # image settype
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
        assert isinstance(atype0.data, SetType) or isinstance(atype0.data, IntegerType)
        return PowerSetType(CartType(atype0, atype0))
    elif isinstance(node, AIterationExpression):
        atype0 = typeit(node.children[0], env, type_env)
        atype1 = typeit(node.children[1], env, type_env)
        ctype = PowerSetType(CartType(PowerSetType(UnknownType(None,None)),PowerSetType(UnknownType(None,None))))
        unify_equal(atype0, ctype, type_env)
        unify_equal(atype1, IntegerType(None), type_env)
        return atype0
    elif isinstance(node, AReflexiveClosureExpression) or isinstance(node, AClosureExpression):
        atype0 = typeit(node.children[0], env, type_env)
        ctype = PowerSetType(CartType(PowerSetType(UnknownType(None,None)),PowerSetType(UnknownType(None,None))))
        unify_equal(atype0, ctype, type_env)
        return atype0
    elif isinstance(node, ADomainRestrictionExpression) or isinstance(node, ADomainSubtractionExpression):
        atype0 = typeit(node.children[0], env, type_env)
        rel_type = typeit(node.children[1], env, type_env)
        assert isinstance(atype0, PowerSetType)
        assert isinstance(atype0.data, SetType) or isinstance(atype0.data, IntegerType) 
        return rel_type
    elif isinstance(node, ARangeSubtractionExpression) or isinstance(node, ARangeRestrictionExpression):
        rel_type = typeit(node.children[0], env, type_env)
        atype0 = typeit(node.children[1], env, type_env)
        assert isinstance(atype0, PowerSetType)
        assert isinstance(atype0.data, SetType) or isinstance(atype0.data, IntegerType) 
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
        return rel_type0.data.data[1]
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
        x = rel_type0.data.data[0]
        m = rel_type0.data.data[1]
        y = rel_type1.data.data[0]
        n = rel_type1.data.data[1]
        return PowerSetType(CartType(PowerSetType(CartType(x,y)),PowerSetType(CartType(m,n))))
    elif isinstance(node, ADirectProductExpression):
        rel_type0 = typeit(node.children[0], env, type_env)
        rel_type1 = typeit(node.children[1], env, type_env)
        assert isinstance(rel_type0, PowerSetType)
        assert isinstance(rel_type0.data, CartType)
        assert isinstance(rel_type1, PowerSetType)
        assert isinstance(rel_type1.data, CartType)
        x = rel_type0.data.data[0]
        y = rel_type0.data.data[1]
        x2 = rel_type1.data.data[0]
        z = rel_type1.data.data[1]
        assert x.__class__ == x2.__class__
        return PowerSetType(CartType(x,PowerSetType(CartType(y,z))))
    elif isinstance(node, AFirstProjectionExpression):
        type0 = typeit(node.children[0], env, type_env)
        type1 = typeit(node.children[1], env, type_env)
        assert isinstance(type0, PowerSetType)
        assert isinstance(type0.data, SetType) or isinstance(type0.data, IntegerType)
        assert isinstance(type1, PowerSetType)
        assert isinstance(type1.data, SetType) or isinstance(type1.data, IntegerType)
        return PowerSetType(CartType(PowerSetType(CartType(type0,type1)), type0))
    elif isinstance(node, ASecondProjectionExpression):
        type0 = typeit(node.children[0], env, type_env)
        type1 = typeit(node.children[1], env, type_env)
        assert isinstance(type0, PowerSetType)
        #assert isinstance(type0.data, SetType) or isinstance(type0.data, IntegerType)
        assert isinstance(type1, PowerSetType)
        #assert isinstance(type1.data, SetType)  or isinstance(type1.data, IntegerType)
        return PowerSetType(CartType(PowerSetType(CartType(type0, type1)), type1))


# *******************
#
#       4.1 Functions
#
# *******************
    elif isinstance(node, APartialFunctionExpression) or isinstance(node, ATotalFunctionExpression) or isinstance(node, APartialInjectionExpression) or isinstance(node, ATotalInjectionExpression) or isinstance(node, APartialSurjectionExpression) or isinstance(node, ATotalSurjectionExpression) or  isinstance(node, ATotalBijectionExpression) or isinstance(node, APartialBijectionExpression):
        type0 = typeit(node.children[0], env, type_env)
        type1 = typeit(node.children[1], env, type_env)
        assert isinstance(type0, PowerSetType)
        assert isinstance(type0.data, SetType) or isinstance(type0.data, IntegerType)
        assert isinstance(type1, PowerSetType)
        assert isinstance(type1.data, SetType) or isinstance(type0.data, IntegerType)
        return PowerSetType(PowerSetType(CartType(type0, type1)))
    elif isinstance(node, AFunctionExpression):
        type0 = typeit(node.children[0], env, type_env)
        if isinstance(type0, IntegerType):
            assert isinstance(node.children[0], APredecessorExpression) or isinstance(node.children[0], ASuccessorExpression)
            return type0
        assert isinstance(type0, PowerSetType)
        assert isinstance(type0.data, CartType)
        #assert isinstance(type0.data.data[1], SetType)
        return type0.data.data[1].data
    elif isinstance(node, ALambdaExpression):
        ids = []
        for n in node.children[:-2]:
            assert isinstance(n.idName, str)
            ids.append(n.idName)
        type_env.push_frame(ids)
        for child in node.children[:-1]:
            typeit(child, env, type_env)
        pre_img_type = typeit(node.children[0], env, type_env)
        img_type = typeit(node.children[-1], env, type_env)
        type_env.pop_frame(env)
        return PowerSetType(CartType(PowerSetType(pre_img_type), PowerSetType(img_type)))


# ********************
#
#       4.2 Sequences
#
# ********************
    elif isinstance(node,ASeqExpression) or isinstance(node,ASeq1Expression) or isinstance(node,AIseqExpression) or isinstance(node,APermExpression) or isinstance(node, AIseq1Expression):
        type0 = typeit(node.children[0], env, type_env)
        assert isinstance(type0, PowerSetType)
        #assert isinstance(type0.data, SetType)
        return PowerSetType(PowerSetType(CartType(PowerSetType(IntegerType(None)),type0)))
    elif isinstance(node, AGeneralConcatExpression):
        type0 = typeit(node.children[0], env, type_env)
        type1 = PowerSetType(CartType(PowerSetType(UnknownType(None,None)), PowerSetType(UnknownType(None,None))))
        unify_equal(type0, type1, type_env)
        return type1 # XXX
    elif isinstance(node, AConcatExpression):
        type0 = typeit(node.children[0], env, type_env)
        type1 = typeit(node.children[1], env, type_env)
        assert isinstance(type0, PowerSetType)
        assert isinstance(type0.data, CartType)
        assert isinstance(type0.data.data[0].data, IntegerType)
        assert isinstance(type1, PowerSetType)
        assert isinstance(type1.data, CartType)
        assert isinstance(type1.data.data[0].data, IntegerType)
        assert type0.data.data[1].data == type1.data.data[1].data
        return PowerSetType(CartType(PowerSetType(IntegerType(None)),type0.data.data[1]))
    elif isinstance(node, AInsertFrontExpression):
        type0 = typeit(node.children[0], env, type_env)
        type1 = typeit(node.children[1], env, type_env)
        assert isinstance(type1, PowerSetType)
        assert isinstance(type1.data, CartType)
        assert isinstance(type1.data.data[0].data, IntegerType)
        assert isinstance(type1.data.data[1].data, SetType)
        assert isinstance(type0, SetType)
        assert type0.data == type1.data.data[1].data.data # Setname
        return type1
    elif isinstance(node, AInsertTailExpression):
        type0 = typeit(node.children[0], env, type_env)
        type1 = typeit(node.children[1], env, type_env)
        assert isinstance(type0, PowerSetType)
        assert isinstance(type0.data, CartType)
        assert isinstance(type0.data.data[0].data, IntegerType)
        assert isinstance(type0.data.data[1].data, SetType)
        assert isinstance(type1, SetType)
        assert type1.data == type0.data.data[1].data.data # Setname
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
        return PowerSetType(CartType(PowerSetType(IntegerType(None)), PowerSetType(atype)))
    elif isinstance(node, ASizeExpression):
        type0 = typeit(node.children[0], env, type_env)
        assert isinstance(type0, PowerSetType)
        assert isinstance(type0.data, CartType)
        assert isinstance(type0.data.data[0].data, IntegerType)
        assert isinstance(type0.data.data[1].data, SetType)
        return IntegerType(None)
    elif isinstance(node, ARevExpression):
        type0 = typeit(node.children[0], env, type_env)
        assert isinstance(type0, PowerSetType)
        assert isinstance(type0.data, CartType)
        assert isinstance(type0.data.data[0].data, IntegerType)
        assert isinstance(type0.data.data[1].data, SetType)
        return type0
    elif isinstance(node, ARestrictFrontExpression) or isinstance(node, ARestrictTailExpression):
        type0 = typeit(node.children[0], env, type_env)
        type1 = typeit(node.children[1], env, type_env)
        assert isinstance(type0, PowerSetType)
        assert isinstance(type0.data, CartType)
        assert isinstance(type0.data.data[0].data, IntegerType)
        assert isinstance(type0.data.data[1].data, SetType)
        assert isinstance(type1, IntegerType)
        return type0
    elif isinstance(node, AFirstExpression) or isinstance(node, ALastExpression):
        type0 = typeit(node.children[0], env, type_env)
        assert isinstance(type0, PowerSetType)
        assert isinstance(type0.data, CartType)
        assert isinstance(type0.data.data[0].data, IntegerType)
        assert isinstance(type0.data.data[1].data, SetType)
        return type0.data.data[1].data
    elif isinstance(node, ATailExpression) or isinstance(node, AFrontExpression):
        type0 = typeit(node.children[0], env, type_env)
        assert isinstance(type0, PowerSetType)
        assert isinstance(type0.data, CartType)
        assert isinstance(type0.data.data[0].data, IntegerType)
        assert isinstance(type0.data.data[1].data, SetType)
        return type0



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
                atype1 = typeit(lhs_node, env, type_env)
                unify_equal(atype0, atype1, type_env)
            else:
                assert isinstance(lhs_node, AFunctionExpression)
                assert isinstance(lhs_node.children[0], AIdentifierExpression)
                func_type = typeit(lhs_node.children[0], env, type_env)
                atype2 = PowerSetType(CartType(PowerSetType(UnknownType(None,None)), PowerSetType(atype0)))
                unify_equal(func_type, atype2, type_env)
    elif isinstance(node, AConvertBoolExpression):
        atype = typeit(node.children[0], env, type_env)
        unify_equal(atype, BoolType(), type_env)
        return atype
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
        assert len(node.children)==1 # TODO: x.y.z
        return typeit(node.children[0], env, type_env)
    elif isinstance(node, AIdentifierExpression):
        type_env.add_node_by_id(node)
        idtype = type_env.get_current_type(node.idName)
        return idtype
    elif isinstance(node, AMinIntExpression) or isinstance(node, AMaxIntExpression) or isinstance(node, ASuccessorExpression) or isinstance(node, APredecessorExpression) or isinstance(node, APowerOfExpression):
        return IntegerType(None)
    elif isinstance(node, ADefinitionExpression) or isinstance(node, ADefinitionPredicate) or isinstance(node, ADefinitionSubstitution):
        ast = env.get_ast_by_definition(node.idName)
        assert isinstance(ast, AExpressionDefinition) or isinstance(ast, APredicateDefinition) or isinstance(ast, ASubstitutionDefinition) #  XXX: substitution!
        # The Type of the definition depends on
        # the type of the parameters
        ids = []
        for i in range(ast.paraNum):
            if isinstance(ast.children[i], AIdentifierExpression):
                ids.append(ast.children[i].idName)
            else:
                # TODO: implement parameter expression
                raise Exception("Parametes can only be Ids at the moment!")
        type_env.push_frame(ids)
        # map paraNames to types
        for i in range(ast.paraNum):
            atype = typeit(node.children[i], env, type_env)
            idtype = typeit(ast.children[i], env, type_env)
            unify_equal(idtype, atype, type_env)
        deftype = typeit(ast.children[-1], env, type_env)
        type_env.pop_frame(env)
        return deftype
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
        return entry_type
    elif isinstance(node, ATransRelationExpression):
        atype = typeit(node.children[0], env, type_env)
        range_type = UnknownType(None,None)
        image_type = UnknownType(None,None)
        func_type = PowerSetType(CartType(PowerSetType(range_type), PowerSetType(PowerSetType(image_type))))
        unify_equal(func_type, atype, type_env)
        return PowerSetType(CartType(PowerSetType(range_type), PowerSetType(image_type)))
    elif isinstance(node, ATransFunctionExpression):
        atype = typeit(node.children[0], env, type_env)
        range_type = UnknownType(None,None)
        image_type = UnknownType(None,None)
        rel_type = PowerSetType(CartType(PowerSetType(range_type), PowerSetType(image_type)))
        unify_equal(rel_type, atype, type_env)
        return PowerSetType(CartType(PowerSetType(range_type), PowerSetType(PowerSetType(image_type))))
    elif isinstance(node, AUnaryExpression):
        atype = typeit(node.children[0], env, type_env)
        unify_equal(IntegerType(None), atype, type_env)
        return atype
    elif isinstance(node, AOperation):
        names = []
        for i in range(0,node.return_Num+ node.parameter_Num):
            assert isinstance(node.children[i], AIdentifierExpression)
            names.append(node.children[i].idName)
        type_env.push_frame(names)
        for child in node.children:
            typeit(child, env, type_env)
        type_env.pop_frame(env)
    else:
        # WARNING: Make sure that is only used when no typeinfo is needed
        #print "WARNING: unhandeld node"
        for child in node.children:
            typeit(child, env, type_env)





# This function exist to handle preds like "x=y & y=1" and find the
# type of x and y after one run.
# TODO: This function is not full implemented!
def unify_equal(maybe_type0, maybe_type1, type_env):
    assert isinstance(type_env, TypeCheck_Environment)
    #print maybe_type0,maybe_type1
    maybe_type0 = unknown_closure(maybe_type0)
    maybe_type1 = unknown_closure(maybe_type1)

    # case 1: BType, BType
    if isinstance(maybe_type0, BType) and isinstance(maybe_type1, BType):
        if isinstance(maybe_type0, PowerSetType) and isinstance(maybe_type1, EmptySetType):
            return maybe_type0
        elif isinstance(maybe_type1, PowerSetType) and isinstance(maybe_type0, EmptySetType):
            return maybe_type1
        elif maybe_type0.__class__ == maybe_type1.__class__:
            # recursive unification-call
            # if not IntegerType, SetType or UnkownType.
            if isinstance(maybe_type0, PowerSetType):
                unify_equal(maybe_type0.data, maybe_type1.data, type_env)
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
                unify_equal(t00.data, t10.data, type_env)
                unify_equal(t01.data, t11.data, type_env)
            elif isinstance(maybe_type0, SetType):
                # learn/set name
                if maybe_type0.data==None:
                    maybe_type0.data = maybe_type1.data
                elif maybe_type1.data==None:
                    maybe_type1.data = maybe_type0.data
                else:
                    assert maybe_type1.data == maybe_type0.data
            else:
                assert isinstance(maybe_type0, IntegerType) or isinstance(maybe_type0, BoolType) or isinstance(maybe_type0, EmptySetType) or isinstance(maybe_type0, StringType)
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