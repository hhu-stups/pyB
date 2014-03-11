# helper functions ONLY(!) used by tests. 
from interp import set_up_constants, exec_initialisation
from typing import typeit, resolve_type, TypeCheck_Environment
from btypes import UnknownType
from ast_nodes import AIdentifierExpression

# The data from the solution-files has already been read at the mch creation time.
# side-effect of this method: may be a state change.
def arbitrary_init_machine(root, env, mch, solution_file_read=False):    
    bstates = set_up_constants(root, env, mch, solution_file_read)
    if len(bstates)>0:
        env.state_space.add_state(bstates[0])
    bstates = exec_initialisation(root, env, mch, solution_file_read)
    if len(bstates)>0:
        env.state_space.add_state(bstates[0]) 


# This helper function performs type checking with 
# start types for some identifiers. Theses types are needed to test
# type checking in some cases
def type_with_known_types(root, env, known_types_list, idNames):
    type_env = TypeCheck_Environment()
    type_env.init_env(idNames)
    # modify type env with solutions from testcases
    for atuple in known_types_list:
        id_Name = atuple[0]
        atype = atuple[1]
        utype = UnknownType(id_Name)
        utype.real_type = atype
        type_env.id_to_types_stack[0][id_Name]     = utype
        type_env.id_to_nodes_stack[0][id_Name]     = []
    # start typing algorithm
    typeit(root, env, type_env)
    type_env.write_to_env(env, type_env.id_to_types_stack[-1], type_env.id_to_nodes_stack[-1])
    resolve_type(env) # throw away unknown types
    return type_env   # contains only knowladge about ids at global level


# This returns the type of the id-node with the name "string".
# It is more easy for test to get the type by name instead of AST-node
def get_type_by_name(env, string):
	assert isinstance(string, str)
	# scoping: if there is more than one "string"
	# e.g x:Nat & !x.(x:S=>card(x)=3)...
	#if string in [n.idName for n in env.node_to_type_map]:
	#	print "WARNING: lookup of type via string. This name is uses more than once: %s" % string        
	# linear search for ID with the name string
	for node in env.node_to_type_map:
		assert isinstance(node, AIdentifierExpression)
		if node.idName==string:
			return env.node_to_type_map[node]
	raise Exception("lookup-error: unknown type of %s" % string)