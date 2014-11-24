# symbolic functions defined by a predicate
from helpers import remove_tuples, build_arg_by_type
from symbolic_helpers import check_syntacticly_equal 
from symbolic_sets import SymbolicSet
from pretty_printer import pretty_print

# __getitem__ implemented inside interp to avoid env and interp_callable link
class SymbolicLambda(SymbolicSet):
    def __init__(self, varList, pred, expr, node, env, interpret, calc_possible_solutions):
        SymbolicSet.__init__(self, env, interpret)
        self.variable_list = varList
        self.predicate = pred
        self.expression = expr
        self.node = node
        self.domain_generator = calc_possible_solutions
        self.explicit_set_repr = None  
    
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
            if not check_syntacticly_equal(self.predicate, aset.predicate):
                return False
            # may throw a DontKnowIfEqualException
            if not check_syntacticly_equal(self.expression, aset.expression):
                return False
            return True
        if isinstance(aset, SymbolicSet):
            return aset==self # impl. use of symbolicSet.__eq__
        if isinstance(aset, frozenset):
            if self.explicit_set_repr==None:
                self.explicit_set_repr = self.enumerate_all()
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
        if self.explicit_set_repr==None:
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
                        tup = tuple([arg, image])
                        func_list.append(tup) 
                except ValueNotInDomainException:
                    continue
            env.pop_frame() # exit scope
            self.explicit_set_repr = frozenset(func_list)
        return self.explicit_set_repr

    # Warning! push/pop frame
    def make_generator(self):
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
        

class SymbolicComprehensionSet(SymbolicSet):
    def __init__(self, varList, pred, node, env, interpret, calc_possible_solutions):
        SymbolicSet.__init__(self, env, interpret)
        self.variable_list = varList
        self.predicate = pred
        self.node = node
        self.domain_generator = calc_possible_solutions
        self.explicit_set_repr = None # not computed at init  
    
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
            if self.explicit_set_repr==None:
                self.explicit_set_repr = self.enumerate_all()
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
        return result  
        
    # convert to explicit frozenset
    def enumerate_all(self):
        if self.explicit_set_repr==None:
            varList   = self.variable_list
            pred      = self.predicate
            env       = self.env
            interpret = self.interpret
            result = []
            # new scope
            self.env.push_new_frame(varList)
            domain_generator = self.domain_generator(pred, env, varList, interpret)        
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
            self.explicit_set_repr = frozenset(result) 
        return self.explicit_set_repr 
    
    
    # Warning! push/pop frame
    def make_generator(self):
        varList   = self.variable_list
        pred      = self.predicate
        env       = self.env
        interpret = self.interpret
        env.push_new_frame(varList)
        domain_generator = self.domain_generator(pred, env, varList, interpret) 
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
                        env.pop_frame()
                        yield tup
                        env.push_new_frame(varList)   
                except ValueNotInDomainException:
                    continue
        env.pop_frame()
        