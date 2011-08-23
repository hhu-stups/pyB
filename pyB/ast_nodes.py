# -*- coding: utf-8 -*-

class Node():
    def __init__(self):
        self.children = []

class Predicate(Node):
    pass

class Expression(Node):
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

class AIdentifierExpression(Expression):
    def __init__(self, idName):
        self.idName = idName

class AIntegerExpression(Expression):
    def __init__(self, intValue):
        self.intValue = intValue