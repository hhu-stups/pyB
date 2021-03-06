# -*- coding: utf-8 -*-
from ast_nodes import *
from config import BMACHINE_SEARCH_DIR, BFILE_EXTENSION, USE_RPYTHON_CODE
from boperation import BOperation
from helpers import file_to_AST_str_no_print, contains_lower_character, ParseObject

if USE_RPYTHON_CODE:
     from rpython_b_objmodel import frozenset
     
# -*- coding: utf-8 -*-
# abstract machine object
class BMachine(ParseObject):
    def __init__(self, node, remove_definitions):
        self.mch_name = ""
        self.const_names = []
        self.var_names   = []
        self.dset_names  = []
        self.eset_names  = []
        self.eset_elem_names = []
        self.root = node

        self.parameter_type_lst = [] # ordered list of type instances 
        self.scalar_params = []   # scalar machine parameter (idNodes)
        self.set_params    = []   # set machine parameter (idNodes)
        self.included_mch  = []   # list of b-mchs
        self.extended_mch  = []   # list of b-mchs
        self.seen_mch      = []   # list of b-mchs
        self.used_mch      = []   # list of b-mchs
        self.operations    = frozenset([])    # set of operations (to easy avoid double entries) only used to init env.operations and env.visible_opertaions
        
        # explicit flags indicate if a field is present. 
        self.has_mch_header 		 = False
        self.has_constants_mc 		 = False
        self.has_abstr_constants_mc  = False
        self.has_constraints_mc 	 = False
        self.has_sets_mc			 = False
        self.has_variables_mc		 = False
        self.has_conc_variables_mc   = False
        self.has_properties_mc	     = False
        self.has_assertions_mc		 = False
        self.has_invariant_mc 		 = False
        self.has_initialisation_mc	 = False
        self.has_definitions_mc		 = False
        self.has_operations_mc		 = False
        self.has_includes_mc		 = False
        self.has_promotes_mc		 = False
        self.has_sees_mc			 = False
        self.has_uses_mc			 = False
        self.has_extends_mc			 = False
        
        self._variable_printing_order = []
        # avoid cyclic import: the parser creates BMachine instances, while this class
        # needs to parse its seen machines
        self.remove_definitions = remove_definitions

        for child in node.children:
        	# Order of clauses is not defined 
            # A clause may only appear at most once in an abstract machine
            # B Language Reference Manual - Version 1.8.6 - Page 110
            # It must be None before assignment
            assert isinstance(child, Clause) or isinstance(child, AMachineHeader)
            if isinstance(child, AConstantsMachineClause):
                assert not self.has_constants_mc
                self.aConstantsMachineClause = child
                self.has_constants_mc = True
            elif isinstance(child, AAbstractConstantsMachineClause):
                assert not self.has_abstr_constants_mc
                self.aAbstractConstantsMachineClause = child
                self.has_abstr_constants_mc = True
            elif isinstance(child, AConstraintsMachineClause):
                assert not self.has_constraints_mc
                self.aConstraintsMachineClause = child
                self.has_constraints_mc = True
            elif isinstance(child, ASetsMachineClause):
                assert not self.has_sets_mc
                self.aSetsMachineClause = child
                self.has_sets_mc = True
            elif isinstance(child, AConcreteVariablesMachineClause):
                assert not self.has_conc_variables_mc
                self.aConcreteVariablesMachineClause = child
                self.has_conc_variables_mc = True
            elif isinstance(child, AVariablesMachineClause):
                assert not self.has_variables_mc
                self.aVariablesMachineClause = child
                self.has_variables_mc = True
            elif isinstance(child, APropertiesMachineClause):
                assert not self.has_properties_mc
                self.aPropertiesMachineClause = child
                self.has_properties_mc = True
            elif isinstance(child, AAssertionsMachineClause):
                assert not self.has_assertions_mc 
                self.aAssertionsMachineClause = child
                self.has_assertions_mc = True
            elif isinstance(child, AInitialisationMachineClause):
                assert not self.has_initialisation_mc
                self.aInitialisationMachineClause = child
                self.has_initialisation_mc = True
            elif isinstance(child, AInvariantMachineClause):
                assert not self.has_invariant_mc
                self.aInvariantMachineClause = child
                self.has_invariant_mc = True
            elif isinstance(child, ADefinitionsMachineClause):
                assert not self.has_definitions_mc
                self.aDefinitionsMachineClause = child
                self.has_definitions_mc = True
            elif isinstance(child, AOperationsMachineClause):
                assert not self.has_operations_mc
                self.aOperationsMachineClause = child
                self.has_operations_mc = True
            elif isinstance(child, AIncludesMachineClause):
                assert not self.has_includes_mc
                self.aIncludesMachineClause = child
                self.has_includes_mc = True
            elif isinstance(child, AMachineHeader):
                assert not self.has_mch_header
                self.aMachineHeader = child
                self.has_mch_header = True
            elif isinstance(child, APromotesMachineClause):
                assert not self.has_promotes_mc
                self.aPromotesMachineClause = child
                self.has_promotes_mc = True
            elif isinstance(child, ASeesMachineClause):
                assert not self.has_sees_mc
                self.aSeesMachineClause = child
                self.has_sees_mc = True
            elif isinstance(child, AUsesMachineClause):
                assert not self.has_uses_mc
                self.aUsesMachineClause = child
                self.has_uses_mc = True
            elif isinstance(child, AExtendsMachineClause):
                assert not self.has_extends_mc
                self.aExtendsMachineClause = child
                self.has_extends_mc = True
            else:
                raise Exception("Unknown clause:",child )
        self.self_check()
        #print self, "Bmachine created",self.mch_name
        

    # parse all child machines (constructs BMachine objects)
    def recursive_self_parsing(self, env):        
        self.parse_parameters()
        # remember this to avoid double-parsing and enable later lookup by name
        env.parsed_bmachines[self.mch_name] = self
        if self.has_includes_mc:
            self.parse_child_machines(self.aIncludesMachineClause, self.included_mch, env)
        if self.has_extends_mc:
            self.parse_child_machines(self.aExtendsMachineClause, self.extended_mch, env)
        if self.has_sees_mc:
            self.parse_child_machines(self.aSeesMachineClause, self.seen_mch, env)
        if self.has_uses_mc:
            self.parse_child_machines(self.aUsesMachineClause, self.used_mch, env)
        self.const_names, self.var_names, self.dset_names, self.eset_names, self.eset_elem_names = self._learn_names()
        all_names = self.const_names + self.var_names #+ self.dset_names + self.eset_names + self.eset_elem_names
        if self.has_operations_mc:
            for op in self.aOperationsMachineClause.children:
                self.parse_operation(op, env)
        # FIXME: This causes a first state already present which is a inconsistency in pybs design 
        bstate = env.state_space.get_state()
        bstate.register_new_bmachine(self, all_names)        
        env.get_all_strings(self.root) # get string expressions inside mch.


    def parse_operation(self, operation, env):
        assert isinstance(operation, AOperation)
        boperation = BOperation(name=operation.opName, operation_ast=operation, bmachine=self)
        self.operations = self.operations.union(frozenset([boperation]))
        env.set_operation_by_name(self.mch_name, operation.opName, boperation)


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
                #print file_path_and_name
                ast_string, error = file_to_AST_str_no_print(file_path_and_name)
                if error:
                    print error
                from parsing import str_ast_to_python_ast
                root = str_ast_to_python_ast(ast_string)
                # Handle definitions in child-machine
                root = self.remove_definitions(root, env)
                # create B machine object
                mch = BMachine(root, self.remove_definitions)
                mch.recursive_self_parsing(env)
                mch_list.append(mch)    


    # get the parameters of the machine (if present)
    def parse_parameters(self):
        assert self.has_mch_header
        self.mch_name = self.aMachineHeader.idName
        for idNode in self.aMachineHeader.children:
            assert isinstance(idNode, AIdentifierExpression)
            # 2.1 id names [a-zA-Z][a-zA-Z0-9_]*
            string = idNode.idName
            if contains_lower_character(string):
                # Page 116. 7.5 
                # scalar parameters: the name of a scalar parameter is an identifier 
                # that must contain at least one lowercase character.
                self.scalar_params.append(idNode)
            else:
                # Page 116. 7.5 
                # set parameters: the name of a set parameter is an identifier 
                # that must not contain a lowercase character.
                # TODO: This impl was always wrong write a Testcase with Book 
                self.set_params.append(idNode)
        if not self.scalar_params==[]:
            assert self.has_constraints_mc
                                   

    # This methods walks ASTs to determine the name of constants, variables and sets.
    # This information (the names) is used by the type checker, the environment 
    # and the interpreter
    def _learn_names(self):
        var_names = []
        const_names = []
        dset_names = []
        eset_names = []
        eset_elem_names =[]
        
        if self.has_constants_mc:
            const_names = [n.idName for n in self.aConstantsMachineClause.children if isinstance(n, AIdentifierExpression)]
        if self.has_abstr_constants_mc:
            const_names += [n.idName for n in self.aAbstractConstantsMachineClause.children if isinstance(n, AIdentifierExpression)]
        if self.has_variables_mc:
            var_names   = [n.idName for n in self.aVariablesMachineClause.children if isinstance(n, AIdentifierExpression)]
        if self.has_conc_variables_mc:
            var_names   += [n.idName for n in self.aConcreteVariablesMachineClause.children if isinstance(n, AIdentifierExpression)]
        if self.has_sets_mc:
            dset_names  = [dSet.idName for dSet in self.aSetsMachineClause .children if isinstance(dSet, ADeferredSetSet)]
            for set in self.aSetsMachineClause.children:
                if isinstance(set, AEnumeratedSetSet):
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
        if self.has_constants_mc or self.has_abstr_constants_mc:
            assert self.has_properties_mc
        if self.has_variables_mc or self.has_conc_variables_mc:
            assert self.has_invariant_mc and self.has_initialisation_mc
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
        assert env.visible_operations.__eq__(frozenset([])) # this method should only called once   
        self._add_seen_and_used_operations(env)
        if self.has_promotes_mc or self.has_extends_mc:
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
                prefix_name = m.mch_name + "." + op.op_name
                op_copy = op.copy_op()
                op_copy.op_name = prefix_name 
                env.visible_operations = env.visible_operations.union(frozenset([op_copy]))      
         

    # TODO: testcase for self instead of mch   
    # TODO: If M2 includes/extends M1, promoted ops should only change the state of M1
    # this method is recursive because extends and includes are transitive (Page 126)
    def _add_extended_and_promoted_ops(self, mch):
        for m in mch.extended_mch + mch.included_mch:
            self._add_extended_and_promoted_ops(m)
        if mch.has_promotes_mc:
            promoted_op_names = [x.idName for x in mch.aPromotesMachineClause.children]
            for m in mch.included_mch:
                for op in m.operations:
                    if op.op_name in promoted_op_names:
                        mch.operations = mch.operations.union(frozenset([op])) 
        if mch.has_extends_mc:
            for m in mch.extended_mch:
                mch.operations = mch.operations.union(m.operations)

    # used to for deterministic hash computation
    @jit.unroll_safe
    def add_to_variable_printing_order(self, ids):
        for idName in ids:
            if idName not in self._variable_printing_order:
                # TODO: implement a sorting algorithm
                self._variable_printing_order.append(idName) 
     
    # used to for deterministic hash computation    
    def get_variable_printing_order(self):
        return self._variable_printing_order
