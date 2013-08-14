from bstate import BState

# TODO: Use a better datastruktur when you impl. modelchecking 
class StateSpace:
    def __init__(self):
        self.stack = [BState()]
    
    def get_state(self):
        return self.stack[-1]
    
    def empty(self):
        return len(self.stack)==1
    
    def undo(self):
        self.stack.pop()
    
    def add_state(self, bstate):
        self.stack.append(bstate)
    
    # call by generators to reset to partial result.
    # doesn't change stack hight 
    def revert(self, revert_bstate):
        self.undo()
        bstate = revert_bstate.clone()
        self.add_state(bstate)