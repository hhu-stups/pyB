# Wrapped basic types to allow RPYTHOn Typing (everthing is a W_Object)

class W_Object:
    pass

# sadly only single inheritance allow in RPYTHON :(
# reimplementation of all needed integer operations
# special methods are NOT supported by RPython. But they allow easy switching of
# build-in types and wrapped types in the python version. A measurement of 
# speed- and space-loose  is possible.
# Immutable (always return W_XXX) to get better performance results with RPTYHON-tranlation
class W_Integer(W_Object):
    def __init__(self, value):
        assert isinstance(value, int)
        self.value = value
    
    def __add__(self, other):
        assert isinstance(other, W_Integer)
        return W_Integer(self.value+other.value)   
    
    def __sub__(self, other):
        assert isinstance(other, W_Integer)
        return W_Integer(self.value - other.value)         

    def __mul__(self, other):
        assert isinstance(other, W_Integer)
        return W_Integer(self.value * other.value)
        
    def __div__(self, other):
        assert isinstance(other, W_Integer)
        return W_Integer(self.value / other.value)      
        
    def __lt__(self, other):
        assert isinstance(other, W_Integer)
        return W_Boolean(self.value < other.value)   
        
    def __le__(self, other):
        assert isinstance(other, W_Integer)
        return W_Boolean(self.value <= other.value)
         
    def __eq__(self, other):
        assert isinstance(other, W_Integer)
        return W_Boolean(self.value < other.value) 
        
    def __ne__(self, other):
        assert isinstance(other, W_Integer)
        return W_Boolean(self.value != other.value) 
            
    def __gt__(self, other):
        assert isinstance(other, W_Integer)
        return W_Boolean(self.value > other.value) 
        
    def __ge__(self, other):
        assert isinstance(other, W_Integer)
        return W_Boolean(self.value >= other.value) 
    
    def __neg__(self):
        return W_Integer(-1*self.value)


class W_Boolean(W_Object):
    def __init__(self, value):
        assert isinstance(value, bool)
        self.value = value 
      
    def __and__(self, other):
        assert isinstance(other, W_Boolean)
        return W_Boolean(self.value and other.value)
                
    def __or__(self, other):
        assert isinstance(other, W_Boolean)
        return W_Boolean(self.value or other.value)
        
    def __not__(self):
        return W_Boolean(not self.value)

class W_None(W_Object):
    pass