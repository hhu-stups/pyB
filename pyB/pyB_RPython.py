# RPYTHON PY Version
# PYTHONPATH="+PYPY_DIR+":. python ../pypy/rpython/translator/goal/translate.py --batch pyB_RPython.py
# e.g. PYPY_DIR  = "/Users/johnwitulski/witulski/git/pyB/pypy/" 
# PYTHONPATH=/Users/johnwitulski/witulski/git/pyB/pypy/:. python ../pypy/rpython/translator/goal/translate.py --batch pyB_RPython.py
import config
config.set_USE_RPYTHON_CODE(True)
config.set_USE_RPYTHON_POPEN(True)

from rpython.rlib import jit
from animation_clui import show_ui, print_values_b_style, print_set_up_bstates ,print_init_bstates
from animation import calc_next_states
from ast_nodes import AInvariantMachineClause, AAbstractMachineParseUnit, AOperationsMachineClause
from bmachine import BMachine
from config import DEFAULT_INPUT_FILENAME, VERBOSE, EVAL_CHILD_INVARIANT, DISABLE_INVARIANT_MC_CHECK
from environment import Environment
from helpers import file_to_AST_str, file_to_AST_str_no_print, solution_file_to_AST_str
from parsing import PredicateParseUnit, ExpressionParseUnit, parse_ast, remove_definitions, str_ast_to_python_ast, remove_defs_and_parse_ast
from pretty_printer import pretty_print, failsafe_pretty_print
from rpython_interp import interpret, exec_initialisation, set_up_constants, eval_Invariant
from typing import type_check_bmch, type_check_root_bmch

#from rpython.rlib.jit import JitDriver
# green: ast node defines the evaluation of a particular expression
#        env is the variable which
# red:   none, the interpreter is side effect free. Nothing is modified by the exec
# maybe all of this is wrong and exec_substitution instead of interp must be considered
#jitdriver = JitDriver(greens=['node', 'env']) # for interp

# console input like python 'pyB.py somefile.mch some_solutionfile.txt'
def read_input_string(argv, offset=0):
    file_name_str = DEFAULT_INPUT_FILENAME
    solution_file_name_str = ""
    if len(argv)==2+offset:
        file_name_str = argv[1+offset]
    elif len(argv)==3+offset:
        file_name_str = argv[1+offset]
        solution_file_name_str = argv[2+offset]
    else:
        print "Warning: No input file! default:",file_name_str
    return file_name_str, solution_file_name_str

    
# add "#PREDICATE" header and read solution 
def read_solution_file(env, solution_file_name_str):
    ast_str, error = solution_file_to_AST_str(solution_file_name_str)
    if error:
        print error
    root = str_ast_to_python_ast(ast_str)
    env.solution_root = root
    env.write_solution_nodes_to_env(root)
    if env.solutions and VERBOSE:
        print "learned from solution-file (constants and variables): ", [x for x in env.solutions] 

# skips set_up or init if there is nothing to setup/init
def __calc_states_and_print_ui(root, env, mch, solution_file_read):
    # Schneider Book page 62-64:
    # The parameters p make the constraints C True
    # #p.C    
    # Sets St and constants k which meet the constraints c make the properties B True
    # C => #St,k.B
    if not env.set_up_done:
        next_states = set_up_constants(root, env, mch, solution_file_read)
        if len(next_states)>0:
            print_set_up_bstates(next_states, mch)
            return next_states
        else:
            # no bstates and no exception: set up to do (e.g no constants)
            env.set_up_done = True 
        
        
    # If C and B is True there should be Variables v which make the Invaraiant I True
    # B & C => #v.I
    if not env.init_done:
        next_states = exec_initialisation(root, env, mch, solution_file_read)
        if len(next_states)>0:
            undo_possible = not env.state_space.empty()
            print_init_bstates(next_states, mch, undo_possible)
            return next_states
        else:
            # no bstates and no exception: no init to do (e.g no variables)
            env.init_done = True

    print mch.mch_name," - Invariant:", eval_Invariant(root, env, mch)  # TODO: move print to animation_clui
    if EVAL_CHILD_INVARIANT:
        bstate = env.state_space.get_state()
        for bmachine in bstate.bmch_list:
            if not bmachine is None and not bmachine.mch_name==mch.mch_name :
                print bmachine.mch_name, " - Invariant:", interpret(bmachine.aInvariantMachineClause, env)
    bstate_lst = calc_next_states(env, mch)
    show_ui(env, mch, bstate_lst)
    next_states = []
    for n in bstate_lst: # all other data inside bstate_lst has already been processed by show_ui
        next_states.append(n.bstate)
    return next_states    


# returns "root, env, parse_object, solution_file_present" if no error occurred 
def startup(argv, offset):
    env = Environment()                                               # 1. create env.
    file_name_str, solution_file_name_str = read_input_string(argv, offset) # 2. read filenames
    ast_string, error = file_to_AST_str_no_print(file_name_str)       # 3. parse input-file to string
    if error:
        print error
    #env.set_search_dir(file_name_str)
    #env.parse_config_parameter(argv)
    root = str_ast_to_python_ast(ast_string)                    # 4. parse string to python ast 
    # uncomment for profiling (e.g. performance tests)
    #import cProfile
    #cProfile.run('mch = interpret(root, env)','pyB_profile_out.txt')
    solution_file_present = not solution_file_name_str==""
    if solution_file_present:                                   # 5. parse solution-file and write to env.
        read_solution_file(env, solution_file_name_str)         # The concreate solution values are added at 
                                                                # the bmachine object-init time to the respective mch

                                                                # 6. replace defs and extern-functions inside mch and solution-file (if present)      
    parse_object = remove_defs_and_parse_ast(root, env)         # 7. which kind of ast?
    return root, env, parse_object, solution_file_present
    
    
# can use a solution file to speed up the init (or make it possible).
# will go into animation mode if possible
def run_animation_mode(argv):
    env = Environment()                                                # 1. create env.
    file_name_str, solution_file_name_str = read_input_string(argv, 1) # 2. read filenames
    ast_string, error = file_to_AST_str_no_print(file_name_str)        # 3. parse input-file to string
    if error:
        print error
    #env.set_search_dir(file_name_str)
    root = str_ast_to_python_ast(ast_string)                    # 4. parse string to python ast TODO: JSON
    # uncomment for profiling (e.g. performance tests)
    #import cProfile
    #cProfile.run('mch = interpret(root, env)','pyB_profile_out.txt')
    solution_file_present = not solution_file_name_str==""
    #if solution_file_present:                                   # 5. parse solution-file and write to env.
    #    read_solution_file(env, solution_file_name_str)         # The concreate solution values are added at 
                                                                # the bmachine object-init time to the respective mch

                                                                # 6. replace defs and extern-functions inside mch and solution-file (if present)      
    parse_object = remove_defs_and_parse_ast(root, env)         # 7. which kind of ast?
    if not isinstance(parse_object, BMachine):                 
        is_ppu = isinstance(parse_object, PredicateParseUnit) 
        is_epu = isinstance(parse_object, ExpressionParseUnit) 
        assert is_ppu or is_epu              
        result = interpret(parse_object.root, env)              # eval predicate or expression
        print result
        # TODO: print_values_b_style needs symbolic set impl
        #print print_values_b_style(result)
        return 0

    assert isinstance(parse_object, BMachine)               # 8. typecheck
    mch = parse_object
    type_check_root_bmch(root, env, mch) # also checks all included, seen, used and extend  
    # TODO: Check with B spec
    
                                                       # 9. animate if ops are present 
    # DO-WHILE Loop
    while True:
        next_states = __calc_states_and_print_ui(root, env, mch, solution_file_present)
        if next_states==[]: # BUG: no enabled ops doesnt mean there are none (deadlock-state)
            pass
        undo_possible = not env.state_space.empty()
        number_of_options = len(next_states)
        if undo_possible: 
            number_of_options = number_of_options + 1 
        input_str = "Input (0-"+str(number_of_options)+"):"
        #number = raw_input(input_str)
        # XXXX
        number = number_of_options
        number = int(number)
        

        # quit
        if number == number_of_options:
            print "goodbye"
            break
        elif undo_possible and number == number_of_options-1:
            x = env.state_space.get_stack_size()
            x = x-1 # BUGFIX: empty state on stack
            if 2==x and env.init_state_on_stack and env.set_up_state_on_stack:
                env.init_state_on_stack==False
                env.init_done = False
            elif 1==x and env.init_state_on_stack and env.set_up_state_on_stack==False:
                env.init_state_on_stack==False
                env.init_done = False
            elif 1==x and env.set_up_state_on_stack:
                env.set_up_done = False
                env.set_up_state_on_stack = False
                env.set_up_bmachines_names   = []
                
            env.state_space.undo()
        elif not env.set_up_done:
            env.set_up_done = True
            env.set_up_state_on_stack = True
            bstate = next_states[number]
            env.state_space.add_state(bstate) 
        elif not env.init_done:
            env.init_done = True
            env.init_state_on_stack = True
            bstate = next_states[number]
            env.state_space.add_state(bstate)
        # init and set_up done. Exec operation:
        elif len(next_states)>number and number >= 0:
            # switch state (
            bstate = next_states[number]
            env.state_space.add_state(bstate)
        else:
            print "Error! Wrong input:", number

    return 0
                                                              
def run_model_checking_mode(argv):
    print "\033[1m\033[91mWARNING\033[00m: model checking still experimental"
    root, env, parse_object, solution_file_present = startup(argv, offset=1)    
    if not isinstance(parse_object, BMachine):                                  
        print "Error: only model checking of b machines" 
        return -1

    assert isinstance(parse_object, BMachine)                   # 6. typecheck
    type_check_root_bmch(root, env, parse_object) # also checks all included, seen, used and extend
    mch = parse_object      

    bstates = set_up_constants(root, env, mch, solution_file_read=False)  # also evals properties
    # TODO: implement setup non determinism
    if len(bstates)==1:
        env.state_space.set_current_state(bstates[0])  
    elif len(bstates)>1:
        print "WARNING: non det. set up constants not supported yet" 
        return -1
        
    bstates = exec_initialisation(root, env, mch, solution_file_read=False)
    # TODO: volvo example 0 instead of 2 states
    for bstate in bstates:
        if not env.state_space.is_seen_state(bstate):
            env.state_space.set_current_state(bstate) 
    if not mch.has_invariant_mc:
        print "WARNING: no invariant present" 
        return -1   
    return _run_model_checking_mode(env, mch)

def get_printable_location(inv):
    return failsafe_pretty_print(inv)[:60]
jitdriver = jit.JitDriver(greens=['inv'], reds=['s_space', 'env', 'mch'], 
                          get_printable_location=get_printable_location, 
                          name="_run_model_checking_mode")
def _run_model_checking_mode(env, mch):
    inv = mch.aInvariantMachineClause
    s_space = env.state_space
    while not env.state_space.empty(): 
        # FIXME: dirty fix to avoid invariant checking of set up states 
        if env.state_space.get_state().opName=="set up":
            env.state_space.undo()
            continue
            
        jitdriver.jit_merge_point(inv=inv, s_space=s_space, env=env, mch=mch)
        if not DISABLE_INVARIANT_MC_CHECK:
            w_bool = inv.eval(env)  # 7. model check  
            if not w_bool.bvalue:
                print "WARNING: invariant violation found after checking", len(env.state_space.seen_states),"states"
                violation = env.state_space.get_state()
                violation.print_bstate()
                #print env.state_space.history
                return -1
            if EVAL_CHILD_INVARIANT:
                bstate = env.state_space.get_state()
                for bmachine in bstate.bmch_list:
                    if not bmachine is None and not bmachine.mch_name==mch.mch_name :
                        w_bool = interpret(bmachine.aInvariantMachineClause, env)
                        if not w_bool.bvalue:
                            print "WARNING: invariant violation in",bmachine.mch_name ," found after checking", len(env.state_space.seen_states),"states"
                            return False 
        next_states = calc_next_states(env, mch)
        s_space.undo()
        schedule_new_states(next_states, s_space)         
    print "checked",len(s_space.seen_states),"states.\033[1m\033[92m No invariant violation found.\033[00m"
    if DISABLE_INVARIANT_MC_CHECK:
        print "invariant check was disabled"
    
    return 0

def schedule_new_states(next_states, s_space):
    for tup in next_states:
        bstate = tup.bstate
        #bstate.print_bstate()
        if not s_space.is_seen_state(bstate):
            s_space.set_current_state(bstate)


# check of init without animation
def run_checking_mode():
    env = Environment()                                          # 1. create env.
    file_name_str, solution_file_name_str = read_input_string(argv, 1) # 2. read filenames
    ast_string, error = file_to_AST_str_no_print(file_name_str)  # 3. parse input-file to string
    if error:
        print error
    #env.set_search_dir(file_name_str)
    root = str_ast_to_python_ast(ast_string)                    # 4. parse string to python ast TODO: JSON
    #if solution_file_name_str:                                  # 5. parse solution-file and write to env.
    #    read_solution_file(env, solution_file_name_str)         # The concreate solution values are added at 
                                                                # the bmachine object-init time to the respective mch

                                                                # 6. replace defs and extern-functions inside mch and solution-file (if present)  
    parse_object = remove_defs_and_parse_ast(root, env)         # 7. which kind of ast?
    if not isinstance(parse_object, BMachine):                  # #PREDICATE or #EXPRESSION                   
        result = interpret(parse_object.root, env)              # eval predicate or expression
        print result
    else:
        assert isinstance(parse_object, BMachine)               # 8. typecheck
        type_check_root_bmch(root, env, parse_object) # also checks all included, seen, used and extend
        mch = parse_object                           
        
        #solution_file_read = not solution_file_name_str==""
        bstates = set_up_constants(root, env, mch, solution_file_read=False)  # also evals properties
        if not bstates==[]: 
            bool = True
            for bstate in bstates:
                env.state_space.add_state(bstate)
                #if mch.has_properties_mc:
                #    assert interpret(mch.aPropertiesMachineClause, env)
                init_bstates = exec_initialisation(root, env, mch, not solution_file_name_str=="")
                for init_bstate in init_bstates:
                    env.state_space.add_state(init_bstate)
                    if mch.has_invariant_mc:
                        w_bool = interpret(mch.aInvariantMachineClause, env)
                        bool = bool and w_bool.bvalue
                    env.state_space.undo()                  
                if mch.has_assertions_mc:
                    interpret(mch.aAssertionsMachineClause, env)
                env.state_space.undo()  
            return bool
        else: # TODO: dont repeat yourself 
            init_bstates = exec_initialisation(root, env, mch, not solution_file_name_str=="")
            for bstate in init_bstates:
                env.state_space.add_state(bstate)
                if mch.has_invariant_mc:
                    w_bool = interpret(mch.aInvariantMachineClause, env)  
                    assert w_bool.bvalue      
                if mch.has_assertions_mc:
                    interpret(mch.aAssertionsMachineClause, env)
                env.state_space.undo() 
            if not init_bstates==[]:  
                env.state_space.add_state(init_bstates[0]) 
        return eval_Invariant(root, env, mch)   

def print_usage():
    print "Usage: pyB <options> MachineFile <SolutionFile>"
    print "options:"
    print "-repl: read eval print loop"
    print "-c:    checking one state using a solution file"
    print "-mc:   model checking"
    print "-a:    animate model"
    return 0
  
def main(argv): 
###### MAIN PROGRAM ######
    # XXX crappy copy-pasted argument handling by cfbolz
    # https://bitbucket.org/cfbolz/pyrolog
    for i in range(len(argv)):
        if argv[i] == "--jit":
            if len(argv) == i + 1:
                print "missing argument after --jit"
                return 2
            jitarg = argv[i + 1] #e.g. --jit off 
            del argv[i:i+2]
            jit.set_user_param(jitdriver, jitarg)
            break
    if len(argv)<2:
        print "Error: Arglen <2 "
        print_usage()
        return 0
    try:
        #if argv[1]=="-repl" or argv[1]=="-r":
        #   run_repl()
        #elif argv[1]=="-check_solution" or argv[1]=="-c":
        #   result = run_checking_mode()
        #   print "Invariant:", result
        if argv[1]=="-model_checking" or argv[1]=="-mc":
            res = run_model_checking_mode(argv)
            return res
        #elif argv[1]=="-check_solution" or argv[1]=="-c":
        #    res = run_checking_mode()
        #    print "Invariant:", res
        #    return res
        #elif sys.argv[1]=="-animate" or sys.argv[1]=="-a":
        #   res = run_animation_mode(sys.argv)
        #   return res
        else:
            print_usage()
            return 0
    except Exception as e1:
        #print "\033[1m\033[91mError in PyB\033[00m:" #, type(e1), e1.args, e1
        import traceback
        #print "Use PyB-Python version to get a detailed error message"
        #print "\033[1m\033[91mBugreports to witulski@cs.uni-duesseldorf.de\033[00m:"
        #print "\033[1m\033[91mError message\033[00m:"
        #print traceback.format_exc()
        #print "\033[1m\033[91m End of error message\033[00m"
        return -1
         
  
def target(*args):
   return main, None # returns the entry point

if __name__ == '__main__':
   import sys
   main(sys.argv)
