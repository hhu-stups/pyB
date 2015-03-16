from rpython_b_objmodel import frozenset

class TestRPythonFrozenset():
    def test_rpython_frozenset_creation(self):
         frozenset([])
         frozenset([1,2,3])
         frozenset([(1,"a"),(1,"b")])
         frozenset([frozenset([1,2,3]),frozenset([1,2])])
         frozenset([(1,2),(3,4)])
    
    
    def test_rpython_frozenset_length(self):
         assert len(frozenset([]))==0
         assert len(frozenset([1,2,3]))==3
         assert len(frozenset([(1,"a"),(1,"b")]))==2
         assert len(frozenset([frozenset([1,2,3]),frozenset([1,2])])) == 2
         
    def test_rpython_frozensets_equal(self):
         assert frozenset([])==frozenset([])
         assert frozenset([1,2,3])==frozenset([1,2,3])
         assert frozenset([(1,"a"),(1,"b")])==frozenset([(1,"a"),(1,"b")])
         assert frozenset([frozenset([1,2,3]),frozenset([1,2])])==frozenset([frozenset([1,2,3]),frozenset([1,2])])
         assert frozenset([(0,frozenset([1,2,3])),(1,frozenset([1,2]))])==frozenset([(0,frozenset([1,2,3])),(1,frozenset([1,2]))])
         assert frozenset([1,1,2])==frozenset([1,2])
         assert frozenset([1,2])==frozenset([2,1])
         assert frozenset([frozenset([1,2]),frozenset([1,2,3])])==frozenset([frozenset([1,2,3]),frozenset([1,2])])
         
         
         
         