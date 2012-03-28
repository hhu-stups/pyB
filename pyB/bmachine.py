# -*- coding: utf-8 -*-
from ast_nodes import *

# -*- coding: utf-8 -*-
class BMachine:
    def __init__(self, node, interpreter_method):
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

        for child in node.children:
            assert isinstance(child, Clause)
            if isinstance(child, AConstantsMachineClause):
                self.aConstantsMachineClause = child
            elif isinstance(child, AConstraintsMachineClause):
                self.aConstraintsMachineClause = child
            elif isinstance(child, ASetsMachineClause):
                self.aSetsMachineClause = child
            elif isinstance(child, AVariablesMachineClause):
                self.aVariablesMachineClause = child
            elif isinstance(child, APropertiesMachineClause):
                self.aPropertiesMachineClause = child
            elif isinstance(child, AAssertionsMachineClause):
                self.aAssertionsMachineClause = child
            elif isinstance(child, AInitialisationMachineClause):
                self.aInitialisationMachineClause = child
            elif isinstance(child, AInvariantMachineClause):
                self.aInvariantMachineClause = child
            elif isinstance(child, ADefinitionsMachineClause):
                self.aDefinitionsMachineClause = child
            elif isinstance(child, AOperationsMachineClause):
                self.aOperationsMachineClause = child
            else:
                raise Exception("Unknown clause:",child )


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

