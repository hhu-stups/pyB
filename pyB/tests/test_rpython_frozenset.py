from rpython_b_objmodel import frozenset, W_Integer, W_Tuple, W_String

class TestRPythonFrozenset():
    def test_rpython_frozenset_creation(self):
         frozenset([])
         frozenset([W_Integer(1),W_Integer(2),W_Integer(3)])
         frozenset([(W_Integer(1),W_String("a")),(W_Integer(1),W_String("b"))])
         frozenset([frozenset([W_Integer(1),W_Integer(2),W_Integer(3)]),frozenset([W_Integer(1),W_Integer(2)])])
         frozenset([(W_Integer(1),W_Integer(2)),(W_Integer(3),W_Integer(4))])
    
    
    def test_rpython_frozenset_length(self):
         assert len(frozenset([]))==0
         assert len(frozenset([W_Integer(1),W_Integer(2),W_Integer(3)]))==3
         assert len(frozenset([W_Tuple((W_Integer(1),W_String("a"))),W_Tuple((W_Integer(1),W_String("b")))]))==2
         assert len(frozenset([frozenset([W_Integer(1),W_Integer(2),W_Integer(3)]),frozenset([W_Integer(1),W_Integer(2)])])) == 2
         
    def test_rpython_frozensets_equal(self):
         assert frozenset([])==frozenset([])
         assert frozenset([W_Integer(1),W_Integer(2),W_Integer(3)])==frozenset([W_Integer(1),W_Integer(2),W_Integer(3)])
         assert frozenset([W_Tuple((W_Integer(1),W_String("a"))),W_Tuple((W_Integer(1),W_String("b")))])==frozenset([W_Tuple((W_Integer(1),W_String("a"))),W_Tuple((W_Integer(1),W_String("b")))])
         assert frozenset([frozenset([W_Integer(1),W_Integer(2),W_Integer(3)]),frozenset([W_Integer(1),W_Integer(2)])])==frozenset([frozenset([W_Integer(1),W_Integer(2),W_Integer(3)]),frozenset([W_Integer(1),W_Integer(2)])])
         assert frozenset([W_Tuple((W_Integer(0),frozenset([W_Integer(1),W_Integer(2),W_Integer(3)]))),W_Tuple((W_Integer(1),frozenset([W_Integer(1),W_Integer(2)])))])==frozenset([W_Tuple((W_Integer(0),frozenset([W_Integer(1),W_Integer(2),W_Integer(3)]))),W_Tuple((W_Integer(1),frozenset([W_Integer(1),W_Integer(2)])))])
         assert frozenset([W_Integer(1),W_Integer(1),W_Integer(2)])==frozenset([W_Integer(1),W_Integer(2)])
         assert frozenset([W_Integer(1),W_Integer(2)])==frozenset([W_Integer(2),W_Integer(1)])
         assert frozenset([frozenset([W_Integer(1),W_Integer(2)]),frozenset([W_Integer(1),W_Integer(2),W_Integer(3)])])==frozenset([frozenset([W_Integer(1),W_Integer(2),W_Integer(3)]),frozenset([W_Integer(1),W_Integer(2)])])
         
         
         
         