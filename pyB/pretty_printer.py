from ast_nodes import *
#TODO: Substitutions

def pretty_print(node):
# *********************
#
#        1. Predicates
#
# *********************
    if isinstance(node, AConjunctPredicate):
        string1 = pretty_print(node.children[0])
        string2 = pretty_print(node.children[1])
        return string1 +" & "+string2
    elif isinstance(node, ADisjunctPredicate):
        string1 = pretty_print(node.children[0])
        string2 = pretty_print(node.children[1])
        return string1 +" or "+ string2
    elif isinstance(node, AImplicationPredicate):
        string1 = pretty_print(node.children[0])
        string2 = pretty_print(node.children[1])
        return string1+ " => " +string2
    elif isinstance(node, AEquivalencePredicate):
        string1 = pretty_print(node.children[0])
        string2 = pretty_print(node.children[1])
        return string1 +" <=> " +string2 
    elif isinstance(node, ANegationPredicate):
        string0 = pretty_print(node.children[0])
        return "not ("+string0+")"
    elif isinstance(node, AUniversalQuantificationPredicate):
        varList = node.children[:-1]
        pred = node.children[-1]
        string = pretty_print(node.children[-1])
        out = "!("
        for i in range(len(varList)):
            out += varList[i].idName
            if i+1<len(varList):
                out += ","
        out +=").("+string+")"
        return out
    elif isinstance(node, AExistentialQuantificationPredicate):
        varList = node.children[:-1]
        pred = node.children[-1]
        string = pretty_print(node.children[-1])
        out = "#("
        for i in range(len(varList)):
            out += varList[i].idName
            if i+1<len(varList):
                out += ","
        out +=").("+string+")"
        return out      
    elif isinstance(node, AEqualPredicate):
        string1 = pretty_print(node.children[0])
        string2 = pretty_print(node.children[1])
        return string1+"="+string2
    elif isinstance(node, AUnequalPredicate):
        string1 = pretty_print(node.children[0])
        string2 = pretty_print(node.children[1])
        return string1+"/="+string2


# **************
#
#       2. Sets
#
# **************
    elif isinstance(node, ASetExtensionExpression):
        out = ""
        for child in node.children:
            out += pretty_print(child)
        return "{"+out+"}"
    elif isinstance(node, AEmptySetExpression):
        return "{}"
    elif isinstance(node, AComprehensionSetExpression):
        varList = node.children[:-1]
        pred = node.children[-1]
        out = "{"
        for i in range(len(varList)):
            out += varList[i].idName
            if i<len(varList):
                out += ","
        string = pretty_print(pred)
        out +="|"+string+"}"
        return out
    elif isinstance(node, AUnionExpression):
        string1 = pretty_print(node.children[0])
        string2 = pretty_print(node.children[1])
        return string1+"\/"+string2
    elif isinstance(node, AIntersectionExpression):
        string1 = pretty_print(node.children[0])
        string2 = pretty_print(node.children[1])
        return string1+"/\\"+string2
    elif isinstance(node, ACoupleExpression):
        string1 = pretty_print(node.children[0])
        string2 = pretty_print(node.children[1])
        return string1+"|->"+string2
    elif isinstance(node, APowSubsetExpression):
        string = pretty_print(node.children[0])
        return "POW("+string+")"
    elif isinstance(node, APow1SubsetExpression):
        string = pretty_print(node.children[0])
        return "POW1("+string+")"
    elif isinstance(node, ACardExpression):
        string = pretty_print(node.children[0])
        return "card("+string+")"
    elif isinstance(node, AGeneralUnionExpression):
        string = pretty_print(node.children[0])
        return "union("+string+")"
    elif isinstance(node, AGeneralIntersectionExpression):
        string = pretty_print(node.children[0])
        return "inter("+string+")"
    elif isinstance(node, AQuantifiedUnionExpression):
        varList = node.children[:-2]
        pred = node.children[-2]
        expr = node.children[-1]
        out = "UNION ("
        for i in range(len(varList)):
            out += varList[i].idName
            if i+1<len(varList):
                out += ","
        out += ").("
        out += pretty_print(pred)
        out += "|"
        out += pretty_print(expr)
        out += ")"
        return out
    elif isinstance(node, AQuantifiedIntersectionExpression):  
        varList = node.children[:-2]
        pred = node.children[-2]
        expr = node.children[-1]
        out = "INTER ("
        for i in range(len(varList)):
            out += varList[i].idName
            if i+1<len(varList):
                out += ","
        out += ").("
        out += pretty_print(pred)
        out += "|"
        out += pretty_print(expr)
        out += ")"
        return out


# *************************
#
#       2.1 Set predicates
#
# *************************
    elif isinstance(node, ABelongPredicate):
        string1 = pretty_print(node.children[0])
        string2 = pretty_print(node.children[1])
        return string1+":"+string2
    elif isinstance(node, ANotBelongPredicate):
        string1 = pretty_print(node.children[0])
        string2 = pretty_print(node.children[1])
        return string1+"/:"+string2
    elif isinstance(node, AIncludePredicate):
        string1 = pretty_print(node.children[0])
        string2 = pretty_print(node.children[1])
        return string1+"<:"+string2
    elif isinstance(node, ANotIncludePredicate):
        string1 = pretty_print(node.children[0])
        string2 = pretty_print(node.children[1])
        return string1+"/<:"+string2
    elif isinstance(node, AIncludeStrictlyPredicate):
        string1 = pretty_print(node.children[0])
        string2 = pretty_print(node.children[1])
        return string1+"<<:"+string2
    elif isinstance(node, ANotIncludeStrictlyPredicate):
        string1 = pretty_print(node.children[0])
        string2 = pretty_print(node.children[1])
        return string1+"/<<:"+string2


# *****************
#
#       3. Numbers
#
# *****************
    elif isinstance(node, ANaturalSetExpression):
        return "NATURAL"
    elif isinstance(node, ANatural1SetExpression):
        return "NATURAL1"
    elif isinstance(node, ANatSetExpression):
        return "NAT"
    elif isinstance(node, ANat1SetExpression):
        return "NAT1"
    elif isinstance(node, AIntSetExpression):
        return "INT"
    elif isinstance(node, AIntegerSetExpression):
        return "INTEGER"
    elif isinstance(node, AMinExpression):
        string = pretty_print(node.children[0])
        return "min("+string+")"
    elif isinstance(node, AMaxExpression):
        string = pretty_print(node.children[0])
        return "max("+string+")"
    elif isinstance(node, AAddExpression):
        string1 = pretty_print(node.children[0])
        string2 = pretty_print(node.children[1])
        return string1+"+" + string2
    elif isinstance(node, AMinusOrSetSubtractExpression) or isinstance(node, ASetSubtractionExpression):
        string1 = pretty_print(node.children[0])
        string2 = pretty_print(node.children[1])
        return string1+"-" + string2
    elif isinstance(node, AMultOrCartExpression):
        string1 = pretty_print(node.children[0])
        string2 = pretty_print(node.children[1])
        return string1+"*" + string2
    elif isinstance(node, ADivExpression):
        string1 = pretty_print(node.children[0])
        string2 = pretty_print(node.children[1])
        return string1+"/" + string2
    elif isinstance(node, AModuloExpression):
        string1 = pretty_print(node.children[0])
        string2 = pretty_print(node.children[1])
        return string1+" mod " + string2
    elif isinstance(node, APowerOfExpression):
        string1 = pretty_print(node.children[0])
        string2 = pretty_print(node.children[1])
        return string1+"**" + string2
    elif isinstance(node, AIntervalExpression):
        string1 = pretty_print(node.children[0])
        string2 = pretty_print(node.children[1])
        return string1+" .. " + string2
    elif isinstance(node, AGeneralSumExpression):
        varList = node.children[:-2]
        pred = node.children[-2]
        expr = node.children[-1]
        out = "SIGMA("
        for i in range(len(varList)):
            out += varList[i].idName
            if i+1<len(varList):
                out += ","
        out += ").("    
        out += pretty_print(pred)
        out += "|"
        out += pretty_print(expr)
        out += ")"
        return out  
    elif isinstance(node, AGeneralProductExpression):
        varList = node.children[:-2]
        pred = node.children[-2]
        expr = node.children[-1]
        out = "PI("
        for i in range(len(varList)):
            out += varList[i].idName
            if i+1<len(varList):
                out += ","
        out += ").("    
        out += pretty_print(pred)
        out += "|"
        out += pretty_print(expr)
        out += ")"
        return out  



# ***************************
#
#       3.1 Number predicates
#
# ***************************
    elif isinstance(node, AGreaterPredicate):
        string1 = pretty_print(node.children[0])
        string2 = pretty_print(node.children[1])
        return string1+">"+string2
    elif isinstance(node, ALessPredicate):
        string1 = pretty_print(node.children[0])
        string2 = pretty_print(node.children[1])
        return string1+"<"+string2
    elif isinstance(node, AGreaterEqualPredicate):
        string1 = pretty_print(node.children[0])
        string2 = pretty_print(node.children[1])
        return string1+">="+string2
    elif isinstance(node, ALessEqualPredicate):
        string1 = pretty_print(node.children[0])
        string2 = pretty_print(node.children[1])
        return string1+"<="+string2


# ******************
#
#       4. Relations
#
# ******************
    elif isinstance(node, ARelationsExpression):
        string1 = pretty_print(node.children[0])
        string2 = pretty_print(node.children[1])
        return string1+"<->"+string2
    elif isinstance(node, ADomainExpression):
        string = pretty_print(node.children[0])
        return "dom("+string+")"
    elif isinstance(node, ARangeExpression):
        string = pretty_print(node.children[0])
        return "ran("+string+")"
    elif isinstance(node, ACompositionExpression):
        string1 = pretty_print(node.children[0])
        string2 = pretty_print(node.children[1])
        return "("+string1+";"+string2+")"
    elif isinstance(node, AIdentityExpression):
        string = pretty_print(node.children[0])
        return "id("+string+")"
    elif isinstance(node, ADomainRestrictionExpression):
        string1 = pretty_print(node.children[0])
        string2 = pretty_print(node.children[1])
        return string1+"<|"+string2
    elif isinstance(node, ADomainSubtractionExpression):
        string1 = pretty_print(node.children[0])
        string2 = pretty_print(node.children[1])
        return string1+"<<|"+string2
    elif isinstance(node, ARangeRestrictionExpression):
        string1 = pretty_print(node.children[0])
        string2 = pretty_print(node.children[1])
        return string1+"|>"+string2
    elif isinstance(node, ARangeSubtractionExpression):
        string1 = pretty_print(node.children[0])
        string2 = pretty_print(node.children[1])
        return string1+"|>>"+string2
    elif isinstance(node, AReverseExpression):
        string = pretty_print(node.children[0])
        return string+"~"
    elif isinstance(node, AImageExpression):
        string1 = pretty_print(node.children[0])
        string2 = pretty_print(node.children[1])
        return string1+"["+string2+"]"
    elif isinstance(node, AOverwriteExpression):
        string1 = pretty_print(node.children[0])
        string2 = pretty_print(node.children[1])
        return string1+"<+"+string2
    elif isinstance(node, ADirectProductExpression):
        string1 = pretty_print(node.children[0])
        string2 = pretty_print(node.children[1])
        return string1+"><"+string2
    elif isinstance(node, AParallelProductExpression):
        string1 = pretty_print(node.children[0])
        string2 = pretty_print(node.children[1])
        return "("+string1+"||"+string2+")"
    elif isinstance(node, AIterationExpression):
        string1 = pretty_print(node.children[0])
        string2 = pretty_print(node.children[1])
        return "iterate("+string1+","+string2+")"
    elif isinstance(node, AReflexiveClosureExpression):
        string = pretty_print(node.children[0])
        return "closure("+string+")"
    elif isinstance(node, AClosureExpression):
        string = pretty_print(node.children[0])
        return "closure1("+string+")"
    elif isinstance(node, AFirstProjectionExpression):
        string1 = pretty_print(node.children[0])
        string2 = pretty_print(node.children[1])
        return "prj1("+string1+","+string2+")"
    elif isinstance(node, ASecondProjectionExpression):
        string1 = pretty_print(node.children[0])
        string2 = pretty_print(node.children[1])
        return "prj2("+string1+","+string2+")"



# *******************
#
#       4.1 Functions
#
# *******************
    elif isinstance(node, APartialFunctionExpression):
        string1 = pretty_print(node.children[0])
        string2 = pretty_print(node.children[1])
        return string1+"+->"+string2
    elif isinstance(node, ATotalFunctionExpression):
        string1 = pretty_print(node.children[0])
        string2 = pretty_print(node.children[1])
        return string1+"-->"+string2
    elif isinstance(node, APartialInjectionExpression):
        string1 = pretty_print(node.children[0])
        string2 = pretty_print(node.children[1])
        return string1+">+>"+string2
    elif isinstance(node, ATotalInjectionExpression):
        string1 = pretty_print(node.children[0])
        string2 = pretty_print(node.children[1])
        return string1+">->"+string2
    elif isinstance(node, APartialSurjectionExpression):
        string1 = pretty_print(node.children[0])
        string2 = pretty_print(node.children[1])
        return string1+"+->>"+string2
    elif isinstance(node, ATotalSurjectionExpression):
        string1 = pretty_print(node.children[0])
        string2 = pretty_print(node.children[1])
        return string1+"-->>"+string2
    elif isinstance(node, ATotalBijectionExpression):
        string1 = pretty_print(node.children[0])
        string2 = pretty_print(node.children[1])
        return string1+">->>"+string2
    elif isinstance(node, APartialBijectionExpression):
        string1 = pretty_print(node.children[0])
        string2 = pretty_print(node.children[1])
        return string1+">+>>"+string2 
    elif isinstance(node, ALambdaExpression):
        varList = node.children[:-2]
        pred = node.children[-2]
        expr = node.children[-1]
        out = "%("
        for i in range(len(varList)):
            out += varList[i].idName
            if i+1<len(varList):
                out += ","
        out += ").("
        out += pretty_print(pred)
        out += "|"
        out += pretty_print(expr)
        out += ")"
        return out          
    elif isinstance(node, AFunctionExpression):
        if isinstance(node.children[0], APredecessorExpression):
            string = pretty_print(node.children[1])
            return "pred("+string+")"
        if isinstance(node.children[0], ASuccessorExpression):
            string = pretty_print(node.children[1])
            return "succ("+string+")"
        string1 = pretty_print(node.children[0])
        string2 = pretty_print(node.children[1])
        return string1+"("+string2+")"




# ********************
#
#       4.2 Sequences
#
# ********************
    elif isinstance(node,AEmptySequenceExpression):
        return "[]"
    elif isinstance(node,ASeqExpression):
        string = pretty_print(node.children[0])
        return "seq("+string+")"
    elif isinstance(node,ASeq1Expression):
        string = pretty_print(node.children[0])
        return "seq1("+string+")"
    elif isinstance(node,AIseqExpression):
        string = pretty_print(node.children[0])
        return "iseq("+string+")"
    elif isinstance(node, AIseq1Expression):
        string = pretty_print(node.children[0])
        return "iseq1("+string+")"
    elif isinstance(node,APermExpression): 
        string = pretty_print(node.children[0])
        return "perm("+string+")"
    elif isinstance(node, AConcatExpression):
        string1 = pretty_print(node.children[0])
        string2 = pretty_print(node.children[1])
        return string1+"^"+string2
    elif isinstance(node, AInsertFrontExpression):
        string1 = pretty_print(node.children[0])
        string2 = pretty_print(node.children[1])
        return string1+"->"+string2 
    elif isinstance(node, AInsertTailExpression):
        string1 = pretty_print(node.children[0])
        string2 = pretty_print(node.children[1])
        return string1+"<-"+string2
    elif isinstance(node, ASequenceExtensionExpression):
        out = "["
        for i in range(len(node.children)):
            out += pretty_print(node.children[i])
            if i+1<len(node.children):
                out += ","
        return out+"]"
    elif isinstance(node, ASizeExpression):
        string = pretty_print(node.children[0])
        return "size("+string+")"
    elif isinstance(node, ARevExpression):
        string = pretty_print(node.children[0])
        return "rev("+string+")"
    elif isinstance(node, ARestrictFrontExpression):
        string1 = pretty_print(node.children[0])
        string2 = pretty_print(node.children[1])
        return string1+"/|\\"+string2
    elif isinstance(node, ARestrictTailExpression):
        string1 = pretty_print(node.children[0])
        string2 = pretty_print(node.children[1])
        return string1+"\\|/"+string2
    elif isinstance(node, AFirstExpression):
        string = pretty_print(node.children[0])
        return "first("+string+")"
    elif isinstance(node, ALastExpression):
        string = pretty_print(node.children[0])
        return "last("+string+")"
    elif isinstance(node, ATailExpression):
        string = pretty_print(node.children[0])
        return "tail("+string+")"
    elif isinstance(node, AFrontExpression):
        string = pretty_print(node.children[0])
        return "front("+string+")"
    elif isinstance(node, AGeneralConcatExpression):
        string = pretty_print(node.children[0])
        return "conc("+string+")"
    elif isinstance(node, AStringExpression):
        return node.stringing

# ****************
#
# 6. Miscellaneous
#
# ****************
    elif isinstance(node,AUnaryExpression):
        string = pretty_print(node.children[0])
        return "-"+string
    elif isinstance(node, AIntegerExpression):
        return str(node.intValue)
    elif isinstance(node, AMinIntExpression):
        return "MININT"
    elif isinstance(node, AMaxIntExpression):
        return "MAXINT"
    elif isinstance(node, AIdentifierExpression):
        return str(node.idName).replace(",",".") # quickfix of java parser bug. creates , instead of .
    elif isinstance(node, APrimedIdentifierExpression):
        return node.idName # TODO test (e.g xx$0 (only allowed in become-such-substitutions))
    elif isinstance(node, ABoolSetExpression):
        return "BOOL"
    elif isinstance(node, ATrueExpression):
        return "TRUE"
    elif isinstance(node, AFalseExpression):
        return "FALSE"
    elif isinstance(node, AStructExpression):
        out = ""
        for i in range(len(node.children)):
            out += pretty_print(node.children[i])
            if i+1<len(node.children):
                out +=","
        return "struct("+out+")"
    elif isinstance(node, ARecExpression):
        out = ""
        for i in range(len(node.children)):
            out += pretty_print(node.children[i])
            if i+1<len(node.children):
                out +=","
        return "rec("+out+")" 
    elif isinstance(node, ARecordFieldExpression):
        string1 = pretty_print(node.children[0])
        string2 = pretty_print(node.children[1])
        return string1+"'"+string2  
    elif isinstance(node, ARecEntry):
        string1 = pretty_print(node.children[0])
        string2 = pretty_print(node.children[1])
        return string1+":"+string2     
    elif isinstance(node, AStringSetExpression):
        return "STRING" 
    elif isinstance(node, ATransRelationExpression):
        string = pretty_print(node.children[0])
        return "rel("+string+")" 
    elif isinstance(node, ATransFunctionExpression):
        string = pretty_print(node.children[0])
        return "func("+string+")" 
    elif isinstance(node, AOpSubstitution):
        return "" # TODO: impl
    elif isinstance(node, AConvertBoolExpression):
        string = pretty_print(node.children[0])
        return "bool("+string+")" 
    else:
        raise Exception("PRETTYORINTBUG>>> Unknown Node: %s",node)