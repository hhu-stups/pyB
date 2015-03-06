# -*- coding: utf-8 -*-
# This classes are used to map Java-AST Nodes to Python-AST Nodes (Objects)


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

class Clause(Node):
    pass

class Substitution(Node):
    pass

class ParseUnit(Node):
    pass

class AAbstractMachineParseUnit(ParseUnit):
    pass

class APredicateParseUnit(ParseUnit):
    pass

class AExpressionParseUnit(ParseUnit):
    pass

class ADefinitionFileParseUnit(ParseUnit):
    pass
    
class AOperation(Node):
    pass

class AEnumeratedSet(Node):
    pass

class ADeferredSet(Node):
    pass

class AMachineHeader(Node):
    pass

class AMachineReference(Node):
    pass

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
    pass

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
    pass

class AInitialisationMachineClause(Clause):
    pass

class APropertiesMachineClause(Clause):
    pass

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

class AUnaryExpression(IntegerExpression):
    pass

class AConvertBoolExpression(Expression):
    pass

class AExpressionDefinition(Expression):
    pass

class ADefinitionExpression(Expression):
    pass

class ABoolSetExpression(SetExpression):
    pass

class ATrueExpression(Expression):
    pass

class AFalseExpression(Expression):
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
    pass

class ACoupleExpression(Expression):
    pass

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
    pass

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
    pass

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
    pass

class AGeneralProductExpression(IntegerExpression):
    pass

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
    pass

class AMinIntExpression(IntegerExpression):
    pass

class AMaxIntExpression(IntegerExpression):
    pass

class APredecessorExpression(IntegerExpression):
    pass

class ASuccessorExpression(IntegerExpression):
    pass

class AQuantifiedIntersectionExpression(SetExpression):
    pass

class AQuantifiedUnionExpression(SetExpression):
    pass

class ADefinitionPredicate(Predicate):
    pass

class APredicateDefinition(Predicate):
    pass

class AComprehensionSetExpression(SetExpression):
    pass

class AExistentialQuantificationPredicate(Predicate):
    pass

class AUniversalQuantificationPredicate(Predicate):
    pass

class ABelongPredicate(Predicate):
    pass

class ANotBelongPredicate(Predicate):
    pass

class AIncludePredicate(Predicate):
    pass

class ANotIncludePredicate(Predicate):
    pass

class AIncludeStrictlyPredicate(Predicate):
    pass

class ANotIncludeStrictlyPredicate(Predicate):
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

class AUnequalPredicate(Predicate):
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
    pass

class AOpWithReturnSubstitution(Substitution):
    pass

class AAssignSubstitution(Substitution):
    pass

class ASequenceSubstitution(Substitution):
    pass

class AParallelSubstitution(Substitution):
    pass

class ABecomesSuchSubstitution(Substitution):
    pass

class ADefinitionSubstitution(Substitution):
    pass

class ASubstitutionDefinition(Substitution):
    pass

class ABecomesElementOfSubstitution(Substitution):
    pass

class ABlockSubstitution(Substitution):
    pass

class AIfSubstitution(Substitution):
    pass

class AIfElsifSubstitution(Substitution):
    pass

class APreconditionSubstitution(Substitution):
    pass

class AAssertionSubstitution(Substitution):
    pass

class AChoiceOrSubstitution(Substitution):
    pass

class AChoiceSubstitution(Substitution):
    pass

class ASelectWhenSubstitution(Substitution):
    pass

class ASelectSubstitution(Substitution):
    pass

class ACaseSubstitution(Substitution):
    pass

class ACaseOrSubstitution(Substitution):
    pass

class AVarSubstitution(Substitution):
    pass

class AAnySubstitution(Substitution):
    pass

class ALetSubstitution(Substitution):
    pass

class ASkipSubstitution(Substitution):
    pass

class AWhileSubstitution(Substitution):
    pass
    
class ARecEntry(Node):
    pass

class AStructExpression(Expression):
    pass

class ARecExpression(Expression):
    pass

class ARecordFieldExpression(Expression):
    pass

class APrimedIdentifierExpression(Expression):
    pass

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
        self.enum_hint = None

class AIntegerExpression(IntegerExpression):
    def __init__(self, intValue):
        self.intValue = intValue

class AFileDefinition(Node):
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