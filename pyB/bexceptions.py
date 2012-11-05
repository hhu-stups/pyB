# e.g: f={(1,42)} & x=f[5] 
class ValueNotInDomainException:   
    def __init__(self, value):
        self.value = value

class ConstraintNotImplementedException:
    def __init__(self, node):
        self.value = node