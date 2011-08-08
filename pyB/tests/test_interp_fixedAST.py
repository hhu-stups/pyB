# -*- coding: utf-8 -*-
from ast_nodes import *
from interp import inperpret, Environment


class TestInterp_fixedAST():

    def test_simple_expr_add(self):
        # Build AST: 1+1=3
        intExp = AIntegerExpression(1)
        intExp2 = AIntegerExpression(1)
        intExp3 = AIntegerExpression(3)
        addExp = AAddExpression()
        addExp.children.append(intExp)
        addExp.children.append(intExp2)
        eqPred = AEqualPredicate()
        eqPred.children.append(addExp)
        eqPred.children.append(intExp3)

        # Test
        env = Environment()
        assert not inperpret(eqPred, env)

    def test_simple_expr_add2(self):
        # Build AST: 1+1=2
        intExp = AIntegerExpression(1)
        intExp2 = AIntegerExpression(1)
        intExp3 = AIntegerExpression(2)
        addExp = AAddExpression()
        addExp.children.append(intExp)
        addExp.children.append(intExp2)
        eqPred = AEqualPredicate()
        eqPred.children.append(addExp)
        eqPred.children.append(intExp3)

        # Test
        env = Environment()
        assert inperpret(eqPred, env)

    def test_simple_expr_sub(self):
        # Build AST: 4-3=1
        intExp = AIntegerExpression(4)
        intExp2 = AIntegerExpression(3)
        intExp3 = AIntegerExpression(1)
        subExp = AMinusOrSetSubtractExpression()
        subExp.children.append(intExp)
        subExp.children.append(intExp2)
        eqPred = AEqualPredicate()
        eqPred.children.append(subExp)
        eqPred.children.append(intExp3)

        # Test
        env = Environment()
        assert inperpret(eqPred, env)

    def test_simple_expr_mul(self):
        # Build AST: 4*0=0
        intExp = AIntegerExpression(4)
        intExp2 = AIntegerExpression(0)
        intExp3 = AIntegerExpression(0)
        mulExp = AMultOrCartExpression()
        mulExp.children.append(intExp)
        mulExp.children.append(intExp2)
        eqPred = AEqualPredicate()
        eqPred.children.append(mulExp)
        eqPred.children.append(intExp3)

        # Test
        env = Environment()
        assert inperpret(eqPred, env)

    def test_simple_expr_div(self):
        # Build AST: 8/2=4
        intExp = AIntegerExpression(8)
        intExp2 = AIntegerExpression(2)
        intExp3 = AIntegerExpression(4)
        divExp = ADivExpression()
        divExp.children.append(intExp)
        divExp.children.append(intExp2)
        eqPred = AEqualPredicate()
        eqPred.children.append(divExp)
        eqPred.children.append(intExp3)

        # Test
        env = Environment()
        assert inperpret(eqPred, env)

    def test_simple_expr_mod(self):
        # Build AST: 8 mod 3=2
        intExp = AIntegerExpression(8)
        intExp2 = AIntegerExpression(3)
        intExp3 = AIntegerExpression(2)
        modExp = AModuloExpression()
        modExp.children.append(intExp)
        modExp.children.append(intExp2)
        eqPred = AEqualPredicate()
        eqPred.children.append(modExp)
        eqPred.children.append(intExp3)

        # Test
        env = Environment()
        assert inperpret(eqPred, env)

    def test_simple_expr_neq(self):
        # Build AST: 0 /= 1
        intExp = AIntegerExpression(0)
        intExp2 = AIntegerExpression(1)
        ueqPred = AUnequalPredicate()
        ueqPred.children.append(intExp)
        ueqPred.children.append(intExp2)

        # Test
        env = Environment()
        assert inperpret(ueqPred, env)

    def test_simple_pred_gt(self):
        # Build AST: 6>x
        intExp = AIntegerExpression(6)
        idExp = AIdentifierExpression("x")
        gtPred = AGreaterPredicate()
        gtPred.children.append(intExp)
        gtPred.children.append(idExp)

        # Test
        env = Environment()
        env.variable_values["x"] = 1
        assert inperpret(gtPred, env)

        env.variable_values["x"] = 10
        assert not inperpret(gtPred, env)

        env.variable_values["x"] = 6
        assert not inperpret(gtPred, env)

    def test_simple_pred_eq(self):
        # Build AST: x=6
        idExp = AIdentifierExpression("x")
        intExp = AIntegerExpression(6)
        eqPred = AEqualPredicate()
        eqPred.children.append(idExp)
        eqPred.children.append(intExp)

        #Test
        env = Environment()
        env.variable_values["x"] = 1
        assert not inperpret(eqPred, env)

        env.variable_values["x"] = 10
        assert not inperpret(eqPred, env)

        env.variable_values["x"] = 6
        assert inperpret(eqPred, env)

    def test_simple_pred_ls(self):
        # Build AST: x<6
        idExp = AIdentifierExpression("x")
        intExp = AIntegerExpression(6)
        lsPred = ALessPredicate()
        lsPred.children.append(idExp)
        lsPred.children.append(intExp)

        #Test
        env = Environment()
        env.variable_values["x"] = 1
        assert inperpret(lsPred, env)

        env.variable_values["x"] = 10
        assert not inperpret(lsPred, env)

        env.variable_values["x"] = 6
        assert not inperpret(lsPred, env)

    def test_simple_pred_and(self):
        # Build AST: x>=6 & y=6
        idExp = AIdentifierExpression("x")
        intExp = AIntegerExpression(6)
        geqPred = AGreaterEqualPredicate()
        geqPred.children.append(idExp)
        geqPred.children.append(intExp)

        idExp2 = AIdentifierExpression("y")
        intExp2 = AIntegerExpression(6)
        eqPred = AEqualPredicate()
        eqPred.children.append(idExp2)
        eqPred.children.append(intExp2)

        conPred = AConjunctPredicate()
        conPred.children.append(geqPred)
        conPred.children.append(eqPred)

        #Test
        env = Environment()
        env.variable_values["x"] = 1
        env.variable_values["y"] = 7
        assert not inperpret(conPred, env)

        env.variable_values["x"] = 10
        env.variable_values["y"] = 3
        assert not inperpret(conPred, env)

        env.variable_values["x"] = 6
        env.variable_values["y"] = 42
        assert not inperpret(conPred, env)

        env.variable_values["x"] = 6
        env.variable_values["y"] = 6
        assert inperpret(conPred, env)

    def test_simple_pred_or(self):
        # Build AST: x<=4 or y=1
        idExp = AIdentifierExpression("x")
        intExp = AIntegerExpression(4)
        leqPred = ALessEqualPredicate()
        leqPred.children.append(idExp)
        leqPred.children.append(intExp)

        idExp2 = AIdentifierExpression("y")
        intExp2 = AIntegerExpression(1)
        eqPred = AEqualPredicate()
        eqPred.children.append(idExp2)
        eqPred.children.append(intExp2)

        dsjPred = ADisjunctPredicate()
        dsjPred.children.append(leqPred)
        dsjPred.children.append(eqPred)

        #Test
        env = Environment()
        env.variable_values["x"] = 1
        env.variable_values["y"] = 7
        assert inperpret(dsjPred, env)

        env.variable_values["x"] = 10
        env.variable_values["y"] = 3
        assert not inperpret(dsjPred, env)

        env.variable_values["x"] = 6
        env.variable_values["y"] = 42
        assert not inperpret(dsjPred, env)

        env.variable_values["x"] = 1
        env.variable_values["y"] = 6
        assert inperpret(dsjPred, env)

    def test_simple_pred_impl(self):
        # Build AST: z>=42 => z>41
        idExp = AIdentifierExpression("z")
        intExp = AIntegerExpression(42)
        geqPred = AGreaterEqualPredicate()
        geqPred.children.append(idExp)
        geqPred.children.append(intExp)

        idExp2 = AIdentifierExpression("z")
        intExp2 = AIntegerExpression(41)
        gtPred = AGreaterPredicate()
        gtPred.children.append(idExp2)
        gtPred.children.append(intExp2)

        implPred = AImplicationPredicate()
        implPred.children.append(geqPred)
        implPred.children.append(gtPred)

        #Test
        env = Environment() # True=>True is True
        env.variable_values["z"] = 42
        assert inperpret(implPred, env)

        env = Environment()
        env.variable_values["z"] = 43
        assert inperpret(implPred, env)

        env = Environment() # False=>False is True
        env.variable_values["z"] = 41
        assert inperpret(implPred, env)

    def test_simple_pred_impl2(self):
        # Build AST: z=42 => 1+1=3
        intExp4 = AIntegerExpression(42)
        idExp = AIdentifierExpression("z")
        eqPred2 = AEqualPredicate()
        eqPred2.children.append(intExp4)
        eqPred2.children.append(idExp)

        intExp = AIntegerExpression(1)
        intExp2 = AIntegerExpression(1)
        intExp3 = AIntegerExpression(3)
        addExp = AAddExpression()
        addExp.children.append(intExp)
        addExp.children.append(intExp2)
        eqPred = AEqualPredicate()
        eqPred.children.append(addExp)
        eqPred.children.append(intExp3)

        implPred = AImplicationPredicate()
        implPred.children.append(eqPred2)
        implPred.children.append(eqPred)

        #Test
        env = Environment() # True=>False is False
        env.variable_values["z"] = 42
        assert not inperpret(implPred, env)

        env = Environment() # False=>False is False
        env.variable_values["z"] = 41
        assert inperpret(implPred, env)

    def test_simple_pred_impl3(self):
        # Build AST: z=42 => 1+1=2
        intExp4 = AIntegerExpression(42)
        idExp = AIdentifierExpression("z")
        eqPred2 = AEqualPredicate()
        eqPred2.children.append(idExp)
        eqPred2.children.append(intExp4)

        intExp = AIntegerExpression(1)
        intExp2 = AIntegerExpression(1)
        intExp3 = AIntegerExpression(2)
        addExp = AAddExpression()
        addExp.children.append(intExp)
        addExp.children.append(intExp2)
        eqPred = AEqualPredicate()
        eqPred.children.append(addExp)
        eqPred.children.append(intExp3)

        implPred = AImplicationPredicate()
        implPred.children.append(eqPred2)
        implPred.children.append(eqPred)

        #Test
        env = Environment() # True=>True is True
        env.variable_values["z"] = 42
        assert inperpret(implPred, env)

        # False=>True is True
        env.variable_values["z"] = 41
        assert inperpret(implPred, env)

    def test_simple_pred_aequ(self):
        # Build AST: 7<8 <=> 6+1<8
        intExp = AIntegerExpression(7)
        intExp2 = AIntegerExpression(8)
        lsPred = ALessPredicate()
        lsPred.children.append(intExp)
        lsPred.children.append(intExp2)

        intExp3 = AIntegerExpression(6)
        intExp4 = AIntegerExpression(1)
        intExp5 = AIntegerExpression(8)
        addExp = AAddExpression()
        addExp.children.append(intExp3)
        addExp.children.append(intExp4)
        lsPred2 = ALessPredicate()
        lsPred2.children.append(addExp)
        lsPred2.children.append(intExp5)

        eqaPred = AEquivalencePredicate()
        eqaPred.children.append(lsPred)
        eqaPred.children.append(lsPred2)

        #Test
        env = Environment()
        assert inperpret(eqaPred, env)

    def test_simple_pred_not(self):
        # Build AST: not (42<23)
        intExp = AIntegerExpression(42)
        intExp2 = AIntegerExpression(23)
        lsPred = ALessPredicate()
        lsPred.children.append(intExp)
        lsPred.children.append(intExp2)
        negPred = ANegationPredicate()
        negPred.children.append(lsPred)

        #Test
        env = Environment()
        assert inperpret(negPred, env)

    def test_simple_set_pred_member(self):
        # Build AST: yy:ID
        idExp = AIdentifierExpression("yy")
        idExp2 = AIdentifierExpression("ID")
        belPred = ABelongPredicate()
        belPred.children.append(idExp)
        belPred.children.append(idExp2)

        #Test
        env = Environment()
        env.variable_values["yy"] = "aa"
        env.variable_values["ID"] = set(["aa","bb"])
        assert inperpret(belPred, env)

        env.variable_values["yy"] = "cc"
        assert not inperpret(belPred, env)

    def test_simple_set_pred_not_member(self):
        # Build AST: yy/:ID
        idExp = AIdentifierExpression("yy")
        idExp2 = AIdentifierExpression("ID")
        notbelPred = ANotBelongPredicate()
        notbelPred.children.append(idExp)
        notbelPred.children.append(idExp2)

        #Test
        env = Environment()
        env.variable_values["yy"] = "aa"
        env.variable_values["ID"] = set(["aa","bb"])
        assert not inperpret(notbelPred, env)

    def test_simple_set_pred_setex(self):
        # Build AST: yy:{aa,bb,cc}
        idExp = AIdentifierExpression("yy")
        idExp2 = AIdentifierExpression("aa")
        idExp3 = AIdentifierExpression("bb")
        idExp4 = AIdentifierExpression("cc")
        sexExp = ASetExtensionExpression()
        sexExp.children.append(idExp2)
        sexExp.children.append(idExp3)
        sexExp.children.append(idExp4)
        belPred = ABelongPredicate()
        belPred.children.append(idExp)
        belPred.children.append(sexExp)
        
        #Test
        env = Environment()
        env.variable_values["yy"] = "aa"
        env.variable_values["aa"] = "aa" #FIXME: maybe this is a Bug..
        env.variable_values["bb"] = "bb" #
        env.variable_values["cc"] = "cc" #
        assert inperpret(belPred, env)

        env.variable_values["yy"] = "yy"
        assert not inperpret(belPred, env)

    def test_simple_set_pred_subset(self):
        # Build AST: A<:B
        idExp = AIdentifierExpression("A")
        idExp2 = AIdentifierExpression("B")
        inclPred = AIncludePredicate()
        inclPred.children.append(idExp)
        inclPred.children.append(idExp2)

        #Test
        env = Environment()
        env.variable_values["A"] = set(["aa"])
        env.variable_values["B"] = set(["aa","bb"])
        assert inperpret(inclPred, env)

        env.variable_values["B"] = set(["aa"])
        env.variable_values["A"] = set(["aa","bb"])
        assert not inperpret(inclPred, env)

        env.variable_values["B"] = set()
        env.variable_values["A"] = set()
        assert inperpret(inclPred, env)

        env.variable_values["B"] = set(["aa","bb"])
        env.variable_values["A"] = set(["aa","bb"])
        assert inperpret(inclPred, env)

    def test_simple_set_pred_not_subset(self):
        # Build AST: A/<:B
        idExp = AIdentifierExpression("A")
        idExp2 = AIdentifierExpression("B")
        notinclPred = ANotIncludePredicate()
        notinclPred.children.append(idExp)
        notinclPred.children.append(idExp2)

        #Test
        env = Environment()
        env.variable_values["A"] = set(["aa"])
        env.variable_values["B"] = set(["aa","bb"])
        assert not inperpret(notinclPred, env)

        env.variable_values["B"] = set(["aa"])
        env.variable_values["A"] = set(["aa","bb"])
        assert inperpret(notinclPred, env)

        env.variable_values["B"] = set()
        env.variable_values["A"] = set()
        assert not inperpret(notinclPred, env)

    def test_simple_set_pred_str_subset(self):
        # Build AST: A<<:B
        idExp = AIdentifierExpression("A")
        idExp2 = AIdentifierExpression("B")
        inclstrPred = AIncludeStrictlyPredicate()
        inclstrPred.children.append(idExp)
        inclstrPred.children.append(idExp2)

        #Test
        env = Environment()
        env.variable_values["A"] = set(["aa"])
        env.variable_values["B"] = set(["aa","bb"])
        assert inperpret(inclstrPred, env)

        env.variable_values["B"] = set(["aa"])
        env.variable_values["A"] = set(["aa","bb"])
        assert not inperpret(inclstrPred, env)

        env.variable_values["B"] = set()
        env.variable_values["A"] = set()
        assert not inperpret(inclstrPred, env)

        env.variable_values["B"] = set(["aa","bb"])
        env.variable_values["A"] = set(["aa","bb"])
        assert not inperpret(inclstrPred, env)

    def test_simple_set_pred_not_str_subset(self):
        # Build AST: A/<<:B
        idExp = AIdentifierExpression("A")
        idExp2 = AIdentifierExpression("B")
        notinclstrPred = ANotIncludeStrictlyPredicate()
        notinclstrPred.children.append(idExp)
        notinclstrPred.children.append(idExp2)

        #Test
        env = Environment()
        env.variable_values["A"] = set(["aa"])
        env.variable_values["B"] = set(["aa","bb"])
        assert not inperpret(notinclstrPred, env)

        env.variable_values["B"] = set(["aa"])
        env.variable_values["A"] = set(["aa","bb"])
        assert inperpret(notinclstrPred, env)

        env.variable_values["B"] = set()
        env.variable_values["A"] = set()
        assert inperpret(notinclstrPred, env)

        env.variable_values["B"] = set(["aa","bb"])
        env.variable_values["A"] = set(["aa","bb"])
        assert inperpret(notinclstrPred, env)

    def test_simple_set_pred_empt_set(self):
        # Build AST: {}<:A
        eSetExp = AEmptySetExpression()
        idExp = AIdentifierExpression("A")
        inclPred = AIncludePredicate()
        inclPred.children.append(eSetExp)
        inclPred.children.append(idExp)

        #Test
        env = Environment()
        env.variable_values["A"] = set(["aa","bb"])
        assert inperpret(inclPred, env)

    def test_simple_set_pred_card(self):
        # Build AST: card(S)>0
        idExp = AIdentifierExpression("S")
        cardExp = ACardExpression()
        cardExp.children.append(idExp)
        intExp = AIntegerExpression(0)
        gtPred = AGreaterPredicate()
        gtPred.children.append(cardExp)
        gtPred.children.append(intExp)

        #TestInterp
        env = Environment()
        env.variable_values["S"] = set(["aa","bb"])
        assert inperpret(gtPred, env)

    def test_simple_set_pred_union(self):
        # Build AST: S <: S \/ T
        idExp = AIdentifierExpression("S")
        idExp2 = AIdentifierExpression("S")
        idExp3 = AIdentifierExpression("T")
        uniExp = AUnionExpression()
        uniExp.children.append(idExp2)
        uniExp.children.append(idExp3)
        inclPred = AIncludePredicate()
        inclPred.children.append(idExp)
        inclPred.children.append(uniExp)

        # Test
        env = Environment()
        env.variable_values["S"] = set(["aa","bb"])
        env.variable_values["T"] = set(["bb","cc","dd"])
        assert inperpret(inclPred, env)

    def test_simple_set_pred_inters(self):
        # Build AST: S <: S /\ T
        idExp = AIdentifierExpression("S")
        idExp2 = AIdentifierExpression("S")
        idExp3 = AIdentifierExpression("T")
        insExp = AIntersectionExpression()
        insExp.children.append(idExp2)
        insExp.children.append(idExp3)
        inclPred = AIncludePredicate()
        inclPred.children.append(idExp)
        inclPred.children.append(insExp)

        # Test
        env = Environment()
        env.variable_values["S"] = set(["aa","bb"])
        env.variable_values["T"] = set(["bb","cc","dd"])
        assert not inperpret(inclPred, env)

        env.variable_values["S"] = set(["aa","bb"])
        env.variable_values["T"] = set(["aa","bb","cc","dd"])
        assert inperpret(inclPred, env)

        env.variable_values["S"] = set(["aa","bb"])
        env.variable_values["T"] = set(["cc","dd"])
        assert not inperpret(inclPred, env)

    def test_simple_set_pred_dif(self):
        # Build AST: S <: S - T
        idExp = AIdentifierExpression("S")
        idExp2 = AIdentifierExpression("S")
        idExp3 = AIdentifierExpression("T")
        subExp = AMinusOrSetSubtractExpression()
        subExp.children.append(idExp2)
        subExp.children.append(idExp3)
        inclPred = AIncludePredicate()
        inclPred.children.append(idExp)
        inclPred.children.append(subExp)

        # Test
        env = Environment()
        env.variable_values["S"] = set(["aa","bb"])
        env.variable_values["T"] = set(["bb","cc","dd"])
        assert not inperpret(inclPred, env)

        env.variable_values["S"] = set(["aa","bb"])
        env.variable_values["T"] = set(["cc","dd"])
        assert inperpret(inclPred, env)

    def test_simple_set_pred_cat_prod(self):
        # Build AST: S <: S * T
        idExp = AIdentifierExpression("S")
        idExp2 = AIdentifierExpression("S")
        idExp3 = AIdentifierExpression("T")
        mulExp = AMultOrCartExpression()
        mulExp.children.append(idExp2)
        mulExp.children.append(idExp3)
        inclPred = AIncludePredicate()
        inclPred.children.append(idExp)
        inclPred.children.append(mulExp)

        # Test
        env = Environment()
        env.variable_values["S"] = set(["aa"])
        env.variable_values["T"] = set(["bb","cc"])
        assert not inperpret(inclPred, env)

        result = set([("aa","bb"),("aa","cc")])
        assert inperpret(mulExp, env)==result

    def test_simple_set_expr_card(self):
        # Build AST: card(S)
        idExp = AIdentifierExpression("S")
        cardExp = ACardExpression()
        cardExp.children.append(idExp)

        #TestInterp
        env = Environment()
        env.variable_values["S"] = set(["aa","bb"])
        assert inperpret(cardExp, env)==2

