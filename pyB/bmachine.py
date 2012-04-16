# -*- coding: utf-8 -*-
from ast_nodes import *

# -*- coding: utf-8 -*-
# abstract machine
class BMachine:
    def __init__(self, node, interpreter_method):
        self.root = node
        self.scalar_params = [] # scalar machine parameter
        self.set_params = []    # Set machine parameter
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
        # TODO: sees, includes, promotes, extends, uses, abstract constants, abstract variables

        for child in node.children:
            # 1. A clause may only appear at most once in an abstract machine
            # B Language Reference Manual - Version 1.8.6 - Page 110
            # It must be None before assignment
            assert isinstance(child, Clause)
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
            else:
                raise Exception("Unknown clause:",child )
        self.self_check()
        self.parse_parameters()


    def parse_parameters(self):
        for param in self.root.para:
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

