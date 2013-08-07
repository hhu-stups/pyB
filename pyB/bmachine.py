# -*- coding: utf-8 -*-
from ast_nodes import *
from helpers import file_to_AST_str_no_print
from config import BMACHINE_SEARCH_DIR, BFILE_EXTENSION
#from environment import Environment

# -*- coding: utf-8 -*-
# abstract machine
class BMachine:
    def __init__(self, node, env):
        self.name = None
        self.const_names = []
        self.var_names = []
        self.dset_names = []
        self.eset_and_elem_names = []
        self.root = node
        self.env = env # TODO: Check if a elimination of this unclean backref is possible
        self.aMachineHeader = None
        self.scalar_params = []   # scalar machine parameter
        self.set_params    = []   # set machine parameter
        self.included_mch  = []   # list of b-mchs
        self.extended_mch  = []   # list of b-mchs
        self.seen_mch      = []   # list of b-mchs
        self.used_mch      = []   # list of b-mchs
        self.operations    = frozenset([])    # set of operations (to easy avoid double entries)
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


    # This method is a dirty solution to enumerate the set of all strings.
    # It collects all string expressions inside the machine
    def get_all_strings(self, node):
        if isinstance(node, AStringExpression):
            self.env.all_strings.append(node.string)
        try:
            for child in node.children:
                self.get_all_strings(child)
        except AttributeError:
            return


    # parse all child machines (constructs BMachine objects)
    def recursive_self_parsing(self):        
        self.parse_parameters()
        # remember this to avoid double-parsing and enable later lookup by name
        self.env.parsed_bmachines[self.name] = self
        
        self.parse_child_machines(self.aIncludesMachineClause, self.included_mch)
        self.parse_child_machines(self.aExtendsMachineClause, self.extended_mch)
        self.parse_child_machines(self.aSeesMachineClause, self.seen_mch)
        self.parse_child_machines(self.aUsesMachineClause, self.used_mch)
        # TODO: better name for "names"
        self.const_names, self.var_names, self.dset_names, self.eset_and_elem_names = self._learn_names(self.aConstantsMachineClause, self.aVariablesMachineClause, self.aSetsMachineClause)
        names = self.const_names + self.var_names + self.dset_names + self.eset_and_elem_names
        bstate = self.env.state_space.get_state()
        # if there are solutions (gotten form a solution file at startup time)
        # than add them to your top level bstate. The reason for this indirection is
        # the following problem: you dont know to which machine an id value (inside the sol-file) belongs
        if self.env.solutions:
            bstate.add_mch_state(self, names, self.env.solutions)
        else:
            bstate.add_mch_state(self, names, {}) 
        self.get_all_strings(self.root) # get string expressions inside mch.


    # parsing of the machines
    def parse_child_machines(self, mch_clause, mch_list):
        if mch_clause:
            for child in mch_clause.children:
                # avoid double parsing and two (or more) BMachine object for the same Machine
                if child.idName in self.env.parsed_bmachines:
                    mch = self.env.parsed_bmachines[child.idName]
                    mch_list.append(mch) 
                    continue

				# BMachine unknown, continue parsing
                if isinstance(child, AIdentifierExpression):
                    assert isinstance(mch_clause, AUsesMachineClause) or isinstance(mch_clause, ASeesMachineClause)
                else:
                    assert isinstance(child, AMachineReference) 
                # TODO: impl search strategy
                file_name = BMACHINE_SEARCH_DIR + child.idName + BFILE_EXTENSION
                ast_string, error = file_to_AST_str_no_print(file_name)
                if error:
                    print error
                exec ast_string
                mch = BMachine(root, self.env)
                mch.recursive_self_parsing()
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
                                   

    def _learn_names(self, cmc, vmc, smc):
        var_names = []
        const_names = []
        dset_names = []
        eset_and_elem_names = []
        if cmc:
            const_names = [n.idName for n in cmc.children if isinstance(n, AIdentifierExpression)]
        if vmc:
            var_names   = [n.idName for n in vmc.children if isinstance(n, AIdentifierExpression)]
        if smc:
            dset_names  = [dSet.idName for dSet in smc.children if isinstance(dSet, ADeferredSet)]
            for set in smc.children:
                if isinstance(set, AEnumeratedSet):
                    eset_and_elem_names.append(set.idName)
                    elem_names = [e.idName for e in set.children]
                    eset_and_elem_names += elem_names
        return const_names, var_names, dset_names, eset_and_elem_names


    # types included, extended, seen or used b machines
    # only called by typing.py
    # only called once
    def type_child_machines(self, type_check_bmch, root_type_env, env):
        machine_list = self.included_mch + self.extended_mch + self.seen_mch + self.used_mch
        for mch in machine_list:
            self.env.current_mch = mch
            type_env = type_check_bmch(mch.root, env, mch)
            id_2_t = type_env.id_to_types_stack[0]
            root_type_env.add_known_types_of_child_env(id_2_t)
        self.env.current_mch = self  


    def self_check(self):
        # B Language Reference Manual - Version 1.8.6 - Page 110
        # 2. If one of the CONCRETE_CONSTANTS or ABSTRACT_CONSTANTS clauses is present, then the PROPERTIES clause must be present.
        # 3. If one of the CONCRETE_VARIABLES or ABSTRACT_VARIABLES clauses is present, then the INVARIANT and INITIALISATION clauses must be present.
        if self.aConstantsMachineClause: #TODO: ABSTRACT_CONSTANTS
            assert self.aPropertiesMachineClause
        if self.aVariablesMachineClause: #TODO: ABSTRACT_VARIABLES
            assert self.aInvariantMachineClause and self.aInitialisationMachineClause
        # TODO: much more self checking to do e.g visibility 



