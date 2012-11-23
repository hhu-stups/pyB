from ast_nodes import *
from bmachine import BMachine
from interp import interpret

class PredicateParseUnit:
    def __init__(self, root):
        self.root = root

class ExpressionParseUnit:
    def __init__(self, root):
        self.root = root

def parse_ast(root, env):
    if isinstance(root, APredicateParseUnit):
        return PredicateParseUnit(root)
    elif isinstance(root, AExpressionParseUnit):
        return ExpressionParseUnit(root)
    else:
        assert isinstance(root, AAbstractMachineParseUnit)
        mch = BMachine(root, interpret, env)
        env.root_mch = mch
        env.current_mch = mch #current mch
        return mch 