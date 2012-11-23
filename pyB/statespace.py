from bstate import BState

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