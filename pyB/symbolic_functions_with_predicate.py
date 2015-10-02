# symbolic functions defined by a predicate
from bexceptions import ValueNotInDomainException, DontKnowIfEqualException
from config import USE_RPYTHON_CODE
from helpers import remove_tuples, build_arg_by_type
from pretty_printer import pretty_print
from rpython_b_objmodel import W_Object, W_Tuple
from symbolic_sets import SymbolicSet

if USE_RPYTHON_CODE:
     from rpython_b_objmodel import frozenset

# True:  these predicates are syntacticly equal
# True examples:
# {x|x:NAT}=={y|y:NAT}
# False: these predicates are unequal
# no false cases yet implemented
# Exception: I dont know if they are equal (likely case)
# DontKnow examples: 
# {x|x>3 & x<5}=={y|y=4}
# {x|x:NAT & x<200}=={y|y<200 & y:NAT}
# {x|x:INTEGER & x>=0 }=={y|y:NATURAL}
# returntype: boolean
def check_syntactically_equal(predicate0, predicate1):
    if predicate0.__class__ == predicate1.__class__:
        try:
            length = range(len(predicate0.children))
        except AttributeError:
            return True #clase check was successful and no more children to check
        for index in length:
            child0 = predicate0.children[index]
            child1 = predicate0.children[index]
            if not check_syntactically_equal(child0, child1):
                return False
        return True
    else:
        message = "ERROR: failed to check if predicates are equal: '%s' and '%s'" %(pretty_print(predicate0),pretty_print(predicate1))
        print message
        raise DontKnowIfEqualException(message)
        return False
        
# __getitem__ implemented inside interp to avoid env and interp_callable link
class SymbolicLambda(SymbolicSet):
    def __init__(self, varList, pred, expr, node, env, interpret, calc_possible_solutions):
        SymbolicSet.__init__(self, env, interpret)
        self.variable_list = varList
        self.predicate = pred
        self.expression = expr
        self.node = node
        self.domain_generator = calc_possible_solutions
        self.explicit_set_computed = False
    
    # TODO: all __getitem__ methods have problems with implicit enum
    # e.g. [x for x in R] with R  SymbolicLambda   
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
        # FIXME: This is not the correct position for a catch. move to higher level  
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
            if not check_syntactically_equal(self.predicate, aset.predicate):
                return False
            # may throw a DontKnowIfEqualException
            if not check_syntactically_equal(self.expression, aset.expression):
                return False
            return True
        if isinstance(aset, SymbolicSet):
            return aset==self # impl. use of symbolicSet.__eq__
        if isinstance(aset, frozenset):
            if not self.explicit_set_computed:
                self.explicit_set_repr = self.enumerate_all()
                self.explicit_set_computed = True
            return aset == self.explicit_set_repr
        # FAIL!
        pp_self = pretty_print(self.node)
        pp_other = pretty_print(aset.node)
        string = "lambda compare not implemented %s = %s" % (pp_self, pp_other)
        print string
        raise DontKnowIfEqualException(string)
    
    def __ne__(self, aset):
        return not self.__eq__(aset)

    # membership test. New Fame. Set bound variables to value. Eval. Return
    def __contains__(self, args):
        args = remove_tuples(args)
        varList = self.variable_list
        self.env.push_new_frame(varList) 
        for i in range(len(varList)):
            idNode = varList[i]
            atype = self.env.get_type_by_node(idNode)
            value = build_arg_by_type(atype, args)
            self.env.set_value(idNode.idName, value)
        domain_value = self.interpret(self.predicate, self.env)
        image_value  = self.interpret(self.expression, self.env) 
        self.env.pop_frame() # exit scope
        return domain_value and image_value==args[-1]
    
    # convert to explicit frozenset
    # dont use generator to avoid rapid frame push/pop
    def enumerate_all(self):
        if not self.explicit_set_computed:
            varList = self.variable_list
            pred    = self.predicate
            expr    = self.expression 
            env       = self.env
            interpret = self.interpret
            func_list = []
            # new scope
            env.push_new_frame(varList)
            domain_generator = self.domain_generator(pred, env, varList, interpret)
            # for every solution-entry found:
            for entry in domain_generator:
                # set all vars (of new frame/scope) to this solution
                i = 0
                for name in [x.idName for x in varList]:
                    value = entry[name]
                    env.set_value(name, value)
                    i = i + 1
                    if i==1:
                        arg = value
                    else:
                        arg = tuple([arg, value])
                # test if it is really a solution
                try:
                    if interpret(pred, env):  # test
                        # yes it is! calculate lambda-fun image an add this tuple to func_list       
                        image = interpret(expr, env)
                        if isinstance(image, SymbolicSet):
                            image = image.enumerate_all()
                        tup = tuple([arg, image])
                        func_list.append(tup) 
                except ValueNotInDomainException:
                    continue
            env.pop_frame() # exit scope
            self.explicit_set_repr = frozenset(func_list)
            self.explicit_set_computed = True
        return self.explicit_set_repr

    # Warning! push/pop frame
    def SymbolicLambda_generator(self):
        varList = self.variable_list
        pred    = self.predicate
        expr    = self.expression 
        env       = self.env
        interpret = self.interpret
        # new scope
        env.push_new_frame(varList)
        domain_generator = self.domain_generator(pred, env, varList, interpret)
        # for every solution-entry found:
        for entry in domain_generator:
            # set all vars (of new frame/scope) to this solution
            i = 0 #i-th argument 
            for name in [x.idName for x in varList]:
                value = entry[name]
                env.set_value(name, value)
                i = i + 1
                if i==1:
                    arg = value
                else:
                    arg = tuple([arg, value])
            # test if it is really a solution
            try:
                if interpret(pred, env):  # test
                    # yes it is! calculate lambda-fun image and yield result (tuple-type)      
                    image = interpret(expr, env)
                    tup = tuple([arg, image])
                    env.pop_frame() # exit scope
                    yield tup
                    env.push_new_frame(varList)
            except ValueNotInDomainException:
                continue                
        env.pop_frame() # exit scope

    def __iter__(self):
        assert isinstance(self, W_Object)
        assert isinstance(self, SymbolicSet)
        self.SymbolicLambda_gen = self.SymbolicLambda_generator()
        return self 
    
    def next(self):
        assert isinstance(self, W_Object)
        assert isinstance(self, SymbolicSet)
        return self.SymbolicLambda_gen.next()            


class SymbolicComprehensionSet(SymbolicSet):
    def __init__(self, varList, pred, node, env, interpret, calc_possible_solutions):
        SymbolicSet.__init__(self, env, interpret)
        self.variable_list = varList
        self.predicate = pred
        self.node = node
        self.domain_generator = calc_possible_solutions
        self.explicit_set_computed = False 
    
    def __getitem__(self, args):
        assert len(self.variable_list)>1
        # 1. map args to var-nodes
        args = remove_tuples(args)
        self.env.push_new_frame(self.variable_list)
        unset = len(self.variable_list)
        for i in range(len(args)):
            idNode = self.variable_list[i]
            atype = self.env.get_type_by_node(idNode)
            value = build_arg_by_type(atype, args)
            self.env.set_value(idNode.idName, value)
            unset = unset -1
        # TODO: 2. compute missing bound variables 
        print unset, "unset bound variables:", [x.idName for x in self.variable_list[unset:]]  
        raise NotImplementedError()
        self.env.pop_frame() # exit scope
        return result    
    
    def __eq__(self, aset):
        if aset is None:
            return False
        if isinstance(aset, SymbolicComprehensionSet):
            if not len(self.variable_list)==len(aset.variable_list):
                return False
            # may throw a DontKnowIfEqualException
            if not check_syntactically_equal(self.predicate, aset.predicate):
                return False
            return True
        if isinstance(aset, frozenset):
            if not self.explicit_set_computed:
                self.explicit_set_repr = self.enumerate_all()
                self.explicit_set_computed = True
            return aset == self.explicit_set_repr
        raise DontKnowIfEqualException("set comp compare not implemented") 

    # membership test. New Fame. Set bound variables to value. Eval. Return
    def __contains__(self, args):
        args = remove_tuples(args)
        varList = self.variable_list
        self.env.push_new_frame(varList)
        #print len(varList), varList
        for i in range(len(varList)):
            idNode = varList[i]
            # type needed to map args to value
            atype = self.env.get_type_by_node(idNode)
            value = build_arg_by_type(atype, args)
            self.env.set_value(idNode.idName, value)
        result = self.interpret(self.predicate, self.env) 
        self.env.pop_frame() # exit scope
        if USE_RPYTHON_CODE:
            return result.bvalue
        return result  
        
    # convert to explicit frozenset
    def enumerate_all(self):
        if not self.explicit_set_computed:
            varList   = self.variable_list
            pred      = self.predicate
            env       = self.env
            interpret = self.interpret
            names     = [x.idName for x in varList]
            result = []
            # new scope
            self.env.push_new_frame(varList)
            domain_generator = self.domain_generator(pred, env, varList, interpret)        
            for entry in domain_generator:
                for name in names:
                    value = entry[name]
                    env.set_value(name, value)
                try:
                    if USE_RPYTHON_CODE:
                        bool = interpret(pred, env).bvalue
                    else:
                        bool = interpret(pred, env)
                    if bool:  # test
                        i = 0
                        name = names[0]
                        tup = env.get_value(name)
                        for name in names[1:]:
                            value = env.get_value(name)
                            i = i + 1
                            if USE_RPYTHON_CODE:
                                tup = W_Tuple((tup, value))
                            else:
                                tup = tuple([tup,value])
                        result.append(tup)  
                except ValueNotInDomainException:
                    continue
            env.pop_frame()
            self.explicit_set_repr = frozenset(result) 
            self.explicit_set_computed = True
        return self.explicit_set_repr 
    
    
    # Warning! push/pop frame
    def SymbolicComprehensionSet_generator(self):
        varList   = self.variable_list
        pred      = self.predicate
        env       = self.env
        interpret = self.interpret
        names     = [x.idName for x in varList]
        env.push_new_frame(varList)
        domain_generator = self.domain_generator(pred, env, varList, interpret) 
        for entry in domain_generator:
                for name in names:
                    value = entry[name]
                    env.set_value(name, value)
                try:
                    if USE_RPYTHON_CODE:
                        bool = interpret(pred, env).bvalue
                    else:
                        bool = interpret(pred, env)
                    if bool:  # test
                        i = 0
                        name = names[0]
                        tup = env.get_value(name)
                        for name in names[1:]:
                            value = env.get_value(name)
                            i = i + 1
                            if USE_RPYTHON_CODE:
                                tup = W_Tuple((tup, value))
                            else:
                                tup = tuple([tup,value])
                        env.pop_frame()
                        yield tup
                        env.push_new_frame(varList)   
                except ValueNotInDomainException:
                    continue
        env.pop_frame()

    def __iter__(self):
        assert isinstance(self, W_Object)
        assert isinstance(self, SymbolicSet)
        self.SymbolicComprehensionSet_gen = self.SymbolicComprehensionSet_generator()
        return self 
    
    def next(self):
        assert isinstance(self, W_Object)
        assert isinstance(self, SymbolicSet)
        return self.SymbolicComprehensionSet_gen.next()   


class SymbolicQuantifiedIntersection(SymbolicSet):
    def __init__(self, varList, pred, expr, node, env, interpret, calc_possible_solutions):
        SymbolicSet.__init__(self, env, interpret)
        self.variable_list = varList
        self.predicate = pred
        self.expression = expr
        self.node = node
        self.domain_generator = calc_possible_solutions
        self.explicit_set_computed = False               
        
    # convert to explicit frozenset
    # dont use generator to avoid rapid frame push/pop
    def enumerate_all(self):
        if not self.explicit_set_computed:
            result = frozenset([])
            varList = self.variable_list
            pred    = self.predicate
            expr    = self.expression 
            env       = self.env
            interpret = self.interpret
            node      = self.node
            names     = [x.idName for x in varList]
            func_list = []
            # new scope
            env.push_new_frame(varList)
            domain_generator = self.domain_generator(pred, env, varList, interpret)
            for entry in domain_generator:
                for name in names:
                    value = entry[name]
                    env.set_value(name, value)
                try:
                    tst = interpret(pred, env)
                    if USE_RPYTHON_CODE:
                        cond = tst.bvalue
                    else:
                        cond = tst
                    if cond:  # test
                        # intersection with empty set is always empty: two cases are needed
                        if result.__eq__(frozenset([])): 
                            result = interpret(expr, env)
                            if isinstance(result, SymbolicSet):
                                result = result.enumerate_all()   
                        else:
                            aSet = interpret(expr, env)
                            if isinstance(aSet, SymbolicSet):
                                aSet = aSet.enumerate_all()       
                            result = result.intersection(aSet)
                except ValueNotInDomainException:
                    continue
            env.pop_frame()
            self.explicit_set_repr = result
            self.explicit_set_computed = True
        return self.explicit_set_repr

    def SymbolicQuantifiedIntersection_generator(self):
        result = self.enumerate_all()
        for e in result:
            yield e

    def __iter__(self):
        assert isinstance(self, W_Object)
        assert isinstance(self, SymbolicSet)
        self.SymbolicQuantifiedIntersection_gen = self.SymbolicQuantifiedIntersection_generator()
        return self 
    
    def next(self):
        assert isinstance(self, W_Object)
        assert isinstance(self, SymbolicSet)
        return self.SymbolicQuantifiedIntersection_gen.next() 


class SymbolicQuantifiedUnion(SymbolicSet):
    def __init__(self, varList, pred, expr, node, env, interpret, calc_possible_solutions):
        SymbolicSet.__init__(self, env, interpret)
        self.variable_list = varList
        self.predicate = pred
        self.expression = expr
        self.node = node
        self.domain_generator = calc_possible_solutions
        self.explicit_set_computed = False

    # convert to explicit frozenset
    # dont use generator to avoid rapid frame push/pop
    def enumerate_all(self):
        if not self.explicit_set_computed:        
            result = frozenset([])
            varList = self.variable_list
            pred    = self.predicate
            expr    = self.expression 
            env       = self.env
            interpret = self.interpret
            node      = self.node
            names     = [x.idName for x in varList]
            # new scope
            env.push_new_frame(varList)
            domain_generator = self.domain_generator(pred, env, varList, interpret)
            for entry in domain_generator:
                for name in names:
                    value = entry[name]
                    env.set_value(name, value)
                try:
                    tst = interpret(pred, env)
                    if USE_RPYTHON_CODE:
                        cond = tst.bvalue
                    else:
                        cond = tst
                    if cond:  # test (|= ior)
                        aSet = interpret(expr, env)
                        if isinstance(aSet, SymbolicSet):
                            aSet = aSet.enumerate_all() 
                        result = result.union(aSet)
                except ValueNotInDomainException:
                    continue
            env.pop_frame()
            self.explicit_set_repr = result
            self.explicit_set_computed = True
        return self.explicit_set_repr

    def SymbolicQuantifiedUnion_generator(self):
        result = self.enumerate_all()
        for e in result:
            yield e

    def __iter__(self):
        assert isinstance(self, W_Object)
        assert isinstance(self, SymbolicSet)
        self.SymbolicQuantifiedUnion_gen = self.SymbolicQuantifiedUnion_generator()
        return self 
    
    def next(self):
        assert isinstance(self, W_Object)
        assert isinstance(self, SymbolicSet)
        return self.SymbolicQuantifiedUnion_gen.next() 