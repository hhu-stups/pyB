# -*- coding: utf-8 -*-
from ast_nodes import *
from helpers import file_to_AST_str_no_print
from config import BMACHINE_SEARCH_DIR, BFILE_EXTENSION
from boperation import BOperation

# -*- coding: utf-8 -*-
# abstract machine object
class BMachine:
    def __init__(self, node):
        self.name = None
        self.const_names = []
        self.var_names   = []
        self.dset_names  = []
        self.eset_names  = []
        self.eset_elem_names = []
        self.root = node
        self.aMachineHeader = None
        self.scalar_params = []   # scalar machine parameter
        self.set_params    = []   # set machine parameter
        self.included_mch  = []   # list of b-mchs
        self.extended_mch  = []   # list of b-mchs
        self.seen_mch      = []   # list of b-mchs
        self.used_mch      = []   # list of b-mchs
        self.operations    = frozenset([])    # set of operations (to easy avoid double entries) only used to init env.operations and env.visible_opertaions
        self.aConstantsMachineClause = None
        self.aAbstractConstantsMachineClause = None
        self.aConstraintsMachineClause = None
        self.aSetsMachineClause = None
        self.aVariablesMachineClause = None
        self.aConcreteVariablesMachineClause = None
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
            elif isinstance(child, AAbstractConstantsMachineClause):
                assert self.aAbstractConstantsMachineClause==None
                self.aAbstractConstantsMachineClause = child
            elif isinstance(child, AConstraintsMachineClause):
                assert self.aConstraintsMachineClause==None
                self.aConstraintsMachineClause = child
            elif isinstance(child, ASetsMachineClause):
                assert self.aSetsMachineClause==None
                self.aSetsMachineClause = child
            elif isinstance(child, AConcreteVariablesMachineClause):
                assert self.aConcreteVariablesMachineClause==None
                self.aConcreteVariablesMachineClause = child
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


    # This method is a dirty solution to enumerate the set of all strings.
    # It collects all string expressions inside the machine
    def get_all_strings(self, node, env):
        if isinstance(node, AStringExpression):
            env.all_strings.append(node.string)
        try:
            for child in node.children:
                self.get_all_strings(child, env)
        except AttributeError:
            return


    # parse all child machines (constructs BMachine objects)
    def recursive_self_parsing(self, env):        
        self.parse_parameters()
        # remember this to avoid double-parsing and enable later lookup by name
        env.parsed_bmachines[self.name] = self
        
        self.parse_child_machines(self.aIncludesMachineClause, self.included_mch, env)
        self.parse_child_machines(self.aExtendsMachineClause, self.extended_mch, env)
        self.parse_child_machines(self.aSeesMachineClause, self.seen_mch, env)
        self.parse_child_machines(self.aUsesMachineClause, self.used_mch, env)
        self.const_names, self.var_names, self.dset_names, self.eset_names, self.eset_elem_names = self._learn_names()
        all_names = self.const_names + self.var_names #+ self.dset_names + self.eset_names + self.eset_elem_names
        if self.aOperationsMachineClause:
            for op in self.aOperationsMachineClause.children:
                self.parse_operation(op, env)
        bstate = env.state_space.get_state()
        bstate.register_new_bmachine(self, all_names)        
        self.get_all_strings(self.root, env) # get string expressions inside mch.


    def parse_operation(self, operation, env):
        assert isinstance(operation, AOperation)
        boperation = BOperation()
        boperation.op_name         = operation.opName
        boperation.ast             = operation
        boperation.owner_machine   = self
        self.operations = self.operations.union(frozenset([boperation]))
        env.set_operation_by_name(self.name, operation.opName, boperation)


    # parsing of the machines
    def parse_child_machines(self, mch_clause, mch_list, env):
        if mch_clause:
            for child in mch_clause.children:
                # avoid double parsing and two (or more) BMachine object for the same Machine
                if child.idName in env.parsed_bmachines:
                    mch = env.parsed_bmachines[child.idName]
                    mch_list.append(mch) 
                    continue

                # BMachine unknown, continue parsing
                if isinstance(child, AIdentifierExpression):
                    assert isinstance(mch_clause, AUsesMachineClause) or isinstance(mch_clause, ASeesMachineClause)
                else:
                    assert isinstance(child, AMachineReference) 
                # TODO: impl search strategy
                file_path_and_name = env._bmachine_search_dir + child.idName + BFILE_EXTENSION
                ast_string, error = file_to_AST_str_no_print(file_path_and_name)
                if error:
                    print error
                exec ast_string
                mch = BMachine(root)
                mch.recursive_self_parsing(env)
                mch_list.append(mch)    


    # get the parameters of the machine (if present)
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
                                   

    # This methods walks ASTs to determine the name of constants, variables and sets.
    # This information (the names) is used by the type checker, the environment 
    # and the interpreter
    def _learn_names(self):
        cmc  = self.aConstantsMachineClause
        acmc = self.aAbstractConstantsMachineClause
        vmc  = self.aVariablesMachineClause
        cvmc = self.aConcreteVariablesMachineClause
        smc  = self.aSetsMachineClause 
        var_names = []
        const_names = []
        dset_names = []
        eset_names = []
        eset_elem_names =[]
        if cmc:
            const_names = [n.idName for n in cmc.children if isinstance(n, AIdentifierExpression)]
        if acmc:
            const_names += [n.idName for n in acmc.children if isinstance(n, AIdentifierExpression)]
        if vmc:
            var_names   = [n.idName for n in vmc.children if isinstance(n, AIdentifierExpression)]
        if cvmc:
            var_names   += [n.idName for n in cvmc.children if isinstance(n, AIdentifierExpression)]
        if smc:
            dset_names  = [dSet.idName for dSet in smc.children if isinstance(dSet, ADeferredSet)]
            for set in smc.children:
                if isinstance(set, AEnumeratedSet):
                    eset_names.append(set.idName)
                    elem_names = [e.idName for e in set.children]
                    eset_elem_names += elem_names # also learn element names 
        return const_names, var_names, dset_names, eset_names, eset_elem_names


    # types included, extended, seen or used b machines
    # only called by typing.py
    # only called once
    def type_child_machines(self, type_check_bmch, root_type_env, env):
        machine_list = self.included_mch + self.extended_mch + self.seen_mch + self.used_mch
        for mch in machine_list:
            env.current_mch = mch
            type_env = type_check_bmch(mch.root, env, mch)
            id_2_t = type_env.id_to_types_stack[0]
            root_type_env.add_known_types_of_child_env(id_2_t)
        env.current_mch = self  


    def self_check(self):
        # B Language Reference Manual - Version 1.8.6 - Page 110
        # 2. If one of the CONCRETE_CONSTANTS or ABSTRACT_CONSTANTS clauses is present, then the PROPERTIES clause must be present.
        # 3. If one of the CONCRETE_VARIABLES or ABSTRACT_VARIABLES clauses is present, then the INVARIANT and INITIALISATION clauses must be present.
        if self.aConstantsMachineClause or self.aAbstractConstantsMachineClause:
            assert self.aPropertiesMachineClause
        if self.aVariablesMachineClause or self.aConcreteVariablesMachineClause:
            assert self.aInvariantMachineClause and self.aInitialisationMachineClause
        # TODO: much more self checking to do e.g visibility 

    # This helper adds alle visible operations to the environment:
    # 1. All ops of the root-machine
    # 2. All promoted ops of included machines.
    # 3. All Ops of extended machines
    # 4. All Ops of used or seen machines (with prefix). This is transitive 
    # TODO: Check this an write test cases
    def add_all_visible_ops_to_env(self, env):
        assert self==env.root_mch 
        # TODO: check for name collisions. 
        # TODO: check for sees/uses includes/extends cycles in the mch graph
        # Otherwise the following code is wrong:
        assert env.visible_operations == frozenset([]) # this method should only called once   
        self._add_seen_and_used_operations(env)
        if self.aPromotesMachineClause or self.aExtendsMachineClause:
            self._add_extended_and_promoted_ops(self)
        env.visible_operations = env.visible_operations.union(self.operations)
    
    
    # A machine can be seen by more than on machine, but its operations should
    # only appear once in the list of available operations   
    def _add_seen_and_used_operations(self, env):
        for m in self.seen_mch + self.used_mch:
            # before making a mch.op visible, calc. the available operations
            self._add_extended_and_promoted_ops(m)
            #if m.aSeesMachineClause or m.aUsesMachineClause:
            #    _add_seen_and_used_operations(m, env)
            for op in m.operations:        
                prefix_name = m.name + "." + op.op_name
                op_copy = op.copy_op()
                op_copy.op_name = prefix_name 
                env.visible_operations = env.visible_operations.union(frozenset([op_copy]))      
         

    # TODO: testcase for self instead of mch   
    # TODO: If M2 includes/extends M1, promoted ops should only change the state of M1
    # this method is recursive because extends and includes are transitive (Page 126)
    def _add_extended_and_promoted_ops(self, mch):
        for m in mch.extended_mch + mch.included_mch:
            self._add_extended_and_promoted_ops(m)
        if mch.aPromotesMachineClause:
            promoted_op_names = [x.idName for x in mch.aPromotesMachineClause.children]
            for m in mch.included_mch:
                for op in m.operations:
                    if op.op_name in promoted_op_names:
                        mch.operations = mch.operations.union(frozenset([op])) 
        if mch.aExtendsMachineClause:
            for m in mch.extended_mch:
                mch.operations = mch.operations.union(m.operations)


