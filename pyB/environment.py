# -*- coding: utf-8 -*-
from ast_nodes import *
from btypes import *
from statespace import StateSpace
from config import *
from bexceptions import ValueNotInBStateException
from pretty_printer import pretty_print

# TODO: This must be a singelton object
class Environment():
    def __init__(self):
        # Types of AST-ID-Nodes: Node->type.
        # This map is used by the enumeration
        # and was created and filled by typeit of the module typing.
        self.node_to_type_map = {}
        # AST-SubTrees: ID(String)->AST
        #self.definition_id_to_ast = {}  
        self.state_space = StateSpace()   # statespace        
        self.solutions = {}               # written by a solution-file
        # from config.py 
        # for possible modification after module import time (e.g. via tests)
        self._min_int = MIN_INT
        self._max_int = MAX_INT
        self._bmachine_search_dir = BMACHINE_SEARCH_DIR
        self.solution_root = None         # predicateparseunit of solution-ast
        self.root_mch = None
        self.current_mch = None           # current Working B-Machine
        self.all_strings = [""]           # remember all strings seen (in this or other bmachines). used to enumerate 'STRING'
        # This is a caching-list which contains all operations of all machines
        # It should prevent from intensive lookup while animation and op_call substitutions
        self.all_operations = frozenset([]) # rettype, opname, paratype, backlink:owner_bmch, bool:is_query_op
        self.mch_operation_type = []   
        self.all_operation_asts = []
        self.parsed_bmachines = {}
        self.init_sets_bmachnes_names = [] # names of all bmachines with set-init done
        self.set_up_bmachines_names   = [] # set up constants done
        self.init_bmachines_names     = [] # init done
        # animation parameters
        self.set_up_state_on_stack  = False
        self.init_state_on_stack    = False
        self.set_up_done            = False
        self.init_done              = False
        #self.op_substitution_value = None # Sores the last value of an op-substitution


    # This method should only(!) be used by the typechecking-tests.
    # It returns the type of the id "string"
    def get_type(self, string):
        assert isinstance(string,str)
        # linear search for ID with the name string
        for node in self.node_to_type_map:
            assert isinstance(node, AIdentifierExpression)
            # FIXME: scoping: if there is more than one "string"
            # e.g x:Nat & !x.(x:S=>card(x)=3)...
            if node.idName==string:
                return self.node_to_type_map[node]
        raise Exception("lookup-error: unknown type of %s" % string)


    # A KeyError or a false assert is a typechecking bug
    # Used by the eumerator: all_values
    def get_type_by_node(self, node):
        assert isinstance(node, AIdentifierExpression)
        #print "XXX:",node.idName, node
        assert node in self.node_to_type_map
        atype = self.node_to_type_map[node]
        assert isinstance(atype, BType)
        return atype


    # reference to the owner-mch of this state/env
    def set_mch(self, mch):
        self.mch = mch


    def get_state(self):
        return self.state_space.get_state()


    def lookup_bmachine(self, idName, mch):
        for m in mch.included_mch + mch.seen_mch + mch.used_mch + mch.extended_mch:
            # FIXME: What if param. or return ids have the same name? add them here?
            names = m.const_names + m.var_names + m.dset_names + m.eset_names + m.eset_elem_names + [n.idName for n in m.scalar_params + m.set_params]
            if idName in names:
                return m
            else:
                bmachine = self.lookup_bmachine(idName, m)
                if not bmachine==None:
                    return bmachine
        return None


    # encapsule kind of parse-unit and statespace
    def set_value(self, id_Name, value):   
        bstate = self.get_state()
        bmachine = self.root_mch 
        try:
            bstate.set_value(id_Name, value, bmachine)
            return
        except ValueNotInBStateException:
            assert id_Name not in bmachine.const_names + bmachine.var_names + bmachine.dset_names 
        # lookup-fail in root. check child-bmachine
        bmachine = self.lookup_bmachine(id_Name, self.root_mch)
        bstate.set_value(id_Name, value, bmachine)

        
    def get_value(self, id_Name):
        bstate = self.get_state()
        bmachine = self.root_mch 
        try:
            return bstate.get_value(id_Name, bmachine)
        except ValueNotInBStateException:
            assert id_Name not in bmachine.const_names + bmachine.var_names + bmachine.dset_names 
        # lookup-fail in root. check child-bmachine
        bmachine = self.lookup_bmachine(id_Name, self.root_mch)
        return bstate.get_value(id_Name, bmachine)
    
    
    def add_ids_to_frame(self, ids):
        bstate = self.get_state()
        bmachine = self.current_mch
        bstate.add_ids_to_frame(ids, bmachine)   

    
    def push_new_frame(self, nodes):
        bstate = self.get_state()
        bmachine = self.root_mch # optimization to avoid lookup ( in get_value or set_value )
        bstate.push_new_frame(nodes, bmachine) 

    
    def pop_frame(self):
        bstate = self.get_state()
        bmachine = self.root_mch # optimization to avoid lookup ( in get_value or set_value )
        bstate.pop_frame(bmachine) 
    
    
    # This is called by a op-substitution only
    # TODO: cache operations
    def find_operation(self, idName):
        # (1) operations of included or extended machines are under full control
        # and can be executed via op-call-substitutions
        # This is not transitive!
        mchs = self.current_mch.included_mch + self.current_mch.extended_mch
        for m in mchs:
            for op in m.operations:
                name = op.op_name
                if idName == name:
                    return op
        # (2) call the query-op of a seen or used mch
        mchs = self.current_mch.used_mch + self.current_mch.seen_mch
        for m in mchs:
            for op in m.operations:
                name = op.op_name
                if idName == name:
                    assert op.is_query_op 
                    return op    
        # (3) fail
        raise Exception("unknown op: ",idName)
    
    # TODO: use dict (name->op) (if unique, otherwise implement lookup mchname.opname)
    def find_operation_type(self, idName):
        for op in self.mch_operation_type:
            name = op.op_name
            if idName == name:
                return op        
    
    def set_search_dir(self, file_name_str):
        import os
        if os.name=='posix' and '/' in file_name_str:
            self._bmachine_search_dir = file_name_str.rpartition("/")[0] + '/'
        else:
            print "WARNING: OS Type not testet. Search dir unknown"

    
    # assumes that every Variable/Constant/Set appears once 
    # TODO: Add typeinfo too
    # This function only maps the solution-expression-node to the id-name.
    # It does not change the env. or execute something. 
    # This will happen in the set_up_constants or exec_init methods
    def write_solution_nodes_to_env(self, root):
        for node in root.children:
            if isinstance(node, AConjunctPredicate): #loop
                self.write_solution_nodes_to_env(node)
            elif isinstance(node, AEqualPredicate):
                try:
                    #TODO: utlb_srv_mrtk__var_e32 --> utlb_srv_mrtk.var_e32 (underscore bug)
                    if isinstance(node.children[0], AIdentifierExpression):
                        self.solutions[node.children[0].idName] = node.children[1]
                        #print "DEBUG: used:",node.children[0].idName ,"=" + pretty_print(node)
                except Exception:
                    if VERBOSE:
                        print "WARNING: PyB failed to use solution: " + pretty_print(node)
                    continue 
    
    
    def get_all_visible_op_asts(self):
        # TODO caching to avoid this calculation
        return [op.ast for op in self.all_operations]