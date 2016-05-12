from ast_nodes import *
from bexceptions import ValueNotInDomainException
from config import USE_RPYTHON_CODE
from enumeration_lazy import make_explicit_set_of_realtion_lists, enumerate_cross_product
from relation_helpers import *
from rpython_b_objmodel import W_Object
from symbolic_sets import SymbolicSet, PowerSetType, SymbolicCartSet
from symbolic_functions_with_predicate import SymbolicLambda, SymbolicComprehensionSet 


if USE_RPYTHON_CODE:
     from rpython_b_objmodel import frozenset

# only used by W_Objects. 
# Rpython does not support x in S
def x_in_S(x, S):
    return S.__contains__(x)
    #for e in S:
    #    if x.__eq__(e):
    #        return True
    #return False
    
class SymbolicRelationSet(SymbolicSet):
    def __init__(self, aset0, aset1, env, node):
        SymbolicSet.__init__(self, env)
        self.left_set = aset0
        self.right_set = aset1
        self.node = node   

    # all elements in Set
    def __contains__(self, element):
        if isinstance(element, SymbolicCartSet):    # check with symb info
            if USE_RPYTHON_CODE:
                for e in element.left_set:
                    if not x_in_S(e, self.left_set):
                        return False
                for e in element.right_set:
                    if not x_in_S(e, self.right_set):
                        return False
                return True
            else: 
                # symbolic cart sets contain sets of all elements and not one element
                for e in element.left_set:
                    if e not in self.left_set:
                        return False
                for e in element.right_set:
                    if e not in self.right_set:
                        return False
                return True
        elif isinstance(element, SymbolicSet):
            if USE_RPYTHON_CODE:
                for t in element:
                    assert isinstance(t, W_Tuple)
                    if not x_in_S(t.tvalue[0], self.left_set) or not x_in_S(t.tvalue[1], self.right_set):
                        return False
                return True 
            else:      
                for t in element:
                    assert isinstance(t, tuple)
                    if not t[0] in self.left_set or not t[1] in self.right_set:
                        return False
                return True 
        elif isinstance(element, PowerSetType): # check with type info
            assert isinstance(element.data, CartType)
            left  = element.data.left.data
            right = element.data.right.data
            return left in self.left_set and right in self.right_set 
        else:                                   # check finite set
            # FIXME: AST Node
            assert isinstance(element, frozenset)
            for e in element:
                if USE_RPYTHON_CODE:
                    if not x_in_S(e.tvalue[0], self.left_set) or not x_in_S(e.tvalue[1], self.right_set):
                        return False
                else:
                    assert isinstance(e, tuple)
                    if not e[0] in self.left_set or not e[1] in self.right_set:
                        return False
            return  True
        raise Exception("Not implemented: relation symbolic membership")

    def enumerate_all(self):
        if not self.explicit_set_computed:
            assert isinstance(self, W_Object)
            assert isinstance(self, SymbolicSet)
            result = []
            # RPython typing constraints made this ugly code necessary 
            if isinstance(self, SymbolicPartialFunctionSet):
                for e in self.SymbolicPartialFunctionSet_generator():
                     result.append(e)
            elif isinstance(self, SymbolicTotalFunctionSet):
                for e in self.SymbolicTotalFunctionSet_generator():
                     result.append(e)
            elif isinstance(self, SymbolicPartialBijectionSet):
                for e in self.SymbolicPartialBijectionSet_generator():
                     result.append(e)
            elif isinstance(self, SymbolicTotalBijectionSet):
                for e in self.SymbolicTotalBijectionSet_generator():
                     result.append(e)
            elif isinstance(self, SymbolicPartialInjectionSet):
                for e in self.SymbolicPartialInjectionSet_generator():
                     result.append(e)
            elif isinstance(self, SymbolicTotalInjectionSet):
                for e in self.SymbolicTotalInjectionSet_generator():
                     result.append(e)
            elif isinstance(self, SymbolicPartialSurjectionSet):
                for e in self.SymbolicPartialSurjectionSet_generator():
                     result.append(e)
            elif isinstance(self, SymbolicTotalSurjectionSet):
                for e in self.SymbolicTotalSurjectionSet_generator():
                     result.append(e)
            else:
                for e in self.SymbolicRelationSet_generator():
                    result.append(e)
                     #raise Exception("INTERNAL ERROR: unimplemented function enumeration")                         
            self.explicit_set_repr = frozenset(result)
            self.explicit_set_computed = True
        return self.explicit_set_repr
      
    def SymbolicRelationSet_generator(self):
        S = self.left_set
        T = self.right_set
        return make_explicit_set_of_realtion_lists(S,T)
        #return frozenset([])
    
    def __eq__(self, other):
        # TODO: handle empty set and maybe more sp. cases
        return SymbolicSet.__eq__(self, other)

    def __iter__(self):
        assert isinstance(self, W_Object)
        assert isinstance(self, SymbolicSet)
        self.SymbolicRelationSet_gen = self.SymbolicRelationSet_generator()
        return self 
    
    def next(self):
        assert isinstance(self, W_Object)
        assert isinstance(self, SymbolicSet)
        return self.SymbolicRelationSet_gen.next() 
    
    # This is NOT a set of tuples but a Set of functions or relations 
    def __getitem__(self, args):
        raise Exception("INTERNAL ERROR: function application f(x) on none-relation")

    def __repr__(self):
        return "@symbolic set: "+str(self.left_set)+"<->"+str(self.right_set)

 
class SymbolicPartialFunctionSet(SymbolicRelationSet): # S+->T
    def SymbolicPartialFunctionSet_generator(self):
        for relation in SymbolicRelationSet.SymbolicRelationSet_generator(self):
            if is_a_function(relation):
                yield relation
    
    # TODO: symbolic case, typing case
    def __contains__(self, element):
        if not SymbolicRelationSet.__contains__(self, element):
           return False
        if not is_a_function(element):
           return False
        return True

    def __iter__(self):
        assert isinstance(self, W_Object)
        assert isinstance(self, SymbolicSet)
        self.SymbolicPartialFunctionSet_gen = self.SymbolicPartialFunctionSet_generator()
        return self 
    
    def next(self):
        assert isinstance(self, W_Object)
        assert isinstance(self, SymbolicSet)
        return self.SymbolicPartialFunctionSet_gen.next()    

    def __repr__(self):
        return "@symbolic set: "+str(self.left_set)+"+->"+str(self.right_set)
    
class SymbolicTotalFunctionSet(SymbolicRelationSet): # S-->T
    def SymbolicTotalFunctionSet_generator(self):
        for relation in SymbolicRelationSet.SymbolicRelationSet_generator(self):
            if is_a_function(relation) and is_a_total_function(relation, self.left_set):
                yield relation

    def __contains__(self, element):
        if not SymbolicRelationSet.__contains__(self, element):
           return False
        if not is_a_function(element) or not is_a_total_function(element, self.left_set):
           return False
        return True
 
    def __iter__(self):
        assert isinstance(self, W_Object)
        assert isinstance(self, SymbolicSet)
        self.SymbolicTotalFunctionSet_gen = self.SymbolicTotalFunctionSet_generator()
        return self 
    
    def next(self):
        assert isinstance(self, W_Object)
        assert isinstance(self, SymbolicSet)
        return self.SymbolicTotalFunctionSet_gen.next()                        

    def __repr__(self):
        return "@symbolic set: "+str(self.left_set)+"-->"+str(self.right_set)
            
class SymbolicPartialInjectionSet(SymbolicRelationSet): # S>+>T 
    def SymbolicPartialInjectionSet_generator(self):
        for relation in SymbolicRelationSet.SymbolicRelationSet_generator(self):
            if is_a_function(relation) and is_a_inje_function(relation):
                yield relation

    def __contains__(self, element):
        if not SymbolicRelationSet.__contains__(self, element):
           return False
        if not is_a_function(element) or not is_a_inje_function(element):
           return False
        return True

    def __iter__(self):
        assert isinstance(self, W_Object)
        assert isinstance(self, SymbolicSet)
        self.SymbolicPartialInjectionSet_gen = self.SymbolicPartialInjectionSet_generator()
        return self 
    
    def next(self):
        assert isinstance(self, W_Object)
        assert isinstance(self, SymbolicSet)
        return self.SymbolicPartialInjectionSet_gen.next()   

    def __repr__(self):
        return "@symbolic set: "+str(self.left_set)+">+>"+str(self.right_set)        

class SymbolicTotalInjectionSet(SymbolicRelationSet): # S>->T
    def SymbolicTotalInjectionSet_generator(self):
        for relation in SymbolicRelationSet.SymbolicRelationSet_generator(self):
            if is_a_function(relation) and is_a_total_function(relation, self.left_set) and is_a_inje_function(relation):
                yield relation

    def __contains__(self, element):
        if not SymbolicRelationSet.__contains__(self, element):
           return False
        if not is_a_function(element) or not is_a_total_function(element, self.left_set) or not is_a_inje_function(element):
           return False
        return True

    def __iter__(self):
        assert isinstance(self, W_Object)
        assert isinstance(self, SymbolicSet)
        self.SymbolicTotalInjectionSet_gen = self.SymbolicTotalInjectionSet_generator()
        return self 
    
    def next(self):
        assert isinstance(self, W_Object)
        assert isinstance(self, SymbolicSet)
        return self.SymbolicTotalInjectionSet_gen.next()             
 
    def __iter__(self):
        assert isinstance(self, W_Object)
        assert isinstance(self, SymbolicSet)
        self.SymbolicTotalInjectionSet_gen = self.SymbolicTotalInjectionSet_generator()
        return self 
    
    def next(self):
        assert isinstance(self, W_Object)
        assert isinstance(self, SymbolicSet)
        return self.SymbolicTotalInjectionSet_gen.next()    

    def __repr__(self):
        return "@symbolic set: "+str(self.left_set)+">->"+str(self.right_set)        
      
class SymbolicPartialSurjectionSet(SymbolicRelationSet): #S+->>T
    def SymbolicPartialSurjectionSet_generator(self):
        for relation in SymbolicRelationSet.SymbolicRelationSet_generator(self):
            if is_a_function(relation) and is_a_surj_function(relation, self.right_set):
                yield relation

    def __contains__(self, element):
        if not SymbolicRelationSet.__contains__(self, element):
           return False
        if not is_a_function(element) or not is_a_surj_function(element, self.right_set):
           return False
        return True

    def __iter__(self):
        assert isinstance(self, W_Object)
        assert isinstance(self, SymbolicSet)
        self.SymbolicPartialSurjectionSet_gen = self.SymbolicPartialSurjectionSet_generator()
        return self 
    
    def next(self):
        assert isinstance(self, W_Object)
        assert isinstance(self, SymbolicSet)
        return self.SymbolicPartialSurjectionSet_gen.next() 

    def __repr__(self):
        return "@symbolic set: "+str(self.left_set)+"+->>"+str(self.right_set)            
    
class SymbolicTotalSurjectionSet(SymbolicRelationSet): # S-->>T
    def SymbolicTotalSurjectionSet_generator(self):
        for relation in SymbolicRelationSet.SymbolicRelationSet_generator(self):
            if is_a_function(relation) and is_a_total_function(relation, self.left_set) and is_a_surj_function(relation, self.right_set):
                yield relation

    def __contains__(self, element):
        if not SymbolicRelationSet.__contains__(self, element):
           return False
        if not is_a_function(element) or not is_a_total_function(element, self.left_set) or not is_a_surj_function(element, self.right_set):
           return False
        return True

    def __iter__(self):
        assert isinstance(self, W_Object)
        assert isinstance(self, SymbolicSet)
        self.SymbolicTotalSurjectionSet_gen = self.SymbolicTotalSurjectionSet_generator()
        return self 
    
    def next(self):
        assert isinstance(self, W_Object)
        assert isinstance(self, SymbolicSet)
        return self.SymbolicTotalSurjectionSet_gen.next() 

    def __repr__(self):
        return "@symbolic set: "+str(self.left_set)+"-->>"+str(self.right_set)            

class SymbolicTotalBijectionSet(SymbolicRelationSet): # S>->>T
    def SymbolicTotalBijectionSet_generator(self):
        for relation in SymbolicRelationSet.SymbolicRelationSet_generator(self):
            if is_a_function(relation) and is_a_total_function(relation, self.left_set) and is_a_surj_function(relation, self.right_set) and is_a_inje_function(relation):
                yield relation

    def __contains__(self, element):
        if not SymbolicRelationSet.__contains__(self, element):
           return False
        if not is_a_function(element) or not is_a_total_function(element, self.left_set) or not is_a_surj_function(element, self.right_set) or not is_a_inje_function(element):
           return False
        return True

    def __iter__(self):
        assert isinstance(self, W_Object)
        assert isinstance(self, SymbolicSet)
        self.SymbolicTotalBijectionSet_gen = self.SymbolicTotalBijectionSet_generator()
        return self 
    
    def next(self):
        assert isinstance(self, W_Object)
        assert isinstance(self, SymbolicSet)
        return self.SymbolicTotalBijectionSet_gen.next() 

    def __repr__(self):
        return "@symbolic set: "+str(self.left_set)+">->>"+str(self.right_set)    
                      
class SymbolicPartialBijectionSet(SymbolicRelationSet):
    def SymbolicPartialBijectionSet_generator(self):
        for relation in SymbolicRelationSet.SymbolicRelationSet_generator(self):
            if is_a_function(relation) and is_a_surj_function(relation, self.right_set) and is_a_inje_function(relation):
                yield relation

    def __contains__(self, element):
        if not SymbolicRelationSet.__contains__(self, element):
           return False
        if not is_a_function(element) or not is_a_surj_function(element, self.right_set) or not is_a_inje_function(element):
           return False
        return True

    def __iter__(self):
        assert isinstance(self, W_Object)
        assert isinstance(self, SymbolicSet)
        self.SymbolicPartialBijectionSet_gen = self.SymbolicPartialBijectionSet_generator()
        return self 
    
    def next(self):
        assert isinstance(self, W_Object)
        assert isinstance(self, SymbolicSet)
        return self.SymbolicPartialBijectionSet_gen.next()   

    def __repr__(self):
        return "@symbolic set: "+str(self.left_set)+">>>"+str(self.right_set)                  

class SymbolicFirstProj(SymbolicSet):
    def __init__(self, aset0, aset1, env, node):
        SymbolicSet.__init__(self, env)
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
        if not (isinstance(arg, tuple) or isinstance(arg, W_Tuple)):
            raise TypeError()
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
                    if USE_RPYTHON_CODE:
                         from rpython_interp import interpret
                    else:
                         from interp import interpret 
                    if isinstance(xx, AIdentifierExpression) and xx.idName==x:
                        S = interpret(belong_pred0.children[1], self.env)
                    if isinstance(yy, AIdentifierExpression) and yy.idName==y:
                        T = interpret(belong_pred1.children[1], self.env)
                    if isinstance(other.expression, AIdentifierExpression): # else: maybe equal.            
                        try:
                            if self.left_set==S and self.right_set==T and x==other.expression.idName:
                                return True              
                        except NameError:
                            pass # maybe equal. use brute-force in symbolic set              
            return SymbolicSet.__eq__(self, other)
    
    def enumerate_all(self):
        if not self.explicit_set_computed:
            assert isinstance(self, W_Object)
            assert isinstance(self, SymbolicSet)
            result = []
            for e in self.SymbolicFirstProj_generator():
                 result.append(e)                                         
            self.explicit_set_repr = frozenset(result)
            self.explicit_set_computed = True
        return self.explicit_set_repr

    
    def SymbolicFirstProj_generator(self):
        for cross_prod in enumerate_cross_product(self.left_set, self.right_set):
             yield tuple([cross_prod,cross_prod[0]])      

    def __iter__(self):
        assert isinstance(self, W_Object)
        assert isinstance(self, SymbolicSet)
        self.SymbolicFirstProj_gen = self.SymbolicFirstProj_generator()
        return self 
    
    def next(self):
        assert isinstance(self, W_Object)
        assert isinstance(self, SymbolicSet)
        return self.SymbolicFirstProj_gen.next() 

    def __repr__(self):
        return "@symbolic set: proj1("+str(self.left_set)+","+str(self.right_set)+")"    

class SymbolicSecondProj(SymbolicSet):
    def __init__(self, aset0, aset1, env, node):
        SymbolicSet.__init__(self, env)
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
        if not (isinstance(arg, tuple) or isinstance(arg, W_Tuple)):
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
                    if USE_RPYTHON_CODE:
                         from rpython_interp import interpret
                    else:
                         from interp import interpret 
                    if isinstance(xx, AIdentifierExpression) and xx.idName==x:
                        S = interpret(belong_pred0.children[1], self.env)
                    if isinstance(yy, AIdentifierExpression) and yy.idName==y:
                        T = interpret(belong_pred1.children[1], self.env)
                    if isinstance(other.expression, AIdentifierExpression): # else: maybe equal.            
                        try:
                            if self.left_set==S and self.right_set==T and y==other.expression.idName:
                                return True              
                        except NameError:
                            pass # maybe equal. use brute-force in symbolic set              
            return SymbolicSet.__eq__(self, other)

    def enumerate_all(self):
        if not self.explicit_set_computed:
            assert isinstance(self, W_Object)
            assert isinstance(self, SymbolicSet)
            result = []
            for e in self.SymbolicSecondProj_generator():
                 result.append(e)                                         
            self.explicit_set_repr = frozenset(result)
            self.explicit_set_computed = True
        return self.explicit_set_repr
        
    def SymbolicSecondProj_generator(self):
        for cross_prod in enumerate_cross_product(self.left_set, self.right_set):
             yield tuple([cross_prod,cross_prod[1]])

    def __iter__(self):
        assert isinstance(self, W_Object)
        assert isinstance(self, SymbolicSet)
        self.SymbolicSecondProj_gen = self.SymbolicSecondProj_generator()
        return self 
    
    def next(self):
        assert isinstance(self, W_Object)
        assert isinstance(self, SymbolicSet)
        return self.SymbolicSecondProj_gen.next()                         

    def __repr__(self):
        return "@symbolic set: proj2("+str(self.left_set)+","+str(self.right_set)+")"
        
# self.left_set==self.right_set    
class SymbolicIdentitySet(SymbolicRelationSet):
    def enumerate_all(self):
        if not self.explicit_set_computed:
            assert self.left_set==self.right_set
            if isinstance(self.left_set, SymbolicSet):
                aSet = self.left_set.enumerate_all()
            else:
                aSet = self.left_set
            if USE_RPYTHON_CODE: 
                id_r = [W_Tuple((e,e)) for e in aSet]
            else:
                id_r = [(x,x) for x in aSet]
            self.explicit_set_repr = frozenset(id_r)
            self.explicit_set_computed = True
        return self.explicit_set_repr

    def SymbolicIdentitySet_generator(self):
        assert self.left_set==self.right_set
        for e in self.left_set:
            if USE_RPYTHON_CODE: 
                yield W_Tuple((e,e))
            else:
                yield tuple([e,e])

    def __contains__(self, element):
        if isinstance(element, W_Tuple):
            if element.tvalue[0].__eq__(element.tvalue[1]) and self.left_set.__contains__(element.tvalue[0]):
                return True
            else:
                return False 
        else:
            assert isinstance(element, tuple)
            if element[0]==element[1] and element[0] in self.left_set:
                return True
            else:
                return False 

    def __iter__(self):
        assert isinstance(self, W_Object)
        assert isinstance(self, SymbolicSet)
        self.SymbolicIdentitySet_gen = self.SymbolicIdentitySet_generator()
        return self 
    
    def next(self):
        assert isinstance(self, W_Object)
        assert isinstance(self, SymbolicSet)
        return self.SymbolicIdentitySet_gen.next()

    def __getitem__(self, arg):
        if self.left_set.__contains__(arg):
            return arg 
        raise IndexError()

    def __repr__(self):
        return "@symbolic set: id("+str(self.left_set)+")"
                             
class SymbolicCompositionSet(SymbolicRelationSet):
    def __init__(self, arelation0, arelation1, env, node):
        SymbolicSet.__init__(self, env)
        self.left_relation = arelation0
        self.right_relation = arelation1
        self.node = node 


    # element in Set
    # WARNING: may cause Timeout
    # FIXME: works only for min/max int because of all types enumeration in enumeration.py
    def __contains__(self, element):
        assert isinstance(element, tuple)
        for tup in [x for x in self.left_relation if x[0]== element[0]]:
            if isinstance(self.right_relation, SymbolicLambda):
                return self.right_relation.__getitem__(tup[1])==element[1]
            for tup2 in [y for y in self.right_relation if y[0]==tup[1]]:
                if tup2[1]==element[1]:
                    return True
        return False
                
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
                    if USE_RPYTHON_CODE:
                         from rpython_interp import interpret
                    else:
                         from interp import interpret 
                    pre_result = interpret(lambda_function.predicate, self.env)
                    if pre_result:
                        # calculate element of composition expression
                        lambda_image = interpret(lambda_function.expression, self.env)
                        result.append(tuple([domain, lambda_image]))
                self.env.pop_frame() # exit scope
                self.explicit_set_repr = frozenset(result)
            else:
                result = []
                for e in self.SymbolicCompositionSet_generator():
                    result.append(e)
                self.explicit_set_repr = frozenset(result)
            self.explicit_set_computed = True
        return self.explicit_set_repr

    def SymbolicCompositionSet_generator(self):
        for e0 in self.left_relation:
            for e1 in self.right_relation:
                #print e0[1], e1[0], e0[1]==e1[0]
                if e0[1]==e1[0]:
                    yield (e0[0],e1[1])

    def __iter__(self):
        assert isinstance(self, W_Object)
        assert isinstance(self, SymbolicSet)
        self.SymbolicCompositionSet_gen = self.SymbolicCompositionSet_generator()
        return self 
    
    def next(self):
        assert isinstance(self, W_Object)
        assert isinstance(self, SymbolicSet)
        return self.SymbolicCompositionSet_gen.next()
        
            
    # may throw valueNotInDomainException
    # e.g. left_relation = {(0,2), (1,5), (2,5), (3,7)} 
    # and  right_relation = {(0,0), (2,-1), (5,8), (6,9)}, 
    # R1 ; R2 = {(0, -1), (1,8), (2,8)}
    def __getitem__(self, arg):
        if isinstance(self.left_relation, frozenset):
            image_set_left = [t[1] for t in self.left_relation if t[0]==arg]
            if image_set_left==[]:
                raise ValueNotInDomainException(arg)
            z = image_set_left[0]            
        else:
            z = self.left_relation[arg]
        # z may not be an element of self.right_relation 
        if isinstance(self.right_relation, frozenset):
            image_set_right = [t[1] for t in self.right_relation if t[0]==z]
            if image_set_right==[]:
                raise ValueNotInDomainException(arg)
            image= image_set_right[0]
        else:
            image = self.right_relation[z]
        return image

    def __repr__(self):
        return "@symbolic set: "+str(self.left_set)+";"+str(self.right_set)

# The SymbolicRelationSet methods asume a domain- and imageset present.
# This type of relation has none(directly).
class SymbolicTransRelation(SymbolicSet):
    def __init__(self, function, env, node):
        SymbolicSet.__init__(self, env)
        self.function = function
        self.node = node
        
    def enumerate_all(self):
        if not self.explicit_set_computed:
            relation = []
            for tup in self.function:
                if USE_RPYTHON_CODE: 
                    preimage = tup.tvalue[0]
                    for image in tup.tvalue[1]:
                        relation.append(W_Tuple((preimage, image)))
                else:
                    preimage = tup[0]
                    for image in tup[1]:
                        relation.append(tuple([preimage, image]))
            self.explicit_set_repr = frozenset(relation)
            self.explicit_set_computed = True
        return self.explicit_set_repr
    
    def SymbolicTransRelation_generator(self):
        for tup in self.function:
            if USE_RPYTHON_CODE: 
                preimage = tup.tvalue[0]
                for image in tup.tvalue[1]:
                    yield W_Tuple((preimage, image))
            else:
                preimage = tup[0]
                for image in tup[1]:
                    yield tuple([preimage, image])

    def __iter__(self):
        assert isinstance(self, W_Object)
        assert isinstance(self, SymbolicSet)
        self.SymbolicTransRelation_gen = self.SymbolicTransRelation_generator()
        return self 
    
    def next(self):
        assert isinstance(self, W_Object)
        assert isinstance(self, SymbolicSet)
        return self.SymbolicTransRelation_gen.next()

    def __repr__(self):
        return "@symbolic set: rel"

# The SymbolicRelationSet methods asume a domain- and imageset present.
# This type of relation has none.
class SymbolicTransFunction(SymbolicSet):
    def __init__(self, relation, env, node):
        SymbolicSet.__init__(self, env)
        self.relation = relation
        self.node = node

    def enumerate_all(self):
        if not self.explicit_set_computed:
            function = []
            for tup in self.relation:
                image = []
                if USE_RPYTHON_CODE:
                    preimage = tup.tvalue[0]
                    for tup2 in self.relation:
                        if tup2.tvalue[0].__eq__(preimage):
                            image.append(tup2.tvalue[1])
                    function.append(W_Tuple((preimage,frozenset(image))))
                else:
                    preimage = tup[0]
                    for tup2 in self.relation:
                        if tup2[0]==preimage:
                            image.append(tup2[1])
                    function.append(tuple([preimage,frozenset(image)]))
            self.explicit_set_repr = frozenset(function)
            self.explicit_set_computed = True
        return self.explicit_set_repr        
        
    def SymbolicTransFunction_generator(self):
        for tup in self.relation:
            image = []
            if USE_RPYTHON_CODE:
                preimage = tup.tvalue[0]
                for tup2 in self.relation:
                    if tup2.tvalue[0].__eq__(preimage):
                        image.append(tup2.tvalue[1])
                yield W_Tuple((preimage,frozenset(image)))
            else: 
                preimage = tup[0]
                for tup2 in self.relation:
                    if tup2[0]==preimage:
                        image.append(tup2[1])
                yield tuple([preimage,frozenset(image)])

    def __iter__(self):
        assert isinstance(self, W_Object)
        assert isinstance(self, SymbolicSet)
        self.SymbolicTransFunction_gen = self.SymbolicTransFunction_generator()
        return self 
    
    def next(self):
        assert isinstance(self, W_Object)
        assert isinstance(self, SymbolicSet)
        return self.SymbolicTransFunction_gen.next()
        

    def __repr__(self):
        return "@symbolic set: trans"                                      

class SymbolicInverseRelation(SymbolicRelationSet):
    def __init__(self, relation, env, node):
        SymbolicSet.__init__(self, env)
        self.relation = relation
        self.node = node
        
    def __len__(self):
        return self.relation.__len__()
        
    def enumerate_all(self):
        if not self.explicit_set_computed:
            if isinstance(self.relation, SymbolicSet):  
                rel = self.relation.enumerate_all()
            else:
                rel = self.relation
            if USE_RPYTHON_CODE:
                inv_rel = [W_Tuple((x.tvalue[1],x.tvalue[0])) for x in rel]
            else:
                inv_rel = [(x[1],x[0]) for x in rel]
            self.explicit_set_repr = frozenset(inv_rel)
            self.explicit_set_computed = True
        return self.explicit_set_repr
    
    def SymbolicInverseRelation_generator(self):
        for e in self.relation:
            if USE_RPYTHON_CODE:
                yield W_Tuple((e.tvalue[1],e.tvalue[0]))
            else:
                yield tuple([e[1],e[0]])
            
    def __iter__(self):
        assert isinstance(self, W_Object)
        assert isinstance(self, SymbolicSet)
        self.SymbolicInverseRelation_gen = self.SymbolicInverseRelation_generator()
        return self 
    
    def next(self):
        assert isinstance(self, W_Object)
        assert isinstance(self, SymbolicSet)
        return self.SymbolicInverseRelation_gen.next()
    
    def __contains__(self, other):
        if USE_RPYTHON_CODE:
            inv_e = W_Tuple((other.tvalue[1],other.tvalue[0]))
            for t in self.relation:
                if t.__eq__(inv_e):
                    return True
            return False
        else:
            inv_element = tuple([other[1],other[0]])
            return inv_element in self.relation


    def __getitem__(self, arg):
        result = []
        for t in self.relation:
            if USE_RPYTHON_CODE:
                if t[1].__eq__(arg):
                    result.append(t[0])
            else:
                if t[1]==arg:
                    result.append(t[0])
        if len(result)==1:
            return result[0]
        else:
            return result
        raise IndexError()

    def __repr__(self):
        return "@symbolic set: inverse("+str(self.relation)+")"
