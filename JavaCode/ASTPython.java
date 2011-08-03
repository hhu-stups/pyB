package de.be4.classicalb.core.parser.analysis.python;

import de.be4.classicalb.core.parser.analysis.DepthFirstAdapter;
import de.be4.classicalb.core.parser.node.*;
// walks the tree and prints a pythonlike AST

public class ASTPython extends DepthFirstAdapter{
    public String out = "";
    int idCounter = 0;

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

    public void defaultOut(Node node)
    {
        printStdOut_twoChildren(node);
    }

    public void outStart(Start node)
    {
        // dont add a start node now
        // dont call defaultOut(Node)
    }


    public void outANegationPredicate(ANegationPredicate node)
    {
        printStdOut_oneChild(node);
    }


    public void outACardExpression(ACardExpression node)
    {
        printStdOut_oneChild(node);
    }


    public void outASetExtensionExpression(ASetExtensionExpression node)
    {
        printStdOut_manyChildren(node);
    }


    private void printStdOut_oneChild(Node node)
    {
        String nodeid   = ""+idCounter;
        String childid = ""+(idCounter-1);
        String clsname = node.getClass().getName();
        int mid= clsname.lastIndexOf ('.') + 1;
        String finalClsName = clsname.substring(mid);
        out += "id"+ (idCounter++) +"=";
        out += finalClsName +"()\n";
        out += "id"+nodeid;
        out += ".children.append(id"+childid+")\n";
    }


    private void printStdOut_twoChildren(Node node)
    {
        String nodeid   = ""+idCounter;
        String childid1 = ""+(idCounter-1);
        String childid2 = ""+(idCounter-2);
        String clsname = node.getClass().getName();
        int mid= clsname.lastIndexOf ('.') + 1;
        String finalClsName = clsname.substring(mid);
        out += "id"+ (idCounter++) +"=";
        out += finalClsName +"()\n";
        out += "id"+nodeid;
        out += ".children.append(id"+childid2+")\n";
        out += "id"+nodeid;
        out += ".children.append(id"+childid1+")\n";
    }


    private void printStdOut_manyChildren(Node node)
    {
        out += "IMPLEMENT ME\n";
    }
}
