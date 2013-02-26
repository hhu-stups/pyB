# -*- coding: utf-8 -*-
# This classes are used to map Java-AST Nodes to Python-AST Nodes (Objects)
# FIXME: A Parsing via "exec <String>" is not RPythong. 
# Write a JSON-parser to avoid the string-eval

class Node():
    def __init__(self):
        self.children = []

# Baseclasses Clause, Predicate, Expression and Substitution are used for assertions
# inside the interpreter. (node classification )
class Predicate(Node):
    pass

class Expression(Node):
    pass

class Clause(Node):
    pass

class Substitution(Node):
    pass

class AMachineHeader(Node):
    pass

class AAbstractMachineParseUnit(Node):
    pass

class APredicateParseUnit(Node):
    pass

class AExpressionParseUnit(Node):
    pass

class AOperation(Node):
    pass

class AEnumeratedSet(Node):
    pass

class ADeferredSet(Node):
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

class AConstantsMachineClause(Clause):
    pass

class AVariablesMachineClause(Clause):
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

class APowerOfExpression(Expression):
    pass

class AUnaryExpression(Expression):
    pass

class AConvertBoolExpression(Expression):
    pass

class AExpressionDefinition(Expression):
    pass

class ADefinitionExpression(Expression):
    pass

class ABoolSetExpression(Expression):
    pass

class ATrueExpression(Expression):
    pass

class AFalseExpression(Expression):
    pass

class AMinExpression(Expression):
    pass

class AMaxExpression(Expression):
    pass

class AGeneralUnionExpression(Expression):
    pass

class AGeneralIntersectionExpression(Expression):
    pass

class AAddExpression(Expression):
    pass

class AMinusOrSetSubtractExpression(Expression):
    pass

class AMultOrCartExpression(Expression):
    pass

class ADivExpression(Expression):
    pass

class AModuloExpression(Expression):
    pass

class ACardExpression(Expression):
    pass

class AUnionExpression(Expression):
    pass

class AIntersectionExpression(Expression):
    pass

class AEmptySetExpression(Expression):
    pass

class ASetExtensionExpression(Expression):
    pass

class ACoupleExpression(Expression):
    pass

class APowSubsetExpression(Expression):
    pass

class APow1SubsetExpression(Expression):
    pass

class ARelationsExpression(Expression):
    pass

class ADomainExpression(Expression):
    pass

class ARangeExpression(Expression):
    pass

class ACompositionExpression(Expression):
    pass

class AIdentityExpression(Expression):
    pass

class AIterationExpression(Expression):
    pass

class AReflexiveClosureExpression(Expression):
    pass

class AClosureExpression(Expression):
    pass

class ADomainRestrictionExpression(Expression):
    pass

class ADomainSubtractionExpression(Expression):
    pass

class ARangeRestrictionExpression(Expression):
    pass

class ARangeSubtractionExpression(Expression):
    pass

class AReverseExpression(Expression):
    pass

class AImageExpression(Expression):
    pass

class AOverwriteExpression(Expression):
    pass

class ADirectProductExpression(Expression):
    pass

class AFirstProjectionExpression(Expression):
    pass

class ASecondProjectionExpression(Expression):
    pass

class AParallelProductExpression(Expression):
    pass

class APartialFunctionExpression(Expression):
    pass

class ATotalFunctionExpression(Expression):
    pass

class APartialInjectionExpression(Expression):
    pass

class ATotalInjectionExpression(Expression):
    pass

class APartialSurjectionExpression(Expression):
    pass

class ATotalSurjectionExpression(Expression):
    pass

class ATotalBijectionExpression(Expression):
    pass


class APartialBijectionExpression(Expression):
    pass


class AFunctionExpression(Expression):
    pass

class AEmptySequenceExpression(Expression):
    pass

class ASeqExpression(Expression):
    pass

class ASeq1Expression(Expression):
    pass

class AIseqExpression(Expression):
    pass

class AIseq1Expression(Expression):
    pass

class APermExpression(Expression):
    pass

class AConcatExpression(Expression):
    pass

class AInsertFrontExpression(Expression):
    pass

class AInsertTailExpression(Expression):
    pass

class ASequenceExtensionExpression(Expression):
    pass

class ASizeExpression(Expression):
    pass

class ARevExpression(Expression):
    pass

class ARestrictFrontExpression(Expression):
    pass

class ARestrictTailExpression(Expression):
    pass

class AGeneralConcatExpression(Expression):
    pass

class AFirstExpression(Expression):
    pass

class ALastExpression(Expression):
    pass

class ATailExpression(Expression):
    pass

class AFrontExpression(Expression):
    pass

class AIntervalExpression(Expression):
    pass

class AGeneralSumExpression(Expression):
    pass

class AGeneralProductExpression(Expression):
    pass

class ANatSetExpression(Expression):
    pass

class ANaturalSetExpression(Expression):
    pass

class ANatural1SetExpression(Expression):
    pass

class ANat1SetExpression(Expression):
    pass

class AIntegerSetExpression(Expression):
    pass

class AIntSetExpression(Expression):
    pass

class ALambdaExpression(Expression):
    pass

class AMinIntExpression(Expression):
    pass

class AMaxIntExpression(Expression):
    pass

class APredecessorExpression(Expression):
    pass

class ASuccessorExpression(Expression):
    pass

class AQuantifiedIntersectionExpression(Expression):
    pass

class AQuantifiedUnionExpression(Expression):
    pass

class ADefinitionPredicate(Predicate):
    pass

class APredicateDefinition(Predicate):
    pass

class AComprehensionSetExpression(Predicate):
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

class AStringSetExpression(Expression):
    pass

class ASetSubtractionExpression(Expression):
    pass

class ATransRelationExpression(Expression):
    pass

class ATransFunctionExpression(Expression):
    pass

class AStringExpression(Expression):
    def __init__(self, string):
        self.string = string

class AIdentifierExpression(Expression):
    def __init__(self, idName):
        self.idName = idName
        self.enum_hint = None

class AIntegerExpression(Expression):
    def __init__(self, intValue):
        self.intValue = intValue

# Hook-node, not generated by AST parser
class AExternalFunctionExpression(Expression):
    def __init__(self, fName, pyb_type, pyb_impl):
        self.fName = fName
        self.pyb_type = pyb_type
        self.pyb_impl = pyb_impl # a callable 