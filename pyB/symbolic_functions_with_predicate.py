# symbolic functions defined by a predicate
from symbolic_helpers import check_syntacticly_equal,make_explicit_set_of_realtion_lists 
from symbolic_sets import *

# __getitem__ implemented inside interp to avoid env and interp_callable link
class SymbolicLambda(SymbolicSet):
    def __init__(self, varList, pred, expr, node, env, interpret, calc_possible_solutions):
        SymbolicSet.__init__(self, env, interpret)
        self.variable_list = varList
        self.predicate = pred
        self.expression = expr
        self.node = node
        self.generator = calc_possible_solutions
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
        if isinstance(aset, frozenset):
            if self.explicit_set_repr==None:
                self.explicit_set_repr = self.enumerate_all()
            return aset == self.explicit_set_repr
        raise DontKnowIfEqualException("lambda compare not implemented")
    
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
            domain_generator = self.generator(pred, env, varList, interpret)
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
        

class SymbolicComprehensionSet(SymbolicSet):
    def __init__(self, varList, pred, node, env, interpret, calc_possible_solutions):
        SymbolicSet.__init__(self, env, interpret)
        self.variable_list = varList
        self.predicate = pred
        self.node = node
        self.generator = calc_possible_solutions
        self.explicit_set_repr = None # not computed at init  
    
    def __getitem__(self, args):
        print args
        raise NotImplementedError()  
    
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
            self.explicit_set_repr = frozenset(result) 
        return self.explicit_set_repr 