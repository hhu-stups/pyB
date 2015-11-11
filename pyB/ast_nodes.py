# -*- coding: utf-8 -*-
# This classes are used to map Java-AST Nodes to Python-AST Nodes (Objects)

# TODO: AMachineMachineVariant
# TODO: use metaprograming at import time to generates clone and _same_class methods

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

    def _same_class_(self, other):
        return isinstance(other, AAbstractMachineParseUnit)


class APredicateParseUnit(ParseUnit):
    def clone(self):
        return APredicateParseUnit()

    def _same_class_(self, other):
        return isinstance(other, APredicateParseUnit)        


class AExpressionParseUnit(ParseUnit):
    def clone(self):
        return AExpressionParseUnit()

    def _same_class_(self, other):
        return isinstance(other, AExpressionParseUnit)          

        
class ADefinitionFileParseUnit(ParseUnit):
    def clone(self):
        return ADefinitionFileParseUnit()

    def _same_class_(self, other):
        return isinstance(other, ADefinitionFileParseUnit)          

            
class AOperation(Node):
    def __init__(self, childNum, opName, return_Num, parameter_Num):
        self.childNum = int(childNum)
        self.opName = opName
        self.return_Num = int(return_Num)
        self.parameter_Num = int(parameter_Num)
        self.children = []

    def clone(self):
        return AOperation(str(self.childNum), self.opName, str(self.return_Num), str(self.parameter_Num))

    def _same_class_(self, other):
        return isinstance(other, AOperation)
        
# old parser: AEnumeratedSet
class AEnumeratedSetSet(Node):
    def __init__(self, childNum, idName):
        assert isinstance(idName, str)
        self.childNum = int(childNum)
        self.idName = idName
        self.children = []

    def clone(self):
        return AEnumeratedSetSet(str(self.childNum), self.idName)

    def _same_class_(self, other):
        return isinstance(other, AEnumeratedSetSet)


# old parser: ADeferredSet
class ADeferredSetSet(Node):
    def __init__(self, idName):
        assert isinstance(idName, str)
        self.idName = idName
        self.children = []
    
    def clone(self):
        return ADeferredSetSet(self.idName)

    def _same_class_(self, other):
        return isinstance(other, ADeferredSetSet)


class AMachineHeader(Node):
    def __init__(self, childNum, idName):
        self.childNum = int(childNum)
        self.idName = idName
        self.children = []

    def clone(self):
        return AMachineHeader(str(self.childNum), self.idName)

    def _same_class_(self, other):
        return isinstance(other, AMachineHeader)

        
class AMachineReference(Node):
    def __init__(self, childNum, idName):
        self.childNum = int(childNum)
        self.idName = idName
        self.children = []

    def clone(self):
        return AMachineReference(str(self.childNum), self.idName)

    def _same_class_(self, other):
        return isinstance(other, AMachineReference)

        
class ASeesMachineClause(Clause):
    def clone(self):
        return ASeesMachineClause(self.childNum)

    def _same_class_(self, other):
        return isinstance(other, ASeesMachineClause)
     
        
class AUsesMachineClause(Clause):
    def clone(self):
        return AUsesMachineClause(self.childNum)

    def _same_class_(self, other):
        return isinstance(other, AUsesMachineClause)
        

class AExtendsMachineClause(Clause):
    def clone(self):
        return AExtendsMachineClause(self.childNum)

    def _same_class_(self, other):
        return isinstance(other, AExtendsMachineClause)

        
class APromotesMachineClause(Clause):
    def clone(self):
        return APromotesMachineClause(self.childNum)

    def _same_class_(self, other):
        return isinstance(other, APromotesMachineClause)
 
        
class AIncludesMachineClause(Clause):
    def clone(self):
        return AIncludesMachineClause(self.childNum)

    def _same_class_(self, other):
        return isinstance(other, AIncludesMachineClause)


class AConstraintsMachineClause(Clause):
    def __init__(self):
        self.children = []
    
    def clone(self):
        return AConstraintsMachineClause()

    def _same_class_(self, other):
        return isinstance(other, AConstraintsMachineClause)


# CONCRETE_CONSTANTS and CONSTANTS-clause
class AConstantsMachineClause(Clause):
    def clone(self):
        return AConstantsMachineClause(self.childNum)

    def _same_class_(self, other):
        return isinstance(other, AConstantsMachineClause)
        
# ABSTRACT_VARIABLES and VARIABLES-clause
class AVariablesMachineClause(Clause):
    def clone(self):
        return AVariablesMachineClause(self.childNum)

    def _same_class_(self, other):
        return isinstance(other, AVariablesMachineClause)
        
            
# CONCRETE_VARIABLES-clause
class AConcreteVariablesMachineClause(Clause):
    def clone(self):
        return AConcreteVariablesMachineClause(self.childNum)

    def _same_class_(self, other):
        return isinstance(other, AConcreteVariablesMachineClause)
 
        
# ABSTRACT_CONSTANTS-clause
class AAbstractConstantsMachineClause(Clause):
    def clone(self):
        return AAbstractConstantsMachineClause(self.childNum)

    def _same_class_(self, other):
        return isinstance(other, AAbstractConstantsMachineClause)

        
class AInvariantMachineClause(Clause):
    def __init__(self):
        self.children = []

    def clone(self):
        return AInvariantMachineClause()

    def _same_class_(self, other):
        return isinstance(other, AInvariantMachineClause)

                
class AInitialisationMachineClause(Clause):
    def __init__(self):
        self.children = []

    def clone(self):
        return AInitialisationMachineClause()

    def _same_class_(self, other):
        return isinstance(other, AInitialisationMachineClause)
        
                
class APropertiesMachineClause(Clause):
    def __init__(self):
        self.children = []

    def clone(self):
        return APropertiesMachineClause()

    def _same_class_(self, other):
        return isinstance(other, APropertiesMachineClause)

                
class AAssertionsMachineClause(Clause):
    def clone(self):
        return AAssertionsMachineClause(self.childNum)

    def _same_class_(self, other):
        return isinstance(other, AAssertionsMachineClause)
        
        
class ASetsMachineClause(Clause):
    def clone(self):
        return ASetsMachineClause(self.childNum)

    def _same_class_(self, other):
        return isinstance(other, ASetsMachineClause)
 
        
class ADefinitionsMachineClause(Clause):
    def clone(self):
        return ADefinitionsMachineClause(self.childNum)

    def _same_class_(self, other):
        return isinstance(other, ADefinitionsMachineClause)

        
class AOperationsMachineClause(Clause):
    def clone(self):
        return AOperationsMachineClause(self.childNum)

    def _same_class_(self, other):
        return isinstance(other, AOperationsMachineClause)
        
        
class APowerOfExpression(IntegerExpression):
    def clone(self):
        return APowerOfExpression()

    def _same_class_(self, other):
        return isinstance(other, APowerOfExpression)
        
        
# old parser: AUnaryExpression
class AUnaryMinusExpression(IntegerExpression):
    def clone(self):
        return AUnaryMinusExpression()

    def _same_class_(self, other):
        return isinstance(other, AUnaryMinusExpression)
        
class AConvertBoolExpression(Expression):
    def clone(self):
        return AConvertBoolExpression()

    def _same_class_(self, other):
        return isinstance(other, AConvertBoolExpression)
        
        
# old parser: AExpressionDefinition
class AExpressionDefinitionDefinition(Expression):
    def __init__(self, childNum, idName, paraNum):
        self.childNum = int(childNum)
        self.idName = idName
        self.paraNum = int(paraNum)
        self.children = []
        
    def clone(self):
        return AExpressionDefinitionDefinition(str(self.childNum), self.idName, str(self.paraNum))

    def _same_class_(self, other):
        return isinstance(other, AExpressionDefinitionDefinition)
        
        
class ADefinitionExpression(Expression):
    def __init__(self, childNum, idName):
        self.childNum = int(childNum)
        self.idName = idName
        self.children = []

    def clone(self):
        return ADefinitionExpression(str(self.childNum), self.idName)

    def _same_class_(self, other):
        return isinstance(other, ADefinitionExpression)
        
                
class ABoolSetExpression(SetExpression):
    def clone(self):
        return ABoolSetExpression()

    def _same_class_(self, other):
        return isinstance(other, ABoolSetExpression)

        
# old parser: ATrueExpression
class ABooleanTrueExpression(Expression):
    def clone(self):
        return ABooleanTrueExpression()

    def _same_class_(self, other):
        return isinstance(other, ABooleanTrueExpression)

        
# old parser: AFalseExpression
class ABooleanFalseExpression(Expression):
    def clone(self):
        return ABooleanFalseExpression()

    def _same_class_(self, other):
        return isinstance(other, ABooleanFalseExpression)
        
        
class AMinExpression(IntegerExpression):
    def clone(self):
        return AMinExpression()

    def _same_class_(self, other):
        return isinstance(other, AMinExpression)

        
class AMaxExpression(IntegerExpression):
    def clone(self):
        return AMaxExpression()

    def _same_class_(self, other):
        return isinstance(other, AMaxExpression)
        
        
class AGeneralUnionExpression(SetExpression):
    def clone(self):
        return AGeneralUnionExpression()

    def _same_class_(self, other):
        return isinstance(other, AGeneralUnionExpression)
        
        
class AGeneralIntersectionExpression(SetExpression):
    def clone(self):
        return AGeneralIntersectionExpression()

    def _same_class_(self, other):
        return isinstance(other, AGeneralIntersectionExpression)
        
        
class AAddExpression(IntegerExpression):
    def clone(self):
        return AAddExpression()

    def _same_class_(self, other):
        return isinstance(other, AAddExpression)
        
        
class AMinusOrSetSubtractExpression(Expression):
    def clone(self):
        return AMinusOrSetSubtractExpression()

    def _same_class_(self, other):
        return isinstance(other, AMinusOrSetSubtractExpression)
        
        
class AMultOrCartExpression(Expression):
    def clone(self):
        return AMultOrCartExpression()

    def _same_class_(self, other):
        return isinstance(other, AMultOrCartExpression)
        
        
class ADivExpression(IntegerExpression):
    def clone(self):
        return ADivExpression()

    def _same_class_(self, other):
        return isinstance(other, ADivExpression)
        
        
class AModuloExpression(IntegerExpression):
    def clone(self):
        return AModuloExpression()

    def _same_class_(self, other):
        return isinstance(other, AModuloExpression)
        
        
class ACardExpression(IntegerExpression):
    def clone(self):
        return ACardExpression()

    def _same_class_(self, other):
        return isinstance(other, ACardExpression)
        
        
class AUnionExpression(SetExpression):
    def clone(self):
        return AUnionExpression()

    def _same_class_(self, other):
        return isinstance(other, AUnionExpression)

        
class AIntersectionExpression(SetExpression):
    def clone(self):
        return AIntersectionExpression()

    def _same_class_(self, other):
        return isinstance(other, AIntersectionExpression)
        
        
class AEmptySetExpression(SetExpression):
    def clone(self):
        return AEmptySetExpression()

    def _same_class_(self, other):
        return isinstance(other, AEmptySetExpression)
        
        
class ASetExtensionExpression(SetExpression):
    def __init__(self, childNum):
        self.childNum = int(childNum)
        self.children = []
    
    def clone(self):
        return ASetExtensionExpression(self.childNum)

    def _same_class_(self, other):
        return isinstance(other, ASetExtensionExpression)
        
        
class ACoupleExpression(Expression):
    def __init__(self, childNum):
        self.childNum = int(childNum)
        self.children = []

    def clone(self):
        return ACoupleExpression(self.childNum)

    def _same_class_(self, other):
        return isinstance(other, ACoupleExpression)
        
                
class APowSubsetExpression(SetExpression):
    def clone(self):
        return APowSubsetExpression()

    def _same_class_(self, other):
        return isinstance(other, APowSubsetExpression)
        
        
class APow1SubsetExpression(SetExpression):
    def clone(self):
        return APow1SubsetExpression()

    def _same_class_(self, other):
        return isinstance(other, APow1SubsetExpression)
        
        
class ARelationsExpression(SetExpression):
    def clone(self):
        return ARelationsExpression()

    def _same_class_(self, other):
        return isinstance(other, ARelationsExpression)
        
        
class ADomainExpression(SetExpression):
    def clone(self):
        return ADomainExpression()

    def _same_class_(self, other):
        return isinstance(other, ADomainExpression)
        
        
class ARangeExpression(SetExpression):
    def clone(self):
        return ARangeExpression()

    def _same_class_(self, other):
        return isinstance(other, ARangeExpression)
        
        
class ACompositionExpression(SetExpression):
    def clone(self):
        return ACompositionExpression()

    def _same_class_(self, other):
        return isinstance(other, ACompositionExpression)
        
        
class AIdentityExpression(SetExpression):
    def clone(self):
        return AIdentityExpression()

    def _same_class_(self, other):
        return isinstance(other, AIdentityExpression)
        
        
class AIterationExpression(SetExpression):
    def clone(self):
        return AIterationExpression()

    def _same_class_(self, other):
        return isinstance(other, AIterationExpression)
        
class AReflexiveClosureExpression(SetExpression):
    def clone(self):
        return AReflexiveClosureExpression()

    def _same_class_(self, other):
        return isinstance(other, AReflexiveClosureExpression)
        
        
class AClosureExpression(SetExpression):
    def clone(self):
        return AClosureExpression()

    def _same_class_(self, other):
        return isinstance(other, AClosureExpression)

        
class ADomainRestrictionExpression(SetExpression):
    def clone(self):
        return ADomainRestrictionExpression()

    def _same_class_(self, other):
        return isinstance(other, ADomainRestrictionExpression)
        
        
class ADomainSubtractionExpression(SetExpression):
    def clone(self):
        return ADomainSubtractionExpression()

    def _same_class_(self, other):
        return isinstance(other, ADomainSubtractionExpression)
        
        
class ARangeRestrictionExpression(SetExpression):
    def clone(self):
        return ARangeRestrictionExpression()

    def _same_class_(self, other):
        return isinstance(other, ARangeRestrictionExpression)
        
        
class ARangeSubtractionExpression(SetExpression):
    def clone(self):
        return ARangeSubtractionExpression()

    def _same_class_(self, other):
        return isinstance(other, ARangeSubtractionExpression)
        
        
class AReverseExpression(SetExpression):
    def clone(self):
        return AReverseExpression()

    def _same_class_(self, other):
        return isinstance(other, AReverseExpression)
        
        
class AImageExpression(SetExpression):
    def clone(self):
        return AImageExpression()

    def _same_class_(self, other):
        return isinstance(other, AImageExpression)
        
        
class AOverwriteExpression(SetExpression):
    def clone(self):
        return AOverwriteExpression()

    def _same_class_(self, other):
        return isinstance(other, AOverwriteExpression)

        
class ADirectProductExpression(SetExpression):
    def clone(self):
        return ADirectProductExpression()

    def _same_class_(self, other):
        return isinstance(other, ADirectProductExpression)
        
        
class AFirstProjectionExpression(SetExpression):
    def clone(self):
        return AFirstProjectionExpression()

    def _same_class_(self, other):
        return isinstance(other, AFirstProjectionExpression)
        
        
class ASecondProjectionExpression(SetExpression):
    def clone(self):
        return ASecondProjectionExpression()

    def _same_class_(self, other):
        return isinstance(other, ASecondProjectionExpression)
        
        
class AParallelProductExpression(SetExpression):
    def clone(self):
        return AParallelProductExpression()

    def _same_class_(self, other):
        return isinstance(other, AParallelProductExpression)
        
        
class APartialFunctionExpression(SetExpression):
    def clone(self):
        return APartialFunctionExpression()

    def _same_class_(self, other):
        return isinstance(other, APartialFunctionExpression)
        
        
class ATotalFunctionExpression(SetExpression):
    def clone(self):
        return ATotalFunctionExpression()

    def _same_class_(self, other):
        return isinstance(other, ATotalFunctionExpression)

        
class APartialInjectionExpression(SetExpression):
    def clone(self):
        return APartialInjectionExpression()

    def _same_class_(self, other):
        return isinstance(other, APartialInjectionExpression)
        
        
class ATotalInjectionExpression(SetExpression):
    def clone(self):
        return ATotalInjectionExpression()

    def _same_class_(self, other):
        return isinstance(other, ATotalInjectionExpression)
        
        
class APartialSurjectionExpression(SetExpression):
    def clone(self):
        return APartialSurjectionExpression()

    def _same_class_(self, other):
        return isinstance(other, APartialSurjectionExpression)
   
        
class ATotalSurjectionExpression(SetExpression):
    def clone(self):
        return ATotalSurjectionExpression()

    def _same_class_(self, other):
        return isinstance(other, ATotalSurjectionExpression)
        
        
class ATotalBijectionExpression(SetExpression):
    def clone(self):
        return ATotalBijectionExpression()

    def _same_class_(self, other):
        return isinstance(other, ATotalBijectionExpression)
        

class APartialBijectionExpression(SetExpression):
    def clone(self):
        return APartialBijectionExpression()

    def _same_class_(self, other):
        return isinstance(other, APartialBijectionExpression)


# e.g. f(x) f~(x) proj1(S,T)(x) (x,y)(x) {(x,y)}(x) {(x|->y)}(x)
class AFunctionExpression(Expression):
    def __init__(self, childNum):
        self.childNum = int(childNum)
        self.children = []

    def clone(self):
        return AFunctionExpression(self.childNum)

    def _same_class_(self, other):
        return isinstance(other, AFunctionExpression)


class AEmptySequenceExpression(SetExpression):
    def clone(self):
        return AEmptySequenceExpression()

    def _same_class_(self, other):
        return isinstance(other, AEmptySequenceExpression)
        
        
class ASeqExpression(SetExpression):
    def clone(self):
        return ASeqExpression()

    def _same_class_(self, other):
        return isinstance(other, ASeqExpression)
        
        
class ASeq1Expression(SetExpression):
    def clone(self):
        return ASeq1Expression()

    def _same_class_(self, other):
        return isinstance(other, ASeq1Expression)
        
        
class AIseqExpression(SetExpression):
    def clone(self):
        return AIseqExpression()

    def _same_class_(self, other):
        return isinstance(other, AIseqExpression)
        
        
class AIseq1Expression(SetExpression):
    def clone(self):
        return AIseq1Expression()

    def _same_class_(self, other):
        return isinstance(other, AIseq1Expression)


class APermExpression(SetExpression):
    def clone(self):
        return APermExpression()

    def _same_class_(self, other):
        return isinstance(other, APermExpression)
        
        
class AConcatExpression(SetExpression):
    def clone(self):
        return AConcatExpression()

    def _same_class_(self, other):
        return isinstance(other, AConcatExpression)
        
        
class AInsertFrontExpression(SetExpression):
    def clone(self):
        return AInsertFrontExpression()

    def _same_class_(self, other):
        return isinstance(other, AInsertFrontExpression)

        
class AInsertTailExpression(SetExpression):
    def clone(self):
        return AInsertTailExpression()

    def _same_class_(self, other):
        return isinstance(other, AInsertTailExpression)
        
        
class ASequenceExtensionExpression(SetExpression):
    def __init__(self, childNum):
        self.childNum = int(childNum)
        self.children = []

    def clone(self):
        return ASequenceExtensionExpression(self.childNum)

    def _same_class_(self, other):
        return isinstance(other, ASequenceExtensionExpression)
        
                
class ASizeExpression(IntegerExpression):
    def clone(self):
        return ASizeExpression()

    def _same_class_(self, other):
        return isinstance(other, ASizeExpression)


class ARevExpression(SetExpression):
    def clone(self):
        return ARevExpression()

    def _same_class_(self, other):
        return isinstance(other, ARevExpression)


class ARestrictFrontExpression(SetExpression):
    def clone(self):
        return ARestrictFrontExpression()

    def _same_class_(self, other):
        return isinstance(other, ARestrictFrontExpression)
        
        
class ARestrictTailExpression(SetExpression):
    def clone(self):
        return ARestrictTailExpression()

    def _same_class_(self, other):
        return isinstance(other, ARestrictTailExpression)
        
        
class AGeneralConcatExpression(SetExpression):
    def clone(self):
        return AGeneralConcatExpression()

    def _same_class_(self, other):
        return isinstance(other, AGeneralConcatExpression)
        
        
class AFirstExpression(Expression):
    def clone(self):
        return AFirstExpression()

    def _same_class_(self, other):
        return isinstance(other, AFirstExpression)
        
        
class ALastExpression(Expression):
    def clone(self):
        return ALastExpression()

    def _same_class_(self, other):
        return isinstance(other, ALastExpression)
        
        
class ATailExpression(SetExpression):
    def clone(self):
        return ATailExpression()

    def _same_class_(self, other):
        return isinstance(other, ATailExpression)
        
        
class AFrontExpression(SetExpression):
    def clone(self):
        return AFrontExpression()

    def _same_class_(self, other):
        return isinstance(other, AFrontExpression)
   
        
class AIntervalExpression(SetExpression):
    def clone(self):
        return AIntervalExpression()

    def _same_class_(self, other):
        return isinstance(other, AIntervalExpression)
        
        
class AGeneralSumExpression(IntegerExpression):
    def __init__(self, childNum):
        self.childNum = int(childNum)
        self.children = []

    def clone(self):
        return AGeneralSumExpression(self.childNum)
 
    def _same_class_(self, other):
        return isinstance(other, AGeneralSumExpression)

       
class AGeneralProductExpression(IntegerExpression):
    def __init__(self, childNum):
        self.childNum = int(childNum)
        self.children = []

    def clone(self):
        return AGeneralProductExpression(self.childNum)

    def _same_class_(self, other):
        return isinstance(other, AGeneralProductExpression)
                
class ANatSetExpression(SetExpression):
    def clone(self):
        return ANatSetExpression()

    def _same_class_(self, other):
        return isinstance(other, ANatSetExpression)
        
        
class ANaturalSetExpression(SetExpression):
    def clone(self):
        return ANaturalSetExpression()

    def _same_class_(self, other):
        return isinstance(other, ANaturalSetExpression)
        
class ANatural1SetExpression(SetExpression):
    def clone(self):
        return ANatural1SetExpression()

    def _same_class_(self, other):
        return isinstance(other, ANatural1SetExpression)
        
        
class ANat1SetExpression(SetExpression):
    def clone(self):
        return ANat1SetExpression()

    def _same_class_(self, other):
        return isinstance(other, ANat1SetExpression)

        
class AIntegerSetExpression(SetExpression):
    def clone(self):
        return AIntegerSetExpression()

    def _same_class_(self, other):
        return isinstance(other, AIntegerSetExpression)
        
        
class AIntSetExpression(SetExpression):
    def clone(self):
        return AIntSetExpression()

    def _same_class_(self, other):
        return isinstance(other, AIntSetExpression)
        
        
class ALambdaExpression(SetExpression):
    def __init__(self, childNum):
        self.childNum = int(childNum)
        self.children = []

    def clone(self):
        return ALambdaExpression(self.childNum)

    def _same_class_(self, other):
        return isinstance(other, ALambdaExpression)
        
                        
class AMinIntExpression(IntegerExpression):
    def clone(self):
        return AMinIntExpression()

    def _same_class_(self, other):
        return isinstance(other, AMinIntExpression)
        
        
class AMaxIntExpression(IntegerExpression):
    def clone(self):
        return AMaxIntExpression()

    def _same_class_(self, other):
        return isinstance(other, AMaxIntExpression)
        
        
class APredecessorExpression(IntegerExpression):
    def clone(self):
        return APredecessorExpression()

    def _same_class_(self, other):
        return isinstance(other, APredecessorExpression)
        
        
class ASuccessorExpression(IntegerExpression):
    def clone(self):
        return ASuccessorExpression()

    def _same_class_(self, other):
        return isinstance(other, ASuccessorExpression)
        
        
class AQuantifiedIntersectionExpression(SetExpression):
    def __init__(self, childNum, idNum):
        self.childNum = int(childNum)
        self.idNum = int(idNum)
        self.children = []

    def clone(self):
        return AQuantifiedIntersectionExpression(str(self.childNum), str(self.idNum))

    def _same_class_(self, other):
        return isinstance(other, AQuantifiedIntersectionExpression)
      
                
class AQuantifiedUnionExpression(SetExpression):
    def __init__(self, childNum, idNum):
        self.childNum = int(childNum)
        self.idNum = int(idNum)
        self.children = []

    def clone(self):
        return AQuantifiedUnionExpression(str(self.childNum), str(self.idNum))

    def _same_class_(self, other):
        return isinstance(other, AQuantifiedUnionExpression)
        
                
class ADefinitionPredicate(Predicate):
    def __init__(self, childNum, idName):
        self.childNum = int(childNum)
        self.idName = idName
        self.children = []

    def clone(self):
        return ADefinitionPredicate(str(self.childNum), self.idName)

    def _same_class_(self, other):
        return isinstance(other, ADefinitionPredicate)
        
                
# old parser: APredicateDefinition
class APredicateDefinitionDefinition(Predicate):
    def __init__(self, childNum, idName, paraNum):
        self.childNum = int(childNum)
        self.idName = idName
        self.paraNum = int(paraNum)
        self.children = []

    def clone(self):
        return APredicateDefinitionDefinition(str(self.childNum), self.idName, str(self.paraNum))

    def _same_class_(self, other):
        return isinstance(other, APredicateDefinitionDefinition)
        
                
class AComprehensionSetExpression(SetExpression):
    def __init__(self, childNum):
        self.childNum = int(childNum)
        self.children = []

    def clone(self):
        return AComprehensionSetExpression(self.childNum)

    def _same_class_(self, other):
        return isinstance(other, AComprehensionSetExpression)
        
        
# old parser: AExistentialQuantificationPredicate 
class AExistsPredicate(Predicate):
    def __init__(self, childNum):
        self.childNum = int(childNum)
        self.children = []

    def clone(self):
        return AExistsPredicate(self.childNum)

    def _same_class_(self, other):
        return isinstance(other, AExistsPredicate)
        
                
# old parser: AUniversalQuantificationPredicate 
class AForallPredicate(Predicate):
    def __init__(self, childNum):
        self.childNum = int(childNum)
        self.children = []

    def clone(self):
        return AForallPredicate(self.childNum)
    
    def _same_class_(self, other):
        return isinstance(other, AForallPredicate)
        
                
# old parser: ABelongPredicate 
class AMemberPredicate(Predicate):
    def clone(self):
        return AMemberPredicate()

    def _same_class_(self, other):
        return isinstance(other, AMemberPredicate)
       
        
# old parser: ANotBelongPredicate 
class ANotMemberPredicate(Predicate):
    def clone(self):
        return ANotMemberPredicate()

    def _same_class_(self, other):
        return isinstance(other, ANotMemberPredicate)
       
        
# old parser: AIncludePredicate
class ASubsetPredicate(Predicate):
    def clone(self):
        return ASubsetPredicate()

    def _same_class_(self, other):
        return isinstance(other, ASubsetPredicate)
 
        
# old parser: ANotIncludePredicate
class ANotSubsetPredicate(Predicate):
    def clone(self):
        return ANotSubsetPredicate()

    def _same_class_(self, other):
        return isinstance(other, ANotSubsetPredicate)
        
        
# old parser: AIncludeStrictlyPredicate
class ASubsetStrictPredicate(Predicate):
    def clone(self):
        return ASubsetStrictPredicate()

    def _same_class_(self, other):
        return isinstance(other, ASubsetStrictPredicate)
        
        
# old parser: ANotIncludeStrictlyPredicate
class ANotSubsetStrictPredicate(Predicate):
    def clone(self):
        return ANotSubsetStrictPredicate()

    def _same_class_(self, other):
        return isinstance(other, ANotSubsetStrictPredicate)
        
        
class ANegationPredicate(Predicate):
    def clone(self):
        return ANegationPredicate()

    def _same_class_(self, other):
        return isinstance(other, ANegationPredicate)
        
        
class AGreaterPredicate(Predicate):
    def clone(self):
        return AGreaterPredicate()

    def _same_class_(self, other):
        return isinstance(other, AGreaterPredicate)
        
        
class AGreaterEqualPredicate(Predicate):
    def clone(self):
        return AGreaterEqualPredicate()

    def _same_class_(self, other):
        return isinstance(other, AGreaterEqualPredicate)
        
        
class AEquivalencePredicate(Predicate):
    def clone(self):
        return AEquivalencePredicate()

    def _same_class_(self, other):
        return isinstance(other, AEquivalencePredicate)
        
        
class AEqualPredicate(Predicate):
    def clone(self):
        return AEqualPredicate()

    def _same_class_(self, other):
        return isinstance(other, AEqualPredicate)
        
        
# old parser: AUnequalPredicate 
class ANotEqualPredicate(Predicate):
    def clone(self):
        return ANotEqualPredicate()

    def _same_class_(self, other):
        return isinstance(other, ANotEqualPredicate)
        
        
class ALessPredicate(Predicate):
    def clone(self):
        return ALessPredicate()

    def _same_class_(self, other):
        return isinstance(other, ALessPredicate)
        
        
class ALessEqualPredicate(Predicate):
    def clone(self):
        return ALessEqualPredicate()

    def _same_class_(self, other):
        return isinstance(other, ALessEqualPredicate)
        
        
class AConjunctPredicate(Predicate):
    def clone(self):
        return AConjunctPredicate()

    def _same_class_(self, other):
        return isinstance(other, AConjunctPredicate)
        
        
class ADisjunctPredicate(Predicate):
    def clone(self):
        return ADisjunctPredicate()

    def _same_class_(self, other):
        return isinstance(other, ADisjunctPredicate)
        
        
class AImplicationPredicate(Predicate):
    def clone(self):
        return AImplicationPredicate()

    def _same_class_(self, other):
        return isinstance(other, AImplicationPredicate)
        
        
class AOpSubstitution(Substitution):
    def __init__(self, childNum, idName, parameter_Num):
        self.childNum = int(childNum)
        self.idName = idName
        self.parameter_Num = int(parameter_Num)
        self.children = []

    def clone(self):
        return AOpSubstitution(str(self.childNum), self.idName, str(self.parameter_Num))

    def _same_class_(self, other):
        return isinstance(other, AOpSubstitution)
        
                
# old parser: AOpWithReturnSubstitution 
class AOperationCallSubstitution(Substitution):
    def __init__(self, childNum, idName, return_Num, parameter_Num):
        self.childNum = int(childNum)
        self.idName = idName
        self.return_Num = int(return_Num)
        self.parameter_Num = int(parameter_Num)
        self.children = []

    def clone(self):
        return AOperationCallSubstitution(str(self.childNum), self.idName, str(self.return_Num), str(self.parameter_Num))

    def _same_class_(self, other):
        return isinstance(other, AOperationCallSubstitution) 
 
        
class AAssignSubstitution(Substitution):
    def __init__(self, childNum, lhs_size, rhs_size):
        self.childNum = int(childNum)
        self.lhs_size = int(lhs_size)
        self.rhs_size = int(rhs_size)
        self.children = []

    def clone(self):
        return AAssignSubstitution(str(self.childNum), str(self.lhs_size), str(self.rhs_size))

    def _same_class_(self, other):
        return isinstance(other, AAssignSubstitution) 
        
                
class ASequenceSubstitution(Substitution):
    def clone(self):
        return ASequenceSubstitution(self.childNum)

    def _same_class_(self, other):
        return isinstance(other, ASequenceSubstitution) 


class AParallelSubstitution(Substitution):
    def clone(self):
        return AParallelSubstitution(self.childNum)

    def _same_class_(self, other):
        return isinstance(other, AParallelSubstitution) 
        
        
class ABecomesSuchSubstitution(Substitution):
    def __init__(self, childNum, idNum):
        self.childNum = int(childNum)
        self.idNum = int(idNum)
        self.children = []

    def clone(self):
        return ABecomesSuchSubstitution(str(self.childNum), str(self.idNum))

    def _same_class_(self, other):
        return isinstance(other, ABecomesSuchSubstitution)
        
                
class ADefinitionSubstitution(Substitution):
    def __init__(self, childNum, idName):
        self.childNum = int(childNum)
        self.idName = idName
        self.children = []

    def clone(self):
        return ADefinitionSubstitution(str(self.childNum), self.idName)

    def _same_class_(self, other):
        return isinstance(other, ADefinitionSubstitution)
        
                
#old parser: ASubstitutionDefinition
class ASubstitutionDefinitionDefinition(Substitution):
    def __init__(self, childNum, idName, paraNum):
        self.childNum = int(childNum)
        self.idName = idName
        self.paraNum = int(paraNum)
        self.children = []

    def clone(self):
        return ASubstitutionDefinitionDefinition(str(self.childNum), self.idName, str(self.paraNum))

    def _same_class_(self, other):
        return isinstance(other, ASubstitutionDefinitionDefinition)
        
                
class ABecomesElementOfSubstitution(Substitution):
    def __init__(self, childNum, idNum):
        self.childNum = int(childNum)
        self.idNum = int(idNum)
        self.children = []

    def clone(self):
        return ABecomesElementOfSubstitution(str(self.childNum), str(self.idNum))

    def _same_class_(self, other):
        return isinstance(other, ABecomesElementOfSubstitution)
        
                
class ABlockSubstitution(Substitution):
    def __init__(self):
        self.children = []

    def clone(self):
        return ABlockSubstitution()

    def _same_class_(self, other):
        return isinstance(other, ABlockSubstitution)

                
class AIfSubstitution(Substitution):
    def __init__(self, childNum, hasElse):
        self.childNum = int(childNum)
        self.hasElse = hasElse # String
        self.children = []

    def clone(self):
        return AIfSubstitution(str(self.childNum), self.hasElse)

    def _same_class_(self, other):
        return isinstance(other, AIfSubstitution)
        
                
class AIfElsifSubstitution(Substitution):
    def __init__(self):
        self.children = []

    def clone(self):
        return AIfElsifSubstitution()

    def _same_class_(self, other):
        return isinstance(other, AIfElsifSubstitution)
        
                
class APreconditionSubstitution(Substitution):
    def __init__(self):
        self.children = []

    def clone(self):
        return APreconditionSubstitution()

    def _same_class_(self, other):
        return isinstance(other, APreconditionSubstitution)
        
                
class AAssertionSubstitution(Substitution):
    def __init__(self):
        self.children = []

    def clone(self):
        return AAssertionSubstitution()

    def _same_class_(self, other):
        return isinstance(other, AAssertionSubstitution)
        
                
class AChoiceOrSubstitution(Substitution):
    def __init__(self):
        self.children = []

    def clone(self):
        return AChoiceOrSubstitution()

    def _same_class_(self, other):
        return isinstance(other, AChoiceOrSubstitution)
        
        
class AChoiceSubstitution(Substitution):
    def clone(self):
        return AChoiceSubstitution(self.childNum)

    def _same_class_(self, other):
        return isinstance(other, AChoiceSubstitution)
        
        
class ASelectWhenSubstitution(Substitution):
    def __init__(self):
        self.children = []

    def clone(self):
        return ASelectWhenSubstitution()

    def _same_class_(self, other):
        return isinstance(other, ASelectWhenSubstitution)
  
                
class ASelectSubstitution(Substitution):
    def __init__(self, childNum, hasElse):
        self.childNum = int(childNum)
        self.hasElse = hasElse # TODO: String
        self.children = []

    def clone(self):
        return ASelectSubstitution(str(self.childNum), self.hasElse)
 
    def _same_class_(self, other):
        return isinstance(other, ASelectSubstitution)
  
               
class ACaseSubstitution(Substitution):
    def __init__(self, childNum, expNum, hasElse):
        self.childNum = int(childNum)
        self.expNum = int(expNum)
        self.hasElse = hasElse # TODO: String
        self.children = []

    def clone(self):
        return ACaseSubstitution(str(self.childNum), str(self.expNum), self.hasElse)

    def _same_class_(self, other):
        return isinstance(other, ACaseSubstitution)
        
                
class ACaseOrSubstitution(Substitution):
    def __init__(self, childNum, expNum):
        self.childNum = int(childNum)
        self.expNum = int(expNum)
        self.children = []

    def clone(self):
        return ACaseOrSubstitution(str(self.childNum), str(self.expNum))

    def _same_class_(self, other):
        return isinstance(other, ACaseOrSubstitution)
        
                
class AVarSubstitution(Substitution):
    def __init__(self, childNum, idNum):
        self.childNum = int(childNum)
        self.idNum = int(idNum)
        self.children = []

    def clone(self):
        return AVarSubstitution(str(self.childNum), str(self.idNum))

    def _same_class_(self, other):
        return isinstance(other, AVarSubstitution)
        
                
class AAnySubstitution(Substitution):
    def __init__(self, childNum, idNum):
        self.childNum = int(childNum)
        self.idNum = int(idNum)
        self.children = []

    def clone(self):
        return AAnySubstitution(str(self.childNum), str(self.idNum))

    def _same_class_(self, other):
        return isinstance(other, AAnySubstitution)
        
                
class ALetSubstitution(Substitution):
    def __init__(self, childNum, idNum):
        self.childNum = int(childNum)
        self.idNum = int(idNum)
        self.children = []

    def clone(self):
        return ALetSubstitution(str(self.childNum), str(self.idNum))

    def _same_class_(self, other):
        return isinstance(other, ALetSubstitution)
        
                
class ASkipSubstitution(Substitution):
    def __init__(self):
        self.children = [] # no childNum

    def clone(self):
        return ASkipSubstitution()

    def _same_class_(self, other):
        return isinstance(other, ASkipSubstitution)
        
                
class AWhileSubstitution(Substitution):
    def clone(self):
        return AWhileSubstitution(self.childNum)

    def _same_class_(self, other):
        return isinstance(other, AWhileSubstitution)
        
            
class ARecEntry(Node):
    def clone(self):
        return ARecEntry()

    def _same_class_(self, other):
        return isinstance(other, ARecEntry)
        
        
class AStructExpression(Expression):
    def __init__(self, childNum):
        self.childNum = int(childNum)
        self.children = []

    def clone(self):
        return AStructExpression(self.childNum)

    def _same_class_(self, other):
        return isinstance(other, AStructExpression)
        
                
class ARecExpression(Expression):
    def __init__(self, childNum):
        self.childNum = int(childNum)
        self.children = []

    def clone(self):
        return ARecExpression(self.childNum)

    def _same_class_(self, other):
        return isinstance(other, ARecExpression)
        
                
class ARecordFieldExpression(Expression):
    def clone(self):
        return ARecordFieldExpression()

    def _same_class_(self, other):
        return isinstance(other, ARecordFieldExpression)
        
        
class APrimedIdentifierExpression(Expression):
    def __init__(self, childNum, grade):
        self.childNum = int(childNum)
        self.grade = int(grade)
        self.children = []

    def clone(self):
        return APrimedIdentifierExpression(str(self.childNum), str(self.grade))

    def _same_class_(self, other):
        return isinstance(other, APrimedIdentifierExpression)
   
                
class AStringSetExpression(SetExpression):
    def clone(self):
        return AStringSetExpression()

    def _same_class_(self, other):
        return isinstance(other, AStringSetExpression)
        
        
class ASetSubtractionExpression(SetExpression):
    def clone(self):
        return ASetSubtractionExpression()

    def _same_class_(self, other):
        return isinstance(other, ASetSubtractionExpression)
        
        
class ATransRelationExpression(SetExpression):
    def clone(self):
        return ATransRelationExpression()

    def _same_class_(self, other):
        return isinstance(other, ATransRelationExpression)
        
        
class ATransFunctionExpression(SetExpression):
    def clone(self):
        return ATransFunctionExpression()

    def _same_class_(self, other):
        return isinstance(other, ATransFunctionExpression)
        
        
class AStringExpression(StringExpression):
    def __init__(self, string):
        self.string = string
        self.children =[]
        
    def clone(self):
        return AStringExpression(self.string)

    def _same_class_(self, other):
        return isinstance(other, AStringExpression)
        
        
class AIdentifierExpression(Expression):
    def __init__(self, idName):
        assert isinstance(idName, str)
        self.idName = idName
        self.children =[]
        
    def get_idName(self):
     	assert isinstance(self.idName, str)
     	return self.idName
    
    def clone(self):
        assert isinstance(self.idName, str)
        return AIdentifierExpression(self.idName)

    def _same_class_(self, other):
        return isinstance(other, AIdentifierExpression)
        
        
class AIntegerExpression(IntegerExpression):
    def __init__(self, intValue):
        self.intValue = intValue
        self.children =[]
        
    def clone(self):
        return AIntegerExpression(self.intValue)

    def _same_class_(self, other):
        return isinstance(other, AIntegerExpression)
        
                
class AFileDefinitionDefinition(Node):
    def __init__(self, idName):
        self.idName = idName
        self.children =[]
        
    def get_name(self):
        return self.idName  
    
    def clone(self):
        return AFileDefinitionDefinition(self.idName)

    def _same_class_(self, other):
        return isinstance(other, AFileDefinitionDefinition)


# Hook-node, not generated by AST parser but include by definition-handler
class AExternalFunctionExpression(Expression):
    def __init__(self, fName, type, pyb_impl):
        import types
        # Sadly not Rpython: types.FunctionType
        #assert isinstance(pyb_impl, types.FunctionType)
        self.fName = fName
        self.type_node = type
        self.pyb_impl = pyb_impl # a python-callable 
        self.children =[]

    def clone(self):
        return AExternalFunctionExpression(self.fName, self.type_node, self.pyb_impl)

    def _same_class_(self, other):
        return isinstance(other, AExternalFunctionExpression)
    