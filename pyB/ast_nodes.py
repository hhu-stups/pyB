# -*- coding: utf-8 -*-

class Node():
    def __init__(self):
        self.children = []

class Predicate(Node):
    pass

class Expression(Node):
    pass

class Clause(Node):
    pass

class AMachineHeader(Node):
    pass

class AAbstractMachineParseUnit(Node):
    pass

class APredicateParseUnit(Node):
    pass

class AEnumeratedSet(Node):
    pass

class ADeferredSet(Node):
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

#class AMinIntExpression(Expression):
#    pass

#class AMaxIntExpression(Expression):
#    pass

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

class ANat1SetExpression(Expression):
    pass

class ALambdaExpression(Expression):
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

class AStringExpression(Expression):
    def __init__(self, string):
        self.string = string

class AIdentifierExpression(Expression):
    def __init__(self, idName):
        self.idName = idName

class AIntegerExpression(Expression):
    def __init__(self, intValue):
        self.intValue = intValue