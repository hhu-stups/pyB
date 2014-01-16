# helper functions ONLY(!) used by tests. 
from interp import set_up_constants, exec_initialisation

# The data from the solution-files has already been read at the mch creation time.
# side-effect of this method may be a state change.
# arbitrary
def arbitrary_init_machine(root, env, mch, solution_file_read=False):    
    bstates = set_up_constants(root, env, mch, solution_file_read)
    if len(bstates)>0:
        env.state_space.add_state(bstates[0])
    bstates = exec_initialisation(root, env, mch, solution_file_read)
    if len(bstates)>0:
        env.state_space.add_state(bstates[0]) 