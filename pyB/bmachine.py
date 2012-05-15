# -*- coding: utf-8 -*-
from ast_nodes import *
from helpers import file_to_AST_str
from environment import Environment

# -*- coding: utf-8 -*-
# abstract machine
class BMachine:
    def __init__(self, node, interpreter_method, env):
        self.name = None
        self.root = node
        self.state = env
        self.aMachineHeader = None
        self.scalar_params = []   # scalar machine parameter
        self.set_params = []      # Set machine parameter
        self.included_nodes = []  # nodes of mch roots
        self.seen_nodes   = []    # nodes of mch roots
        self.used_nodes   = []    # nodes of mch roots 
        self.extended_nodes = []  # nodes of mch roots 
        self.included_mch = []    # list of b-mchs
        self.extended_mch = []    # list of b-mchs
        self.seen_mch     = []    # list of b-mchs
        self.used_mch     = []    # list of b-mchs
        self.promoted_ops = []    # list of operation
        self.seen_ops     = []    # list of operation
        self.used_ops     = []    # list of operation 
        self.extended_ops = []    # list of operation
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
            # 1. A clause may only appear at most once in an abstract machine
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
        self.parse_parameters()
        self.parse_included()
        self.parse_extended()
        self.parse_seen()
        self.parse_used()


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


    def parse_included(self):
        if self.aIncludesMachineClause:
            for child in self.aIncludesMachineClause.children:
                assert isinstance(child, AMachineReference)
                # FIXME: impl search strategy
                file_name = "examples/"+ child.idName + ".mch"
                ast_string = file_to_AST_str(file_name)
                exec ast_string
                self.included_nodes.append({0:root,1:child.idName,2:Environment()})


    def parse_extended(self):
        if self.aExtendsMachineClause:
            for child in self.aExtendsMachineClause.children:
                assert isinstance(child, AMachineReference)
                # FIXME: impl search strategy
                file_name = "examples/"+ child.idName + ".mch"
                ast_string = file_to_AST_str(file_name)
                exec ast_string
                self.extended_nodes.append({0:root,1:child.idName,2:Environment()})        

    def parse_seen(self):
        if self.aSeesMachineClause:
            for child in self.aSeesMachineClause.children:
                assert isinstance(child, AIdentifierExpression)
                file_name = "examples/"+ child.idName + ".mch"
                ast_string = file_to_AST_str(file_name)
                exec ast_string
                self.seen_nodes.append({0:root,1:child.idName,2:Environment()})
 
 
    def parse_used(self):
        if self.aUsesMachineClause:
            for child in self.aUsesMachineClause.children:
                assert isinstance(child, AIdentifierExpression)
                file_name = "examples/"+ child.idName + ".mch"
                ast_string = file_to_AST_str(file_name)
                exec ast_string
                self.used_nodes.append({0:root,1:child.idName,2:Environment()})
                               

    def get_includes_op_type(self, idName):
        for d in self.included_nodes:
            node = d[0]
            name = d[1]
            env = d[2]
            for op in env.mch_operation_type:
                name = op[2]
                if idName == name:
                    return op, env
        raise Exception("unknown op",idName)


    def type_included(self, type_check_bmch, root_type_env):
        for d in self.included_nodes:
            node = d[0]
            name = d[1]
            env = d[2]
            mch = BMachine(node, self.interpreter_method, env)
            type_env = type_check_bmch(node, mch)
            id_2_t = type_env.id_to_types_stack[0]
            root_type_env.add_known_types_of_child_env(id_2_t)


    def type_extended(self, type_check_bmch, root_type_env):
        for d in self.extended_nodes:
            node = d[0]
            name = d[1]
            env = d[2]
            mch = BMachine(node, self.interpreter_method, env)
            type_env = type_check_bmch(node, mch)
            id_2_t = type_env.id_to_types_stack[0]
            root_type_env.add_known_types_of_child_env(id_2_t)


    def type_seen(self, type_check_bmch, root_type_env):
        for d in self.seen_nodes:
            node = d[0]
            name = d[1]
            env = d[2]
            mch = BMachine(node, self.interpreter_method, env)
            type_env = type_check_bmch(node, mch)
            id_2_t = type_env.id_to_types_stack[0]
            root_type_env.add_known_types_of_child_env(id_2_t)


    def type_used(self, type_check_bmch, root_type_env):
        for d in self.used_nodes:
            node = d[0]
            name = d[1]
            env = d[2]
            mch = BMachine(node, self.interpreter_method, env)
            type_env = type_check_bmch(node, mch)
            id_2_t = type_env.id_to_types_stack[0]
            root_type_env.add_known_types_of_child_env(id_2_t)


    def init_include_mchs(self):
        if self.included_nodes: # nodes of mch roots
            for d in self.included_nodes:
                node = d[0]
                name = d[1]
                env  = d[2]
                # FIXME: performance: double typechecking
                mch = self.interpreter_method(node, env)
                self.included_mch.append(mch)
        self.add_promoted_ops()
 
 
    def init_extended_mchs(self):
        if self.extended_nodes: # nodes of mch roots
            for d in self.extended_nodes:
                node = d[0]
                name = d[1]
                env  = d[2]
                # FIXME: performance: double typechecking
                mch = self.interpreter_method(node, env)
                self.extended_mch.append(mch)
        self.add_extended_ops()       


    def init_seen_mchs(self):
        if self.seen_nodes: # nodes of mch roots
            for d in self.seen_nodes:
                node = d[0]
                name = d[1]
                env  = d[2]
                # FIXME: performance: double typechecking
                mch = self.interpreter_method(node, env)
                self.seen_mch.append(mch)
        self.add_seen_ops()
 
 
    def init_used_mchs(self):
        if self.used_nodes: # nodes of mch roots
            for d in self.used_nodes:
                node = d[0]
                name = d[1]
                env  = d[2]
                # FIXME: performance: double typechecking
                mch = self.interpreter_method(node, env)
                self.used_mch.append(mch)
        self.add_used_ops()                   


    def parse_parameters(self):
        assert not self.aMachineHeader == None
        self.name = self.aMachineHeader.idName
        for idNode in self.aMachineHeader.children:
            assert isinstance(idNode, AIdentifierExpression)
            param = idNode.idName
            if str.islower(param):
                self.scalar_params.append(param)
            else:
                self.set_params.append(param)
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

