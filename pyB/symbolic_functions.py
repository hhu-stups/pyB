from symbolic_helpers import check_syntacticly_equal,make_explicit_set_of_realtion_lists 
from symbolic_sets import *
from symbolic_functions_with_predicate import SymbolicLambda, SymbolicComprehensionSet 
from ast_nodes import *

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
    
    # TODO: write test
    def __eq__(self, aset):
        # special case for performance
        if aset==frozenset([]):
            return False
        if isinstance(aset, frozenset):
            explicit_set_repr = self.enumerate_all()
            return aset == explicit_set_repr
        raise Exception("Not implemented: relation symbolic equalety")
        
    def __ne__(self, aset):
        return not self.__eq__(aset)

    def make_generator(self):
        S = self.left_set
        T = self.right_set
        return make_explicit_set_of_realtion_lists(S,T)

        
class SymbolicPartialFunctionSet(SymbolicRelationSet):
    pass

    
class SymbolicTotalFunctionSet(SymbolicRelationSet):
    def next(self):
        while True: # StopIterationException exit loop
            relation_lst = self.generator.next()
            domain = [x[0] for x in relation_lst]
            if double_element_check(domain): # check if function
                continue
            if not frozenset(domain) == self.left_set: # check if total (domain equal S)
                continue
            return frozenset(relation_lst) 
    
    # XXX
    def make_generator(self):
        S = self.left_set
        T = self.right_set
        return make_explicit_set_of_realtion_lists(S,T)
    
class SymbolicPartialInjectionSet(SymbolicRelationSet):
    pass
    
class SymbolicTotalInjectionSet(SymbolicRelationSet):
    pass
    
class SymbolicPartialSurjectionSet(SymbolicRelationSet):
    pass
    
class SymbolicTotalSurjectionSet(SymbolicRelationSet):
    pass
    
class SymbolicTotalBijectionSet(SymbolicRelationSet):
    pass
    
class SymbolicPartialBijectionSet(SymbolicRelationSet):
    pass
    
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
                if isinstance(belong_pred0, ABelongPredicate) and isinstance(belong_pred1, ABelongPredicate):                
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
                if isinstance(belong_pred0, ABelongPredicate) and isinstance(belong_pred1, ABelongPredicate):                
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
        
    
class SymbolicIdentitySet(SymbolicRelationSet):
    def enumerate_all(self):
        if self.explicit_set_repr==None:
            assert self.left_set==self.right_set
            if isinstance(self.left_set, SymbolicSet):
                aSet = self.left_set.enumerate_all()
            else:
                aSet = self.left_set 
            id_r = [(x,x) for x in aSet]
            self.explicit_set_repr = frozenset(id_r)
        return self.explicit_set_repr

class SymbolicCompositionSet(SymbolicRelationSet):
    # convert to explicit set
    def enumerate_all(self):
        if self.explicit_set_repr==None:      
            if isinstance(self.left_set, frozenset) and isinstance(self.right_set, SymbolicLambda):
                result = []
                lambda_function = self.right_set        
                self.env.push_new_frame(lambda_function.variable_list)
                for tup in self.left_set:
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
                if PRINT_WARNINGS:
                    print "\033[1m\033[91mWARNING\033[00m: convert symbolic to explicit set failed! Case not implemented"
                raise EnumerationNotPossibleException(self)
        return self.explicit_set_repr


class SymbolicInverseRelation(SymbolicRelationSet):
    def __init__(self, relation, env, interpret, node):
        SymbolicSet.__init__(self, env, interpret)
        self.relation = relation
        self.node = node
        
    def enumerate_all(self):
        if self.explicit_set_repr==None:  
            rel = self.relation.enumerate_all()
            inv_rel = [(x[1],x[0]) for x in rel]
            self.explicit_set_repr = frozenset(inv_rel)
        return self.explicit_set_repr