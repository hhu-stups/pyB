# this classes represent set which should not be enumerated as long as possible (beste case: never)
# warning: some set behavior is implemented inside the interpreter and its helper-methodes and NOT here
# design decision: most functionality should implemented in this module. the goal is that
# symbolic sets behave like frozensets (as much as possible) 
# x (not)in S implemented in quick_eval.py (called by Belong-predicates x:S)
from bexceptions import ValueNotInDomainException, DontKnowIfEqualException
from helpers import double_element_check, remove_tuples, build_arg_by_type
from btypes import *
from config import PRINT_WARNINGS
from pretty_printer import pretty_print


class SymbolicSet(object):
    # evn: min and max int values may be needed for large sets 
    # interpret: for function call on tuple-sets
    def __init__(self, env, interpret):
        self.env = env 
        self.interpret = interpret
    
    def __mul__(self, aset):
        return SymbolicCartSet(self, aset, self.env, self.interpret)
    
    def __rmul__(self, aset):
        return SymbolicCartSet(aset, self, self.env, self.interpret)
    
    def __eq__(self, aset):
        print "WARNING: equalety not implemented for symbolic sets!", self," and", aset
        raise Exception("fail: can not compare symbolic set")
        #if self.__class__ == aset.__class__:
        #    return True
        #return False

    def __ne__(self, aset):
        print "WARNING: equalety not implemented for symbolic sets!", self," and", aset
        raise Exception("fail: can not compare symbolic set")
        #if self.__class__ == aset.__class__:
        #    return False
        #return True

class LargeSet(SymbolicSet):
    def __sub__(self, other):
        # TODO: add possible symbolic cases
        assert isinstance(other, frozenset)
        return self.enumerate_all()-other
    

class InfiniteSet(SymbolicSet):
    ## WARNING: python only accept int as return values
    ## so __len__ is not implemented
    pass


class NaturalSet(InfiniteSet):
    def __contains__(self, element):
        return isinstance(element, int) and element >= 0 
    
    def __le__(self, aset): # NaturalSet <= aset
        if isinstance(aset, (NaturalSet,IntegerSet)):
            return True
        return False 
    
    def __ge__(self, aset): # NaturalSet >= aset
        if isinstance(aset, (IntegerSet, IntSet)): # no neg nums
            return False
        elif isinstance(aset, frozenset):
            for x in aset:
                if x<0:
                    return False
            return True
        elif isinstance(aset, (NatSet, Nat1Set, NaturalSet, Natural1Set)):
            return True 
        raise NotImplementedError("inclusion with unknown set-type")
       
    def __lt__(self, aset): # NaturalSet < aset
        if isinstance(aset,IntegerSet):
            return True
        return False

    def __gt__(self, aset): # NaturalSet > aset
        if isinstance(aset, (IntegerSet, NaturalSet, IntSet)):
            return False
        elif isinstance(aset, frozenset):
            for x in aset:
                if x<0:
                    return False
                return True
        elif isinstance(aset, (NatSet, Nat1Set, Natural1Set)):
            return True 
        raise NotImplementedError("inclusion with unknown set-type")  
    
    def __eq__(self, aset):
        if self.__class__ == aset.__class__:
            return True
        return False
    
    def __ne__(self, aset):
        if self.__class__ == aset.__class__:
            return False
        return True
        

class Natural1Set(InfiniteSet):
    def __contains__(self, element):
        return isinstance(element, int) and element > 0  
    
    def __le__(self, aset): # Natural1Set <= aset
        if isinstance(aset, InfiniteSet):
            return True
        return False
 
    def __ge__(self, aset): # Natural1Set >= aset
        if isinstance(aset, (NaturalSet, IntegerSet, NatSet, IntSet)): # zero
            return False
        elif isinstance(aset, frozenset):
            for x in aset:
                if x<=0:
                    return False
            return True
        elif isinstance(aset, (Nat1Set, Natural1Set)):
            return True 
        raise NotImplementedError("inclusion with unknown set-type")

    def __lt__(self, aset): # Natural1Set < aset
        if isinstance(aset,(IntegerSet, NaturalSet)):
            return True
        return False

    def __gt__(self, aset): # Natura1lSet > aset
        if isinstance(aset,(InfiniteSet, LargeSet)):
            return False
        elif isinstance(aset, frozenset):
            for x in aset:
                if x<0:
                    return False
                return True
        raise NotImplementedError("inclusion with unknown set-type")  

    def __eq__(self, aset):
        if self.__class__ == aset.__class__:
            return True
        return False
    
    def __ne__(self, aset):
        if self.__class__ == aset.__class__:
            return False
        return True


# the infinite B-set INTEGER    
class IntegerSet(InfiniteSet): 
    def __contains__(self, element):
        return isinstance(element, int) or isinstance(element, IntegerType) #type for symbolic checks
    
    def __le__(self, aset): # IntegerSet <= aset
        if isinstance(aset, IntegerSet):
            return True
        return False

    def __ge__(self, aset): # IntegerSet >= aset
        if isinstance(aset, SymbolicSet): 
            return True
        elif isinstance(aset, frozenset):
            for x in aset:
                if not int(x):
                    return False
            return True
        raise NotImplementedError("inclusion with unknown set-type")

    def __lt__(self, aset): # IntegerSet < aset
        return False

    def __gt__(self, aset): # IntegerSet > aset
        if isinstance(aset,IntegerSet):
            return False
        elif isinstance(aset, frozenset):
            for x in aset:
                if x<0:
                    return False
                return True
        elif isinstance(aset, (NatSet, Nat1Set, IntSet, NaturalSet, Natural1Set)):
            return True 
        raise NotImplementedError("inclusion with unknown set-type")  
    
    def __eq__(self, aset):
        if self.__class__ == aset.__class__:
            return True
        return False
    
    def __ne__(self, aset):
        if self.__class__ == aset.__class__:
            return False
        return True

        
# if min and max-int change over exec. this class will notice this change (env)
class NatSet(LargeSet):
    def __contains__(self, element):
        return isinstance(element, int) and element >=0 and element <= self.env._max_int
      
    def __len__(self):
        return self.env._max_int+1
     
    def __le__(self, aset): # NatSet <=
        if isinstance(aset, (NatSet, IntSet, NaturalSet, IntegerSet)):
            return True
        elif isinstance(aset, frozenset):
            for x in aset:
                if not self.__contains__(x):
                    return False
            return len(aset)>=self.__len__()
        elif isinstance(aset, (Natural1Set, Nat1Set)):
            return False
        raise NotImplementedError("inclusion with unknown set-type")
    
    def __ge__(self, aset): # NatSet >= aset
        if isinstance(aset, (InfiniteSet, IntSet)): 
            return False
        elif isinstance(aset, (NatSet, Nat1Set)):
            return True
        elif isinstance(aset, frozenset):
            for x in aset:
                if x<=0:
                    return False
            return True
        raise NotImplementedError("inclusion with unknown set-type")       

    def __lt__(self, aset): # NatSet < aset
        if isinstance(aset,(IntegerSet, NaturalSet, IntSet)):
            return True
        return False
        
    def __gt__(self, aset): # NatSet > aset
        if isinstance(aset,InfiniteSet,  IntSet, NatSet):
            return False
        elif isinstance(aset, frozenset):
            for x in aset:
                if x<0:
                    return False
                return True
        elif isinstance(aset, Nat1Set):
            return True 
        raise NotImplementedError("inclusion with unknown set-type")         
        
    def __or__(self, aset):
        if isinstance(aset, NatSet):
            return self
        elif isinstance(aset, Nat1Set):
            return aset
        elif isinstance(aset, IntSet):
            return aset
        elif isinstance(aset, InfiniteSet):
            return aset
        else:
            raise NotImplementedError()

    def __eq__(self, aset):
        if self.__class__ == aset.__class__:
            return True
        return False
    
    def __ne__(self, aset):
        if self.__class__ == aset.__class__:
            return False
        return True

    def enumerate_all(self):
        return frozenset(range(0,self.env._max_int+1))
    
    def __len__(self):
        return self.env._max_int+1

    # not used for performance reasons
    #def __getitem__(self, key):
    #    return key
  
      
class Nat1Set(LargeSet):
    def __contains__(self, element):
        return isinstance(element, int) and element >0 and element <= self.env._max_int

    def __len__(self):
        return self.env._max_int
    
    def __le__(self, aset): # Nat1Set <=
        if isinstance(aset, (InfiniteSet, LargeSet)):
            return True
        elif isinstance(aset, frozenset):
            for x in aset:
                if not self.__contains__(x):
                    return False
            return len(aset)>=self.__len__()
        raise NotImplementedError("inclusion with unknown set-type")
    
    def __ge__(self, aset): # Nat1Set >= aset
        if isinstance(aset, (NatSet, IntSet,InfiniteSet)): 
            return False
        elif isinstance(aset, Nat1Set):
            return True
        elif isinstance(aset, frozenset):
            for x in aset:
                if x<0:
                    return False
            return True
        raise NotImplementedError("inclusion with unknown set-type")

    def __lt__(self, aset): # Nat1Set < aset
        if isinstance(aset, Nat1Set):
            return False
        return True     

    def __gt__(self, aset): # Nat1Set > aset
        if isinstance(aset,(InfiniteSet,LargeSet)):
            return False
        elif isinstance(aset, frozenset):
            for x in aset:
                if x<0:
                    return False
                return True
        raise NotImplementedError("inclusion with unknown set-type")  

    def __eq__(self, aset):
        if self.__class__ == aset.__class__:
            return True
        return False
    
    def __ne__(self, aset):
        if self.__class__ == aset.__class__:
            return False
        return True
    
    def enumerate_all(self):
        return frozenset(range(1,self.env._max_int+1))

    def __len__(self):
        return self.env._max_int

    # not used for performance reasons
    #def __getitem__(self, key):
    #    return 1+key
        

class IntSet(LargeSet):
    def __contains__(self, element):
        return isinstance(element, int) and element >= self.env._min_int and element <= self.env._max_int

    def __len__(self):
        return self.env._max_int + (-1)*self.env._min_int + 1 
    
    def __le__(self, aset): # IntSet <=
        if isinstance(aset, (IntSet, IntegerSet)):
            return True
        elif isinstance(aset, frozenset):
            for x in aset:
                if not self.__contains__(x):
                    return False
            return len(aset)>=self.__len__()
        elif isinstance (aset, (NatSet, Nat1Set, NaturalSet, Natural1Set)):
            return False
        raise NotImplementedError("inclusion with unknown set-type")
    
    def __ge__(self, aset): # IntSet >= aset
        if isinstance(aset, InfiniteSet): 
            return False
        elif isinstance(aset, LargeSet):
            return True
        elif isinstance(aset, frozenset):
            for x in aset:
                if not int(x):
                    return False
            return True
        raise NotImplementedError("inclusion with unknown set-type") 

    def __lt__(self, aset): # IntSet < aset
        if isinstance(aset, IntegerSet):
            return True
        return False    

    def __gt__(self, aset): # IntSet > aset
        if isinstance(aset,(InfiniteSet, IntSet)):
            return False
        elif isinstance(aset, frozenset):
            for x in aset:
                if x<0:
                    return False
                return True
        elif isinstance(aset, (Nat1Set, NatSet)):
            return True 
        raise NotImplementedError("inclusion with unknown set-type")  

    def __eq__(self, aset):
        if self.__class__ == aset.__class__:
            return True
        return False
    
    def __ne__(self, aset):
        if self.__class__ == aset.__class__:
            return False
        return True

    def enumerate_all(self):
        return frozenset(range(self.env._min_int, self.env._max_int+1))

    def __len__(self):
        return -1*self.env._min_int+self.env._max_int+1
 
    # not used for performance reasons   
    #def __getitem__(self, key):
    #    return self.env._min_int+key

class StringSet(SymbolicSet):
    def __contains__(self, element):
        return isinstance(element, str) or isinstance(element, StringType)
    
    # aSet<:STRING
    def issubset(self, aSet):
        if isinstance(aSet, StringSet):
            return True
        return False
    
    # aSet<:STRING(!)
    def issuperset(self, aSet):
        if isinstance(aSet, StringSet):
            return True
        if isinstance(aSet, frozenset):
            for e in aSet:
                if not isinstance(e, str):
                    return False
            return True
        return False
    
    def __eq__(self, aset):
        if self.__class__ == aset.__class__:
            return True
        return False
    
    def __ne__(self, aset):
        if self.__class__ == aset.__class__:
            return False
        return True
    
class SymbolicCartSet(SymbolicSet):
    def __init__(self, aset0, aset1, env, interpret):
        SymbolicSet.__init__(self, env, interpret)
        self.left_set = aset0
        self.right_set = aset1
    
    def __contains__(self, element):
        #print "elemet", element
        if isinstance(element, tuple):
            l = element[0]
            r = element[1]
        else:
            raise NotImplementedError()
        return l in self.left_set and r in self.right_set
    
    def __eq__(self, aset):
        if not isinstance(aset, SymbolicCartSet):
            return False
        elif (self.left_set==aset.left_set) and (self.right_set==aset.right_set):
            return True
        return False
    
    def __ne__(self, aset):
        return not self.__eq__(aset)

class SymbolicUnionSet(SymbolicSet):
    def __init__(self, aset0, aset1, env, interpret):
        SymbolicSet.__init__(self, env, interpret)
        self.left_set = aset0
        self.right_set = aset1
    
    # function call of set
    def __getitem__(self, arg):
        if isinstance(self.left_set, SymbolicLambda) and isinstance(self.right_set, SymbolicLambda):
            try:
                result = self.left_set[arg] 
                return result
            except:
                result = self.right_set[arg] 
                return result
        raise Exception("Not implemented: relation symbolic membership")  


class SymbolicPowerSet(SymbolicSet):
    def __init__(self, aset, env, interpret):
        SymbolicSet.__init__(self, env, interpret)
        self.set = aset

    # e:S (element:self.set)
    def __contains__(self, element):
        print element
        print self.set
        raise Exception("not implemented")


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

# __getitem__ implemented inside interp to avoid env and interp_callable link
class SymbolicLambda(SymbolicSet):
    def __init__(self, varList, pred, expr, node, env, interpret, calc_possible_solutions):
        SymbolicSet.__init__(self, env, interpret)
        self.variable_list = varList
        self.predicate = pred
        self.expression = expr
        self.node = node
        self.generator = calc_possible_solutions  
        
    def __getitem__(self, args):
        varList = self.variable_list
        self.env.push_new_frame(varList)
        for i in range(len(varList)):
            idNode = varList[i]
            if len(varList)==1:
                value  = args
            else:
                value = args[i]
            self.env.set_value(idNode.idName, value)
        value = self.interpret(self.predicate, self.env) 
        if not value:
            raise ValueNotInDomainException(args)
        result = self.interpret(self.expression, self.env)  
        self.env.pop_frame() # exit scope
        return result

    def __eq__(self, aset):
        if aset==None:
            return False
        if isinstance(aset, SymbolicLambda):
            if not len(self.variable_list)==len(aset.variable_list):
                return False
            # may throw a DontKnowIfEqualException
            if not check_syntacticly_equal(self.predicate, aset.predicate):
                return False
            # may throw a DontKnowIfEqualException
            if not check_syntacticly_equal(self.expression, aset.expression):
                return False
            return True
        raise DontKnowIfEqualException("lambda compare not implemented")
    
    def __ne__(self, aset):
        return not self.__eq__(aset)
    
    # convert to explicit frozenset
    def enumerate_all(self):
        varList = self.variable_list
        pred    = self.predicate
        expr    = self.expression 
        func_list = []
        # new scope
        self.env.push_new_frame(varList)
        domain_generator = self.generator(pred, env, varList, interpret)
        # for every solution-entry found:
        for entry in domain_generator:
            # set all vars (of new frame/scope) to this solution
            i = 0
            for name in [x.idName for x in varList]:
                value = entry[name]
                self.env.set_value(name, value)
                i = i + 1
                if i==1:
                    arg = value
                else:
                    arg = tuple([arg, value])
            # test if it is really a solution
            try:
                if self.interpret(pred, env):  # test
                    # yes it is! calculate lambda-fun image an add this tuple to func_list       
                    image = interpret(expr, env)
                    tup = tuple([arg, image])
                    func_list.append(tup) 
            except ValueNotInDomainException:
                continue
        env.pop_frame() # exit scope
        return frozenset(func_list)

class SymbolicComprehensionSet(SymbolicSet):
    def __init__(self, varList, pred, node, env, interpret, calc_possible_solutions):
        SymbolicSet.__init__(self, env, interpret)
        self.variable_list = varList
        self.predicate = pred
        self.node = node
        self.generator = calc_possible_solutions    
    
    def __eq__(self, aset):
        if aset==None:
            return False
        if isinstance(aset, SymbolicComprehensionSet):
            if not len(self.variable_list)==len(aset.variable_list):
                return False
            # may throw a DontKnowIfEqualException
            if not check_syntacticly_equal(self.predicate, aset.predicate):
                return False
            return True
        if isinstance(aset, frozenset):
            explicit_set_repr = self.enumerate_all()
            return aset == explicit_set_repr
        raise DontKnowIfEqualException("set comp compare not implemented") 

    def __contains__(self, args):
        args = remove_tuples(args)
        varList = self.variable_list
        self.env.push_new_frame(varList)
        print len(varList), varList
        for i in range(len(varList)):
            idNode = varList[i]
            atype = self.env.get_type_by_node(idNode)
            value = build_arg_by_type(atype, args)
            self.env.set_value(idNode.idName, value)
        result = self.interpret(self.predicate, self.env) 
        self.env.pop_frame() # exit scope
        return result  
        
    # convert to explicit frozenset
    def enumerate_all(self):
        varList   = self.variable_list
        pred      = self.predicate
        env       = self.env
        interpret = self.interpret
        result = []
        # new scope
        self.env.push_new_frame(varList)
        domain_generator = self.generator(pred, env, varList, interpret)        
        for entry in domain_generator:
            for name in [x.idName for x in varList]:
                value = entry[name]
                env.set_value(name, value)
            try:
                if interpret(pred, env):  # test
                    i = 0
                    for name in [x.idName for x in varList]:
                        value = env.get_value(name)
                        i = i + 1
                        if i==1:
                            tup = value
                        else:
                            tup = tuple([tup,value])
                    result.append(tup)  
            except ValueNotInDomainException:
                continue
        env.pop_frame()
        return frozenset(result)      


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
    
    
# Ture:  these predicates are syntacticly equal
# True examples:
# {x|x:NAT}=={y|y:NAT}
# False: these predicates are unequal
# no false cases yet implemented
# Exception: I dont know if they are equal (likely case)
# DontKnow examples: 
# {x|x>3 & x<5}=={y|y=4}
# {x|x:NAT & x<200}=={y|y<200 & y:NAT}
# {x|x:INTEGER & x>=0 }=={y|y:NATURAL}
def check_syntacticly_equal(predicate0, predicate1):
    if predicate0.__class__ == predicate1.__class__:
        try:
            length = range(len(predicate0.children))
        except AttributeError:
            return True #clase check was successful and no more children to check
        for index in length:
            child0 = predicate0.children[index]
            child1 = predicate0.children[index]
            if not check_syntacticly_equal(child0, child1):
                return False
        return True
    else:
        raise DontKnowIfEqualException()


# This generator returns one relation(-list) between S and T S<-->T.
# S and T can both be symbolic or explicit. If S or T is not finit enumerable, 
# this function throws an exception. It returns no frozensets because some check
# operations (e.g. function property) are more easy on lists.
# TODO: returning a symbolic set here is possible, but needs more tests an
# interpreter modification
def make_explicit_set_of_realtion_lists(S,T):   
    # convert to explicit  
    if isinstance(S, frozenset):
        left = S
    else:
        left = S.enumerate_all()
    if isinstance(T, frozenset):
        right = T
    else:
        right = T.enumerate_all()
    # TODO: it is also possible to lazy-generate this set,
    #       but the _take generator becomes more complicated if 
    #       its input is a generator instead of a set
    all_combinations = [(x,y) for x in left for y in right]
    # size = |S|*|T|
    size = len(all_combinations)
    # empty relation
    yield []
    # calc all permutations
    for i in range(size):
        for lst in _take(all_combinations, i+1):
            assert len(lst)==i+1
            yield lst


# This function takes n elements of a list and returns them.
# It is a helper only used by make_explicit_set_of_realtion_lists to generate 
# all combinations/sub-lists of length n.
def _take(lst, n):
    # Basecase, take all in a row
    if n==1:
        for k in range(len(lst)):
            yield [lst[k]]
    # take one, remove it, take n-1, concatenate 
    else:
        assert n>1
        for k in range(len(lst)):
            e = lst[k]
            lst2 = list(lst)
            lst2.pop(k)
            for L in _take(lst2, n-1):
                yield L+[e]