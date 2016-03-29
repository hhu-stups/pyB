from bstate import BState
from config import DEPTH_FIRST_SEARCH_MODEL_CHECKING, USE_ANIMATION_HISTORY, USE_RPYTHON_CODE

if USE_RPYTHON_CODE:
    from rpython_b_objmodel import frozenset
    from rpython.rlib.objectmodel import r_ordereddict

def key_eq(s1, s2):
    return s1.equal(s2)
    
def key_hash(s):
    return s.__hash__()
     
# TODO: Use a better datastruktur when you impl. modelchecking 
class StateSpace:
    def __init__(self):
        self.stack = [BState()]
        self.seen_states = {} #r_ordereddict(key_eq, key_hash)
    
    # returntype: BState
    def get_state(self):
        if DEPTH_FIRST_SEARCH_MODEL_CHECKING:
            return self.stack[-1] # top of stack
        else:
            return self.stack[0]
        
    # return type: boolean
    def empty(self):
        return len(self.stack)==1
    
    def undo(self):
        if DEPTH_FIRST_SEARCH_MODEL_CHECKING:
           self.stack.pop()
        else:
           self.stack.pop(0)
           
    def is_seen_state(self, bstate):
        assert isinstance(bstate, BState)
        #return bstate in self.seen_states # TODO: use this!
        h = bstate.__hash__()
        if h in self.seen_states:
             # check hash collision. Be sure this state is new!
             s = self.seen_states[h]
             return s.equal(bstate)
        return False             
    
    def add_state(self, bstate, op_name="unknown"):
        assert isinstance(bstate, BState)
        self.stack.append(bstate)
        
    # not used by substitution generators, but by model checking
    def set_current_state(self, bstate):
        assert isinstance(bstate, BState)
        self.stack.append(bstate)
        #self.seen_states[h] = None
        h = bstate.__hash__()
        self.seen_states[h] = bstate
          
    
    # returntype: int
    def get_stack_size(self):
        return len(self.stack)
    
    # call by generators to reset to partial result.
    # doesn't change stack hight 
    def revert(self, revert_bstate):
        self.undo()
        bstate = revert_bstate.clone()
        self.add_state(bstate)
        
    def print_history(self):
        if USE_ANIMATION_HISTORY:
            bstate = self.get_state()
            while bstate is not None:
                string = bstate.opName 
                if bstate.parameter_values is not None:
                    string += ": " 
                    for value in bstate.parameter_values:
                        string += str(value)
                print string
                bstate = bstate.prev_bstate
                
    
