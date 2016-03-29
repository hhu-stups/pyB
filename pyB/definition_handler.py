# -*- coding: utf-8 -*-
from ast_nodes import *
from config import USE_RPYTHON_CODE
from external_functions import EXTERNAL_FUNCTIONS_DICT
from helpers import file_to_AST_str_no_print, print_ast
from pretty_printer import pretty_print


if USE_RPYTHON_CODE:
     from rpython_b_objmodel import frozenset

# This class modifies an AST. It generates a "definition free" AST ahead of time. (after parsing, before interpretation)
class DefinitionHandler():
    
    def __init__(self, env, parsing_method):
        self.def_map = {} # string --> AST
        self.external_functions_found = [] # string
        self.external_functions_types_found = {} # 
        self.used_def_files = []
        self.env = env # needed for search path of definition-files
        # avoid cyclic import: parser needs to handele definitions inside the AST and
        # definition handler needs to parse (definition-) files
        self.str_ast_to_python_ast = parsing_method
        

    def repl_defs(self, root):
        for clause in root.children:
            if isinstance(clause, ADefinitionsMachineClause):
                self._save_definitions(clause)
        self._replace_definitions(root)
        self._replace_ext_funcs_in_solution_file(self.env.solution_root)
        

    # fill def_map with "definition-definitions"
    def _save_definitions(self, clause):
        assert isinstance(clause, ADefinitionsMachineClause)
        self._process_definition_files(clause)
        for definition in clause.children:
            if isinstance(definition, AFileDefinitionDefinition):
                continue
            assert isinstance(definition, AExpressionDefinitionDefinition) or isinstance(definition, APredicateDefinitionDefinition) or isinstance(definition, ASubstitutionDefinitionDefinition)
            self.def_map[definition.idName] = definition
            # make sure only ext. funs. are replaced if definition entry is presend
            if definition.idName in EXTERNAL_FUNCTIONS_DICT.keys():
                self.external_functions_found.append(definition.idName)
            if definition.idName.startswith("EXTERNAL_FUNCTION_"):
                self.external_functions_types_found[definition.idName[18:]] = definition.children[0]
                         

    # Defs can use definitions from these files. 
    # All of them musst be processed before any def in this file                    
    def _process_definition_files(self, clause):
        for definition in clause.children :
            if isinstance(definition, AFileDefinitionDefinition): #TODO: implement me
                if definition.idName in self.used_def_files: # avoid def-file loops
                    continue
                self.used_def_files.append(definition.idName)
                # get def-file ast
                file_path_and_name = self.env._bmachine_search_dir + definition.idName
                ast_string, error = file_to_AST_str_no_print(file_path_and_name) 
                root = self.str_ast_to_python_ast(ast_string)
                assert isinstance(root, ADefinitionFileParseUnit)  
                assert isinstance(root.children[0], ADefinitionsMachineClause)
                # used definitions
                self._save_definitions(root.children[0])                   

 
    # side-effect: change definitions to def free Asts
    def _replace_definitions(self, root):
        try:
            for i in range(len(root.children)):
                child = root.children[i]
                if isinstance(child, ADefinitionExpression) or isinstance(child, ADefinitionPredicate) or isinstance(child,  ADefinitionSubstitution):
                    # replace with ext. fun node if necessary 
                    if child.idName in self.external_functions_found:
                       name = child.idName
                       type_ast = self.external_functions_types_found[name]
                       func = EXTERNAL_FUNCTIONS_DICT[name]
                       root.children[i] = AExternalFunctionExpression(name, type_ast, func)
                       root.children[i].children = child.children # args of the function
                       return 
                    def_free_ast = self._gen_def_free_ast(child)
                    root.children[i] = def_free_ast
                else:
                    self._replace_definitions(child)
        except AttributeError as e: # leaf:no children
            print "AttributeError while definition handling",e
            return


    # solution files dont know they use extern functions.
    # comments like /*EXT:*/ are removed by the parser. 
    def _replace_ext_funcs_in_solution_file(self, root):
        if root is None: # e.g. no solution file present
            return
        try:
            for i in range(len(root.children)):
                child = root.children[i]
                if isinstance(child, AFunctionExpression) and isinstance(child.children[0], AIdentifierExpression):
                    try:
                        name = child.children[0].idName
                        type_ast = self.external_functions_types_found[name]
                        func = EXTERNAL_FUNCTIONS_DICT[name]
                        root.children[i] = AExternalFunctionExpression(name, type_ast, func)
                        root.children[i].children = child.children[1:] # args of the function, first id is function name
                    except KeyError:
                        continue
                else:
                    self._replace_ext_funcs_in_solution_file(child)
        except AttributeError as e:
            print "AttributeError while definition handling", e
            return
        
    
    def _gen_def_free_ast(self, def_node):
        ast = self.def_map[def_node.idName]
        assert isinstance(ast, AExpressionDefinitionDefinition) or isinstance(ast, APredicateDefinitionDefinition) or isinstance(ast, ASubstitutionDefinitionDefinition)
        replace_nodes = {}
        # (1) find nodes to be replaced 
        for i in range(ast.paraNum):
            if isinstance(ast.children[i], AIdentifierExpression):
                replace_nodes[ast.children[i].idName] = def_node.children[i]
            else:
                raise Exception("Definition-Parametes must be IdentifierExpressions! %s" % ast.children[i])
        # (2) replace nodes
        # the ast instance is a reusable pattern found in the definition clause and used
        # in some other clause (def_node). Def_node can be a INITIALISATION or the body
        # of a operation. The copy is needed because the 'pattern' ast can be used on
        # more than one location
        #
        # example:
        # def_node:     INITIALISATION Assign(z, 1+1) || Assign(b, TRUE) 
        # ast:          DEFINITIONS Assign(VarName,Expr) == VarName := Expr; 
        # replace nodes: {(VarName,z),(Expr,1+1)}
        ast_clone = self._clone_ast(ast)
        self._replace_nodes(ast_clone, replace_nodes)
        return ast_clone.children[-1]
    
    
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
    

    def _clone_ast(self, ast):
        # deepcopy is not Rpython
        #import copy
        #print "original"
        #print_ast(ast)
        #result = copy.deepcopy(ast)
        result = ast.deepcopy()
        #print "clone"
        #print_ast(result)
        return result
        