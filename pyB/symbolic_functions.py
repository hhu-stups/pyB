from symbolic_helpers import check_syntacticly_equal,make_explicit_set_of_realtion_lists 
from symbolic_sets import *
from symbolic_functions_with_predicate import *

class SymbolicRelationSet(SymbolicSet):
    def __init__(self, aset0, aset1, env, interpret):
        SymbolicSet.__init__(self, env, interpret)
        self.left_set = aset0
        self.right_set = aset1   
    
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
        
    def __iter__(self):
        return self 
    
    def next(self):
        raise Exception("Not implemented: relation symbolic iteration over explicit values")

        
class SymbolicPartialFunctionSet(SymbolicRelationSet):
    pass

    
class SymbolicTotalFunctionSet(SymbolicRelationSet):
    def next(self):
        S = self.left_set
        T = self.right_set
        for relation_lst in make_explicit_set_of_realtion_lists(S,T): # S<->T
            domain = [x[0] for x in relation_lst]
            if double_element_check(domain): # check if function
                continue
            if not frozenset(domain) == S: # check if total
                continue
            return frozenset(relation_lst) 
    
    
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
    def __init__(self, aset0, aset1, env, interpret):
        SymbolicSet.__init__(self, env, interpret)
        self.left_set = aset0
        self.right_set = aset1  
        
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


class SymbolicSecondProj(SymbolicSet):
    def __init__(self, aset0, aset1, env, interpret):
        SymbolicSet.__init__(self, env, interpret)
        self.left_set = aset0
        self.right_set = aset1  
    
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
        
    
class SymbolicIdentitySet(SymbolicRelationSet):
    def enumerate_all(self):
        assert self.left_set==self.right_set
        if isinstance(self.left_set, SymbolicSet):
            aSet = self.left_set.enumerate_all()
        else:
            aSet = self.left_set 
        id_r = [(x,x) for x in aSet]
        return frozenset(id_r)

class SymbolicCompositionSet(SymbolicRelationSet):
    # convert to explicit set
    def enumerate_all(self):
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
            return frozenset(result)
        if PRINT_WARNINGS:
            print "convert symbolic to explicit set failed! Case not implemented"
        raise EnumerationNotPossibleException(self) 