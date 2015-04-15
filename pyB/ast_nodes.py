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
        
    def deepcopy(self):
        clone = self.clone()
        assert clone.children == []
        child_copy = []
        for child in self.children:
             child_clone = child.deepcopy()
             clone.children.append(child_clone)
        assert len(clone.children) == len(self.children)
        return clone
    
    def copy(self):
        return self.clone()

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
        
    def clone(self):
        return AAbstractMachineParseUnit(self.childNum)


class APredicateParseUnit(ParseUnit):
    def clone(self):
        return APredicateParseUnit(self.childNum)
        


class AExpressionParseUnit(ParseUnit):
    def clone(self):
        return AExpressionParseUnit(self.childNum)
        
        
class ADefinitionFileParseUnit(ParseUnit):
    def clone(self):
        return ADefinitionFileParseUnit(self.childNum)
        
            
class AOperation(Node):
    def __init__(self, childNum, opName, return_Num, parameter_Num):
        self.childNum = int(childNum)
        self.opName = opName
        self.return_Num = int(return_Num)
        self.parameter_Num = int(parameter_Num)
        self.children = []

    def clone(self):
        return AAOperation(self.childNum, self.opName, self.return_Num, self.parameter_Num)

        
# old parser: AEnumeratedSet
class AEnumeratedSetSet(Node):
    def __init__(self, childNum, idName):
        self.childNum = int(childNum)
        self.idName = idName
        self.children = []

    def clone(self):
        return AEnumeratedSetSet(self.childNum, self.idName)


# old parser: ADeferredSet
class ADeferredSetSet(Node):
    def __init__(self, idName):
        self.idName = idName
        self.children = []
    
    def clone(self):
        return ADeferredSetSet(self.idName)


class AMachineHeader(Node):
    def __init__(self, childNum, idName):
        self.childNum = int(childNum)
        self.idName = idName
        self.children = []

    def clone(self):
        return AMachineHeader(self.childNum, self.idName)

        
class AMachineReference(Node):
    def __init__(self, childNum, idName):
        self.childNum = int(childNum)
        self.idName = idName
        self.children = []

    def clone(self):
        return AMachineReference(self.childNum, self.idName)

        
class ASeesMachineClause(Clause):
    def clone(self):
        return ASeesMachineClause(self.childNum)

        
class AUsesMachineClause(Clause):
    def clone(self):
        return AUsesMachineClause(self.childNum)


class AExtendsMachineClause(Clause):
    def clone(self):
        return AExtendsMachineClause(self.childNum)

class APromotesMachineClause(Clause):
    def clone(self):
        return APromotesMachineClause(self.childNum)

class AIncludesMachineClause(Clause):
    def clone(self):
        return AIncludesMachineClause(self.childNum)


class AConstraintsMachineClause(Clause):
    def __init__(self):
        self.children = []
    
    def clone(self):
        return AConstraintsMachineClause()


# CONCRETE_CONSTANTS and CONSTANTS-clause
class AConstantsMachineClause(Clause):
    def clone(self):
        return AConstantsMachineClause(self.childNum)

# ABSTRACT_VARIABLES and VARIABLES-clause
class AVariablesMachineClause(Clause):
    def clone(self):
        return AVariablesMachineClause(self.childNum)
    
# CONCRETE_VARIABLES-clause
class AConcreteVariablesMachineClause(Clause):
    def clone(self):
        return AConcreteVariablesMachineClause(self.childNum)

# ABSTRACT_CONSTANTS-clause
class AAbstractConstantsMachineClause(Clause):
    def clone(self):
        return AAbstractConstantsMachineClause(self.childNum)

class AInvariantMachineClause(Clause):
    def __init__(self):
        self.children = []

    def clone(self):
        return AInvariantMachineClause()
        
class AInitialisationMachineClause(Clause):
    def __init__(self):
        self.children = []

    def clone(self):
        return AInitialisationMachineClause()
        
class APropertiesMachineClause(Clause):
    def __init__(self):
        self.children = []

    def clone(self):
        return APropertiesMachineClause()
        
class AAssertionsMachineClause(Clause):
    def clone(self):
        return AAssertionsMachineClause(self.childNum)

class ASetsMachineClause(Clause):
    def clone(self):
        return ASetsMachineClause(self.childNum)

class ADefinitionsMachineClause(Clause):
    def clone(self):
        return ADefinitionsMachineClause(self.childNum)

class AOperationsMachineClause(Clause):
    def clone(self):
        return AOperationsMachineClause(self.childNum)

class APowerOfExpression(IntegerExpression):
    def clone(self):
        return APowerOfExpression()

# old parser: AUnaryExpression
class AUnaryMinusExpression(IntegerExpression):
    def clone(self):
        return AUnaryMinusExpression()

class AConvertBoolExpression(Expression):
    def clone(self):
        return AConvertBoolExpression()

# old parser: AExpressionDefinition
class AExpressionDefinitionDefinition(Expression):
    def __init__(self, childNum, idName, paraNum):
        self.childNum = int(childNum)
        self.idName = idName
        self.paraNum = int(paraNum)
        self.children = []
        
    def clone(self):
        return AExpressionDefinitionDefinition(self.childNum, self.idName, self.paraNum)

class ADefinitionExpression(Expression):
    def __init__(self, childNum, idName):
        self.childNum = int(childNum)
        self.idName = idName
        self.children = []

    def clone(self):
        return ADefinitionExpression(self.childNum, self.idName)
        
class ABoolSetExpression(SetExpression):
    def clone(self):
        return ABoolSetExpression()

# old parser: ATrueExpression
class ABooleanTrueExpression(Expression):
    def clone(self):
        return ABooleanTrueExpression()

# old parser: AFalseExpression
class ABooleanFalseExpression(Expression):
    def clone(self):
        return ABooleanFalseExpression()

class AMinExpression(IntegerExpression):
    def clone(self):
        return AMinExpression()

class AMaxExpression(IntegerExpression):
    def clone(self):
        return AMaxExpression()

class AGeneralUnionExpression(SetExpression):
    def clone(self):
        return AGeneralUnionExpression()

class AGeneralIntersectionExpression(SetExpression):
    def clone(self):
        return AGeneralIntersectionExpression()

class AAddExpression(IntegerExpression):
    def clone(self):
        return AAddExpression()

class AMinusOrSetSubtractExpression(Expression):
    def clone(self):
        return AMinusOrSetSubtractExpression()

class AMultOrCartExpression(Expression):
    def clone(self):
        return AMultOrCartExpression()

class ADivExpression(IntegerExpression):
    def clone(self):
        return ADivExpression()

class AModuloExpression(IntegerExpression):
    def clone(self):
        return AModuloExpression()

class ACardExpression(IntegerExpression):
    def clone(self):
        return ACardExpression()

class AUnionExpression(SetExpression):
    def clone(self):
        return AUnionExpression()

class AIntersectionExpression(SetExpression):
    def clone(self):
        return AIntersectionExpression()

class AEmptySetExpression(SetExpression):
    def clone(self):
        return AEmptySetExpression()

class ASetExtensionExpression(SetExpression):
    def __init__(self, childNum):
        self.childNum = int(childNum)
        self.children = []
    
    def clone(self):
        return ASetExtensionExpression(self.childNum)

class ACoupleExpression(Expression):
    def __init__(self, childNum):
        self.childNum = int(childNum)
        self.children = []

    def clone(self):
        return ACoupleExpression(self.childNum)
        
class APowSubsetExpression(SetExpression):
    def clone(self):
        return APowSubsetExpression()

class APow1SubsetExpression(SetExpression):
    def clone(self):
        return APow1SubsetExpression()

class ARelationsExpression(SetExpression):
    def clone(self):
        return ARelationsExpression()

class ADomainExpression(SetExpression):
    def clone(self):
        return ADomainExpression()

class ARangeExpression(SetExpression):
    def clone(self):
        return ARangeExpression()

class ACompositionExpression(SetExpression):
    def clone(self):
        return ACompositionExpression()

class AIdentityExpression(SetExpression):
    def clone(self):
        return AIdentityExpression()

class AIterationExpression(SetExpression):
    def clone(self):
        return AIterationExpression()

class AReflexiveClosureExpression(SetExpression):
    def clone(self):
        return AReflexiveClosureExpression()

class AClosureExpression(SetExpression):
    def clone(self):
        return AClosureExpression()

class ADomainRestrictionExpression(SetExpression):
    def clone(self):
        return ADomainRestrictionExpression()

class ADomainSubtractionExpression(SetExpression):
    def clone(self):
        return ADomainSubtractionExpression()

class ARangeRestrictionExpression(SetExpression):
    def clone(self):
        return ARangeRestrictionExpression()

class ARangeSubtractionExpression(SetExpression):
    def clone(self):
        return ARangeSubtractionExpression()

class AReverseExpression(SetExpression):
    def clone(self):
        return AReverseExpression()

class AImageExpression(SetExpression):
    def clone(self):
        return AImageExpression()

class AOverwriteExpression(SetExpression):
    def clone(self):
        return AOverwriteExpression()

class ADirectProductExpression(SetExpression):
    def clone(self):
        return ADirectProductExpression()

class AFirstProjectionExpression(SetExpression):
    def clone(self):
        return AFirstProjectionExpression()

class ASecondProjectionExpression(SetExpression):
    def clone(self):
        return ASecondProjectionExpression()

class AParallelProductExpression(SetExpression):
    def clone(self):
        return AParallelProductExpression()

class APartialFunctionExpression(SetExpression):
    def clone(self):
        return APartialFunctionExpression()

class ATotalFunctionExpression(SetExpression):
    def clone(self):
        return ATotalFunctionExpression()

class APartialInjectionExpression(SetExpression):
    def clone(self):
        return APartialInjectionExpression()

class ATotalInjectionExpression(SetExpression):
    def clone(self):
        return ATotalInjectionExpression()

class APartialSurjectionExpression(SetExpression):
    def clone(self):
        return APartialSurjectionExpression()

class ATotalSurjectionExpression(SetExpression):
    def clone(self):
        return ATotalSurjectionExpression()

class ATotalBijectionExpression(SetExpression):
    def clone(self):
        return ATotalBijectionExpression()


class APartialBijectionExpression(SetExpression):
    def clone(self):
        return APartialBijectionExpression()

# e.g. f(x) f~(x) proj1(S,T)(x) (x,y)(x) {(x,y)}(x) {(x|->y)}(x)
class AFunctionExpression(Expression):
    def __init__(self, childNum):
        self.childNum = int(childNum)
        self.children = []

    def clone(self):
        return AFunctionExpression(self.childNum)

class AEmptySequenceExpression(SetExpression):
    def clone(self):
        return AEmptySequenceExpression()

class ASeqExpression(SetExpression):
    def clone(self):
        return ASeqExpression()

class ASeq1Expression(SetExpression):
    def clone(self):
        return ASeq1Expression()

class AIseqExpression(SetExpression):
    def clone(self):
        return AIseqExpression()

class AIseq1Expression(SetExpression):
    def clone(self):
        return AIseq1Expression()

class APermExpression(SetExpression):
    def clone(self):
        return APermExpression()

class AConcatExpression(SetExpression):
    def clone(self):
        return AConcatExpression()

class AInsertFrontExpression(SetExpression):
    def clone(self):
        return AInsertFrontExpression()

class AInsertTailExpression(SetExpression):
    def clone(self):
        return AInsertTailExpression()

class ASequenceExtensionExpression(SetExpression):
    def __init__(self, childNum):
        self.childNum = int(childNum)
        self.children = []

    def clone(self):
        return ASequenceExtensionExpression(self.childNum)
        
class ASizeExpression(IntegerExpression):
    def clone(self):
        return ASizeExpression()

class ARevExpression(SetExpression):
    def clone(self):
        return ARevExpression()

class ARestrictFrontExpression(SetExpression):
    def clone(self):
        return ARestrictFrontExpression()

class ARestrictTailExpression(SetExpression):
    def clone(self):
        return ARestrictTailExpression()

class AGeneralConcatExpression(SetExpression):
    def clone(self):
        return AGeneralConcatExpression()

class AFirstExpression(Expression):
    def clone(self):
        return AFirstExpression()

class ALastExpression(Expression):
    def clone(self):
        return ALastExpression()

class ATailExpression(SetExpression):
    def clone(self):
        return ATailExpression()

class AFrontExpression(SetExpression):
    def clone(self):
        return AFrontExpression()

class AIntervalExpression(SetExpression):
    def clone(self):
        return AIntervalExpression()

class AGeneralSumExpression(IntegerExpression):
    def __init__(self, childNum):
        self.childNum = int(childNum)
        self.children = []

    def clone(self):
        return AGeneralSumExpression(self.childNum)
        
class AGeneralProductExpression(IntegerExpression):
    def __init__(self, childNum):
        self.childNum = int(childNum)
        self.children = []

    def clone(self):
        return AGeneralProductExpression(self.childNum)
        
class ANatSetExpression(SetExpression):
    def clone(self):
        return ANatSetExpression()

class ANaturalSetExpression(SetExpression):
    def clone(self):
        return ANaturalSetExpression()

class ANatural1SetExpression(SetExpression):
    def clone(self):
        return ANatural1SetExpression()

class ANat1SetExpression(SetExpression):
    def clone(self):
        return ANat1SetExpression()

class AIntegerSetExpression(SetExpression):
    def clone(self):
        return AIntegerSetExpression()

class AIntSetExpression(SetExpression):
    def clone(self):
        return AIntSetExpression()

class ALambdaExpression(SetExpression):
    def __init__(self, childNum):
        self.childNum = int(childNum)
        self.children = []

    def clone(self):
        return ALambdaExpression(self.childNum)
                
class AMinIntExpression(IntegerExpression):
    def clone(self):
        return AMinIntExpression()

class AMaxIntExpression(IntegerExpression):
    def clone(self):
        return AMaxIntExpression()

class APredecessorExpression(IntegerExpression):
    def clone(self):
        return APredecessorExpression()

class ASuccessorExpression(IntegerExpression):
    def clone(self):
        return ASuccessorExpression()

class AQuantifiedIntersectionExpression(SetExpression):
    def __init__(self, childNum, idNum):
        self.childNum = int(childNum)
        self.idNum = int(idNum)
        self.children = []

    def clone(self):
        return AQuantifiedIntersectionExpression(self.childNum, self.idNum)
        
class AQuantifiedUnionExpression(SetExpression):
    def __init__(self, childNum, idNum):
        self.childNum = int(childNum)
        self.idNum = int(idNum)
        self.children = []

    def clone(self):
        return AQuantifiedUnionExpression(self.childNum, self.idNum)
        
class ADefinitionPredicate(Predicate):
    def __init__(self, childNum, idName):
        self.childNum = int(childNum)
        self.idName = idName
        self.children = []

    def clone(self):
        return ADefinitionPredicate(self.childNum, self.idNum)
        
# old parser: APredicateDefinition
class APredicateDefinitionDefinition(Predicate):
    def __init__(self, childNum, idName, paraNum):
        self.childNum = int(childNum)
        self.idName = idName
        self.paraNum = int(paraNum)
        self.children = []

    def clone(self):
        return APredicateDefinitionDefinition(self.childNum, self.idName, self.paraNum)
        
class AComprehensionSetExpression(SetExpression):
    def __init__(self, childNum):
        self.childNum = int(childNum)
        self.children = []

    def clone(self):
        return AComprehensionSetExpression(self.childNum)

# old parser: AExistentialQuantificationPredicate 
class AExistsPredicate(Predicate):
    def __init__(self, childNum):
        self.childNum = int(childNum)
        self.children = []

    def clone(self):
        return AExistsPredicate(self.childNum)
        
# old parser: AUniversalQuantificationPredicate 
class AForallPredicate(Predicate):
    def __init__(self, childNum):
        self.childNum = int(childNum)
        self.children = []

    def clone(self):
        return AForallPredicate(self.childNum)
        
# old parser: ABelongPredicate 
class AMemberPredicate(Predicate):
    def clone(self):
        return AMemberPredicate()

# old parser: ANotBelongPredicate 
class ANotMemberPredicate(Predicate):
    def clone(self):
        return ANotMemberPredicate()

# old parser: AIncludePredicate
class ASubsetPredicate(Predicate):
    def clone(self):
        return ASubsetPredicate()

# old parser: ANotIncludePredicate
class ANotSubsetPredicate(Predicate):
    def clone(self):
        return ANotSubsetPredicate()

# old parser: AIncludeStrictlyPredicate
class ASubsetStrictPredicate(Predicate):
    def clone(self):
        return ASubsetStrictPredicate()

# old parser: ANotIncludeStrictlyPredicate
class ANotSubsetStrictPredicate(Predicate):
    def clone(self):
        return ANotSubsetStrictPredicate()

class ANegationPredicate(Predicate):
    def clone(self):
        return ANegationPredicate()

class AGreaterPredicate(Predicate):
    def clone(self):
        return AGreaterPredicate()

class AGreaterEqualPredicate(Predicate):
    def clone(self):
        return AGreaterEqualPredicate()

class AEquivalencePredicate(Predicate):
    def clone(self):
        return AEquivalencePredicate()

class AEqualPredicate(Predicate):
    def clone(self):
        return AEqualPredicate()

# old parser: AUnequalPredicate 
class ANotEqualPredicate(Predicate):
    def clone(self):
        return ANotEqualPredicate()

class ALessPredicate(Predicate):
    def clone(self):
        return ALessPredicate()

class ALessEqualPredicate(Predicate):
    def clone(self):
        return ALessEqualPredicate()

class AConjunctPredicate(Predicate):
    def clone(self):
        return AConjunctPredicate()

class ADisjunctPredicate(Predicate):
    def clone(self):
        return ADisjunctPredicate()

class AImplicationPredicate(Predicate):
    def clone(self):
        return AImplicationPredicate()

class AOpSubstitution(Substitution):
    def __init__(self, childNum, idName, parameter_Num):
        self.childNum = int(childNum)
        self.idName = idName
        self.parameter_Num = int(parameter_Num)
        self.children = []

    def clone(self):
        return AOpSubstitution(self.childNum, self.idNum, self.parameter_Num)
        
# old parser: AOpWithReturnSubstitution 
class AOperationCallSubstitution(Substitution):
    def __init__(self, childNum, idName, return_Num, parameter_Num):
        self.childNum = int(childNum)
        self.idName = idName
        self.return_Num = int(return_Num)
        self.parameter_Num = int(parameter_Num)
        self.children = []

    def clone(self):
        return AOperationCallSubstitution(self.childNum, self.idNum, self.return_Num, self.parameter_Num)
        
class AAssignSubstitution(Substitution):
    def __init__(self, childNum, lhs_size, rhs_size):
        self.childNum = int(childNum)
        self.lhs_size = int(lhs_size)
        self.rhs_size = int(rhs_size)
        self.children = []

    def clone(self):
        return AAssignSubstitution(self.childNum, self.lhs_size, self.rhs_size)
        
class ASequenceSubstitution(Substitution):
    def clone(self):
        return ASequenceSubstitution(self.childNum)

class AParallelSubstitution(Substitution):
    def clone(self):
        return AParallelSubstitution(self.childNum)

class ABecomesSuchSubstitution(Substitution):
    def __init__(self, childNum, idNum):
        self.childNum = int(childNum)
        self.idNum = int(idNum)
        self.children = []

    def clone(self):
        return ABecomesSuchSubstitution(self.childNum, self.idNum)
        
class ADefinitionSubstitution(Substitution):
    def __init__(self, childNum, idName):
        self.childNum = int(childNum)
        self.idName = idName
        self.children = []

    def clone(self):
        return ADefinitionSubstitution(self.childNum, self.idName)
        
#old parser: ASubstitutionDefinition
class ASubstitutionDefinitionDefinition(Substitution):
    def __init__(self, childNum, idName, paraNum):
        self.childNum = int(childNum)
        self.idName = idName
        self.paraNum = int(paraNum)
        self.children = []

    def clone(self):
        return ASubstitutionDefinitionDefinition(self.childNum, self.idName, self.paraNum)
        
class ABecomesElementOfSubstitution(Substitution):
    def __init__(self, childNum, idNum):
        self.childNum = int(childNum)
        self.idNum = int(idNum)
        self.children = []

    def clone(self):
        return ABecomesElementOfSubstitution(self.childNum, self.idNum)
        
class ABlockSubstitution(Substitution):
    def __init__(self):
        self.children = []

    def clone(self):
        return ABlockSubstitution()
        
class AIfSubstitution(Substitution):
    def __init__(self, childNum, hasElse):
        self.childNum = int(childNum)
        self.hasElse = hasElse # String
        self.children = []

    def clone(self):
        return AIfSubstitution(self.childNum, self.hasElse)
        
class AIfElsifSubstitution(Substitution):
    def __init__(self):
        self.children = []

    def clone(self):
        return AIfElsifSubstitution()
        
class APreconditionSubstitution(Substitution):
    def __init__(self):
        self.children = []

    def clone(self):
        return APreconditionSubstitution()
        
class AAssertionSubstitution(Substitution):
    def __init__(self):
        self.children = []

    def clone(self):
        return AAssertionSubstitution()
        
class AChoiceOrSubstitution(Substitution):
    def __init__(self):
        self.children = []

    def clone(self):
        return AChoiceOrSubstitution()

class AChoiceSubstitution(Substitution):
    def clone(self):
        return AChoiceSubstitution(self.childNum)

class ASelectWhenSubstitution(Substitution):
    def __init__(self):
        self.children = []

    def clone(self):
        return ASelectWhenSubstitution()
        
class ASelectSubstitution(Substitution):
    def __init__(self, childNum, hasElse):
        self.childNum = int(childNum)
        self.hasElse = hasElse # TODO: String
        self.children = []

    def clone(self):
        return ASelectSubstitution(self.childNum, self.hasElse)
        
class ACaseSubstitution(Substitution):
    def __init__(self, childNum, expNum, hasElse):
        self.childNum = int(childNum)
        self.expNum = int(expNum)
        self.hasElse = hasElse # TODO: String
        self.children = []

    def clone(self):
        return ACaseSubstitution(self.childNum, self.expNum, self.hasElse)
        
class ACaseOrSubstitution(Substitution):
    def __init__(self, childNum, expNum):
        self.childNum = int(childNum)
        self.expNum = int(expNum)
        self.children = []

    def clone(self):
        return ACaseOrSubstitution(self.childNum, self.expNum)
        
class AVarSubstitution(Substitution):
    def __init__(self, childNum, idNum):
        self.childNum = int(childNum)
        self.idNum = int(idNum)
        self.children = []

    def clone(self):
        return AVarSubstitution(self.childNum, self.idNum)
        
class AAnySubstitution(Substitution):
    def __init__(self, childNum, idNum):
        self.childNum = int(childNum)
        self.idNum = int(idNum)
        self.children = []

    def clone(self):
        return AAnySubstitution(self.childNum, self.idNum)
        
class ALetSubstitution(Substitution):
    def __init__(self, childNum, idNum):
        self.childNum = int(childNum)
        self.idNum = int(idNum)
        self.children = []

    def clone(self):
        return ALetSubstitution(self.childNum, self.idNum)
        
class ASkipSubstitution(Substitution):
    def __init__(self):
        self.children = [] # no childNum

    def clone(self):
        return ASkipSubstitution()
        
class AWhileSubstitution(Substitution):
    def clone(self):
        return AWhileSubstitution(self.childNum)
    
class ARecEntry(Node):
    def clone(self):
        return ARecEntry()

class AStructExpression(Expression):
    def __init__(self, childNum):
        self.childNum = int(childNum)
        self.children = []

    def clone(self):
        return AStructExpression(self.childNum)
        
class ARecExpression(Expression):
    def __init__(self, childNum):
        self.childNum = int(childNum)
        self.children = []

    def clone(self):
        return ARecExpression(self.childNum)
        
class ARecordFieldExpression(Expression):
    def clone(self):
        return ARecordFieldExpression()

class APrimedIdentifierExpression(Expression):
    def __init__(self, childNum, grade):
        self.childNum = int(childNum)
        self.grade = int(grade)
        self.children = []

    def clone(self):
        return APrimedIdentifierExpression(self.childNum, self.grade)
        
class AStringSetExpression(SetExpression):
    def clone(self):
        return AStringSetExpression()

class ASetSubtractionExpression(SetExpression):
    def clone(self):
        return ASetSubtractionExpression()

class ATransRelationExpression(SetExpression):
    def clone(self):
        return ATransRelationExpression()

class ATransFunctionExpression(SetExpression):
    def clone(self):
        return ATransFunctionExpression()

class AStringExpression(StringExpression):
    def __init__(self, string):
        self.string = string
        self.children =[]
        
    def clone(self):
        return AStringExpression(self.string)

        
class AIdentifierExpression(Expression):
    def __init__(self, idName):
        self.idName = idName
        self.children =[]
    
    def clone(self):
        return AIdentifierExpression(self.idName)

        
class AIntegerExpression(IntegerExpression):
    def __init__(self, intValue):
        self.intValue = intValue
        self.children =[]
        
    def clone(self):
        return AIntegerExpression(self.intValue)

        
class AFileDefinitionDefinition(Node):
    def __init__(self, idName):
        self.idName = idName
        self.children =[]  
    
    def clone(self):
        return AFileDefinitionDefinition(self.idName)



# Hook-node, not generated by AST parser but include by definition-handler
class AExternalFunctionExpression(Expression):
    def __init__(self, fName, type, pyb_impl):
        import types
        assert isinstance(pyb_impl, types.FunctionType)
        self.fName = fName
        self.type_node = type
        self.pyb_impl = pyb_impl # a python-callable 
        self.children =[]

    def clone(self):
        return AExternalFunctionExpression(self.fName, self.type, self.pyb_impl)
    