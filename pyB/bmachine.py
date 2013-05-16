# -*- coding: utf-8 -*-
from ast_nodes import *
from helpers import file_to_AST_str_no_print
from config import BMACHINE_SEARCH_DIR, BFILE_EXTENSION
#from environment import Environment

# -*- coding: utf-8 -*-
# abstract machine
class BMachine:
    def __init__(self, node, interpreter_method, env):
        self.name = None
        self.const_names = []
        self.var_names = []
        self.dset_names = []
        self.root = node
        self.env = env
        self.aMachineHeader = None
        self.scalar_params = []   # scalar machine parameter
        self.set_params = []      # Set machine parameter
        self.included_mch = []    # list of b-mchs
        self.extended_mch = []    # list of b-mchs
        self.seen_mch     = []    # list of b-mchs
        self.used_mch     = []    # list of b-mchs
        self.promoted_ops = []    # list of operations
        self.seen_ops     = []    # list of operations
        self.used_ops     = []    # list of operations 
        self.extended_ops = []    # list of operations
        self.operations   = []    # list of operations
        self.interpreter_method = interpreter_method
        self.aConstantsMachineClause = None
        self.aConstraintsMachineClause = None
        self.aSetsMachineClause = None
        self.aVariablesMachineClause = None
        self.aPropertiesMachineClause = None
        self.aAssertionsMachineClause = None
        self.aInvariantMachineClause = None
        self.aInitialisationMachineClause = None
        self.aDefinitionsMachineClause = None
        self.aOperationsMachineClause = None
        self.aIncludesMachineClause = None
        self.aPromotesMachineClause = None
        self.aSeesMachineClause = None
        self.aUsesMachineClause = None
        self.aExtendsMachineClause = None
        # TODO: sees, includes, promotes, extends, uses, abstract constants, abstract variables

        for child in node.children:
            # A clause may only appear at most once in an abstract machine
            # B Language Reference Manual - Version 1.8.6 - Page 110
            # It must be None before assignment
            assert isinstance(child, Clause) or isinstance(child, AMachineHeader)
            if isinstance(child, AConstantsMachineClause):
                assert self.aConstantsMachineClause==None
                self.aConstantsMachineClause = child
            elif isinstance(child, AConstraintsMachineClause):
                assert self.aConstraintsMachineClause==None
                self.aConstraintsMachineClause = child
            elif isinstance(child, ASetsMachineClause):
                assert self.aSetsMachineClause==None
                self.aSetsMachineClause = child
            elif isinstance(child, AVariablesMachineClause):
                assert self.aVariablesMachineClause==None
                self.aVariablesMachineClause = child
            elif isinstance(child, APropertiesMachineClause):
                assert self.aPropertiesMachineClause==None
                self.aPropertiesMachineClause = child
            elif isinstance(child, AAssertionsMachineClause):
                assert self.aAssertionsMachineClause==None
                self.aAssertionsMachineClause = child
            elif isinstance(child, AInitialisationMachineClause):
                assert self.aInitialisationMachineClause==None
                self.aInitialisationMachineClause = child
            elif isinstance(child, AInvariantMachineClause):
                assert self.aInvariantMachineClause==None
                self.aInvariantMachineClause = child
            elif isinstance(child, ADefinitionsMachineClause):
                assert self.aDefinitionsMachineClause==None
                self.aDefinitionsMachineClause = child
            elif isinstance(child, AOperationsMachineClause):
                assert self.aOperationsMachineClause==None
                self.aOperationsMachineClause = child
            elif isinstance(child, AIncludesMachineClause):
                assert self.aIncludesMachineClause==None
                self.aIncludesMachineClause = child
            elif isinstance(child, AMachineHeader):
                assert self.aMachineHeader == None
                self.aMachineHeader = child
            elif isinstance(child, APromotesMachineClause):
                assert self.aPromotesMachineClause == None
                self.aPromotesMachineClause = child
            elif isinstance(child, ASeesMachineClause):
                assert self.aSeesMachineClause == None
                self.aSeesMachineClause = child
            elif isinstance(child, AUsesMachineClause):
                assert self.aUsesMachineClause == None
                self.aUsesMachineClause = child
            elif isinstance(child, AExtendsMachineClause):
                assert self.aExtendsMachineClause == None
                self.aExtendsMachineClause = child
            else:
                raise Exception("Unknown clause:",child )
        self.self_check()
        #print self, "Bmachine created",self.name


    def recursive_self_parsing(self):
        self.parse_parameters()
        self.parse_child_machines(self.aIncludesMachineClause, self.included_mch)
        self.parse_child_machines(self.aExtendsMachineClause, self.extended_mch)
        self.parse_child_machines(self.aSeesMachineClause, self.seen_mch)
        self.parse_child_machines(self.aUsesMachineClause, self.used_mch)
        # TODO: better name for "names"
        self.const_names, self.var_names, self.dset_names = self._learn_names(self.aConstantsMachineClause, self.aVariablesMachineClause, self.aSetsMachineClause)
        names = self.const_names + self.var_names + self.dset_names
        bstate = self.env.state_space.get_state()
        # if there are solutions (gotten form a solution file at startup time)
        # than add them to your top level bstate. The reason for this indirection is
        # the following problem: you dont know to which machine an id value (inside the sol-file) belongs
        if self.env.solutions:
            bstate.add_mch_state(self, names, self.env.solutions)
        else:
            bstate.add_mch_state(self, names, {}) 
        self.get_all_strings(self.root) #Stringexpr.  inside mch.
    
    
    def get_all_strings(self, node):
        if isinstance(node, AStringExpression):
            self.env.all_strings.append(node.string)
        try:
            for child in node.children:
                self.get_all_strings(child)
        except AttributeError:
            return
                   


    def _learn_names(self, cmc, vmc, smc):
        var_names = []
        const_names = []
        dset_names = []
        if cmc:
            for idNode in cmc.children:
                assert isinstance(idNode, AIdentifierExpression)
                const_names.append(idNode.idName)
        if vmc:
            for idNode in vmc.children:
                assert isinstance(idNode, AIdentifierExpression)
                var_names.append(idNode.idName)
        if smc:
            for dSet in smc.children:
                if isinstance(dSet, ADeferredSet):
                    dset_names.append(dSet.idName)
        return const_names, var_names, dset_names


    def add_promoted_ops(self):
        if self.aPromotesMachineClause:
            for idNode in self.aPromotesMachineClause.children:
                assert isinstance(idNode, AIdentifierExpression)
                name = idNode.idName
                for mch in self.included_mch:
                    if mch.aOperationsMachineClause:
                        for op in mch.aOperationsMachineClause.children+mch.promoted_ops:
                            if op.opName==name:
                                self.promoted_ops.append(op)


    def add_extended_ops(self):
        if self.aExtendsMachineClause:
             for mch in self.extended_mch:
                if mch.aOperationsMachineClause:
                    for op in mch.aOperationsMachineClause.children+mch.promoted_ops:
                        self.extended_ops.append(op) 

                                    
    def add_seen_ops(self):
        if self.aSeesMachineClause:
            for mch in self.seen_mch:
                if mch.aOperationsMachineClause:
                    for op in mch.aOperationsMachineClause.children+mch.promoted_ops:
                        self.seen_ops.append(op) 
            

    def add_used_ops(self):
        if self.aUsesMachineClause:
            for mch in self.used_mch:
                if mch.aOperationsMachineClause:
                    for op in mch.aOperationsMachineClause.children+mch.promoted_ops:
                        self.used_ops.append(op)                  


    
    def parse_child_machines(self, mch_clause, mch_list):
        if mch_clause:
            for child in mch_clause.children:
                if isinstance(child, AIdentifierExpression):
                    assert isinstance(mch_clause, AUsesMachineClause) or isinstance(mch_clause, ASeesMachineClause)
                else:
                    assert isinstance(child, AMachineReference) 
                # FIXME: impl search strategy
                file_name = BMACHINE_SEARCH_DIR + child.idName + BFILE_EXTENSION
                ast_string, error = file_to_AST_str_no_print(file_name)
                if error:
                    print error
                exec ast_string
                mch = BMachine(root, self.interpreter_method, self.env)
                mch.recursive_self_parsing()
                mch_list.append(mch)
                               

    # maybe refactor this strange lookup some day 
    def get_includes_op_type(self, idName):
        for mch in self.included_mch:
            node = mch.root
            name = mch.name
            for op in self.env.mch_operation_type:
                name = op[2]
                mch = op[4]
                #print name == idName
                if idName == name:
                    return op
        raise Exception("unknown op",idName)

    # TODO: Dont repeat yourself 
    def type_included(self, type_check_bmch, root_type_env):
        for mch in self.included_mch:
            self.env.current_mch = mch
            type_env = type_check_bmch(mch.root, mch)
            id_2_t = type_env.id_to_types_stack[0]
            root_type_env.add_known_types_of_child_env(id_2_t)
        self.env.current_mch = self


    def type_extended(self, type_check_bmch, root_type_env):
        for mch in self.extended_mch:
            self.env.current_mch = mch
            type_env = type_check_bmch(mch.root, mch)
            id_2_t = type_env.id_to_types_stack[0]
            root_type_env.add_known_types_of_child_env(id_2_t)
        self.env.current_mch = self


    def type_seen(self, type_check_bmch, root_type_env):
        for mch in self.seen_mch:
            self.env.current_mch = mch
            type_env = type_check_bmch(mch.root, mch)
            id_2_t = type_env.id_to_types_stack[0]
            root_type_env.add_known_types_of_child_env(id_2_t)
        self.env.current_mch = self


    def type_used(self, type_check_bmch, root_type_env):
        for mch in self.used_mch:
            self.env.current_mch = mch
            type_env = type_check_bmch(mch.root, mch)
            id_2_t = type_env.id_to_types_stack[0]
            root_type_env.add_known_types_of_child_env(id_2_t)
        self.env.current_mch = self


    def init_include_mchs(self):
        if self.included_mch: # list of BMachines
            for mch in self.included_mch:                
                self.env.current_mch = mch
                self.interpreter_method(mch.root, self.env)
            self.env.current_mch = self
        self.add_promoted_ops()
 
 
    def init_extended_mchs(self):
        if self.extended_mch: # list of BMachines 
            for mch in self.extended_mch:
                self.env.current_mch = mch
                self.interpreter_method(mch.root, self.env)
            self.env.current_mch = self
        self.add_extended_ops()       


    def init_seen_mchs(self):
        if self.seen_mch: # list of BMachines
            for mch in self.seen_mch:
                self.env.current_mch = mch
                self.interpreter_method(mch.root, self.env)
            self.env.current_mch = self
        self.add_seen_ops()
 
 
    def init_used_mchs(self):
        if self.used_mch: # list of BMachines 
            for mch in self.used_mch:
                self.env.current_mch = mch
                mch = self.interpreter_method(mch.root, self.env)
            self.env.current_mch = self
        self.add_used_ops()                   


    def parse_parameters(self):
        assert not self.aMachineHeader == None
        self.name = self.aMachineHeader.idName
        for idNode in self.aMachineHeader.children:
            assert isinstance(idNode, AIdentifierExpression)
            if str.islower(idNode.idName):
                self.scalar_params.append(idNode)
            else:
                self.set_params.append(idNode)
        if not self.scalar_params==[]:
            assert not self.aConstraintsMachineClause==None


    def self_check(self):
        # B Language Reference Manual - Version 1.8.6 - Page 110
        # 2. If one of the CONCRETE_CONSTANTS or ABSTRACT_CONSTANTS clauses is present, then the PROPERTIES clause must be present.
        # 3. If one of the CONCRETE_VARIABLES or ABSTRACT_VARIABLES clauses is present, then the INVARIANT and INITIALISATION clauses must be present.
        if self.aConstantsMachineClause: #TODO: ABSTRACT_CONSTANTS
            assert self.aPropertiesMachineClause
        if self.aVariablesMachineClause: #TODO: ABSTRACT_VARIABLES
            assert self.aInvariantMachineClause and self.aInitialisationMachineClause


    def eval_Variables(self, env):
        if self.aVariablesMachineClause:
            self.interpreter_method(self.aVariablesMachineClause, env)


    def eval_Init(self, env):
        if self.aInitialisationMachineClause:
            self.interpreter_method(self.aInitialisationMachineClause, env)


    def eval_Invariant(self, env):
        if self.aInvariantMachineClause:
            return self.interpreter_method(self.aInvariantMachineClause, env)
        else:
            return None


    def eval_Assertions(self, env):
        if self.aAssertionsMachineClause:
            self.interpreter_method(self.aAssertionsMachineClause, env)

