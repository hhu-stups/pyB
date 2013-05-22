class BOperation:
    def __init__self(self):
        self.return_types = None
        self.parameter_types = None
        self.op_name = ""
        self.ast = None        
        self.owner_machine = None
        self.is_query_op = False
  
    # only used ti change the name (prefix)
    def copy(self):
        op = BOperation()
        op.return_types = self.return_types
        op.parameter_types = self.parameter_types
        op.op_name = self.op_name
        op.ast = self.ast     
        op.owner_machine = self.owner_machine
        op.is_query_op = self.is_query_op
        return op