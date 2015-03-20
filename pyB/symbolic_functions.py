from symbolic_helpers import check_syntacticly_equal, make_explicit_set_of_realtion_lists 
from symbolic_sets import SymbolicSet, PowerSetType, SymbolicCartSet
from symbolic_functions_with_predicate import SymbolicLambda, SymbolicComprehensionSet 
from ast_nodes import *
from relation_helpers import *
from helpers import enumerate_cross_product
from bexceptions import ValueNotInDomainException
from config import USE_COSTUM_FROZENSET
if USE_COSTUM_FROZENSET:
     from rpython_b_objmodel import frozenset

class SymbolicRelationSet(SymbolicSet):
    def __init__(self, aset0, aset1, env, interpret, node):
        SymbolicSet.__init__(self, env, interpret)
        self.left_set = aset0
        self.right_set = aset1
        self.node = node   
    
    # element in Set
    def __contains__(self, element):
        #print "SymbolicRelationSet", self.left_set , self.right_set
        #print "SymbolicRelationSet", element
        if isinstance(element, SymbolicSet):
            assert isinstance(element, SymbolicCartSet)
            return element.left_set in self.left_set and element.right_set in self.right_set
        elif isinstance(element, PowerSetType):  
            assert isinstance(element.data, CartType)
            left  = element.data.data[0].data
            right = element.data.data[1].data
            return left in self.left_set and right in self.right_set 
        else: 
            assert isinstance(element, tuple)
            return element[0] in self.left_set and element[1] in self.right_set 
        raise Exception("Not implemented: relation symbolic membership")

    def make_generator(self):
        S = self.left_set
        T = self.right_set
        return make_explicit_set_of_realtion_lists(S,T)
    
    def __eq__(self, other):
        # TODO: handle empty set and maybe more sp. cases
        return SymbolicSet.__eq__(self, other)

        
class SymbolicPartialFunctionSet(SymbolicRelationSet):
    def make_generator(self):
        for relation in SymbolicRelationSet.make_generator(self):
            if is_a_function(relation):
                yield relation

    
class SymbolicTotalFunctionSet(SymbolicRelationSet):
    def make_generator(self):
        for relation in SymbolicRelationSet.make_generator(self):
            if is_a_function(relation) and is_a_total_function(relation, self.left_set):
                yield relation
                
    
class SymbolicPartialInjectionSet(SymbolicRelationSet):
    def make_generator(self):
        for relation in SymbolicRelationSet.make_generator(self):
            if is_a_function(relation) and is_a_inje_function(relation):
                yield relation

    
class SymbolicTotalInjectionSet(SymbolicRelationSet):
    def make_generator(self):
        for relation in SymbolicRelationSet.make_generator(self):
            if is_a_function(relation) and is_a_total_function(relation, self.left_set) and is_a_inje_function(relation):
                yield relation
    
    
class SymbolicPartialSurjectionSet(SymbolicRelationSet):
    def make_generator(self):
        for relation in SymbolicRelationSet.make_generator(self):
            if is_a_function(relation) and is_a_surj_function(relation,self.right_set):
                yield relation
    
    
class SymbolicTotalSurjectionSet(SymbolicRelationSet):
    def make_generator(self):
        for relation in SymbolicRelationSet.make_generator(self):
            if is_a_function(relation) and is_a_total_function(relation, self.left_set) and is_a_surj_function(relation, self.right_set):
                yield relation

    
class SymbolicTotalBijectionSet(SymbolicRelationSet):
    def make_generator(self):
        for relation in SymbolicRelationSet.make_generator(self):
            if is_a_function(relation) and is_a_total_function(relation, self.left_set) and is_a_surj_function(relation, self.right_set) and is_a_inje_function(relation):
                yield relation

    
class SymbolicPartialBijectionSet(SymbolicRelationSet):
    def make_generator(self):
        for relation in SymbolicRelationSet.make_generator(self):
            if is_a_function(relation) and is_a_surj_function(relation, self.right_set) and is_a_inje_function(relation):
                yield relation

class SymbolicFirstProj(SymbolicSet):
    def __init__(self, aset0, aset1, env, interpret, node):
        SymbolicSet.__init__(self, env, interpret)
        self.left_set = aset0
        self.right_set = aset1
        self.node = node  
        
    # ((x,y),z):proj1(S,T)
    def __contains__(self, element):
        if isinstance(element, SymbolicSet):
            raise Exception("Not implemented: proj1 symbolic membership")
        x = element[0][0]
        y = element[0][1]
        z = element[1]
        if x not in self.left_set or y not in self.right_set or not(x==z) :
            return False
        return True
    
    # proj1(S,T)(arg)
    def __getitem__(self, arg):
        if arg[0] not in self.left_set or arg[1] not in self.right_set:
            raise ValueNotInDomainException(arg) 
        return arg[0]  
    
    def __eq__(self, other):
        # check importent special case first
        # %(x,y).(x:S & y:T|x) = prj1(S,T)
        if isinstance(other, SymbolicLambda): 
            if not len(other.variable_list)==2:
                return False
            if isinstance(other.predicate, AConjunctPredicate):    
                belong_pred0 = other.predicate.children[0]
                belong_pred1 = other.predicate.children[1]
                if isinstance(belong_pred0, AMemberPredicate) and isinstance(belong_pred1, AMemberPredicate):                
                    x = other.variable_list[0].idName
                    y = other.variable_list[1].idName
                    xx = belong_pred0.children[0]
                    yy = belong_pred1.children[0]
                    if isinstance(xx, AIdentifierExpression) and xx.idName==x:
                        S = self.interpret(belong_pred0.children[1], self.env)
                    if isinstance(yy, AIdentifierExpression) and yy.idName==y:
                        T = self.interpret(belong_pred1.children[1], self.env)
                    if isinstance(other.expression, AIdentifierExpression): # else: maybe equal.            
                        try:
                            if self.left_set==S and self.right_set==T and x==other.expression.idName:
                                return True              
                        except NameError:
                            pass # maybe equal. use brute-force in symbolic set              
            return SymbolicSet.__eq__(self, other)
    
    def make_generator(self):
        for cross_prod in enumerate_cross_product(self.left_set, self.right_set):
             yield tuple([cross_prod,cross_prod[0]])      


class SymbolicSecondProj(SymbolicSet):
    def __init__(self, aset0, aset1, env, interpret, node):
        SymbolicSet.__init__(self, env, interpret)
        self.left_set = aset0
        self.right_set = aset1  
        self.node = node
    
    # ((x,y),z):proj2(S,T)
    def __contains__(self, element):
        if isinstance(element, SymbolicSet):
            raise Exception("Not implemented: proj2 symbolic membership")
        x = element[0][0]
        y = element[0][1]
        z = element[1]
        if x not in self.left_set or y not in self.right_set or not(y==z) :
            return False
        return True
        
    
    # proj2(S,T)(arg)
    def __getitem__(self, arg):
        if not isinstance(arg, tuple):
            raise TypeError()
        if arg[0] not in self.left_set or arg[1] not in self.right_set:
            raise ValueNotInDomainException(arg) 
        return arg[1] 


    def __eq__(self, other):
        # check importent special case first
        # %(x,y).(x:S & y:T|y) = prj2(S,T)
        if isinstance(other, SymbolicLambda): 
            if not len(other.variable_list)==2:
                return False
            if isinstance(other.predicate, AConjunctPredicate):    
                belong_pred0 = other.predicate.children[0]
                belong_pred1 = other.predicate.children[1]
                if isinstance(belong_pred0, AMemberPredicate) and isinstance(belong_pred1, AMemberPredicate):                
                    x = other.variable_list[0].idName
                    y = other.variable_list[1].idName
                    xx = belong_pred0.children[0]
                    yy = belong_pred1.children[0]
                    if isinstance(xx, AIdentifierExpression) and xx.idName==x:
                        S = self.interpret(belong_pred0.children[1], self.env)
                    if isinstance(yy, AIdentifierExpression) and yy.idName==y:
                        T = self.interpret(belong_pred1.children[1], self.env)
                    if isinstance(other.expression, AIdentifierExpression): # else: maybe equal.            
                        try:
                            if self.left_set==S and self.right_set==T and y==other.expression.idName:
                                return True              
                        except NameError:
                            pass # maybe equal. use brute-force in symbolic set              
            return SymbolicSet.__eq__(self, other)

    def make_generator(self):
        for cross_prod in enumerate_cross_product(self.left_set, self.right_set):
             yield tuple([cross_prod,cross_prod[1]])
                         
    
class SymbolicIdentitySet(SymbolicRelationSet):
    def enumerate_all(self):
        if not self.explicit_set_computed:
            assert self.left_set==self.right_set
            if isinstance(self.left_set, SymbolicSet):
                aSet = self.left_set.enumerate_all()
            else:
                aSet = self.left_set 
            id_r = [(x,x) for x in aSet]
            self.explicit_set_repr = frozenset(id_r)
            self.explicit_set_computed = True
        return self.explicit_set_repr

    def make_generator(self):
        assert self.left_set==self.right_set
        for e in self.left_set:
            yield tuple([e,e])

    def __contains__(self, element):
        assert isinstance(element, tuple)
        if element[0]==element[1] and element[0] in self.left_set:
            return True
        else:
            return False 
             
class SymbolicCompositionSet(SymbolicRelationSet):
    def __init__(self, arelation0, arelation1, env, interpret, node):
        SymbolicSet.__init__(self, env, interpret)
        self.left_relation = arelation0
        self.right_relation = arelation1
        self.node = node 


    # element in Set
    # WARNING: may cause Timeout
    # FIXME: works only for min/max int because of all types enumeration in enumeration.py
    def __contains__(self, element):
        #for t in [y for y in self.right_relation]:
        #    print t
        #    if t[1]>1000:
        #        break
        assert isinstance(element, tuple)
        for tup in [x for x in self.left_relation if x[0]== element[0]]:
            for tup2 in [y for y in self.right_relation if y[0]==tup[1]]:
                if tup2[1]==element[1]:
                    return True
        return False
        return SymbolicRelationSet.__contains__(self, element)
                
    # convert to explicit set
    def enumerate_all(self):
        if not self.explicit_set_computed:      
            if isinstance(self.left_relation, frozenset) and isinstance(self.right_relation, SymbolicLambda):
                result = []
                lambda_function = self.right_relation        
                self.env.push_new_frame(lambda_function.variable_list)
                for tup in self.left_relation:
                    domain = tup[0]
                    args   = remove_tuples(tup[1])
                    for i in range(len(lambda_function.variable_list)):
                        idNode = lambda_function.variable_list[i]
                        #TODO: check all tuple confusion e.g x:(NAT*(NAT*NAT)
                        # onne carttype can contain more...
                        # set args to correct bound variable in lambda expression using type-info
                        atype = self.env.get_type_by_node(idNode)
                        value = build_arg_by_type(atype, args) # args-mod via sideeffect
                        self.env.set_value(idNode.idName, value)
                    # check if value is in lambda domain
                    pre_result = self.interpret(lambda_function.predicate, self.env)
                    if pre_result:
                        # calculate element of composition expression
                        lambda_image = self.interpret(lambda_function.expression, self.env)
                        result.append(tuple([domain, lambda_image]))
                self.env.pop_frame() # exit scope
                self.explicit_set_repr = frozenset(result)
            else:
                self.explicit_set_repr = SymbolicRelationSet.enumerate_all(self)
            self.explicit_set_computed = True
        return self.explicit_set_repr

    def make_generator(self):
        for e0 in self.left_relation:
            for e1 in self.right_relation:
                #print e0[1], e1[0], e0[1]==e1[0]
                if e0[1]==e1[0]:
                    yield (e0[0],e1[1])
    
    # may throw valueNotInDomainException
    def __getitem__(self, arg):
        if isinstance(self.left_relation, frozenset):
            z = [t[1] for t in self.left_relation if t[0]==arg][0]
        else:
            z = self.left_relation[arg]
        # TODO: z may not be an element of self.right_relation 
        if isinstance(self.right_relation, frozenset):
            image = [t[1] for t in self.right_relation if t[0]==z][0]
        else:
            image = self.right_relation[z]
        return image


# The SymbolicRelationSet methods asume a domain- and imageset present.
# This type of relation has none(directly).
class SymbolicTransRelation(SymbolicSet):
    def __init__(self, function, env, interpret, node):
        SymbolicSet.__init__(self, env, interpret)
        self.function = function
        self.node = node
        
    def enumerate_all(self):
        if not self.explicit_set_computed:
            relation = []
            for tup in self.function:
                preimage = tup[0]
                for image in tup[1]:
                    relation.append(tuple([preimage, image]))
            self.explicit_set_repr = frozenset(relation)
            self.explicit_set_computed = True
        return self.explicit_set_repr
    
    def make_generator(self):
        for tup in self.function:
            preimage = tup[0]
            for image in tup[1]:
                yield tuple([preimage, image])


# The SymbolicRelationSet methods asume a domain- and imageset present.
# This type of relation has none.
class SymbolicTransFunction(SymbolicSet):
    def __init__(self, relation, env, interpret, node):
        SymbolicSet.__init__(self, env, interpret)
        self.relation = relation
        self.node = node

    def enumerate_all(self):
        if not self.explicit_set_computed:
            function = []
            for tup in self.relation:
                image = []
                preimage = tup[0]
                for tup2 in self.relation:
                    if tup2[0]==preimage:
                        image.append(tup2[1])
                function.append(tuple([preimage,frozenset(image)]))
            self.explicit_set_repr = frozenset(function)
            self.explicit_set_computed = True
        return self.explicit_set_repr        
        
    def make_generator(self):
        for tup in self.relation:
            image = []
            preimage = tup[0]
            for tup2 in self.relation:
                if tup2[0]==preimage:
                    image.append(tup2[1])
            yield tuple([preimage,frozenset(image)])
                                      
# XXX: not enabled. see interpreter.py AReverseExpression
class SymbolicInverseRelation(SymbolicRelationSet):
    def __init__(self, relation, env, interpret, node):
        SymbolicSet.__init__(self, env, interpret)
        self.relation = relation
        self.node = node
        
    def enumerate_all(self):
        if not self.explicit_set_computed:
            if isinstance(self.relation, SymbolicSet):  
                rel = self.relation.enumerate_all()
            else:
                rel = self.relation
            inv_rel = [(x[1],x[0]) for x in rel]
            self.explicit_set_repr = frozenset(inv_rel)
            self.explicit_set_computed = True
        return self.explicit_set_repr
    
    def make_generator(self):
        for e in self.relation:
            yield tuple([e[1],e[0]])
    
    def __contains__(self, other):
        inv_element = tuple([other[1],other[0]])
        return inv_element in self.relation