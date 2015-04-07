from bstate import BState
from config import DEPTH_FIRST_SEARCH_MODEL_CHECKING

# TODO: Use a better datastruktur when you impl. modelchecking 
class StateSpace:
    def __init__(self):
        self.stack = [BState()]
        self.history = [] # only strings
    
    # returntype: BState
    def get_state(self):
        if DEPTH_FIRST_SEARCH_MODEL_CHECKING:
            return self.stack[-1]
        else:
            return self.stack[0]
    
    # returntype: boolean
    def empty(self):
        return len(self.stack)==1
    
    def undo(self):
        if DEPTH_FIRST_SEARCH_MODEL_CHECKING:
           self.stack.pop()
           self.history.pop()
        else:
           self.stack.pop(0)
           self.history.pop(0)           
    
    def add_state(self, bstate, op_name="unknown"):
        self.history.append(op_name)
        self.stack.append(bstate)
    
    # returntype: int
    def get_stack_size(self):
        return len(self.stack)
    
    # call by generators to reset to partial result.
    # doesn't change stack hight 
    def revert(self, revert_bstate):
        self.undo()
        bstate = revert_bstate.clone()
        self.add_state(bstate)
