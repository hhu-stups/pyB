# -*- coding: utf-8 -*-
from ast_nodes import *
from helpers import file_to_AST_str
from environment import Environment

# -*- coding: utf-8 -*-
# abstract machine
class BMachine:
    def __init__(self, node, interpreter_method, env):
        self.root = node
        self.state = env
        self.aMachineHeader = None
        self.scalar_params = []   # scalar machine parameter
        self.set_params = []      # Set machine parameter
        self.included_nodes = []  # nodes of mch roots
        self.included_mch = []    # list of b-mchs
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
            else:
                raise Exception("Unknown clause:",child )
        self.self_check()
        self.parse_parameters()
        self.parse_included()


    def parse_included(self):
        if self.aIncludesMachineClause:
            for child in self.aIncludesMachineClause.children:
                assert isinstance(child, AMachineReference)
                # FIXME: impl search strategy
                file_name = "examples/"+ child.idName + ".mch"
                ast_string = file_to_AST_str(file_name)
                exec ast_string
                self.included_nodes.append({0:root,1:child.idName,2:Environment()})


    def type_included(self, type_check_bmch, root_type_env):
        for d in self.included_nodes:
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


    def parse_parameters(self):
        assert not self.aMachineHeader == None
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

