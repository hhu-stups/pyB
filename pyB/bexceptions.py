# e.g: f={(1,42)} & x=f[5] 
class ValueNotInDomainException:   
    def __init__(self, value):
        self.value = value

class ConstraintNotImplementedException:
    def __init__(self, node):
        self.value = node

class ValueNotInBStateException:
    def __init__(self, value):
        self.value = value
        
class INITNotPossibleException:
    def __init__(self, string):
        self.value = string

class SETUPNotPossibleException:
    def __init__(self, string):
        self.value = string
