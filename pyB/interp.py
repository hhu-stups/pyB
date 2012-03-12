# -*- coding: utf-8 -*-
from ast_nodes import *
from typing import typeit, IntegerType, PowerSetType, SetType, BType, CartType, BoolType, Substitution, Predicate, _test_typeit
from helpers import find_var_names

min_int = -1
max_int = 5
enable_assertions = True

class Environment():
    def __init__(self):
        # Values of global and local vars: string -> value.
        # NEW FRAME on this stack via append <=> New Var. Scope.
        self.value_stack = [{}]
        # Types of AST-ID-Nodes: Node->type.
        # This map is used by the enumeration
        # and was created and filled by typeit of the module typing.
        self.node_to_type_map = {}
        # AST-SubTrees: ID(String)->AST
        self.definition_id_to_ast = {}


    def set_definition(self, id_Name, ast):
        assert isinstance(id_Name, str)
        self.definition_id_to_ast[id_Name] = ast


    def get_ast_by_definition(self, id_Name):
        assert isinstance(id_Name, str)
        return self.definition_id_to_ast[id_Name]


    def get_value(self, id_Name):
        assert isinstance(id_Name, str)
        value_map_copy =  [x for x in self.value_stack] # no ref. copy
        value_map_copy.reverse()
        stack_depth = len(value_map_copy)
        # lookup:
        for i in range(stack_depth):
            try:
                return value_map_copy[i][id_Name]
            except KeyError:
                continue
        # No entry in the value_stack. The Variable with the name id_Name
        # is unknown. This is an Error found by the typechecker
        # TODO: raise custom exception. e.g lookuperror
        print "LookupErr:", id_Name
        raise KeyError



    # TODO: (maybe) check if value has the correct type
    # used by tests and emumaration and substitutipn
    def set_value(self, id_Name, value):
        for i in range(len(self.value_stack)):
            top_map = self.value_stack[-(i+1)]
            if id_Name in top_map:
                top_map[id_Name] = value
                return
        print "LookupErr:", id_Name
        raise KeyError


    def add_ids_to_frame(self, ids):
        top_map = self.value_stack[-1]
        for i in ids:
            assert isinstance(i,str)
            top_map[i] = None


    # This method is used only(!) by the typechecking-tests.
    # It returns the type of the id "string"
    def get_type(self, string):
        assert isinstance(string,str)
        # linear search for ID with the name string
        for node in self.node_to_type_map:
            assert isinstance(node, AIdentifierExpression)
            # FIXME: scoping: if there is more than one "string"
            # e.g x:Nat & !x.(x:S=>card(x)=3)...
            if node.idName==string:
                return self.node_to_type_map[node]


    # A KeyError or a false assert is a typechecking bug
    # Used by the eumerator: all_values
    def get_type_by_node(self, node):
        assert isinstance(node, AIdentifierExpression)
        atype = self.node_to_type_map[node]
        assert isinstance(atype, BType) 
        return atype


    # new scope:
    # push a new frame with new local vars
    def push_new_frame(self, nodes):
        # TODO: throw warning if local var with 
        # the same name like a global var. This is not a B error
        # but maybe not intended by the User
        var_map = {}
        for node in nodes:
            assert isinstance(node, AIdentifierExpression)
            var_map[node.idName] = node.idName
        self.value_stack.append(var_map)


    # leave scope: throw all values of local vars away
    def pop_frame(self):
        self.value_stack.pop()


# sideeffect:
# evals pred and sets var to values
# main interpreter-switch (sorted/grouped like b-toolkit list)
def interpret(node, env):

# ******************************
#
#        0. Interpretation-mode
#
# ******************************
    if isinstance(node,APredicateParseUnit):
        idNames = []
        find_var_names(node.children[0], idNames) #sideef: fill list
        _test_typeit(node.children[0], env, [], idNames) ## FIXME: replace this call someday
        if idNames ==[]:
            result = interpret(node.children[0], env)
            print result
            return
        else:
            print "enum. vars:",idNames
            gen = try_all_values(node.children[0], env, idNames)
            if gen.next():
                for i in idNames:
                    print i,":", env.get_value(i)
            else:
                print "No Solution found"
                print False
                return
        print True
        return
    elif isinstance(node, AAbstractMachineParseUnit):
        idNames = []
        find_var_names(node, idNames) #sideef: fill list
        for name in node.para:
            idNames.append(name) # add machine-parameters
        _test_typeit(node, env, [], idNames) ## FIXME: replace

        aConstantsMachineClause = None
        aConstraintsMachineClause = None
        aSetsMachineClause = None
        aVariablesMachineClause = None
        aPropertiesMachineClause = None
        aAssertionsMachineClause = None
        aInvariantMachineClause = None
        aInitialisationMachineClause = None
        aDefinitionsMachineClause = None

        for child in node.children:
            if isinstance(child, AConstantsMachineClause):
                aConstantsMachineClause = child
            elif isinstance(child, AConstraintsMachineClause):
                aConstraintsMachineClause = child
            elif isinstance(child, ASetsMachineClause):
                aSetsMachineClause = child
            elif isinstance(child, AVariablesMachineClause):
                aVariablesMachineClause = child
            elif isinstance(child, APropertiesMachineClause):
                aPropertiesMachineClause = child
            elif isinstance(child, AAssertionsMachineClause):
                aAssertionsMachineClause = child
            elif isinstance(child, AInitialisationMachineClause):
                aInitialisationMachineClause = child
            elif isinstance(child, AInvariantMachineClause):
                aInvariantMachineClause = child
            elif isinstance(child, ADefinitionsMachineClause):
                aDefinitionsMachineClause = child
            else:
                raise Exception("Unknown clause:",child )

        # TODO: Check with B spec
        # TODO: aDefinitionsMachineClause
        # Schneider Book page 62-64:
        # The parameters p make the constraints c True
        # #p.C
        # FIXME: dummy-init of mch-parameters
        env.add_ids_to_frame(node.para)
        for name in node.para:
            atype = env.get_type(name) # XXX
            values = all_values_by_type(atype, env)
            env.set_value(name, values[0]) #XXX
        if aConstraintsMachineClause: # C
            interpret(aConstraintsMachineClause, env)

        # Sets St and constants k which meet the constraints c make the properties B True
        # C => #St,k.B
        if aSetsMachineClause: # St
            interpret(aSetsMachineClause, env)
        if aConstantsMachineClause: # k
            interpret(aConstantsMachineClause, env)
        if aPropertiesMachineClause: # B
            # set up constants
            #TODO: Sets
            # Some Constants are set via Prop. Preds
            # FIXME: This is a hack! Introduce fresh envs!
            res = interpret(aPropertiesMachineClause, env)
            # Now set that constants which still dont have a value
            if aConstantsMachineClause:
                const_names = []
                for idNode in aConstantsMachineClause.children:
                    assert isinstance(idNode, AIdentifierExpression)
                    const_names.append(idNode.idName)
                if not res:
                    gen = try_all_values(aPropertiesMachineClause, env,const_names)
                    assert gen.next()

        # If C and B is True there should be Variables v which make the Invaraiant I True
        # TODO: B & C => #v.I
        if aVariablesMachineClause:
            interpret(aVariablesMachineClause, env)
        if aInitialisationMachineClause:
            interpret(aInitialisationMachineClause, env)
        if aInvariantMachineClause:
            res = interpret(aInvariantMachineClause, env)
            print "Invariant:",res

        # Not in schneiders book:
        if aAssertionsMachineClause:
            interpret(aAssertionsMachineClause, env)
    elif isinstance(node, AConstantsMachineClause):
        const_names = []
        for idNode in node.children:
            assert isinstance(idNode, AIdentifierExpression)
            const_names.append(idNode.idName)
            #atype = env.get_type_by_node(idNode)
        env.add_ids_to_frame(const_names)
    elif isinstance(node, AVariablesMachineClause):
        var_names = []
        for idNode in node.children:
            assert isinstance(idNode, AIdentifierExpression)
            var_names.append(idNode.idName)
            #atype = env.get_type_by_node(idNode)
        env.add_ids_to_frame(var_names)
    elif isinstance(node, ASetsMachineClause):
        for child in node.children:
            if isinstance(child, AEnumeratedSet):
                elm_lst = []
                for elm in child.children:
                    assert isinstance(elm, AIdentifierExpression)
                    elm_lst.append(elm.idName)
                env.add_ids_to_frame([child.idName])
                env.set_value(child.idName, frozenset(elm_lst))
            else:
                assert isinstance(child, ADeferredSet)
    elif isinstance(node, AConstraintsMachineClause):
        for child in node.children:
            interpret(child, env)
    elif isinstance(node, APropertiesMachineClause):
        assert len(node.children)==1
        return interpret(node.children[0], env)
    elif isinstance(node, AInitialisationMachineClause):
        for child in node.children:
            interpret(child, env)
    elif isinstance(node, AInvariantMachineClause):
        return interpret(node.children[0], env)
    elif isinstance(node, AAssertionsMachineClause):
        if enable_assertions:
            print "checking assertions"
            for child in node.children:
                print "\t", interpret(child, env)
            print "checking done."


# *********************
#
#        1. Predicates
#
# *********************
    elif isinstance(node, AConjunctPredicate):
        expr1 = interpret(node.children[0], env)
        expr2 = interpret(node.children[1], env)
        return expr1 and expr2
    elif isinstance(node, ADisjunctPredicate):
        expr1 = interpret(node.children[0], env)
        expr2 = interpret(node.children[1], env)
        return expr1 or expr2
    elif isinstance(node, AImplicationPredicate):
        expr1 = interpret(node.children[0], env)
        expr2 = interpret(node.children[1], env)
        if expr1 and not expr2:
            return False # True=>False is False
        else:
            return True
    elif isinstance(node, AEquivalencePredicate):
        expr1 = interpret(node.children[0], env)
        expr2 = interpret(node.children[1], env)
        return expr1 == expr2 # FIXME: maybe this is wrong...
    elif isinstance(node, ANegationPredicate):
        expr = interpret(node.children[0], env)
        return not expr
    elif isinstance(node, AUniversalQuantificationPredicate):
        # new scope 
        env.push_new_frame(node.children[:-1])
        max_depth = len(node.children) -2 # (two preds)
        if not forall_recursive_helper(0, max_depth, node, env):
            env.pop_frame()
            return False
        else:
            env.pop_frame()
            return True
    elif isinstance(node, AExistentialQuantificationPredicate):
        # new scope
        env.push_new_frame(node.children[:-1])
        max_depth = len(node.children) -2 # (two preds)
        if exist_recursive_helper(0, max_depth, node, env):
            env.pop_frame()
            return True
        else:
            env.pop_frame()
            return False
    elif isinstance(node, AEqualPredicate):
        expr1 = interpret(node.children[0], env)
        expr2 = interpret(node.children[1], env)
        # special case: learn values if None (optimization)
        if isinstance(node.children[0], AIdentifierExpression) and env.get_value(node.children[0].idName)==None:
            env.set_value(node.children[0].idName, expr2)
            return True
        elif isinstance(node.children[1], AIdentifierExpression) and env.get_value(node.children[1].idName)==None:
            env.set_value(node.children[1].idName, expr1)
            return True
        else:
            # else normal check
            return expr1 == expr2
    elif isinstance(node, AUnequalPredicate):
        expr1 = interpret(node.children[0], env)
        expr2 = interpret(node.children[1], env)
        return expr1 != expr2


# **************
#
#       2. Sets
#
# **************
    elif isinstance(node, ASetExtensionExpression):
        lst = []
        for child in node.children:
            elm = interpret(child, env)
            lst.append(elm)
        return frozenset(lst)
    elif isinstance(node, AEmptySetExpression):
        return frozenset()
    elif isinstance(node, AComprehensionSetExpression):
        # new scope
        env.push_new_frame(node.children[:-1])
        max_depth = len(node.children) -2
        lst = set_comprehension_recursive_helper(0, max_depth, node, env)
        # FIXME: maybe wrong:
        # [[x1,y1],[x2,y2]..] => [(x1,y2),(x2,y2)...]
        result = []
        if is_flat(lst):
            result = lst
        else:
            for i in lst:
                result.append(tuple(flatten(i,[])))
        env.pop_frame()
        return frozenset(result)
    elif isinstance(node, AUnionExpression):
        aSet1 = interpret(node.children[0], env)
        aSet2 = interpret(node.children[1], env)
        return aSet1.union(aSet2)
    elif isinstance(node, AIntersectionExpression):
        aSet1 = interpret(node.children[0], env)
        aSet2 = interpret(node.children[1], env)
        return aSet1.intersection(aSet2)
    elif isinstance(node, ACoupleExpression):
        lst = []
        for child in node.children:
            elm = interpret(child, env)
            lst.append(elm)
        return tuple(lst)
    elif isinstance(node, APowSubsetExpression):
        aSet = interpret(node.children[0], env)
        res = powerset(aSet)
        powerlist = list(res)
        lst = [frozenset(e) for e in powerlist]
        return frozenset(lst)
    elif isinstance(node, APow1SubsetExpression):
        aSet = interpret(node.children[0], env)
        res = powerset(aSet)
        powerlist = list(res)
        lst = [frozenset(e) for e in powerlist]
        lst.remove(frozenset([]))
        return frozenset(lst)
    elif isinstance(node, ACardExpression):
        aSet = interpret(node.children[0], env)
        return len(aSet)
    elif isinstance(node, AGeneralUnionExpression):
        set_of_sets = interpret(node.children[0], env)
        elem_lst = list(set_of_sets)
        acc = elem_lst[0]
        for aset in elem_lst[1:]:
            acc = acc.union(aset)
        return acc
    elif isinstance(node, AGeneralIntersectionExpression):
        set_of_sets = interpret(node.children[0], env)
        elem_lst = list(set_of_sets)
        acc = elem_lst[0]
        for aset in elem_lst[1:]:
            acc = acc.intersection(aset)
        return acc
    elif isinstance(node, AQuantifiedUnionExpression):
        nodes = []
        idNames = []
        result = frozenset([])
        for idNode in node.children[:node.idNum]:
            assert isinstance(idNode, AIdentifierExpression)
            nodes.append(idNode)
            idNames.append(idNode.idName)
        env.push_new_frame(nodes)
        pred = node.children[-2]
        assert isinstance(pred, Predicate)
        gen = try_all_values(pred, env, idNames)
        while gen.next():
            result |= interpret(node.children[-1], env)
        env.pop_frame()
        return result
    elif isinstance(node, AQuantifiedIntersectionExpression):
        nodes = []
        idNames = []
        result = frozenset([])
        for idNode in node.children[:node.idNum]:
            assert isinstance(idNode, AIdentifierExpression)
            nodes.append(idNode)
            idNames.append(idNode.idName)
        env.push_new_frame(nodes)
        pred = node.children[-2]
        assert isinstance(pred, Predicate)
        gen = try_all_values(pred, env, idNames)
        if gen.next():
            result = interpret(node.children[-1], env)
        while gen.next():
            result &= interpret(node.children[-1], env)
        env.pop_frame()
        return result


# *************************
#
#       2.1 Set predicates
#
# *************************
    elif isinstance(node, ABelongPredicate):
        elm = interpret(node.children[0], env)
        aSet = interpret(node.children[1], env)
        if isinstance(elm,str) and aSet=="":
            return True # FIXME: hack
        return elm in aSet
    elif isinstance(node, ANotBelongPredicate):
        elm = interpret(node.children[0], env)
        aSet = interpret(node.children[1], env)
        return not elm in aSet
    elif isinstance(node, AIncludePredicate):
        aSet1 = interpret(node.children[0], env)
        aSet2 = interpret(node.children[1], env)
        return aSet1.issubset(aSet2)
    elif isinstance(node, ANotIncludePredicate):
        aSet1 = interpret(node.children[0], env)
        aSet2 = interpret(node.children[1], env)
        return not aSet1.issubset(aSet2)
    elif isinstance(node, AIncludeStrictlyPredicate):
        aSet1 = interpret(node.children[0], env)
        aSet2 = interpret(node.children[1], env)
        return aSet1.issubset(aSet2) and aSet1 != aSet2
    elif isinstance(node, ANotIncludeStrictlyPredicate):
        aSet1 = interpret(node.children[0], env)
        aSet2 = interpret(node.children[1], env)
        return not (aSet1.issubset(aSet2) and aSet1 != aSet2)


# *****************
#
#       3. Numbers
#
# *****************
    elif isinstance(node, ANatSetExpression) or isinstance(node, ANaturalSetExpression):
        return frozenset(range(0,max_int+1))
    elif isinstance(node, ANat1SetExpression):
        return frozenset(range(1,max_int+1))
    elif isinstance(node, AMinExpression):
        aSet = interpret(node.children[0], env)
        return min(list(aSet))
    elif isinstance(node, AMaxExpression):
        aSet = interpret(node.children[0], env)
        return max(list(aSet))
    elif isinstance(node, AAddExpression):
        expr1 = interpret(node.children[0], env)
        expr2 = interpret(node.children[1], env)
        return expr1 + expr2
    elif isinstance(node, AMinusOrSetSubtractExpression) or isinstance(node, ASetSubtractionExpression):
        expr1 = interpret(node.children[0], env)
        expr2 = interpret(node.children[1], env)
        return expr1 - expr2
    elif isinstance(node, AMultOrCartExpression):
        expr1 = interpret(node.children[0], env)
        expr2 = interpret(node.children[1], env)
        if isinstance(expr1, frozenset) and isinstance(expr2, frozenset):
            return frozenset(((x,y) for x in expr1 for y in expr2))
        else:
            return expr1 * expr2
    elif isinstance(node, ADivExpression):
        expr1 = interpret(node.children[0], env)
        expr2 = interpret(node.children[1], env)
        return expr1 / expr2
    elif isinstance(node, AModuloExpression):
        expr1 = interpret(node.children[0], env)
        expr2 = interpret(node.children[1], env)
        assert expr2 > 0
        return expr1 % expr2
    elif isinstance(node, APowerOfExpression):
        basis = interpret(node.children[0], env)
        exp = interpret(node.children[1], env)
        return basis ** exp
    elif isinstance(node, AIntervalExpression):
        left = interpret(node.children[0], env)
        right = interpret(node.children[1], env)
        return frozenset(range(left, right+1))
    elif isinstance(node, AGeneralSumExpression):
        sum_ = 0
        # new scope
        env.push_new_frame(node.children[:-2])
        preds = node.children[-2]
        expr = node.children[-1]
        # TODO: this code (maybe) dont checks all possibilities!
        # gen. all values:
        for child in node.children[:-2]:
            # enumeration
            for i in all_values(child, env):
                env.set_value(child.idName, i)
                if interpret(preds, env):
                    sum_ += interpret(expr, env)
        # done
        env.pop_frame()
        return sum_
    elif isinstance(node, AGeneralProductExpression):
        prod = 1
        # new scope
        env.push_new_frame(node.children[:-2])
        preds = node.children[-2]
        expr = node.children[-1]
        # gen. all values:
        # TODO: this code (maybe) dont checks all possibilities!
        for child in node.children[:-2]:
            # enumeration
            for i in all_values(child, env):
                env.set_value(child.idName, i)
                if interpret(preds, env):
                    prod *= interpret(expr, env)
        env.pop_frame()
        return prod


# ***************************
#
#       3.1 Number predicates
#
# ***************************
    elif isinstance(node, AGreaterPredicate):
        expr1 = interpret(node.children[0], env)
        expr2 = interpret(node.children[1], env)
        return expr1 > expr2
    elif isinstance(node, ALessPredicate):
        expr1 = interpret(node.children[0], env)
        expr2 = interpret(node.children[1], env)
        return expr1 < expr2
    elif isinstance(node, AGreaterEqualPredicate):
        expr1 = interpret(node.children[0], env)
        expr2 = interpret(node.children[1], env)
        return expr1 >= expr2
    elif isinstance(node, ALessEqualPredicate):
        expr1 = interpret(node.children[0], env)
        expr2 = interpret(node.children[1], env)
        return expr1 <= expr2


# ******************
#
#       4. Relations
#
# ******************
    elif isinstance(node, ARelationsExpression):
        aSet1 = interpret(node.children[0], env)
        aSet2 = interpret(node.children[1], env)
        aSet = make_set_of_realtions(aSet1, aSet2)
        return aSet
    elif isinstance(node, ADomainExpression):
        # FIXME: crashs if this is not a set of 2-tuple
        aSet = interpret(node.children[0], env)
        dom = [e[0] for e in list(aSet)]
        return frozenset(dom)
    elif isinstance(node, ARangeExpression):
        # FIXME: crashs if this is not a set of 2-tuple
        aSet = interpret(node.children[0], env)
        ran = [e[1] for e in list(aSet)]
        return frozenset(ran)
    elif isinstance(node, ACompositionExpression):
        aSet1 = interpret(node.children[0], env)
        aSet2 = interpret(node.children[1], env)
        new_rel = [(p[0],q[1]) for p in aSet1 for q in aSet2 if p[1]==q[0]]
        return frozenset(new_rel)
    elif isinstance(node, AIdentityExpression):
        aSet = interpret(node.children[0], env)
        id_r = [(x,x) for x in aSet]
        return frozenset(id_r)
    elif isinstance(node, ADomainRestrictionExpression):
        aSet = interpret(node.children[0], env)
        rel = interpret(node.children[1], env)
        new_rel = [x for x in rel if x[0] in aSet]
        return frozenset(new_rel)
    elif isinstance(node, ADomainSubtractionExpression):
        aSet = interpret(node.children[0], env)
        rel = interpret(node.children[1], env)
        new_rel = [x for x in rel if not x[0] in aSet]
        return frozenset(new_rel)
    elif isinstance(node, ARangeRestrictionExpression):
        aSet = interpret(node.children[1], env)
        rel = interpret(node.children[0], env)
        new_rel = [x for x in rel if x[1] in aSet]
        return frozenset(new_rel)
    elif isinstance(node, ARangeSubtractionExpression):
        aSet = interpret(node.children[1], env)
        rel = interpret(node.children[0], env)
        new_rel = [x for x in rel if not x[1] in aSet]
        return frozenset(new_rel)
    elif isinstance(node, AReverseExpression):
        rel = interpret(node.children[0], env)
        new_rel = [(x[1],x[0]) for x in rel]
        return frozenset(new_rel)
    elif isinstance(node, AImageExpression):
        rel = interpret(node.children[0], env)
        aSet = interpret(node.children[1], env)
        image = [x[1] for x in rel if x[0] in aSet ]
        return frozenset(image)
    elif isinstance(node, AOverwriteExpression):
        r1 = interpret(node.children[0], env)
        r2 = interpret(node.children[1], env)
        dom_r2 = [x[0] for x in r2]
        new_r  = [x for x in r1 if x[0] not in dom_r2]
        r2_list= [x for x in r2]
        return frozenset(r2_list + new_r)
    elif isinstance(node, ADirectProductExpression):
        p = interpret(node.children[0], env)
        q = interpret(node.children[1], env)
        d_prod = [(x[0],(x[1],y[1])) for x in p for y in q if x[0]==y[0]]
        return frozenset(d_prod)
    elif isinstance(node, AParallelProductExpression):
        p = interpret(node.children[0], env)
        q = interpret(node.children[1], env)
        p_prod = [((x[0],y[0]),(x[1],y[1])) for x in p for y in q]
        return frozenset(p_prod)
    elif isinstance(node, AIterationExpression):
        arel = interpret(node.children[0], env)
        n = interpret(node.children[1], env)
        assert n>=0
        rel = list(arel)
        rel = [(x[0],x[0]) for x in rel]
        for i in range(n):
            rel = [(y[0],x[1]) for y in rel for x in arel if y[1]==x[0]]
        return frozenset(rel)
    elif isinstance(node, AReflexiveClosureExpression):
        arel = interpret(node.children[0], env)
        rel = list(arel)
        temp = [(x[1],x[1]) for x in rel] # also image
        rel = [(x[0],x[0]) for x in rel]
        rel += temp
        rel = list(frozenset(rel)) # throw away doubles
        while True: # fixpoint-search (do-while-loop)
            new_rel = [(y[0],x[1]) for y in rel for x in arel if y[1]==x[0]]
            if frozenset(new_rel).union(frozenset(rel))==frozenset(rel):
                return frozenset(rel)
            rel =list(frozenset(new_rel).union(frozenset(rel)))
    elif isinstance(node, AClosureExpression):
        arel = interpret(node.children[0], env)
        rel = list(arel)
        while True: # fixpoint-search (do-while-loop)
            new_rel = [(y[0],x[1]) for y in rel for x in arel if y[1]==x[0]]
            if frozenset(new_rel).union(frozenset(rel))==frozenset(rel):
                return frozenset(rel)
            rel =list(frozenset(new_rel).union(frozenset(rel)))
    elif isinstance(node, AFirstProjectionExpression):
        S = interpret(node.children[0], env)
        T = interpret(node.children[1], env)
        cart = frozenset(((x,y) for x in S for y in T))
        proj = [(x,x[0]) for x in cart]
        return frozenset(proj)
    elif isinstance(node, ASecondProjectionExpression):
        S = interpret(node.children[0], env)
        T = interpret(node.children[1], env)
        cart = frozenset(((x,y) for x in S for y in T))
        proj = [(x,x[1]) for x in cart]
        return frozenset(proj)



# *******************
#
#       4.1 Functions
#
# *******************
    elif isinstance(node, APartialFunctionExpression):
        S = interpret(node.children[0], env)
        T = interpret(node.children[1], env)
        relation_set = make_set_of_realtions(S,T) # S<-->T
        fun = filter_no_function(relation_set) # S+->T
        return fun
    elif isinstance(node, ATotalFunctionExpression):
        S = interpret(node.children[0], env)
        T = interpret(node.children[1], env)
        relation_set = make_set_of_realtions(S,T) # S<-->T
        fun = filter_no_function(relation_set) # S+->T
        total_fun = filter_not_total(fun, S) # S-->T
        return total_fun
    elif isinstance(node, APartialInjectionExpression):
        S = interpret(node.children[0], env)
        T = interpret(node.children[1], env)
        relation_set = make_set_of_realtions(S,T) # S<-->T
        fun = filter_no_function(relation_set) # S+->T
        inj_fun = filter_not_injective(fun) # S>+>T
        return inj_fun
    elif isinstance(node, ATotalInjectionExpression):
        S = interpret(node.children[0], env)
        T = interpret(node.children[1], env)
        relation_set = make_set_of_realtions(S,T) # S<-->T
        fun = filter_no_function(relation_set) # S+->T
        inj_fun = filter_not_injective(fun) # S>+>T
        total_inj_fun = filter_not_total(inj_fun, S) # S>->T
        return total_inj_fun
    elif isinstance(node, APartialSurjectionExpression):
        S = interpret(node.children[0], env)
        T = interpret(node.children[1], env)
        relation_set = make_set_of_realtions(S,T) # S<-->T
        fun = filter_no_function(relation_set) # S+->T
        surj_fun = filter_not_surjective(fun, T) # S+->>T
        return surj_fun
    elif isinstance(node, ATotalSurjectionExpression):
        S = interpret(node.children[0], env)
        T = interpret(node.children[1], env)
        relation_set = make_set_of_realtions(S,T) # S<-->T
        fun = filter_no_function(relation_set) # S+->T
        surj_fun = filter_not_surjective(fun, T) # S+->>T
        total_surj_fun = filter_not_total(surj_fun, S) # S-->>T
        return total_surj_fun
    elif isinstance(node, ATotalBijectionExpression):
        S = interpret(node.children[0], env)
        T = interpret(node.children[1], env)
        relation_set = make_set_of_realtions(S,T) # S<-->T
        fun = filter_no_function(relation_set) # S+->T
        inj_fun = filter_not_injective(fun) # S>+>T
        total_inj_fun = filter_not_total(inj_fun, S) # S>->T
        bij_fun = filter_not_surjective(total_inj_fun,T) # S>->>T
        return bij_fun
    elif isinstance(node, APartialBijectionExpression):
        S = interpret(node.children[0], env)
        T = interpret(node.children[1], env)
        relation_set = make_set_of_realtions(S,T) # S<-->T
        fun = filter_no_function(relation_set) # S+->T
        inj_fun = filter_not_injective(fun) # S>+>T
        bij_fun = filter_not_surjective(inj_fun,T)
        return bij_fun
    elif isinstance(node, ALambdaExpression):
        func_list = []
        # new scope
        env.push_new_frame(node.children[:-2])
        pred = node.children[-2]
        expr = node.children[-1]
        # TODO: this code (maybe) dont checks all possibilities!
        # gen. all values:
        for child in node.children[:-2]:
            # enumeration
            for i in all_values(child, env):
                env.set_value(child.idName, i)
                if interpret(pred, env):
                    image = interpret(expr, env)
                    tup = tuple([i, image])
                    func_list.append(tup)
        # done
        env.pop_frame()
        return frozenset(func_list)
    elif isinstance(node, AFunctionExpression):
        if isinstance(node.children[0], APredecessorExpression):
            value = interpret(node.children[1], env)
            return value-1
        if isinstance(node.children[0], ASuccessorExpression):
            value = interpret(node.children[1], env)
            return value+1
        function = interpret(node.children[0], env)
        args = [] 
        for child in node.children[1:]:
            arg = interpret(child, env)
            args.append(arg)
        if len(args) > 1:
            return get_image(function, tuple(args))
        else:
            return get_image(function, args[0])


# ********************
#
#       4.2 Sequences
#
# ********************
    elif isinstance(node,AEmptySequenceExpression):
        return frozenset([])
    elif isinstance(node,ASeqExpression):
        S = interpret(node.children[0], env)
        sequence_list = [frozenset([])]
        max_len = 1
        # find all seq. from 1..max_int
        for i in range(1,max_int+1):
            sequence_list += create_all_seq_w_fixlen(list(S),i)
        return frozenset(sequence_list)
    elif isinstance(node,ASeq1Expression):
        S = interpret(node.children[0], env)
        sequence_list = []
        max_len = 1
        # find all seq. from 1..max_int
        for i in range(1,max_int+1):
            sequence_list += create_all_seq_w_fixlen(list(S),i)
        return frozenset(sequence_list)
    elif isinstance(node,AIseqExpression):
        # TODO: this can be impl. much better
        S = interpret(node.children[0], env)
        sequence_list = [frozenset([])]
        max_len = 1
        # find all seq from 1..max_int
        for i in range(1,max_int+1):
            sequence_list += create_all_seq_w_fixlen(list(S),i)
        inj_sequence_list = filter_not_injective(sequence_list)
        return frozenset(inj_sequence_list)
    elif isinstance(node, AIseq1Expression):
        # TODO: this can be impl. much better
        S = interpret(node.children[0], env)
        sequence_list = [frozenset([])]
        max_len = 1
        # find all seq from 1..max_int
        for i in range(1,max_int+1):
            sequence_list += create_all_seq_w_fixlen(list(S),i)
        inj_sequence_list = filter_not_injective(sequence_list)
        return frozenset(inj_sequence_list)
    elif isinstance(node,APermExpression): 
        # TODO: this can be impl. much better
        S = interpret(node.children[0], env)
        sequence_list = [frozenset([])]
        max_len = 1
        # TODO: maybe call all_values() here...
        # find all seq from 1..max_int
        for i in range(1,max_int+1):
            sequence_list += create_all_seq_w_fixlen(list(S),i)
        inj_sequence_list = filter_not_injective(sequence_list)
        perm_sequence_list = filter_not_surjective(inj_sequence_list, S)
        return frozenset(perm_sequence_list)
    elif isinstance(node, AConcatExpression):
        s = interpret(node.children[0], env)
        t = interpret(node.children[1], env)
        new_t = []
        for tup in t: # FIXME: maybe wrong order
            new_t.append(tuple([tup[0]+len(s),tup[1]]))
        return frozenset(list(s)+new_t)
    elif isinstance(node, AInsertFrontExpression):
        E = interpret(node.children[0], env)
        s = interpret(node.children[1], env)
        new_s = [(1,E)]
        for tup in s:
            new_s.append(tuple([tup[0]+1,tup[1]]))
        return frozenset(new_s)
    elif isinstance(node, AInsertTailExpression):
        s = interpret(node.children[0], env)
        E = interpret(node.children[1], env)
        return frozenset(list(s)+[tuple([len(s)+1,E])])
    elif isinstance(node, ASequenceExtensionExpression):
        sequence = []
        i = 0
        for child in node.children:
            i = i+1
            e = interpret(child, env)
            sequence.append(tuple([i,e]))
        return frozenset(sequence)
    elif isinstance(node, ASizeExpression):
        sequence = interpret(node.children[0], env)
        return len(sequence)
    elif isinstance(node, ARevExpression):
        sequence = interpret(node.children[0], env)
        new_sequence = []
        i = len(sequence)
        for tup in sequence:
            new_sequence.append(tuple([i,tup[1]]))
            i = i-1
        return frozenset(new_sequence)
    elif isinstance(node, ARestrictFrontExpression):
        sequence = interpret(node.children[0], env)
        take = interpret(node.children[1], env)
        assert take>0
        lst = list(sequence)
        lst.sort()
        return frozenset(lst[:-take])
    elif isinstance(node, ARestrictTailExpression):
        sequence = interpret(node.children[0], env)
        drop = interpret(node.children[1], env)
        assert drop>0
        lst = list(sequence)
        lst.sort()
        new_list = []
        i = 0
        for tup in lst[drop:]:
            i = i+1
            new_list.append(tuple([i,tup[1]]))
        return frozenset(new_list)
    elif isinstance(node, AFirstExpression):
        sequence = interpret(node.children[0], env)
        lst = list(sequence)
        lst.sort()
        assert lst[0][0]==1
        return lst[0][1]
    elif isinstance(node, ALastExpression):
        sequence = interpret(node.children[0], env)
        lst = list(sequence)
        lst.sort()
        assert lst[len(sequence)-1][0]==len(sequence)
        return lst[len(sequence)-1][1]
    elif isinstance(node, ATailExpression):
        sequence = interpret(node.children[0], env)
        lst = list(sequence)
        lst.sort()
        assert lst[0][0]==1
        return frozenset(lst[1:])
    elif isinstance(node, AFrontExpression):
        sequence = interpret(node.children[0], env)
        lst = list(sequence)
        lst.sort()
        lst.pop()
        return frozenset(lst)
    elif isinstance(node, AGeneralConcatExpression):
        s = interpret(node.children[0], env)
        t = []
        index = 0
        for squ in dict(s).values():
            for val in dict(squ).values():
                index = index +1
                t.append(tuple([index, val]))
        return frozenset(t)
    elif isinstance(node, AStringExpression):
        return node.string


# ****************
#
# 5. Substitutions
#
# ****************
    elif isinstance(node, ASkipSubstitution):
        pass
    elif isinstance(node, AAssignSubstitution):
        assert int(node.lhs_size) == int(node.rhs_size)
        for i in range(int(node.lhs_size)):
            lhs_node = node.children[i]
            rhs = node.children[i+int(node.rhs_size)]
            value = interpret(rhs, env)
            if isinstance(lhs_node, AIdentifierExpression): 
                env.set_value(lhs_node.idName, value)
            else:
                assert isinstance(lhs_node, AFunctionExpression)
                assert isinstance(lhs_node.children[0], AIdentifierExpression)
                func_name = lhs_node.children[0].idName
                # get args
                args = []
                for child in lhs_node.children[1:]:
                    arg = interpret(child, env)
                    args.append(arg)
                func = dict(env.get_value(func_name))
                # change
                if len(args)==1:
                    func[args[0]] = value
                else:
                    func[tuple(args)] = value
                # convert back
                lst = []
                for key in func:
                    lst.append(tuple([key,func[key]]))
                new_func = frozenset(lst)
                # write to env
                env.set_value(func_name, new_func)
    elif isinstance(node, AConvertBoolExpression):
        return interpret(node.children[0], env)
    elif isinstance(node, ABecomesElementOfSubstitution):
        values = interpret(node.children[-1], env)
        value = list(values)[0] # XXX
        for child in node.children[:-1]:
            assert isinstance(child, AIdentifierExpression)
            env.set_value(child.idName, value)
    elif isinstance(node, ABecomesSuchSubstitution):
        # TODO: more than on ID
        ids = []
        nodes = []
        for child in node.children[:-1]:
            assert isinstance(child, AIdentifierExpression)
            ids.append(child.idName)
            nodes.append(child)
        # new frame to enable primed-ids
        env.push_new_frame(nodes)
        gen = try_all_values(node.children[-1], env, ids) 
        gen.next() # sideeffect: set values
        results = []
        for i in ids:
            results.append(env.get_value(i))
        env.pop_frame()
        # write back
        for i in range(len(ids)):
            env.set_value(ids[i], results[i])
    elif isinstance(node, AParallelSubstitution) or isinstance(node, ASequenceSubstitution):
        for child in node.children:
            interpret(child, env)


# **********************
#
# 5.1. Alternative Syntax
#
# ***********************
    elif isinstance(node, ABlockSubstitution):
        for child in node.children:
            interpret(child, env)
    elif isinstance(node, APreconditionSubstitution):
        assert isinstance(node.children[0], Predicate)
        assert isinstance(node.children[1], Substitution)
        condition = interpret(node.children[0], env)
        if condition:
            interpret(node.children[1], env)
            return
    elif isinstance(node, AAssertionSubstitution):
        assert isinstance(node.children[0], Predicate)
        assert isinstance(node.children[1], Substitution)
        assert interpret(node.children[0], env)
        interpret(node.children[1], env)
    elif isinstance(node, AIfSubstitution):
        assert isinstance(node.children[0], Predicate)
        assert isinstance(node.children[1], Substitution)
        condition = interpret(node.children[0], env)
        if condition:
            interpret(node.children[1], env)
            return
        for child in node.children[2:]:
            if isinstance(child, AIfElsifSubstitution):
                assert isinstance(child.children[0], Predicate)
                assert isinstance(child.children[1], Substitution)
                condition = interpret(child.children[0], env)
                if condition:
                    interpret(child.children[1], env)
                    return
            else:
                # ELSE (B Level)
                assert isinstance(child, Substitution)
                assert child==node.children[-1] # last child
                interpret(child, env)
                return
    elif isinstance(node, AChoiceSubstitution):
        assert isinstance(node.children[0], Substitution)
        for child in node.children[1:]:
            assert isinstance(child, AChoiceOrSubstitution)
        # TODO: random choice
        return interpret(node.children[0], env)
    elif isinstance(node, ASelectSubstitution):
        nodes = []
        assert isinstance(node.children[0], Predicate)
        assert isinstance(node.children[1], Substitution)
        if interpret(node.children[0], env):
            nodes.append(node.children[1])
        for child in node.children[2:]:
            if isinstance(child, ASelectWhenSubstitution):
                assert isinstance(child.children[0], Predicate)
                assert isinstance(child.children[1], Substitution)
                if interpret(child.children[0], env):
                    nodes.append(child.children[1])
            else:
                assert isinstance(child, Substitution)
                assert child==node.children[-1]
        if not nodes == []:
            # TODO: random choice
            interpret(nodes[0], env)
        elif not isinstance(node.children[-1], ASelectSubstitution):
            interpret(node.children[-1], env)
    elif isinstance(node, ACaseSubstitution):
        assert isinstance(node.children[0], Expression)
        elem = interpret(node.children[0], env)
        for child in node.children[1:1+node.expNum]:
            assert isinstance(child, Expression)
            value = interpret(child, env)
            if elem == value:
                assert isinstance(node.children[node.expNum+1], Substitution)
                interpret(node.children[node.expNum+1], env)
                return
        for child in node.children[2+node.expNum:]:
            if isinstance(child, ACaseOrSubstitution):
                for expNode in child.children[:child.expNum]:
                    assert isinstance(expNode, Expression)
                    value = interpret(expNode, env)
                    if elem == value:
                        assert isinstance(child.children[-1], Substitution)
                        interpret(child.children[-1], env)
                        return
            else:
                assert isinstance(child, Substitution)
                assert child==node.children[-1]
                interpret(child, env)
                return
    elif isinstance(node, AVarSubstitution):
        nodes = []
        for idNode in node.children[:-1]:
            assert isinstance(idNode, AIdentifierExpression)
            nodes.append(idNode)
        env.push_new_frame(nodes)
        interpret(node.children[-1], env)
        env.pop_frame()
    elif isinstance(node, AAnySubstitution) or isinstance(node, ALetSubstitution):
        nodes = []
        idNames = []
        for idNode in node.children[:node.idNum]:
            assert isinstance(idNode, AIdentifierExpression)
            nodes.append(idNode)
            idNames.append(idNode.idName)
        pred = node.children[-2]
        assert isinstance(pred, Predicate)
        assert isinstance(node.children[-1], Substitution)
        env.push_new_frame(nodes)
        gen = try_all_values(pred, env, idNames)
        if gen.next():
            interpret(node.children[-1], env)
        env.pop_frame()


# ****************
#
# 6. Miscellaneous
#
# ****************
    elif isinstance(node,AUnaryExpression):
        result = interpret(node.children[0], env)
        return result*(-1)
    elif isinstance(node, AIntegerExpression):
        return node.intValue
    elif isinstance(node, AMinIntExpression):
        return min_int
    elif isinstance(node, AMaxIntExpression):
        return max_int
    elif isinstance(node, AIdentifierExpression):
        return env.get_value(node.idName)
    elif isinstance(node, APrimedIdentifierExpression):
        assert len(node.children)==1 # TODO x.y.z
        assert node.grade==0 #TODO: fix for while loop
        assert isinstance(node.children[0], AIdentifierExpression)
        id_Name = node.children[0].idName
        # copy paste :-)
        assert isinstance(id_Name, str)
        value_map_copy =  [x for x in env.value_stack] # no ref. copy
        # pop frame to get old value (you are inside an enumeration):
        value_map_copy.pop()
        value_map_copy.reverse() # FIXME
        stack_depth = len(value_map_copy)
        # lookup:
        for i in range(stack_depth):
            try:
                return value_map_copy[i][id_Name]
            except KeyError:
                continue
        print "LookupErr:", id_Name
        raise KeyError
    elif isinstance(node, ABoolSetExpression):
        return frozenset([True,False])
    elif isinstance(node, ATrueExpression):
        return True
    elif isinstance(node, AFalseExpression):
        return False
    elif isinstance(node, ADefinitionExpression) or isinstance(node, ADefinitionPredicate):
        # i hope this is faster than rebuilding asts...
        ast = env.get_ast_by_definition(node.idName)
        assert isinstance(ast, AExpressionDefinition) or isinstance(ast, APredicateDefinition)
        # The Value of the definition depends on
        # the Value of the parameters
        nodes = []
        for i in range(ast.paraNum):
            if isinstance(ast.children[i], AIdentifierExpression):
                nodes.append(ast.children[i])
            else:
                raise Exception("Parametes can only be Ids at the moment!")
        env.push_new_frame(nodes)
        # set nodes(variables) to values
        for i in range(ast.paraNum):
            value = interpret(node.children[i], env)
            nothing = interpret(ast.children[i], env)
            assert nothing==ast.children[i].idName # no value
            env.set_value(ast.children[i].idName, value)
        result = interpret(ast.children[-1], env)
        env.pop_frame()
        return result
    elif isinstance(node, ADefinitionSubstitution):
        import copy
        ast = env.get_ast_by_definition(node.idName)
        new_ast = copy.deepcopy(ast)
        #_print_ast(ast)
        assert isinstance(ast, ASubstitutionDefinition)
        for i in range(ast.paraNum):
            idNode = ast.children[i]
            isinstance(idNode, AIdentifierExpression)
            replaceNode = node.children[i]
            new_ast = replace_node(new_ast, idNode, replaceNode)
        #_print_ast(new_ast)
        return interpret(new_ast.children[-1], env)
    elif isinstance(node, AStructExpression):
        dictionary = {}
        for rec_entry in node.children:
            assert isinstance(rec_entry, ARecEntry)
            name = ""
            if isinstance(rec_entry.children[0], AIdentifierExpression):
                name = rec_entry.children[0].idName
            assert isinstance(rec_entry.children[-1], Expression)
            value = interpret(rec_entry.children[-1], env)
            dictionary[name] = value
        res = []
        all_records(dictionary, res, {}, 0)
        result = []
        for dic in res:
            for entry in dic:
                result.append(tuple([entry,dic[entry]]))
        return frozenset(result)
    elif isinstance(node, ARecExpression):
        result = []
        for rec_entry in node.children:
            assert isinstance(rec_entry, ARecEntry)
            name = ""
            if isinstance(rec_entry.children[0], AIdentifierExpression):
                name = rec_entry.children[0].idName
            assert isinstance(rec_entry.children[-1], Expression)
            value = interpret(rec_entry.children[-1], env)
            result.append(tuple([name,value]))
        return frozenset(result)
    elif isinstance(node, ARecordFieldExpression):
        record = interpret(node.children[0], env)
        assert isinstance(node.children[1], AIdentifierExpression)
        name = node.children[1].idName
        for entry in record:
            if entry[0]==name:
                return entry[1]
        raise Exception("wrong entry:", name)
    elif isinstance(node, AStringSetExpression):
        return "" # TODO: return set of "all" strings
    else:
        raise Exception("Unknown Node: %s",node)


def replace_node(ast, idNode, replaceNode):
    if isinstance(ast, AIdentifierExpression) or isinstance(ast, AStringExpression) or isinstance(ast, AIntegerExpression):
        return ast
    for i in range(len(ast.children)):
        child = ast.children[i]
        if isinstance(child, AIdentifierExpression):
            if child.idName == idNode.idName:
                ast.children[i] = replaceNode
        else:
            replace_node(child, idNode, replaceNode)
    return ast


def _print_ast(root):
    print root
    __print_ast(root, 1)
    print


def __print_ast(node, num):
    if isinstance(node, AIdentifierExpression) or isinstance(node, AStringExpression) or isinstance(node, AIntegerExpression):
        return
    for child in node.children:
        print "\t"*num,"|-",child
        __print_ast(child, num+1)


# WARNING: this could take some time...
def all_records(value_dict, result, acc, index):
    if len(value_dict)==index:
        import copy
        result.append(copy.deepcopy(acc))
    else:
        name = list(value_dict.keys())[index]
        values = list(value_dict.values())[index]
        for v in values:
            acc[name] = v
            all_records(value_dict, result, acc, index+1)


# WARNING: this could take some time...
def create_all_seq_w_fixlen(images, length):
    result = []
    basis = len(images)
    noc = basis**length # number of combinations
    for i in range(noc):
        lst = create_sequence(images, i, length)
        result.append(frozenset(lst))
    return result


def create_sequence(images, number, length):
    result = []
    basis = len(images)
    for i in range(length):
        symbol = tuple([i+1,images[number % basis]])
        result.append(symbol)
        number /= basis
    result.reverse()
    return result


# [[1,2],[3,[[4]]]] -> [1,2,3,4]
def flatten(lst, res):
    for e in lst:
        if not isinstance(e,list):
            res.append(e)
        else:
            res = flatten(e, res)
    return res


def is_flat(lst):
    for e in lst:
        if isinstance(e, list):
            return False
    return True
def get_image(function, preimage):
    for atuple in function:
        if atuple[0] == preimage:
            return atuple[1]
    return None #no image found


# checks if a list contains a duplicate element
def double_element_check(lst):
    for element in lst:
        if lst.count(element)>1:
            return True
    return False


# filters out every function which is not injective
def filter_not_injective(functions):
    injective_funs = []
    for fun in functions:
        image = [x[1] for x in fun]
        if not double_element_check(image):
            injective_funs.append(fun)
    return frozenset(injective_funs)


# filters out every function which is not surjective
def filter_not_surjective(functions, T):
    surj_funs = []
    for fun in functions:
        if is_a_surj_function(fun, T):
            surj_funs.append(fun)
    return frozenset(surj_funs)


# filters out every function which is not total
def filter_not_total(functions, S):
    total_funs = []
    for fun in functions:
        if is_a_total_function(fun, S):
            total_funs.append(fun)
    return frozenset(total_funs)


# checks if the function it total 
def is_a_total_function(function, preimage_set):
    preimage = [x[0] for x in function]
    preimage_set2 =  frozenset(preimage)
    return preimage_set == preimage_set2


# checks if the function it surjective
def is_a_surj_function(function, image_set):
    image = [x[1] for x in function]
    image_set2= frozenset(image) # remove duplicate items
    return image_set == image_set2


# filters out every set which is no function
def filter_no_function(relations):
    functions = []
    for r in relations:
        if is_a_function(r):
            functions.append(r)
    return frozenset(functions)


# checks if a relation is a function
def is_a_function(relation):
    preimage_set = [x[0] for x in relation]
    if double_element_check(preimage_set):
        return False
    else:
        return True


# returns S<-->T
def make_set_of_realtions(S,T):
    cartSet = frozenset(((x,y) for x in S for y in T))
    res = powerset(cartSet)
    powerlist = list(res)
    lst = [frozenset(e) for e in powerlist]
    return frozenset(lst)


# from http://docs.python.org/library/itertools.html
# WARNING: this could take some time...
def powerset(iterable):
    "powerset([1,2,3]) --> () (1,) (2,) (3,) (1,2) (1,3) (2,3) (1,2,3)"
    from itertools import chain, combinations
    s = list(iterable)
    return chain.from_iterable(combinations(s, r) for r in range(len(s)+1))


# FIXME: rename quantified variables!
def set_comprehension_recursive_helper(depth, max_depth, node, env):
    result = []
    pred = node.children[len(node.children) -1]
    idName = node.children[depth].idName
    if depth == max_depth: #basecase
        for i in all_values(node.children[depth], env):
            env.set_value(idName, i)
            if interpret(pred, env):
                result.append(i)
        return result
    else: # recursive call
        for i in all_values(node.children[depth], env):
            env.set_value(idName, i)
            partial_result = set_comprehension_recursive_helper(depth+1, max_depth, node, env)
            for j in partial_result:
                temp = []
                temp.append(i)
                temp.append(j)
                result.append(temp)
        return result


def exist_recursive_helper(depth, max_depth, node, env):
    pred = node.children[len(node.children) -1]
    idName = node.children[depth].idName
    if depth == max_depth: #basecase
        for i in all_values(node.children[depth], env):
            env.set_value(idName, i)
            if interpret(pred, env):
                return True
        return False
    else: # recursive call
        for i in all_values(node.children[depth], env):
            env.set_value(idName, i)
            if exist_recursive_helper(depth+1, max_depth, node, env):
                return True
        return False



def forall_recursive_helper(depth, max_depth, node, env):
    pred = node.children[len(node.children) -1]
    idName = node.children[depth].idName
    if depth == max_depth: #basecase
        for i in all_values(node.children[depth], env):
            env.set_value(idName, i)
            if not interpret(pred, env):
                return False
        return True
    else: # recursive call
        for i in all_values(node.children[depth], env):
            env.set_value(idName, i)
            if not forall_recursive_helper(depth+1, max_depth, node, env):
                return False
        return True


# ** THE ENUMERATOR **
# returns a list with "all" possible values of a type
# only works if the typechecking/typing of typeit was successful
def all_values(node, env):
    assert isinstance(node, AIdentifierExpression)
    atype = env.get_type_by_node(node)
    return all_values_by_type(atype, env)


def all_values_by_type(atype, env):
    if isinstance(atype, IntegerType):
        return range(min_int, max_int+1)
    elif isinstance(atype, BoolType):
        return [True, False]
    elif isinstance(atype, SetType):
        type_name =  atype.data
        assert isinstance(env.get_value(type_name), frozenset)
        return env.get_value(type_name)
    elif isinstance(atype, PowerSetType):
        val_list = all_values_by_type(atype.data, env)
        res = powerset(val_list)
        powerlist = list(res)
        lst = [frozenset(e) for e in powerlist]
        return lst
    elif isinstance(atype, CartType):
        val_pi = all_values_by_type(atype.data[0], env)
        val_i = all_values_by_type(atype.data[1], env)
        lst = frozenset(((x,y) for x in val_pi for y in val_i))
        return lst
    string = "Unknown Type / Not Implemented: %s", atype
    raise Exception(string)


def try_all_values(root, env, idNames):
    name = idNames[0]
    atype = env.get_type(name)
    all_values = all_values_by_type(atype, env)
    if len(idNames)<=1:
        for val in all_values:
            env.set_value(name, val)
            if interpret(root, env):
                yield True
    else:
        for val in all_values:
            env.set_value(name, val)
            gen = try_all_values(root, env, idNames[1:])
            if gen.next():
                yield True
    yield False