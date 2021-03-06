# -*- coding: utf-8 -*-
# moved for testing-reasons
import os

from ast_nodes import *
from bexceptions import ValueNotInDomainException
from btypes import CartType
from config import VERBOSE, EXAMPLE_DIR, JAR_DIR, USE_RPYTHON_CODE
from subprocess import Popen, PIPE

if USE_RPYTHON_CODE:
    from rpython_b_objmodel import W_Tuple
    from rpython_b_objmodel import frozenset
     
#from pretty_printer import pretty_print
#from boperation import BOperation

# FIXME: automatic usage of 
#'java -cp "..\jars\*" de.prob.cliparser.CliBParser %s %s'
# on Windows 
command_str = "java -Xms64m -Xmx1024m -cp "
if os.name=='nt':
    command_str += ";"+JAR_DIR
    command_str += ";"+EXAMPLE_DIR
    command_str += ";. -jar "+JAR_DIR+"javaparser.jar "
    #command_str += ";. de.prob.cliparser.CliBParser "
else:
    command_str += ":"+JAR_DIR
    command_str += ":"+EXAMPLE_DIR
    command_str += ":. -jar "+JAR_DIR+"javaparser.jar "
    #command_str += ":. de.prob.cliparser.CliBParser "
#option_str = " -json"
option_str = " -python "

# only introduced for PyPy rtpyer. Base class of BMachine, PredicateParseUnit, ExpressionParseUnit
class ParseObject:
    pass

# TODO: ((0,1),2)[0]==(0,1)
def _tuple_equal(t0, t1):
    if USE_RPYTHON_CODE:
        return t0.__eq__(t1)
    else:
        return t0==t1

# f(x) on frozensets
def my_get_item(finite_set, arg):
    assert isinstance(finite_set, frozenset)
    result = []
    for atuple in finite_set:
        if _tuple_equal(atuple[0], arg):
            result.append(atuple[1])
    if result==[]:
        raise ValueNotInDomainException("")
    return result
    
    
# TODO: list of lists    
def set_to_list(aSet):
    if USE_RPYTHON_CODE:
        return aSet.to_list()
    return list(aSet) 

def solution_file_to_AST_str(file_name_str):
    f = open(file_name_str,"r")
    string = "#PREDICATE \n"+f.read()
    f.close()
    f = open("solution.tmp", "w")
    f.write(string)
    f.close()
    if VERBOSE:
        print "reading solution file "+file_name_str+" ..."
    result, err = file_to_AST_str_no_print("solution.tmp")
    return result, err


def create_file(b_str, bfile_name):
    from subprocess import Popen, PIPE
    p =  Popen("echo \"%s\" > %s.mch" % (b_str, bfile_name), shell=True, stderr=PIPE, stdin=PIPE, stdout=PIPE)
    e = p.stderr
    err_out = e.read()
    print err_out
    e.close()


# no print of error-messages
def file_to_AST_str_no_print(file_name_str):
    from config import USE_RPYTHON_POPEN
    out = ""
    c_str = command_str + option_str + " "+file_name_str
    #print c_str
    if USE_RPYTHON_POPEN:
        # TODO: remove % s
        from rpython.rlib.rfile import create_popen_file   
        file = create_popen_file(c_str, "r")
        out = file.read()
        file.close()
        return del_spaces(out), None
    else:      
        p =  Popen(c_str, shell=True, stderr=PIPE, stdin=PIPE, stdout=PIPE)
        w, r, e = (p.stdin, p.stdout, p.stderr)
        out = r.read()
        err_out = e.read()
        r.close()
        w.close()
        e.close()
        return del_spaces(out), err_out


def file_to_AST_str(file_name_str, path=""):
    from config import USE_RPYTHON_POPEN
    out = ""
    c_str = command_str + option_str + " "+path+file_name_str # java call
    if USE_RPYTHON_POPEN:
        from rpython.rlib.rfile import create_popen_file
        file = create_popen_file(c_str, "r")
        out = file.read()
        file.close()
    else:        
        p =  Popen(c_str , shell=True, stderr=PIPE, stdin=PIPE, stdout=PIPE)
        w, r, e = (p.stdin, p.stdout, p.stderr)
        out = r.read()
        err_out = e.read()
        if err_out:
            print err_out
        r.close()
        w.close()
        e.close()
    return del_spaces(out)


# returns list of 2-tuples (predicate, substitution) for every select-branch
# FIXME:(ISSUE #26) not used
def select_ast_to_list(select_ast):
    assert isinstance(select_ast, ASelectSubstitution)
    result = []
    predicate = select_ast.children[0]
    substitution = select_ast.children[1]
    assert isinstance(predicate, Predicate)
    assert isinstance(substitution, Substitution)
    result.append(tuple([predicate,substitution]))
    for case in select_ast.children[2:]:
        if isinstance(case, ASelectWhenSubstitution):
            predicate = case.children[0]
            substitution = case.children[1]
            assert isinstance(predicate, Predicate)
            assert isinstance(substitution, Substitution)
            result.append(tuple([predicate,substitution]))
        elif isinstance(case, Substitution):
            assert select_ast.hasElse=="True"
            result.append(tuple([None,case]))
        else:
            raise Exception("wrong select ast!")          
    return result


# del all space except that into b-strings
#FIXME \x00 compare problem in pypy-trans tests. Branches are not equivalent 
def del_spaces(string):
    from config import USE_RPYTHON_POPEN
    out = ""
    # Rpython does not work with line.replace(' ','')
    if USE_RPYTHON_POPEN:
        for line in string.split("\n"):
            if "AStringExpression" in line:
                out += line + "\n"
            else:
                out += my_replace(line) + "\n"
    else: 
        for line in string.split("\n"):
            if "AStringExpression" in line:
                out += line + "\n"
            else:
                out += line.replace(' ', '') + "\n"
    return out


# Bad performance. Removes spaces
def my_replace(string):
    from rpython.rlib.rstring import StringBuilder
    result = StringBuilder()
    for char in string:
        if not char==' ':
            result.append(char)
    return result.build()

def string_to_file(string, file_name, path=""):
    f = open(path+file_name,"w")
    f.write(string)
    f.close
    return f

# input is computation part of a membership or equal node.
# Used to find all variables to be computed first.
# TODO: find expr. like y = f(g(x))
def find_constraining_var_nodes(node, varList):
    lst = []
    _find_var_nodes(node, lst) #side-effect: fills list
    # varList is a list of all bound variables of the set defined by the predicate(node).
    # only bound vars are of interest. 
    result = []
    for var in lst:
        name = var.idName
        if name in [x.idName for x in varList]:
            result.append(var)
    for x in result:
        assert isinstance(x, AIdentifierExpression)
    #print [x.idName for x in result]
    return result    

def find_var_nodes(node):
    #print pretty_print(node.children[0])
    #assert isinstance(node, APredicateParseUnit) or isinstance(node, AExpressionParseUnit)
    lst = []
    _find_var_nodes(node, lst) #side-effect: fills list
    return lst


# helper for find_var_nodes, used only by typing of predicates or typing expressions.
# Quantified predicates are not visited because their variabels are enumerated separate. 
def _find_var_nodes(node, lst):
    # (case 1) new scope needed, stop search. This variables will be typed later
    if isinstance(node, AQuantifiedUnionExpression) or isinstance(node, AQuantifiedIntersectionExpression) or isinstance(node, AForallPredicate) or isinstance(node, AExistsPredicate) or isinstance(node, AComprehensionSetExpression) or isinstance(node, ALambdaExpression):
        return
    elif isinstance(node, AGeneralSumExpression) or isinstance(node, AGeneralProductExpression) or isinstance(node, AGeneralUnionExpression) or isinstance(node, AGeneralIntersectionExpression):
        return
    # (case 2) Ast leaf. Nothing to do. (avoid AttributeError in case 4)
    elif isinstance(node, AIntegerExpression) or isinstance(node, AStringExpression) or isinstance(node, AFileDefinitionDefinition): 
        return 
    # (case 3) Id node found. Add to list   
    elif isinstance(node, AIdentifierExpression):
        if (not node.idName in [l.idName for l in lst]):
            lst.append(node)
    elif isinstance(node, AEnumeratedSetSet) or isinstance(node, ADeferredSetSet):
        if not node.idName in [l.idName for l in lst]:
            lst.append(node)
    # (case 4) deep first search. 
    else:
        for n in node.children:
            _find_var_nodes(n, lst)


# search for all substitutions which change a variable.
# This is only used in parallel-substitutions to detect modifications of the same vars.
# TODO: Think of some way to do this not at runtime, but only once static at startup
def find_assignd_vars(node):
    lst = []
    _find_assignd_vars(node, lst)  # side-effect: fills list
    return lst 


def _find_assignd_vars(node, lst):
    # (case 1) Assignment found
    if isinstance(node, AAssignSubstitution):
        for i in range(int(node.lhs_size)):
            idNode = node.children[i]
            if isinstance(idNode, AIdentifierExpression):
                lst.append(idNode.idName)
            else:
                # FIXME:(ISSUE #25) This assumption may be wrong. Write test: {(1,2)}(1)
                assert isinstance(idNode, AFunctionExpression)
                assert isinstance(idNode.children[0], AIdentifierExpression)
                lst.append(idNode.children[0].idName)
    elif isinstance(node, AOperationCallSubstitution):
        for i in range(node.return_Num):
            idNode = node.children[i]
            assert isinstance(idNode, AIdentifierExpression)
            lst.append(idNode.idName)
    elif isinstance(node, ABecomesElementOfSubstitution) or isinstance(node, ABecomesSuchSubstitution):
        for i in range(node.idNum):
            idNode = node.children[i]
            assert isinstance(idNode, AIdentifierExpression)
            lst.append(idNode.idName)
    # (case 2) Ast leaf. Nothing to do. (avoid AttributeError in case 3)
    elif isinstance(node, AIntegerExpression) or isinstance(node, AStringExpression) or isinstance(node, AFileDefinitionDefinition) or isinstance(node, AIdentifierExpression): 
        return 
    # (case 3) deep first search.             
    else:
        for n in node.children:
            _find_assignd_vars(n, lst)


# [[1,2],[3,[[4]]]] -> [1,2,3,4]
def flatten(lst, res):
    for e in lst:
        if not isinstance(e,list):
            res.append(e)
        else:
            res = flatten(e, res)
    return res
    
    
# ((3, 4), 5) -> [3,4,5]
def remove_tuples(tup):
    if isinstance(tup, tuple):
        a = remove_tuples(tup[0])
        b = remove_tuples(tup[1])
        return a+b
    elif USE_RPYTHON_CODE and isinstance(tup, W_Tuple):
        a = remove_tuples(tup.tvalue[0])
        b = remove_tuples(tup.tvalue[1])
        return a+b        
    else:
        return [tup]


# this helper gets the type of an id and calcs how many 
# args are needed for this type. This is used by symbolic compositions to set
# id nodes of symbolic lambda expressions. E.g ((a,b),c)= 3 args
# SIDE-EFFECT: modifies value_list
def build_arg_by_type(atype, value_list):
     if isinstance(atype, CartType):
         a = build_arg_by_type(atype.left, value_list)
         b = build_arg_by_type(atype.right, value_list)
         if USE_RPYTHON_CODE:
             return W_Tuple((a,b))
         else:
             return tuple([a,b])
     return value_list.pop(0)
 
     
# only used by RPython. Number of 'element' in lst. used to find double entrys
def my_count(lst, element):
    count = 0
    for e in lst:
        if e.__eq__(element):
            count = count +1
    return count

# TODO: horrible runtime!
# only used by RPython. sequence represented as list of W_Tuple
def sort_sequence(s):
    result = []
    i = 0
    while i!=len(s):
        for w_tup in s:
            if w_tup.tvalue[0].ivalue==i+1:
                result.append(w_tup)
                continue
        i=i+1
    assert len(s)==len(result)
    return result
        
    


# checks if a list contains a duplicate element. 
# e.g used to check if a relation is a function
def double_element_check(lst):
    for element in lst:
        more_than_one = False
        if USE_RPYTHON_CODE:
            more_than_one = my_count(lst, element)>1
        else:
            more_than_one = lst.count(element)>1
        if more_than_one:
            return True
    return False


# used by machine parameters
def contains_lower_character(string):
    for c in string:
        if c>='a' and c<='z':
            return True
    return False

# True if all free variables have an value BEFORE the visit of this AST
# E.g. "x=42" is False if x has no value BEFORE 
def all_ids_known(node, env):
    if isinstance(node, AIdentifierExpression):
        value = env.get_value(node.idName)
        if value==None:
            return False
        return True
    elif isinstance(node, AStringExpression) or isinstance(node, AIntegerExpression) or isinstance(node, ABooleanTrueExpression) or isinstance(node, ABooleanFalseExpression):
        return True
    elif isinstance(node, AExistsPredicate) or isinstance(node, AForallPredicate):
        return False # TODO: implement me
    elif isinstance(node, AStructExpression):
        return False # TODO: implement me
    elif isinstance(node, AComprehensionSetExpression):
        id_names = []
        for idNode in node.children[:-1]:
            id_names.append(idNode.idName)
        env.add_ids_to_frame(id_names)
        for idNode in node.children[:-1]:
            env.set_value(idNode.idName, "dummy_value_for_bound_variables")
        # search for free variables which have no values        
        return all_ids_known(node.children[-1], env)
    elif isinstance(node, ALambdaExpression):
        id_names = []
        for idNode in node.children[:-2]:
            id_names.append(idNode.idName)  
        env.add_ids_to_frame(id_names)
        for idNode in node.children[:-2]:
            env.set_value(idNode.idName, "dummy_value_for_bound_variables")
        # search for free variables which have no values  
        predicate_ids_known  = all_ids_known(node.children[-2], env) 
        expression_ids_known = all_ids_known(node.children[-1], env) 
        return predicate_ids_known and expression_ids_known
    else:
        for child in node.children:
            if all_ids_known(child, env)==False:
                return False
    return True
    
# AST: P0 & P1 ...PN ->[P0,P1,..PN]
# returns a list of predicates 
def conj_tree_to_conj_list(ast):
    if isinstance(ast, AConjunctPredicate):
        lst0 = conj_tree_to_conj_list(ast.children[0])
        lst1 = conj_tree_to_conj_list(ast.children[1])
        return lst0 + lst1
    else:
        return [ast]


# returns a list of elements (maybe ids) 
def couple_tree_to_conj_list(ast):
    if isinstance(ast, ACoupleExpression):
        lst0 = couple_tree_to_conj_list(ast.children[0])
        lst1 = couple_tree_to_conj_list(ast.children[1])
        return lst0 + lst1
    else:
        return [ast]     
 
        
# Helper for debugging                     
def print_ast(root):
    print root
    __print_ast(root, 1)
    print


def __print_ast(node, num):
    if isinstance(node, AIdentifierExpression):
        print "\t"*num, " " ,node.idName
        return
    elif isinstance(node, AStringExpression) or isinstance(node, AIntegerExpression) or isinstance(node, AFileDefinitionDefinition):
        return
    for child in node.children:
        print "\t"*num,"|-",child
        __print_ast(child, num+1)