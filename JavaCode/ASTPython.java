package de.be4.classicalb.core.parser.analysis.python;

import de.be4.classicalb.core.parser.analysis.DepthFirstAdapter;
import de.be4.classicalb.core.parser.node.*;
// walks the tree and prints a pythonlike AST

public class ASTPython extends DepthFirstAdapter{
    public String out = "";
    private int idCounter = 0;

    private String getClassName(Node node)
    {
        String clsname = node.getClass().getName();
        int mid= clsname.lastIndexOf ('.') + 1;
        return clsname.substring(mid);
    }


    public void outAPredicateParseUnit(APredicateParseUnit node)
    {
        out += "root = id"+(idCounter-1)+ "\n";
    }


    public void outAIntegerExpression(AIntegerExpression node)
    {
        out += "id"+ (idCounter++) +"=";
        out += "AIntegerExpression(";
        out += node.getLiteral().toString() + ")\n";
    }


    public void outAIdentifierExpression(AIdentifierExpression node)
    {
        out += "id"+ (idCounter++) +"=";
        out += "AIdentifierExpression(\"";
        out += node.getIdentifier().toString().replace("[","").replace("]","") + "\")\n";
    }


    public void outAEmptySetExpression(AEmptySetExpression node)
    {
        out += "id"+ (idCounter++) +"=";
        out += "AEmptySetExpression()\n";
    }


    public void outStart(Start node)
    {
        // dont add a start node now
        // dont call defaultOut(Node)
    }

    public void outASetExtensionExpression(ASetExtensionExpression node)
    {
        printStdOut_manyChildren(node);
    }


    public void caseAAddExpression(AAddExpression node)
    {
        printStdOut_twoChildren(node, node.getLeft(), node.getRight());
    }


    public void caseAMinusOrSetSubtractExpression(AMinusOrSetSubtractExpression node)
    {
        printStdOut_twoChildren(node, node.getLeft(), node.getRight());
    }


    public void caseAMultOrCartExpression(AMultOrCartExpression node)
    {
        printStdOut_twoChildren(node, node.getLeft(), node.getRight());
    }


    public void caseADivExpression(ADivExpression node)
    {
        printStdOut_twoChildren(node, node.getLeft(), node.getRight());
    }


    public void caseAModuloExpression(AModuloExpression node)
    {
        printStdOut_twoChildren(node, node.getLeft(), node.getRight());
    }


    public void caseACardExpression(ACardExpression node)
    {
        printStdOut_oneChild(node, node.getExpression());
    }


    public void caseAUnionExpression(AUnionExpression node)
    {
        printStdOut_twoChildren(node, node.getLeft(), node.getRight());
    }


    public void caseAIntersectionExpression(AIntersectionExpression node)
    {
        printStdOut_twoChildren(node, node.getLeft(), node.getRight());
    }


    public void caseABelongPredicate(ABelongPredicate node)
    {
        printStdOut_twoChildren(node, node.getLeft(), node.getRight());
    }


    public void caseANotBelongPredicate(ANotBelongPredicate node)
    {
        printStdOut_twoChildren(node, node.getLeft(), node.getRight());
    }


    public void caseAIncludePredicate(AIncludePredicate node)
    {
        printStdOut_twoChildren(node, node.getLeft(), node.getRight());
    }


    public void caseANotIncludePredicate(ANotIncludePredicate node)
    {
        printStdOut_twoChildren(node, node.getLeft(), node.getRight());
    }


    public void caseAIncludeStrictlyPredicate(AIncludeStrictlyPredicate node)
    {
        printStdOut_twoChildren(node, node.getLeft(), node.getRight());
    }


    public void caseANotIncludeStrictlyPredicate(ANotIncludeStrictlyPredicate node)
    {
        printStdOut_twoChildren(node, node.getLeft(), node.getRight());
    }


    public void caseANegationPredicate(ANegationPredicate node)
    {
        printStdOut_oneChild(node, node.getPredicate());
    }


    public void caseAGreaterPredicate(AGreaterPredicate node)
    {
        printStdOut_twoChildren(node, node.getLeft(), node.getRight());
    }


    public void caseAGreaterEqualPredicate(AGreaterEqualPredicate node)
    {
        printStdOut_twoChildren(node, node.getLeft(), node.getRight());
    }


    public void caseAEquivalencePredicate(AEquivalencePredicate node)
    {
        printStdOut_twoChildren(node, node.getLeft(), node.getRight());
    }


    public void caseAEqualPredicate(AEqualPredicate node)
    {
        printStdOut_twoChildren(node, node.getLeft(), node.getRight());
    }


    public void caseAUnequalPredicate(AUnequalPredicate node)
    {
        printStdOut_twoChildren(node, node.getLeft(), node.getRight());
    }


    public void caseALessPredicate(ALessPredicate node)
    {
        printStdOut_twoChildren(node, node.getLeft(), node.getRight());
    }


    public void caseALessEqualPredicate(ALessEqualPredicate node)
    {
        printStdOut_twoChildren(node, node.getLeft(), node.getRight());
    }


    public void caseAConjunctPredicate(AConjunctPredicate node)
    {
        printStdOut_twoChildren(node, node.getLeft(), node.getRight());
    }


    public void caseADisjunctPredicate(ADisjunctPredicate node)
    {
        printStdOut_twoChildren(node, node.getLeft(), node.getRight());
    }


    public void caseAImplicationPredicate(AImplicationPredicate node)
    {
        printStdOut_twoChildren(node, node.getLeft(), node.getRight());
    }


    private void printStdOut_oneChild(Node node, Node cnode)
    {
        String nodeid, childid;

        if(cnode != null)
        {
            cnode.apply(this);
            childid = ""+(idCounter-1);
            nodeid = ""+idCounter;
            out += "id"+ nodeid +"=";
            out += getClassName(node) +"()\n";
            idCounter++;
            out += "id"+nodeid+".children.append(id"+childid+")\n";
        }
    }


    private void printStdOut_twoChildren(Node node, Node left, Node right)
    {
        String nodeid, childid1="", childid2="";

        if(left != null)
        {
            left.apply(this);
            childid1 = ""+(idCounter-1);
        }

        if(right != null)
        {
            right.apply(this);
            childid2 = ""+(idCounter-1);
        }

        nodeid = ""+ idCounter;
        out += "id" + nodeid + "=";
        out += getClassName(node) +"()\n";
        idCounter++;

        if(left != null)
            out += "id"+nodeid+".children.append(id"+childid1+")\n";

        if(right != null)
            out += "id"+nodeid+".children.append(id"+childid2+")\n";
    }


    private void printStdOut_manyChildren(Node node)
    {
        out += "IMPLEMENT ME\n";
    }
}
