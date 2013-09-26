from ast_nodes import *
from helpers import file_to_AST_str, string_to_file
from definition_handler import DefinitionHandler

file_name = "input.txt"

class TestDefinitionHandler():
    def test_def_find(self):
        string='''
        MACHINE Test
        VARIABLES z, b, x
        INVARIANT x:NAT & z:NAT & b:BOOL
        INITIALISATION x:=2 ; Assign(x+1, z) ; Assign(TRUE, b)
        DEFINITIONS Assign(Expr, VarName) == VarName := Expr;
        END'''
        string_to_file(string, file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string
        
        dh = DefinitionHandler()
        dh.save_definitions(root.children[4])
        assert isinstance(dh.def_map["Assign"], ASubstitutionDefinition)


    def test_replace_defs(self):
        string='''
        MACHINE Test
        VARIABLES z, b, x
        INVARIANT x:NAT & z:NAT & b:BOOL
        INITIALISATION x:=2 ; Assign(x+1, z) ; Assign(TRUE, b)
        DEFINITIONS Assign(Expr, VarName) == VarName := Expr;
        END'''
        string_to_file(string, file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string
        
        init = root.children[3]
        assert isinstance(init, AInitialisationMachineClause)
        subst = init.children[0]
        assert isinstance(subst.children[1], ADefinitionSubstitution)
        assert isinstance(subst.children[2], ADefinitionSubstitution)
        dh = DefinitionHandler()
        dh.save_definitions(root.children[4])
        def_free_ast = dh.replace_definitions(root)
        assert isinstance(subst.children[1], AAssignSubstitution)
        assert isinstance(subst.children[2], AAssignSubstitution)


    def test_replace_defs2(self):
        string='''
        MACHINE Test
        VARIABLES z, b, x
        INVARIANT x:NAT & z:NAT & b:BOOL
        INITIALISATION x:=2 ; Assign(x+1, z) ; Assign(TRUE, b)
        DEFINITIONS Assign(Expr, VarName) == VarName := Expr;
        END'''
        string_to_file(string, file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string
        
        init = root.children[3]
        assert isinstance(init, AInitialisationMachineClause)
        subst = init.children[0]
        assert isinstance(subst.children[1], ADefinitionSubstitution)
        assert isinstance(subst.children[2], ADefinitionSubstitution)
        dh = DefinitionHandler()
        dh.repl_defs(root)
        assert isinstance(subst.children[1], AAssignSubstitution)
        assert isinstance(subst.children[2], AAssignSubstitution)
        assert subst.children[1].children[0].idName  == "z" 
        assert subst.children[2].children[0].idName  == "b"        
  

    def test_def_files(self):
        string='''
        MACHINE Test
		DEFINITIONS 
		  "common1.def" ; 
		  begin==-2*UNIT ; 
		  end == 10 * UNIT
		END'''
        string_to_file(string, file_name)
        ast_string = file_to_AST_str(file_name)
        exec ast_string 
        
        dh = DefinitionHandler()                                    # 5. replace defs if present 
        dh.repl_defs(root) 
   