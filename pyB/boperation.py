from rpython_b_objmodel import W_Object

class BOperation(W_Object):
    def __init__(self, name, operation_ast, bmachine):
        self.return_types = []
        self.parameter_types = []
        self.op_name = name
        self.ast = operation_ast        
        self.owner_machine = bmachine
        self.is_query_op = False

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