# RPYTHON PY Version
# PYTHONPATH="+PYPY_DIR+":. python ../pypy/rpython/translator/goal/translate.py --batch pyB_RPython.py
# e.g. PYPY_DIR  = "/Users/johnwitulski/witulski/git/pyB/pypy/" 

from animation import calc_next_states
from ast_nodes import AInvariantMachineClause, AAbstractMachineParseUnit, AOperationsMachineClause
from bmachine import BMachine
from environment import Environment
from helpers import file_to_AST_str
from parsing import parse_ast, remove_definitions, str_ast_to_python_ast, remove_defs_and_parse_ast
from rpython_interp import interpret, exec_initialisation, set_up_constants
from typing import type_check_bmch, type_check_root_bmch


def main(argv):      
	print "WARNING: model checking still experimental"
	if len(argv)<2:
		return 0
		
	env = Environment()                                         # 1. create env.
	file_name_str = argv[1]                                     # 2. read filenames
	ast_string = file_to_AST_str(file_name_str)                 # 3. parse input-file to string
	#env.set_search_dir(file_name_str)
	root = str_ast_to_python_ast(ast_string)                    # 4. parse string to python ast                                                                
	parse_object = remove_defs_and_parse_ast(root, env)         # 5. replace defs and extern-functions inside mch and solution-file (if present) 
	if not isinstance(parse_object, BMachine):                                  
		print "Error: only model checking of b machines" 
		return -1

	assert isinstance(parse_object, BMachine)                   # 6. typecheck
	type_check_root_bmch(root, env, parse_object) # also checks all included, seen, used and extend
	mch = parse_object      

	bstates = set_up_constants(root, env, mch, solution_file_read=False)  # also evals properties
	# TODO: implement setup and init non determinism 
	if len(bstates)>0:
	   print "WARNING: set up constants not supported yet" 
	   return -1
	bstates = exec_initialisation(root, env, mch, solution_file_read=False)
	if not len(bstates)==1:
	   print "WARNING: only one init. expected" 
	   return -1
	#if not mch.has_invariant_mc:
	#   print "WARNING: no invariant present" 
	#   return -1  

	env.state_space.set_current_state(bstates[0], op_name="initialisation")
	while not env.state_space.empty():                          # 7. model check  
		if not interpret(mch.aInvariantMachineClause, env):
			print "WARNING: invariant violation found after checking", len(env.state_space.seen_states),"states"
			#print env.state_space.history
			return -1
		next_states = calc_next_states(env, mch)
		env.state_space.undo()
		for tup in next_states:
			bstate = tup.bstate
			#bstate.print_bstate()
			if not env.state_space.is_seen_state(bstate):
				env.state_space.set_current_state(bstate)  
	print "checked",len(env.state_space.seen_states),"states. No invariant violation found."
	return 0
	
def target(*args):
   return main, None # returns the entry point

if __name__ == '__main__':
   import sys
   main(sys.argv)
