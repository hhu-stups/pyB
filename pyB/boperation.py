from rpython_b_objmodel import W_Object
from config import USE_RPYTHON_CODE

class BOperation(W_Object):
    def __init__(self, name, operation_ast, bmachine):
        self.return_types = []
        self.parameter_types = []
        self.op_name = name
        self.ast = operation_ast        
        self.owner_machine = bmachine
        self.is_query_op = False
    
    # TODO: self.ast not used. 
    # if ast are different, but all attr are _eq_ the ops are eq. 
    def __eq__(self, other):
        if not isinstance(other, BOperation):
            return False
 
        if not self.op_name == other.op_name:
            return False           
        if not self.return_types == other.return_types:
            return False
        if not self.parameter_types == other.parameter_types:
            return False   
        #if not self.owner_machine == other.owner_machine:
        #    return False 
        if not self.is_query_op == other.is_query_op:
            return False           
        return True

    # called by typeit once inside a operation node (self.ast)  
    def set_types(self, ret_types, para_types, ret_nodes, para_nodes):
        self.return_types    = ret_types
        self.parameter_types = para_types
        self.return_nodes    = ret_nodes
        self.parameter_nodes = para_nodes


    # only used to change the name (prefix)
    def copy_op(self):
        op = BOperation(self.op_name, self.ast, self.owner_machine)
        #op.return_types = self.return_types
        #op.parameter_types = self.parameter_types
        #op.is_query_op = self.is_query_op
        return op


    def __hash__(self):
        if USE_RPYTHON_CODE:
            from rpython.rlib.objectmodel import compute_hash
            hash_str = compute_hash(self.__repr__())
        else:
            hash_str = hash(self.__repr__())
        return hash_str 
    
    def __repr__(self):
        string = ""
        string += str(self.return_types)
        string += str(self.parameter_types)
        string += str(self.op_name)
        #string += self.ast = operation_ast        
        string += str(self.owner_machine)
        string += str(self.is_query_op)
        return string
        