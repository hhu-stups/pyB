from ast_nodes import *

class DefinitionHandler():
    
    def __init__(self):
        self.def_map = {}
        

    def repl_defs(self, root):
        self.save_definitions(root)
        self.replace_definitions(root)


    def save_definitions(self, root):
        for clause in root.children:
            if isinstance(clause, ADefinitionsMachineClause):
                for definition in clause.children:
                    assert isinstance(definition, AExpressionDefinition) or isinstance(definition, APredicateDefinition) or isinstance(definition, ASubstitutionDefinition)
                    self.def_map[definition.idName] = definition

 
    # side-effect: change definitions to def free Asts
    def replace_definitions(self, root):
        try:
            for i in range(len(root.children)):
                child = root.children[i]
                if isinstance(child, ADefinitionExpression) or isinstance(child, ADefinitionPredicate) or isinstance(child, ADefinitionSubstitution):
                    def_free_ast = self._gen_def_free_ast(child)
                    root.children[i] = def_free_ast
                else:
                    self.replace_definitions(child)
        except AttributeError: # leaf:no children
            return

    
    def _gen_def_free_ast(self, def_node):
        ast = self.def_map[def_node.idName]
        replace_nodes = {}
        # (1) find nodes to be replaced 
        for i in range(ast.paraNum):
            if isinstance(ast.children[i], AIdentifierExpression):
                replace_nodes[ast.children[i].idName] = def_node.children[i]
            else:
                raise Exception("Definition-Parametes must be IdentifierExpressions!")
        # (2) replace nodes
        import copy
        result = copy.deepcopy(ast)
        self._replace_nodes(result, replace_nodes)
        return result.children[-1]
    
    
    # side-effect: change definition-nodes to def-free nodes   
    def _replace_nodes(self, ast, map):
        try:
            for i in range(len(ast.children)):
                child = ast.children[i]
                if isinstance(child, AIdentifierExpression) and child.idName in map:
                    ast.children[i] = map[child.idName]
                else:
                    self._replace_nodes(child, map)
        except AttributeError: # leaf:no children
            return