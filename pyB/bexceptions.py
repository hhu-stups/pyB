class ValueNotInDomainException:   
    def __init__(self, value):
        self.value = value

class ConstraintNotImplementedException:
    def __init__(self, node):
        self.value = node