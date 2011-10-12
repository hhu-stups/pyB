# -*- coding: utf-8 -*-
from ast_nodes import *
from typing import typeit, IntegerType, PowerSetType, SetType

min_int = -1
max_int = 5

class Environment():
    def __init__(self):
        # TODO: del maps
        self.variable_values = {} 
        self.variable_type = {}  
        # values of global and local vars vv: str->val
        self.vv_stack = [{}]
        # types of global and local vars vt: str->str or str->type
        self.vt_stack = [self.variable_type]


    def get_value(self, id_Name):
        value_map_copy =  [x for x in self.vv_stack] # no ref. copy
        value_map_copy.reverse()
        # lookup:
        for i in range(len(value_map_copy)):
            try:
                return value_map_copy[i][id_Name]
            except KeyError:
                continue
        # no ID known, if the inerp called that inside
        # an ID-Node the keyerror is used to add a (maybe quantified) var
        raise KeyError 

    # TODO: lookup + Throw Typeerror:
    # TODO: set-lookup tests
    def set_value(self, id_Name, value):
        top_map = self.vv_stack[-1]
        top_map[id_Name] = value


    # Throws Keyerror if lookpup fails: for add Id
    def get_type(self, id_Name):
        type_map_copy = [x for x in self.vt_stack] # no ref. copy
        type_map_copy.reverse()
        # lookup:
        for i in range(len(type_map_copy)):
            try:
                return type_map_copy[i][id_Name]
            except KeyError:
                continue
        # no ID known, if the inerp called that inside
        # an ID-Node the keyerror is used to add a (maybe quantified) var
        raise KeyError 

    # XXX: maybe lookup
    # returns the topframe
    def get_all_types(self):
        return self.vt_stack[-1]

    # TODO: lookup
    def set_type(self, id_Name, atype):
        top_map = self.vt_stack[-1]
        top_map[id_Name] = atype

    # new scope:
    # push a new frame with new local vars
    def push_new_frame(self, nodes, ids):
        self.vv_stack.append({})
        type_map = {}
        for i in ids:
            assert isinstance(i, str)
            type_map[i] = i
        self.vt_stack.append(type_map)
        # FIXME: Typecheck on the fly
        for node in nodes: # Side-Effect: changes vv and vt_stack
            typeit(node, self)

    # leave scope:
    def pop_frame(self):
        self.vv_stack.pop()
        self.vt_stack.pop()


def interpret(node, env):
    if isinstance(node, AConjunctPredicate):
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
    elif isinstance(node, AEqualPredicate):
        expr1 = interpret(node.children[0], env)
        expr2 = interpret(node.children[1], env)
        return expr1 == expr2
    elif isinstance(node, AUnequalPredicate):
        expr1 = interpret(node.children[0], env)
        expr2 = interpret(node.children[1], env)
        return expr1 != expr2
    elif isinstance(node, AGreaterPredicate):
        expr1 = interpret(node.children[0], env)
        expr2 = interpret(node.children[1], env)
        return expr1 > expr2
    elif isinstance(node, AGreaterEqualPredicate):
        expr1 = interpret(node.children[0], env)
        expr2 = interpret(node.children[1], env)
        return expr1 >= expr2
    elif isinstance(node, ALessPredicate):
        expr1 = interpret(node.children[0], env)
        expr2 = interpret(node.children[1], env)
        return expr1 < expr2
    elif isinstance(node, ALessEqualPredicate):
        expr1 = interpret(node.children[0], env)
        expr2 = interpret(node.children[1], env)
        return expr1 <= expr2
    elif isinstance(node, ANegationPredicate):
        expr = interpret(node.children[0], env)
        return not expr
    elif isinstance(node, AIntegerExpression):
        return node.intValue
    elif isinstance(node, AAddExpression):
        expr1 = interpret(node.children[0], env)
        expr2 = interpret(node.children[1], env)
        return expr1 + expr2
    elif isinstance(node, AMinusOrSetSubtractExpression):
        expr1 = interpret(node.children[0], env)
        expr2 = interpret(node.children[1], env)
        return expr1 - expr2
    elif isinstance(node, AMultOrCartExpression):
        expr1 = interpret(node.children[0], env)
        expr2 = interpret(node.children[1], env)
        if isinstance(expr1, set) and isinstance(expr2, set):
            return set(((x,y) for x in expr1 for y in expr2))
        else:
            return expr1 * expr2
    elif isinstance(node, ADivExpression):
        expr1 = interpret(node.children[0], env)
        expr2 = interpret(node.children[1], env)
        return expr1 / expr2
    elif isinstance(node, AModuloExpression):
        expr1 = interpret(node.children[0], env)
        expr2 = interpret(node.children[1], env)
        return expr1 % expr2
    elif isinstance(node, AIdentifierExpression):
        return env.get_value(node.idName)
    elif isinstance(node, ABelongPredicate):
        elm = interpret(node.children[0], env)
        aSet = interpret(node.children[1], env)
        return elm in aSet
    elif isinstance(node, ANotBelongPredicate):
        elm = interpret(node.children[0], env)
        aSet = interpret(node.children[1], env)
        return not elm in aSet
    elif isinstance(node, ASetExtensionExpression):
        lst = []
        for child in node.children:
            elm = interpret(child, env)
            lst.append(elm)
        return set(lst)
    elif isinstance(node, ACardExpression):
        aSet = interpret(node.children[0], env)
        return len(aSet)
    elif isinstance(node, AEmptySetExpression):
        return set()
    elif isinstance(node, AUnionExpression):
        aSet1 = interpret(node.children[0], env)
        aSet2 = interpret(node.children[1], env)
        return aSet1.union(aSet2)
    elif isinstance(node, AIntersectionExpression):
        aSet1 = interpret(node.children[0], env)
        aSet2 = interpret(node.children[1], env)
        return aSet1.intersection(aSet2)
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
    elif isinstance(node, AUniversalQuantificationPredicate):
        max_depth = len(node.children) -2
        if not forall_recursive_helper(0, max_depth, node, env):
            return False
        else:
            return True
    elif isinstance(node, AExistentialQuantificationPredicate):
        max_depth = len(node.children) -2
        if exist_recursive_helper(0, max_depth, node, env):
            return True
        else:
            return False
    elif isinstance(node, AComprehensionSetExpression):
        # FIXME: supports only integers!
        max_depth = len(node.children) -2
        lst = set_comprehension_recursive_helper(0, max_depth, node, env)
        # FIXME: maybe wrong:
        # [[x1,y1],[x2,y2]..] => [(x1,y2),(x2,y2)...]
        result = []
        for i in lst:
            result.append(tuple(flatten(i,[])))
        return set(result)
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
        return set(lst)
    elif isinstance(node, APow1SubsetExpression):
        aSet = interpret(node.children[0], env)
        res = powerset(aSet)
        powerlist = list(res)
        lst = [frozenset(e) for e in powerlist]
        lst.remove(frozenset([]))
        return set(lst)
    elif isinstance(node, ARelationsExpression):
        aSet1 = interpret(node.children[0], env)
        aSet2 = interpret(node.children[1], env)
        aSet = make_set_of_realtions(aSet1, aSet2)
        return aSet
    elif isinstance(node, ADomainExpression):
        # FIXME: crashs if this is not a set of 2-tuple
        aSet = interpret(node.children[0], env)
        dom = [e[0] for e in list(aSet)]
        return set(dom)
    elif isinstance(node, ARangeExpression):
        # FIXME: crashs if this is not a set of 2-tuple
        aSet = interpret(node.children[0], env)
        ran = [e[1] for e in list(aSet)]
        return set(ran)
    elif isinstance(node, ACompositionExpression):
        aSet1 = interpret(node.children[0], env)
        aSet2 = interpret(node.children[1], env)
        new_rel = [(p[0],q[1]) for p in aSet1 for q in aSet2 if p[1]==q[0]]
        return set(new_rel)
    elif isinstance(node, AIdentityExpression):
        aSet = interpret(node.children[0], env)
        id_r = [(x,x) for x in aSet]
        return set(id_r)
    elif isinstance(node, ADomainRestrictionExpression):
        aSet = interpret(node.children[0], env)
        rel = interpret(node.children[1], env)
        new_rel = [x for x in rel if x[0] in aSet]
        return set(new_rel)
    elif isinstance(node, ADomainSubtractionExpression):
        aSet = interpret(node.children[0], env)
        rel = interpret(node.children[1], env)
        new_rel = [x for x in rel if not x[0] in aSet]
        return set(new_rel)
    elif isinstance(node, ARangeRestrictionExpression):
        aSet = interpret(node.children[1], env)
        rel = interpret(node.children[0], env)
        new_rel = [x for x in rel if x[1] in aSet]
        return set(new_rel)
    elif isinstance(node, ARangeSubtractionExpression):
        aSet = interpret(node.children[1], env)
        rel = interpret(node.children[0], env)
        new_rel = [x for x in rel if not x[1] in aSet]
        return set(new_rel)
    elif isinstance(node, AReverseExpression):
        rel = interpret(node.children[0], env)
        new_rel = [(x[1],x[0]) for x in rel]
        return set(new_rel)
    elif isinstance(node, AImageExpression):
        rel = interpret(node.children[0], env)
        aSet = interpret(node.children[1], env)
        image = [x[1] for x in rel if x[0] in aSet ]
        return set(image)
    elif isinstance(node, AOverwriteExpression):
        r1 = interpret(node.children[0], env)
        r2 = interpret(node.children[1], env)
        dom_r2 = [x[0] for x in r2]
        new_r  = [x for x in r1 if x[0] not in dom_r2]
        r2_list= [x for x in r2]
        return set(r2_list + new_r)
    elif isinstance(node, AFirstProjectionExpression):
        S = interpret(node.children[0], env)
        T = interpret(node.children[1], env)
        cart = set(((x,y) for x in S for y in T))
        proj = [(x,x[0]) for x in cart]
        return set(proj)
    elif isinstance(node, ASecondProjectionExpression):
        S = interpret(node.children[0], env)
        T = interpret(node.children[1], env)
        cart = set(((x,y) for x in S for y in T))
        proj = [(x,x[1]) for x in cart]
        return set(proj)
    elif isinstance(node, ADirectProductExpression):
        p = interpret(node.children[0], env)
        q = interpret(node.children[1], env)
        d_prod = [(x[0],(x[1],y[1])) for x in p for y in q if x[0]==y[0]]
        return set(d_prod)
    elif isinstance(node, AParallelProductExpression):
        p = interpret(node.children[0], env)
        q = interpret(node.children[1], env)
        p_prod = [((x[0],y[0]),(x[1],y[1])) for x in p for y in q]
        return set(p_prod)
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
    elif isinstance(node, AFunctionExpression):
        function = interpret(node.children[0], env)
        args = [] # TODO: enamble many args
        for child in node.children[1:]:
            arg = interpret(child, env)
            args.append(arg)
        return get_image(function, args[0])
    elif isinstance(node,AEmptySequenceExpression):
        return set([])
    elif isinstance(node,ASeqExpression):
        S = interpret(node.children[0], env)
        sequence_list = [frozenset([])]
        max_len = 1
        # find all seq from 1..max_int
        for i in range(1,max_int+1):
            sequence_list += create_all_seq_w_fixlen(list(S),i)
        return set(sequence_list)
    elif isinstance(node,ASeq1Expression):
        S = interpret(node.children[0], env)
        sequence_list = []
        max_len = 1
        # find all seq from 1..max_int
        for i in range(1,max_int+1):
            sequence_list += create_all_seq_w_fixlen(list(S),i)
        return set(sequence_list)
    elif isinstance(node,AIseqExpression):
        # TODO: this can be impl. much better
        S = interpret(node.children[0], env)
        sequence_list = [frozenset([])]
        max_len = 1
        # find all seq from 1..max_int
        for i in range(1,max_int+1):
            sequence_list += create_all_seq_w_fixlen(list(S),i)
        inj_sequence_list = filter_not_injective(sequence_list)
        return set(inj_sequence_list)
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
        return set(perm_sequence_list)
    elif isinstance(node, AConcatExpression):
        s = interpret(node.children[0], env)
        t = interpret(node.children[1], env)
        new_t = []
        for tup in t:
            new_t.append(tuple([tup[0]+len(s),tup[1]]))
        return set(list(s)+new_t)
    elif isinstance(node, AInsertFrontExpression):
        E = interpret(node.children[0], env)
        s = interpret(node.children[1], env)
        new_s = [(1,E)]
        for tup in s:
            new_s.append(tuple([tup[0]+1,tup[1]]))
        return set(new_s)
    elif isinstance(node, AInsertTailExpression):
        s = interpret(node.children[0], env)
        E = interpret(node.children[1], env)
        return set(list(s)+[tuple([len(s)+1,E])])
    elif isinstance(node, ASequenceExtensionExpression):
        sequence = []
        i = 0
        for child in node.children:
            i = i+1
            e = interpret(child, env)
            sequence.append(tuple([i,e]))
        return set(sequence)
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
        return set(new_sequence)
    elif isinstance(node, ARestrictFrontExpression):
        sequence = interpret(node.children[0], env)
        take = interpret(node.children[1], env)
        assert take>0
        lst = list(sequence)
        lst.sort()
        return set(lst[:-take])
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
        return set(new_list)
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
        return set(lst[1:])
    elif isinstance(node, AFrontExpression):
        sequence = interpret(node.children[0], env)
        lst = list(sequence)
        lst.sort()
        lst.pop()
        return set(lst)
    elif isinstance(node, AIntervalExpression):
        left = interpret(node.children[0], env)
        right = interpret(node.children[1], env)
        return set(range(left, right+1))
    elif isinstance(node, AGeneralSumExpression):
        sum_ = 0
        ids = []
        for child in node.children[:-2]:
            assert isinstance(child, AIdentifierExpression)
            ids.append(child.idName)
        # new scope - side-effect: typechecking of node.children
        env.push_new_frame(node.children, ids)
        preds = node.children[-2] 
        # gen. all values:
        #TODO: this code (maybe) dont checks all possibilities!
        for idName in ids:
            for i in all_values(idName, env):
                env.set_value(idName, i)
                if interpret(preds, env):
                    sum_ += interpret(node.children[-1], env)
        env.pop_frame()
        return sum_
    elif isinstance(node, AGeneralProductExpression):
        # BUG: only works in sp. cases
        # TODO: implement me: find solutuions for ids if ids are not nums
        prod = 1
        ids = []
        for child in node.children[:-2]:
            ids.append(interpret(child, env))
        preds = node.children[-2] 
        # gen. all values:
        all_val = [x for x in range(min_int,max_int+1)]
        for idName in ids: #TODO: this code dont checks all possibilities!
            for i in all_val:
                env.set_value(idName, i)
                if interpret(preds, env):
                    prod *= interpret(node.children[-1], env)
        return prod
    elif isinstance(node, ANatSetExpression):
        return set(range(0,max_int+1))
    elif isinstance(node, ANat1SetExpression):
        return set(range(1,max_int+1))
    else:
        raise Exception("Unknown Node: %s",node)


# XXX: Warning: this could take some time...
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
    return set(injective_funs)


# filters out every function which is not surjective
def filter_not_surjective(functions, T):
    surj_funs = []
    for fun in functions:
        if is_a_surj_function(fun, T):
            surj_funs.append(fun)
    return set(surj_funs)


# filters out every function which is not total
def filter_not_total(functions, S):
    total_funs = []
    for fun in functions:
        if is_a_total_function(fun, S):
            total_funs.append(fun)
    return set(total_funs)


# checks if the function it total 
def is_a_total_function(function, preimage_set):
    preimage = [x[0] for x in function]
    preimage_set2 =  set(preimage)
    return preimage_set == preimage_set2


# checks if the function it surjective
def is_a_surj_function(function, image_set):
    image = [x[1] for x in function]
    image_set2= set(image) # remove duplicate items
    return image_set == image_set2


# filters out every set which is no function
def filter_no_function(relations):
    functions = []
    for r in relations:
        if is_a_function(r):
            functions.append(r)
    return set(functions)


# checks if a relation is a function
def is_a_function(relation):
    preimage_set = [x[0] for x in relation]
    if double_element_check(preimage_set):
        return False
    else:
        return True


# returns S<-->T
def make_set_of_realtions(S,T):
    cartSet = set(((x,y) for x in S for y in T))
    res = powerset(cartSet)
    powerlist = list(res)
    lst = [frozenset(e) for e in powerlist]
    return set(lst)


# from http://docs.python.org/library/itertools.html
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
        for i in range(min_int, max_int):
            env.set_value(idName, i)
            if interpret(pred, env):
                result.append(i)
        return result
    else: # recursive call
        for i in range(min_int, max_int):
            env.set_value(idName, i)
            partial_result = set_comprehension_recursive_helper(depth+1, max_depth, node, env)
            for j in partial_result:
                temp = []
                temp.append(i)
                temp.append(j)
                result.append(temp)
        return result


# FIXME: rename quantified variables!
def exist_recursive_helper(depth, max_depth, node, env):
    pred = node.children[len(node.children) -1]
    idName = node.children[depth].idName
    if depth == max_depth: #basecase
        for i in all_values(idName, env):
            env.set_value(idName, i)
            if interpret(pred, env):
                return True
        return False
    else: # recursive call
        for i in all_values(idName, env):
            env.set_value(idName, i)
            if exist_recursive_helper(depth+1, max_depth, node, env):
                return True
        return False


# FIXME: rename quantified variables!
def forall_recursive_helper(depth, max_depth, node, env):
    pred = node.children[len(node.children) -1]
    idName = node.children[depth].idName
    if depth == max_depth: #basecase
        for i in all_values(idName, env):
            env.set_value(idName, i)
            if not interpret(pred, env):
                return False
        return True
    else: # recursive call
        for i in all_values(idName, env):
            env.set_value(idName, i)
            if not forall_recursive_helper(depth+1, max_depth, node, env):
                return False
        return True


# ** THE ENUMERATOR **
# returns a list with "all" possible values of a type
# only works if the typechecking/typing of typeit was successful
def all_values(idName, env):
    # TODO: support cart prod
    if isinstance(env.get_type(idName), IntegerType):
        return range(min_int, max_int+1)
    elif isinstance(env.get_type(idName), SetType):
        type_name =  env.get_type(idName).data
        assert isinstance(env.get_value(type_name), set)
        return env.get_value(type_name)
    elif isinstance(env.get_type(idName), PowerSetType):
        if isinstance(env.get_type(idName).data, SetType):
            type_name = env.get_type(idName).data.data
            assert isinstance(env.get_value(type_name), set)
            res = powerset(env.get_value(type_name))
            powerlist = list(res)
            lst = [frozenset(e) for e in powerlist]
            return lst
        elif isinstance(env.get_type(idName).data, PowerSetType):
            count = 1
            atype = env.get_type(idName).data
            # TODO: Think of this again ;-)
            # unpack POW(POW(S)), POW(POW(POW(S))) ect. ....
            while not isinstance(atype, SetType):
                count = count +1
                atype = atype.data
            value = env.get_value(atype.data)
            assert isinstance(value, set)
            # create all(!) values
            for i in range(count):
                res = powerset(value)
                powerlist = list(res)
                value = [frozenset(e) for e in powerlist]
            return value
    raise Exception("Unknown Type / Not Implemented: %s", idName)
