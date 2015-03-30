# -*- coding: utf-8 -*-
# This classes are used to map Java-AST Nodes to Python-AST Nodes (Objects)

# TODO: AMachineMachineVariant

class Node():
    def __init__(self):
        self.children = []
    
    # Rpython typing fails on direct access like node.children[i].
    # But it doesnt fails when a method does it
    def get(self, index):
        return self.children[index]

# Baseclasses Clause, Predicate, Expression and Substitution are used for assertions
# inside the interpreter. (node classification )


# Return type unknown: boolean, integer, string, frozenset or struct
class Expression(Node):
    pass


# Evaluation always returns a frozenset
class SetExpression(Expression):
    pass

    
# Evaluation always returns a integer
class IntegerExpression(Expression):
    pass


# Evaluation always returns a string
class StringExpression(Expression):
    pass
    
# Evaluation always returns a boolean
class Predicate(Node):
    pass

# constructor overwritten in special cases
class Clause(Node):
    def __init__(self, childNum):
        self.childNum = int(childNum)
        self.children = []

# constructor overwritten in special cases        
class Substitution(Node):
    def __init__(self, childNum):
        self.childNum = int(childNum)
        self.children = []

class ParseUnit(Node):
    pass

class AAbstractMachineParseUnit(ParseUnit):
    def __init__(self, childNum):
        self.childNum = int(childNum)
        self.children = []

class APredicateParseUnit(ParseUnit):
    pass

class AExpressionParseUnit(ParseUnit):
    pass

class ADefinitionFileParseUnit(ParseUnit):
    pass
    
class AOperation(Node):
    def __init__(self, childNum, opName, return_Num, parameter_Num):
        self.childNum = int(childNum)
        self.opName = opName
        self.return_Num = int(return_Num)
        self.parameter_Num = int(parameter_Num)
        self.children = []

# old parser: AEnumeratedSet
class AEnumeratedSetSet(Node):
    def __init__(self, childNum, idName):
        self.childNum = int(childNum)
        self.idName = idName
        self.children = []

# old parser: ADeferredSet
class ADeferredSetSet(Node):
    def __init__(self, idName):
        self.idName = idName
        self.children = []

class AMachineHeader(Node):
    def __init__(self, childNum, idName):
        self.childNum = int(childNum)
        self.idName = idName
        self.children = []

class AMachineReference(Node):
     def __init__(self, childNum, idName):
        self.childNum = int(childNum)
        self.idName = idName
        self.children = []

class ASeesMachineClause(Clause):
    pass

class AUsesMachineClause(Clause):
    pass

class AExtendsMachineClause(Clause):
    pass

class APromotesMachineClause(Clause):
    pass

class AIncludesMachineClause(Clause):
    pass

class AConstraintsMachineClause(Clause):
    def __init__(self):
        self.children = []

# CONCRETE_CONSTANTS and CONSTANTS-clause
class AConstantsMachineClause(Clause):
    pass

# ABSTRACT_VARIABLES and VARIABLES-clause
class AVariablesMachineClause(Clause):
    pass
    
# CONCRETE_VARIABLES-clause
class AConcreteVariablesMachineClause(Clause):
    pass

# ABSTRACT_CONSTANTS-clause
class AAbstractConstantsMachineClause(Clause):
    pass

class AInvariantMachineClause(Clause):
    def __init__(self):
        self.children = []

class AInitialisationMachineClause(Clause):
    def __init__(self):
        self.children = []

class APropertiesMachineClause(Clause):
    def __init__(self):
        self.children = []

class AAssertionsMachineClause(Clause):
    pass

class ASetsMachineClause(Clause):
    pass

class ADefinitionsMachineClause(Clause):
    pass

class AOperationsMachineClause(Clause):
    pass

class APowerOfExpression(IntegerExpression):
    pass

# old parser: AUnaryExpression
class AUnaryMinusExpression(IntegerExpression):
    pass

class AConvertBoolExpression(Expression):
    pass

# old parser: AExpressionDefinition
class AExpressionDefinitionDefinition(Expression):
    def __init__(self, childNum, idName, paraNum):
        self.childNum = int(childNum)
        self.idName = idName
        self.paraNum = int(paraNum)
        self.children = []

class ADefinitionExpression(Expression):
    def __init__(self, childNum, idName):
        self.childNum = int(childNum)
        self.idName = idName
        self.children = []

class ABoolSetExpression(SetExpression):
    pass

# old parser: ATrueExpression
class ABooleanTrueExpression(Expression):
    pass

# old parser: AFalseExpression
class ABooleanFalseExpression(Expression):
    pass

class AMinExpression(IntegerExpression):
    pass

class AMaxExpression(IntegerExpression):
    pass

class AGeneralUnionExpression(SetExpression):
    pass

class AGeneralIntersectionExpression(SetExpression):
    pass

class AAddExpression(IntegerExpression):
    pass

class AMinusOrSetSubtractExpression(Expression):
    pass

class AMultOrCartExpression(Expression):
    pass

class ADivExpression(IntegerExpression):
    pass

class AModuloExpression(IntegerExpression):
    pass

class ACardExpression(IntegerExpression):
    pass

class AUnionExpression(SetExpression):
    pass

class AIntersectionExpression(SetExpression):
    pass

class AEmptySetExpression(SetExpression):
    pass

class ASetExtensionExpression(SetExpression):
    def __init__(self, childNum):
        self.childNum = int(childNum)
        self.children = []

class ACoupleExpression(Expression):
    def __init__(self, childNum):
        self.childNum = int(childNum)
        self.children = []

class APowSubsetExpression(SetExpression):
    pass

class APow1SubsetExpression(SetExpression):
    pass

class ARelationsExpression(SetExpression):
    pass

class ADomainExpression(SetExpression):
    pass

class ARangeExpression(SetExpression):
    pass

class ACompositionExpression(SetExpression):
    pass

class AIdentityExpression(SetExpression):
    pass

class AIterationExpression(SetExpression):
    pass

class AReflexiveClosureExpression(SetExpression):
    pass

class AClosureExpression(SetExpression):
    pass

class ADomainRestrictionExpression(SetExpression):
    pass

class ADomainSubtractionExpression(SetExpression):
    pass

class ARangeRestrictionExpression(SetExpression):
    pass

class ARangeSubtractionExpression(SetExpression):
    pass

class AReverseExpression(SetExpression):
    pass

class AImageExpression(SetExpression):
    pass

class AOverwriteExpression(SetExpression):
    pass

class ADirectProductExpression(SetExpression):
    pass

class AFirstProjectionExpression(SetExpression):
    pass

class ASecondProjectionExpression(SetExpression):
    pass

class AParallelProductExpression(SetExpression):
    pass

class APartialFunctionExpression(SetExpression):
    pass

class ATotalFunctionExpression(SetExpression):
    pass

class APartialInjectionExpression(SetExpression):
    pass

class ATotalInjectionExpression(SetExpression):
    pass

class APartialSurjectionExpression(SetExpression):
    pass

class ATotalSurjectionExpression(SetExpression):
    pass

class ATotalBijectionExpression(SetExpression):
    pass


class APartialBijectionExpression(SetExpression):
    pass

# e.g. f(x) f~(x) proj1(S,T)(x) (x,y)(x) {(x,y)}(x) {(x|->y)}(x)
class AFunctionExpression(Expression):
    def __init__(self, childNum):
        self.childNum = int(childNum)
        self.children = []

class AEmptySequenceExpression(SetExpression):
    pass

class ASeqExpression(SetExpression):
    pass

class ASeq1Expression(SetExpression):
    pass

class AIseqExpression(SetExpression):
    pass

class AIseq1Expression(SetExpression):
    pass

class APermExpression(SetExpression):
    pass

class AConcatExpression(SetExpression):
    pass

class AInsertFrontExpression(SetExpression):
    pass

class AInsertTailExpression(SetExpression):
    pass

class ASequenceExtensionExpression(SetExpression):
    def __init__(self, childNum):
        self.childNum = int(childNum)
        self.children = []

class ASizeExpression(IntegerExpression):
    pass

class ARevExpression(SetExpression):
    pass

class ARestrictFrontExpression(SetExpression):
    pass

class ARestrictTailExpression(SetExpression):
    pass

class AGeneralConcatExpression(SetExpression):
    pass

class AFirstExpression(Expression):
    pass

class ALastExpression(Expression):
    pass

class ATailExpression(SetExpression):
    pass

class AFrontExpression(SetExpression):
    pass

class AIntervalExpression(SetExpression):
    pass

class AGeneralSumExpression(IntegerExpression):
    def __init__(self, childNum):
        self.childNum = int(childNum)
        self.children = []

class AGeneralProductExpression(IntegerExpression):
    def __init__(self, childNum):
        self.childNum = int(childNum)
        self.children = []

class ANatSetExpression(SetExpression):
    pass

class ANaturalSetExpression(SetExpression):
    pass

class ANatural1SetExpression(SetExpression):
    pass

class ANat1SetExpression(SetExpression):
    pass

class AIntegerSetExpression(SetExpression):
    pass

class AIntSetExpression(SetExpression):
    pass

class ALambdaExpression(SetExpression):
    def __init__(self, childNum):
        self.childNum = int(childNum)
        self.children = []
        
class AMinIntExpression(IntegerExpression):
    pass

class AMaxIntExpression(IntegerExpression):
    pass

class APredecessorExpression(IntegerExpression):
    pass

class ASuccessorExpression(IntegerExpression):
    pass

class AQuantifiedIntersectionExpression(SetExpression):
    def __init__(self, childNum, idNum):
        self.childNum = int(childNum)
        self.idNum = int(idNum)
        self.children = []

class AQuantifiedUnionExpression(SetExpression):
    def __init__(self, childNum, idNum):
        self.childNum = int(childNum)
        self.idNum = int(idNum)
        self.children = []

class ADefinitionPredicate(Predicate):
    def __init__(self, childNum, idName):
        self.childNum = int(childNum)
        self.idName = idName
        self.children = []

# old parser: APredicateDefinition
class APredicateDefinitionDefinition(Predicate):
    def __init__(self, childNum, idName, paraNum):
        self.childNum = int(childNum)
        self.idName = idName
        self.paraNum = int(paraNum)
        self.children = []

class AComprehensionSetExpression(SetExpression):
    def __init__(self, childNum):
        self.childNum = int(childNum)
        self.children = []


# old parser: AExistentialQuantificationPredicate 
class AExistsPredicate(Predicate):
    def __init__(self, childNum):
        self.childNum = int(childNum)
        self.children = []

# old parser: AUniversalQuantificationPredicate 
class AForallPredicate(Predicate):
    def __init__(self, childNum):
        self.childNum = int(childNum)
        self.children = []

# old parser: ABelongPredicate 
class AMemberPredicate(Predicate):
    pass

# old parser: ANotBelongPredicate 
class ANotMemberPredicate(Predicate):
    pass

# old parser: AIncludePredicate
class ASubsetPredicate(Predicate):
    pass

# old parser: ANotIncludePredicate
class ANotSubsetPredicate(Predicate):
    pass

# old parser: AIncludeStrictlyPredicate
class ASubsetStrictPredicate(Predicate):
    pass

# old parser: ANotIncludeStrictlyPredicate
class ANotSubsetStrictPredicate(Predicate):
    pass

class ANegationPredicate(Predicate):
    pass

class AGreaterPredicate(Predicate):
    pass

class AGreaterEqualPredicate(Predicate):
    pass

class AEquivalencePredicate(Predicate):
    pass

class AEqualPredicate(Predicate):
    pass

# old parser: AUnequalPredicate 
class ANotEqualPredicate(Predicate):
    pass

class ALessPredicate(Predicate):
    pass

class ALessEqualPredicate(Predicate):
    pass

class AConjunctPredicate(Predicate):
    pass

class ADisjunctPredicate(Predicate):
    pass

class AImplicationPredicate(Predicate):
    pass

class AOpSubstitution(Substitution):
    def __init__(self, childNum, idName, parameter_Num):
        self.childNum = int(childNum)
        self.idName = idName
        self.parameter_Num = int(parameter_Num)
        self.children = []

# old parser: AOpWithReturnSubstitution 
class AOperationCallSubstitution(Substitution):
    def __init__(self, childNum, idName, return_Num, parameter_Num):
        self.childNum = int(childNum)
        self.idName = idName
        self.return_Num = int(return_Num)
        self.parameter_Num = int(parameter_Num)
        self.children = []

class AAssignSubstitution(Substitution):
    def __init__(self, childNum, lhs_size, rhs_size):
        self.childNum = int(childNum)
        self.lhs_size = int(lhs_size)
        self.rhs_size = int(rhs_size)
        self.children = []

class ASequenceSubstitution(Substitution):
    pass

class AParallelSubstitution(Substitution):
    pass

class ABecomesSuchSubstitution(Substitution):
    def __init__(self, childNum, idNum):
        self.childNum = int(childNum)
        self.idNum = int(idNum)
        self.children = []

class ADefinitionSubstitution(Substitution):
    def __init__(self, childNum, idName):
        self.childNum = int(childNum)
        self.idName = idName
        self.children = []

#old parser: ASubstitutionDefinition
class ASubstitutionDefinitionDefinition(Substitution):
    def __init__(self, childNum, idName, paraNum):
        self.childNum = int(childNum)
        self.idName = idName
        self.paraNum = int(paraNum)
        self.children = []

class ABecomesElementOfSubstitution(Substitution):
    def __init__(self, childNum, idNum):
        self.childNum = int(childNum)
        self.idNum = int(idNum)
        self.children = []

class ABlockSubstitution(Substitution):
    def __init__(self):
        self.children = []

class AIfSubstitution(Substitution):
    def __init__(self, childNum, hasElse):
        self.childNum = int(childNum)
        self.hasElse = hasElse # String
        self.children = []

class AIfElsifSubstitution(Substitution):
    def __init__(self):
        self.children = []

class APreconditionSubstitution(Substitution):
    def __init__(self):
        self.children = []

class AAssertionSubstitution(Substitution):
    def __init__(self):
        self.children = []

class AChoiceOrSubstitution(Substitution):
    def __init__(self):
        self.children = []

class AChoiceSubstitution(Substitution):
    pass

class ASelectWhenSubstitution(Substitution):
    def __init__(self):
        self.children = []

class ASelectSubstitution(Substitution):
    def __init__(self, childNum, hasElse):
        self.childNum = int(childNum)
        self.hasElse = hasElse # TODO: String
        self.children = []

class ACaseSubstitution(Substitution):
    def __init__(self, childNum, expNum, hasElse):
        self.childNum = int(childNum)
        self.expNum = int(expNum)
        self.hasElse = hasElse # TODO: String
        self.children = []

class ACaseOrSubstitution(Substitution):
    def __init__(self, childNum, expNum):
        self.childNum = int(childNum)
        self.expNum = int(expNum)
        self.children = []

class AVarSubstitution(Substitution):
    def __init__(self, childNum, idNum):
        self.childNum = int(childNum)
        self.idNum = int(idNum)
        self.children = []

class AAnySubstitution(Substitution):
    def __init__(self, childNum, idNum):
        self.childNum = int(childNum)
        self.idNum = int(idNum)
        self.children = []

class ALetSubstitution(Substitution):
    def __init__(self, childNum, idNum):
        self.childNum = int(childNum)
        self.idNum = int(idNum)
        self.children = []

class ASkipSubstitution(Substitution):
    def __init__(self):
        self.children = [] # no childNum

class AWhileSubstitution(Substitution):
    pass
    
class ARecEntry(Node):
    pass

class AStructExpression(Expression):
    def __init__(self, childNum):
        self.childNum = int(childNum)
        self.children = []

class ARecExpression(Expression):
    def __init__(self, childNum):
        self.childNum = int(childNum)
        self.children = []

class ARecordFieldExpression(Expression):
    pass

class APrimedIdentifierExpression(Expression):
    def __init__(self, childNum, grade):
        self.childNum = int(childNum)
        self.grade = int(grade)
        self.children = []

class AStringSetExpression(SetExpression):
    pass

class ASetSubtractionExpression(SetExpression):
    pass

class ATransRelationExpression(SetExpression):
    pass

class ATransFunctionExpression(SetExpression):
    pass

class AStringExpression(StringExpression):
    def __init__(self, string):
        self.string = string

class AIdentifierExpression(Expression):
    def __init__(self, idName):
        self.idName = idName
        #self.enum_hint = None

class AIntegerExpression(IntegerExpression):
    def __init__(self, intValue):
        self.intValue = intValue

class AFileDefinitionDefinition(Node):
    def __init__(self, idName):
        self.idName = idName  


# Hook-node, not generated by AST parser but include by definition-handler
class AExternalFunctionExpression(Expression):
    def __init__(self, fName, type, pyb_impl):
        import types
        assert isinstance(pyb_impl, types.FunctionType)
        self.fName = fName
        self.type_node = type
        self.pyb_impl = pyb_impl # a python-callable 