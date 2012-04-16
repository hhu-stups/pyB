package de.be4.classicalb.core.parser.analysis.python;

import de.be4.classicalb.core.parser.analysis.DepthFirstAdapter;
import de.be4.classicalb.core.parser.node.*;
import java.util.ArrayList;
import java.util.List;
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



    public void outAIntegerExpression(AIntegerExpression node)
    {
        out += "id"+ (idCounter++) +"=";
        out += "AIntegerExpression(";
        out += node.getLiteral().toString() + ")\n";
    }


    public void outAIdentifierExpression(AIdentifierExpression node)
    {
        // FIXME: some bug with a space at the end
        out += "id"+ (idCounter++) +"=";
        out += "AIdentifierExpression(\"";
        out += node.getIdentifier().toString().replace("[","").replace("]","") + "\")\n";
    }


    public void caseAStringExpression(AStringExpression node)
    {
        out += "id"+ (idCounter++) +"=";
        out += "AStringExpression(\"";
        out += node.getContent().getText()+ "\")\n";;
    }


    public void caseAStringSetExpression(AStringSetExpression node)
    {
        out += "id"+ (idCounter++) +"=";
        out += "AStringSetExpression()\n";
    }


    public void outAEmptySetExpression(AEmptySetExpression node)
    {
        out += "id"+ (idCounter++) +"=";
        out += "AEmptySetExpression()\n";
    }


    public void caseAEmptySequenceExpression(AEmptySequenceExpression node)
    {
        out += "id"+ (idCounter++) +"=";
        out += "AEmptySequenceExpression()\n";
    }

    public void caseANatSetExpression(ANatSetExpression node)
    {
        out += "id"+ (idCounter++) +"=";
        out += "ANatSetExpression()\n";
    }

    public void caseANaturalSetExpression(ANaturalSetExpression node)
    {
        out += "id"+ (idCounter++) +"=";
        out += "ANaturalSetExpression()\n";
    }

    public void caseANat1SetExpression(ANat1SetExpression node)
    {
        out += "id"+ (idCounter++) +"=";
        out += "ANat1SetExpression()\n";
    }


    public void caseATrueExpression(ATrueExpression node)
    {
        out += "id"+ (idCounter++) +"=";
        out += "ATrueExpression()\n";
    }


    public void caseABoolSetExpression(ABoolSetExpression node)
    {
        out += "id"+ (idCounter++) +"=";
        out += "ABoolSetExpression()\n";
    }


    public void caseAFalseExpression(AFalseExpression node)
    {
        out += "id"+ (idCounter++) +"=";
        out += "AFalseExpression()\n";
    }


    public void caseASkipSubstitution(ASkipSubstitution node)
    {
        out += "id"+ (idCounter++) +"=";
        out += "ASkipSubstitution()\n";
    }


    public void caseAMinIntExpression(AMinIntExpression node)
    {
        out += "id"+ (idCounter++) +"=";
        out += "AMinIntExpression()\n";
    }


    public void caseAMaxIntExpression(AMaxIntExpression node)
    {
        out += "id"+ (idCounter++) +"=";
        out += "AMaxIntExpression()\n";
    }


    public void caseASuccessorExpression(ASuccessorExpression node)
    {
        out += "id"+ (idCounter++) +"=";
        out += "ASuccessorExpression()\n";
    }


    public void caseAPredecessorExpression(APredecessorExpression node)
    {
        out += "id"+ (idCounter++) +"=";
        out += "APredecessorExpression()\n";
    }


    public void outStart(Start node)
    {
        // dont add a start node now
        // dont call defaultOut(Node)
    }


    public void caseAGeneralSumExpression(AGeneralSumExpression node)
    {
        List<Node> children = new ArrayList<Node>(node.getIdentifiers());
        if(node.getPredicates() != null)
            children.add(node.getPredicates());
        if(node.getExpression() != null)
            children.add(node.getExpression());
        printStdOut_manyChildren(node, children);
    }


    public void caseALambdaExpression(ALambdaExpression node)
    {
        List<Node> children = new ArrayList<Node>(node.getIdentifiers());
        if(node.getPredicate() != null)
            children.add(node.getPredicate());
        if(node.getExpression() != null)
            children.add(node.getExpression());
        printStdOut_manyChildren(node, children);
    }


    public void caseAGeneralProductExpression(AGeneralProductExpression node)
    {
        List<Node> children = new ArrayList<Node>(node.getIdentifiers());
        if(node.getPredicates() != null)
            children.add(node.getPredicates());
        if(node.getExpression() != null)
            children.add(node.getExpression());
        printStdOut_manyChildren(node, children);
    }


    // TODO: implement me
    public void caseAAbstractMachineParseUnit(AAbstractMachineParseUnit node)
    {
        List<PMachineClause> copy = new ArrayList<PMachineClause>(node.getMachineClauses());
        String[] ids = new String[copy.size()];

        String mtype="";
        if(node.getType() != null)
        {
            mtype = node.getType().toString();
        }

        String mname="";
        String[] param = null;
        int para_num = 0;
        if(node.getHeader() != null)
        {
            // TODO: catch classcast-Exception
            if(node.getHeader() instanceof AMachineHeader)
            {
                AMachineHeader head = (AMachineHeader)node.getHeader();
                mname = head.getName().toString().toString().replace("[","").replace("]","");
                List<PExpression> para = head.getParameters();
                param = new String[para.size()];
                para_num = para.size();
                int y = 0;
                for(PExpression p : para)
                {
                    param[y++] = p.toString();
                }
            }
        }

        int i=0;
        for(PMachineClause e : copy)
        {
            e.apply(this);
            ids[i++] = ""+(idCounter-1);
        }


        String nodeid = ""+ idCounter;
        out += "id" + nodeid + "=";
        out += getClassName(node) +"()\n";
        idCounter++;

        i = 0;
        for(int k=i; k<copy.size(); k++)
            out += "id"+nodeid+".children.append(id"+ids[i++]+")\n";
        out += "id"+nodeid+".mtype = \""+mtype+"\"\n";
        out += "id"+nodeid+".mname = \""+mname+"\"\n";

        if(param!=null && para_num!=0)
        {
            out += "id"+nodeid+".para = [\""+param[0]+"\"";
            for(int x=1; x<para_num; x++)
                out += ",\""+param[x]+"\"";
            out += "]\n";
        }
        else
        {
            out += "id"+nodeid+".para = []\n";
        }

        out += "root = id"+(idCounter-1)+ "\n";
    }


    public void caseARefinementMachineParseUnit(ARefinementMachineParseUnit node)
    {
        inARefinementMachineParseUnit(node);
        if(node.getHeader() != null)
        {
            node.getHeader().apply(this);
        }
        if(node.getRefMachine() != null)
        {
            node.getRefMachine().apply(this);
        }
        {
            List<PMachineClause> copy = new ArrayList<PMachineClause>(node.getMachineClauses());
            for(PMachineClause e : copy)
            {
                e.apply(this);
            }
        }
        outARefinementMachineParseUnit(node);
    }


    public void caseAMachineHeader(AMachineHeader node)
    {
        List<TIdentifierLiteral> copy0 = new ArrayList<TIdentifierLiteral>(node.getName());
        List<PExpression> copy1 = new ArrayList<PExpression>(node.getParameters());
        String[] ids = new String[copy1.size()];
        int i=0;

        String idName = "";
        for(TIdentifierLiteral e : copy0)
        {
            // XXX
            e.apply(this);
            idName = idName + e.toString();
        }

        for(PExpression e : copy1)
        {
            e.apply(this);
            ids[i++] = ""+(idCounter-1);
        }


        String nodeid = ""+ idCounter;
        out += "id" + nodeid + "=";
        out += getClassName(node) +"()\n";
        idCounter++;

        i=0;
        for(int k=i; k<copy1.size(); k++)
            out += "id"+nodeid+".children.append(id"+ids[i++]+")\n";
        out += "id"+nodeid+".idName = \""+idName+"\"\n";
    }



    public void caseADefinitionsMachineClause(ADefinitionsMachineClause node)
    {
        List<Node> children = new ArrayList<Node>(node.getDefinitions());
        printStdOut_manyChildren(node, children);
    }


    public void caseASubstitutionDefinition(ASubstitutionDefinition node)
    {
        List<Node> children = new ArrayList<Node>(node.getParameters());
        if(node.getRhs() != null)
            children.add(node.getRhs());
        printStdOut_manyChildren(node, children);

        String idName = "";
        if(node.getName() != null)
            idName = node.getName().toString();

        int nodeid = idCounter-1;
        out += "id"+nodeid+".idName = \""+idName+"\"\n";
        if (node.getParameters()!=null)
            out += "id"+nodeid+".paraNum = "+node.getParameters().size()+"\n";
        else
            out += "id"+nodeid+".paraNum = 0";
    }


    public void caseAPredicateDefinition(APredicateDefinition node)
    {
        List<PExpression> copy = new ArrayList<PExpression>(node.getParameters());
        String[] ids = new String[copy.size()+1]; // +1 rhs
        String idName = "";
        int i=0;


        if(node.getName() != null)
        {
            idName = node.getName().toString();
        }

        for(PExpression e : copy)
        {
            e.apply(this);
            ids[i++] = ""+(idCounter-1);
        }

        if(node.getRhs() != null)
        {
            node.getRhs().apply(this);
            ids[i++] = ""+(idCounter-1);
        }

        String nodeid = ""+ idCounter;
        out += "id" + nodeid + "=";
        out += getClassName(node) +"()\n";
        idCounter++;

        for(i = 0 ; i<ids.length-1; i++)
            out += "id"+nodeid+".children.append(id"+ids[i]+")\n";
        if(node.getRhs() != null)
            out += "id"+nodeid+".children.append(id"+ids[ids.length-1]+")\n";
        out += "id"+nodeid+".idName = \""+idName+"\"\n";
        if (copy!=null)
            out += "id"+nodeid+".paraNum = "+copy.size()+"\n";
        else
            out += "id"+nodeid+".paraNum = 0";
    }


    public void caseAExpressionDefinition(AExpressionDefinition node)
    {
        List<PExpression> copy = new ArrayList<PExpression>(node.getParameters());
        String[] ids = new String[copy.size()+1]; // +1 rhs
        String idName = "";
        int i=0;


        if(node.getName() != null)
        {
            idName = node.getName().toString();
        }

        for(PExpression e : copy)
        {
            e.apply(this);
            ids[i++] = ""+(idCounter-1);
        }

        if(node.getRhs() != null)
        {
            node.getRhs().apply(this);
            ids[i++] = ""+(idCounter-1);
        }

        String nodeid = ""+ idCounter;
        out += "id" + nodeid + "=";
        out += getClassName(node) +"()\n";
        idCounter++;

        for(i = 0 ; i<ids.length-1; i++)
            out += "id"+nodeid+".children.append(id"+ids[i]+")\n";
        if(node.getRhs() != null)
            out += "id"+nodeid+".children.append(id"+ids[ids.length-1]+")\n";
        out += "id"+nodeid+".idName = \""+idName+"\"\n";
        if (copy!=null)
            out += "id"+nodeid+".paraNum = "+copy.size()+"\n";
        else
            out += "id"+nodeid+".paraNum = 0";
    }


    public void caseADefinitionExpression(ADefinitionExpression node)
    {
        List<PExpression> copy = new ArrayList<PExpression>(node.getParameters());
        String[] ids = new String[copy.size()]; 
        String idName = "";
        int i=0;

        if(node.getDefLiteral() != null)
        {
            idName = node.getDefLiteral().toString();
        }

        for(PExpression e : copy)
        {
            e.apply(this);
            ids[i++] = ""+(idCounter-1);
        }

        String nodeid = ""+ idCounter;
        out += "id" + nodeid + "=";
        out += getClassName(node) +"()\n";
        idCounter++;

        for(i = 0 ; i<ids.length; i++)
            out += "id"+nodeid+".children.append(id"+ids[i]+")\n";
        out += "id"+nodeid+".idName = \""+idName+"\"\n";
    }


    public void caseADefinitionPredicate(ADefinitionPredicate node)
    {
        List<PExpression> copy = new ArrayList<PExpression>(node.getParameters());
        String[] ids = new String[copy.size()]; 
        String idName = "";
        int i=0;

        if(node.getDefLiteral() != null)
        {
            idName = node.getDefLiteral().toString();
        }

        for(PExpression e : copy)
        {
            e.apply(this);
            ids[i++] = ""+(idCounter-1);
        }

        String nodeid = ""+ idCounter;
        out += "id" + nodeid + "=";
        out += getClassName(node) +"()\n";
        idCounter++;

        for(i = 0 ; i<ids.length; i++)
            out += "id"+nodeid+".children.append(id"+ids[i]+")\n";
        out += "id"+nodeid+".idName = \""+idName+"\"\n";
    }


    public void caseADefinitionSubstitution(ADefinitionSubstitution node)
    {
        List<PExpression> copy = new ArrayList<PExpression>(node.getParameters());
        String[] ids = new String[copy.size()]; 
        String idName = "";
        int i=0;

        if(node.getDefLiteral() != null)
        {
            idName = node.getDefLiteral().toString();
        }

        for(PExpression e : copy)
        {
            e.apply(this);
            ids[i++] = ""+(idCounter-1);
        }

        String nodeid = ""+ idCounter;
        out += "id" + nodeid + "=";
        out += getClassName(node) +"()\n";
        idCounter++;

        for(i = 0 ; i<ids.length; i++)
            out += "id"+nodeid+".children.append(id"+ids[i]+")\n";
        out += "id"+nodeid+".idName = \""+idName+"\"\n";
    }

    public void caseAAssignSubstitution(AAssignSubstitution node)
    {
        List<PExpression> copy0 = new ArrayList<PExpression>(node.getLhsExpression());
        List<PExpression> copy1 = new ArrayList<PExpression>(node.getRhsExpressions());
        String[] ids = new String[copy0.size()+copy1.size()]; 
        String idName = "";
        int i=0;

        for(PExpression e : copy0)
        {
            e.apply(this);
            ids[i++] = ""+(idCounter-1);
        }


        for(PExpression e : copy1)
        {
            e.apply(this);
            ids[i++] = ""+(idCounter-1);
        }

        String nodeid = ""+ idCounter;
        out += "id" + nodeid + "=";
        out += getClassName(node) +"()\n";
        idCounter++;

        for(i = 0 ; i<ids.length; i++)
            out += "id"+nodeid+".children.append(id"+ids[i]+")\n";
        out += "id"+nodeid+".lhs_size = \""+copy0.size()+"\"\n";
        out += "id"+nodeid+".rhs_size = \""+copy1.size()+"\"\n";
    }


    public void caseAParallelSubstitution(AParallelSubstitution node)
    {
        List<Node> children = new ArrayList<Node>(node.getSubstitutions());
        printStdOut_manyChildren(node, children);
    }


    public void caseASequenceSubstitution(ASequenceSubstitution node)
    {
        List<Node> children = new ArrayList<Node>(node.getSubstitutions());
        printStdOut_manyChildren(node, children);
    }


    public void caseAChoiceSubstitution(AChoiceSubstitution node)
    {
        List<Node> children = new ArrayList<Node>(node.getSubstitutions());
        printStdOut_manyChildren(node, children);
    }


    public void caseAIfSubstitution(AIfSubstitution node)
    {
        List<Node> children = new ArrayList<Node>();
        if(node.getCondition()!=null)
            children.add(node.getCondition());
        if(node.getThen()!=null)
            children.add(node.getThen());
        if(node.getElsifSubstitutions()!=null)
            children.addAll(node.getElsifSubstitutions());
        if(node.getElse()!=null)
            children.add(node.getElse());
        printStdOut_manyChildren(node, children);
    }


    public void caseASelectSubstitution(ASelectSubstitution node)
    {
        List<Node> children = new ArrayList<Node>();
        if(node.getCondition()!=null)
            children.add(node.getCondition());
        if(node.getThen()!=null)
            children.add(node.getThen());
        if(node.getWhenSubstitutions()!=null)
            children.addAll(node.getWhenSubstitutions());
        if(node.getElse()!=null)
            children.add(node.getElse());
        printStdOut_manyChildren(node, children);
    }


    public void caseACaseSubstitution(ACaseSubstitution node)
    {
        List<Node> children = new ArrayList<Node>();
        if(node.getExpression()!=null)
            children.add(node.getExpression());
        if(node.getEitherExpr()!=null)
            children.addAll(node.getEitherExpr());
        if(node.getEitherSubst()!=null)
            children.add(node.getEitherSubst());
        if(node.getOrSubstitutions()!=null)
            children.addAll(node.getOrSubstitutions());
        if(node.getElse()!=null)
            children.add(node.getElse());
        printStdOut_manyChildren(node, children);

        out += "id"+(idCounter-1)+".expNum = "+node.getEitherExpr().size()+"\n";
    }


    public void caseACaseOrSubstitution(ACaseOrSubstitution node)
    {
        List<Node> children = new ArrayList<Node>(node.getExpressions());
        if(node.getSubstitution()!=null)
            children.add(node.getSubstitution());
        printStdOut_manyChildren(node, children);

        out += "id"+(idCounter-1)+".expNum = "+node.getExpressions().size()+"\n";
    }


    public void caseAVarSubstitution(AVarSubstitution node)
    {
        List<Node> children = new ArrayList<Node>(node.getIdentifiers());
        if(node.getSubstitution()!=null)
            children.add(node.getSubstitution());
        printStdOut_manyChildren(node, children);

        out += "id"+(idCounter-1)+".idNum = "+node.getIdentifiers().size()+"\n";
    }


    public void caseAAnySubstitution(AAnySubstitution node)
    {
        List<Node> children = new ArrayList<Node>(node.getIdentifiers());
        if(node.getWhere()!=null)
            children.add(node.getWhere());
        if(node.getThen()!=null)
            children.add(node.getThen());
        printStdOut_manyChildren(node, children);

        out += "id"+(idCounter-1)+".idNum = "+node.getIdentifiers().size()+"\n";
    }



    public void caseALetSubstitution(ALetSubstitution node)
    {
        List<Node> children = new ArrayList<Node>(node.getIdentifiers());
        if(node.getPredicate()!=null)
            children.add(node.getPredicate());
        if(node.getSubstitution()!=null)
            children.add(node.getSubstitution());
        printStdOut_manyChildren(node, children);

        out += "id"+(idCounter-1)+".idNum = "+node.getIdentifiers().size()+"\n";
    }


    public void caseAQuantifiedUnionExpression(AQuantifiedUnionExpression node)
    {
        List<Node> children = new ArrayList<Node>(node.getIdentifiers());
        if(node.getPredicates()!=null)
            children.add(node.getPredicates());
        if(node.getExpression()!=null)
            children.add(node.getExpression());
        printStdOut_manyChildren(node, children);

        out += "id"+(idCounter-1)+".idNum = "+node.getIdentifiers().size()+"\n";
    }


    public void caseAQuantifiedIntersectionExpression(AQuantifiedIntersectionExpression node)
    {
        List<Node> children = new ArrayList<Node>(node.getIdentifiers());
        if(node.getPredicates()!=null)
            children.add(node.getPredicates());
        if(node.getExpression()!=null)
            children.add(node.getExpression());
        printStdOut_manyChildren(node, children);

        out += "id"+(idCounter-1)+".idNum = "+node.getIdentifiers().size()+"\n";
    }


    public void caseAStructExpression(AStructExpression node)
    {
        List<Node> children = new ArrayList<Node>(node.getEntries());
        printStdOut_manyChildren(node, children);
    }


    public void caseARecExpression(ARecExpression node)
    {
        List<Node> children = new ArrayList<Node>(node.getEntries());
        printStdOut_manyChildren(node, children);
    }


    public void caseAExistentialQuantificationPredicate(AExistentialQuantificationPredicate node)
    {
        List<Node> children = new ArrayList<Node>(node.getIdentifiers());
        if(node.getPredicate()!=null)
            children.add(node.getPredicate());
        printStdOut_manyChildren(node, children);
    }


    public void caseAComprehensionSetExpression(AComprehensionSetExpression node)
    {
        List<Node> children = new ArrayList<Node>(node.getIdentifiers());
        if(node.getPredicates()!=null)
            children.add(node.getPredicates());
        printStdOut_manyChildren(node, children);
    }


    public void caseABecomesSuchSubstitution(ABecomesSuchSubstitution node)
    {
        List<Node> children = new ArrayList<Node>(node.getIdentifiers());
        if (node.getPredicate()!=null)
            children.add(node.getPredicate());
        printStdOut_manyChildren(node, children);
    }


    public void caseAUniversalQuantificationPredicate(AUniversalQuantificationPredicate node)
    {
        List<Node> children = new ArrayList<Node>(node.getIdentifiers());
        if (node.getImplication()!=null)
            children.add(node.getImplication());
        printStdOut_manyChildren(node, children);
    }


    public void caseASetExtensionExpression(ASetExtensionExpression node)
    {
        List<Node> children = new ArrayList<Node>(node.getExpressions());
        printStdOut_manyChildren(node, children);
    }


    public void caseACoupleExpression(ACoupleExpression node)
    {
        List<Node> children = new ArrayList<Node>(node.getList());
        printStdOut_manyChildren(node, children);
    }


    public void caseASequenceExtensionExpression(ASequenceExtensionExpression node)
    {
        List<Node> children = new ArrayList<Node>(node.getExpression());
        printStdOut_manyChildren(node, children);
    }


    public void caseAConstantsMachineClause(AConstantsMachineClause node)
    {
        List<Node> children = new ArrayList<Node>(node.getIdentifiers());
        printStdOut_manyChildren(node, children);
    }


    public void caseAEnumeratedSet(AEnumeratedSet node)
    {
        List<TIdentifierLiteral> copy0 = new ArrayList<TIdentifierLiteral>(node.getIdentifier());
        List<PExpression> copy1 = new ArrayList<PExpression>(node.getElements());
        String[] ids = new String[copy1.size()];
        int i=0;

        String idName = "";
        for(TIdentifierLiteral e : copy0)
        {
            // XXX
            e.apply(this);
            idName = idName + e.toString();
        }

        for(PExpression e : copy1)
        {
            e.apply(this);
            ids[i++] = ""+(idCounter-1);
        }


        String nodeid = ""+ idCounter;
        out += "id" + nodeid + "=";
        out += getClassName(node) +"()\n";
        idCounter++;

        for(i=0; i<copy1.size(); i++)
            out += "id"+nodeid+".children.append(id"+ids[i]+")\n";
        out += "id"+nodeid+".idName = \""+idName+"\"\n";
    }


    public void caseAAssertionsMachineClause(AAssertionsMachineClause node)
    {
        List<Node> children = new ArrayList<Node>(node.getPredicates());
        printStdOut_manyChildren(node, children);
    }


    public void caseADeferredSet(ADeferredSet node)
    {
        List<TIdentifierLiteral> copy = new ArrayList<TIdentifierLiteral>(node.getIdentifier());

        String idName = "";
        for(TIdentifierLiteral e : copy)
        {
            // XXX
            e.apply(this);
            idName = idName + e.toString();
        }

        String nodeid = ""+ idCounter;
        out += "id" + nodeid + "=";
        out += getClassName(node) +"()\n";
        idCounter++;
        out += "id"+nodeid+".idName = \""+idName+"\"\n";
    }


    public void caseAVariablesMachineClause(AVariablesMachineClause node)
    {
        List<Node> children = new ArrayList<Node>(node.getIdentifiers());
        printStdOut_manyChildren(node, children);
    }


    public void caseASetsMachineClause(ASetsMachineClause node)
    {
        List<Node> children = new ArrayList<Node>(node.getSetDefinitions());
        printStdOut_manyChildren(node, children);
    }

    public void caseAOperationsMachineClause(AOperationsMachineClause node)
    {
        List<Node> children = new ArrayList<Node>(node.getOperations());
        printStdOut_manyChildren(node, children);
    }


    public void caseAOperation(AOperation node)
    {
        List<PExpression> copy1 = new ArrayList<PExpression>(node.getReturnValues());
        List<TIdentifierLiteral> copy2 = new ArrayList<TIdentifierLiteral>(node.getOpName());
        List<PExpression> copy3 = new ArrayList<PExpression>(node.getParameters());
        String[] ids = new String[copy1.size()+copy3.size()+1];
        int i=0;
        for(PExpression e : copy1)
        {
            e.apply(this);
            ids[i++] = ""+(idCounter-1);
        }
        String idName = "";
        for(TIdentifierLiteral e : copy2)
        {
            e.apply(this);
            idName = idName + e.toString();
        }
        for(PExpression e : copy3)
        {
            e.apply(this);
            ids[i++] = ""+(idCounter-1);
        }
        if(node.getOperationBody() != null)
        {
            node.getOperationBody().apply(this);
            ids[i++] = ""+(idCounter-1);
        }
        String nodeid = ""+ idCounter;
        out += "id" + nodeid + "=";
        out += getClassName(node) +"()\n";
        idCounter++;

        int k = 0;
        for(i=0; i<copy1.size(); i++)
            out += "id"+nodeid+".children.append(id"+ids[k++]+")\n";
        for(i=0; i<copy3.size(); i++)
            out += "id"+nodeid+".children.append(id"+ids[k++]+")\n";
        if(node.getOperationBody() != null)
            out += "id"+nodeid+".children.append(id"+ids[k++]+")\n";
        out += "id"+nodeid+".opName = \""+idName+"\"\n";
        out += "id"+nodeid+".return_Num = "+copy1.size()+"\n";
        out += "id"+nodeid+".parameter_Num = "+copy3.size()+"\n";
    }


    public void caseAPrimedIdentifierExpression(APrimedIdentifierExpression node)
    {
        List<TIdentifierLiteral> copy = new ArrayList<TIdentifierLiteral>(node.getIdentifier());
        String[] ids = new String[copy.size()+1];
        int i=0;
        String grade="";
        for(TIdentifierLiteral e : copy)
        {
            e.apply(this);
            ids[i++] = ""+(idCounter-1);
        }
        if(node.getGrade() != null)
        {
            grade = node.getGrade().toString();
        }
        String nodeid = ""+ idCounter;
        out += "id" + nodeid + "=";
        out += getClassName(node) +"()\n";
        idCounter++;

        i = 0;
        for(int k=0; k<copy.size(); k++)
            out += "id"+nodeid+".children.append(id"+ids[i++]+")\n";
        if(node.getGrade() != null)
            out += "id"+nodeid+".grade = "+grade+"\n";
    }


    public void caseABecomesElementOfSubstitution(ABecomesElementOfSubstitution node)
    {
        List<Node> children = new ArrayList<Node>(node.getIdentifiers());
        if (node.getSet()!=null)
            children.add(node.getSet());
        printStdOut_manyChildren(node, children);
    }


    public void caseAFunctionExpression(AFunctionExpression node)
    {
        List<Node> children = new ArrayList<Node>();
        children.add(node.getIdentifier());
        if (node.getParameters()!=null)
            children.addAll(node.getParameters());
        printStdOut_manyChildren(node, children);
    }


    public void caseAPowerOfExpression(APowerOfExpression node)
    {
        printStdOut_twoChildren(node, node.getLeft(), node.getRight());
    }


    public void caseARecordFieldExpression(ARecordFieldExpression node)
    {
        printStdOut_twoChildren(node, node.getRecord(), node.getIdentifier());
    }


    public void caseARecEntry(ARecEntry node)
    {
        printStdOut_twoChildren(node, node.getIdentifier(),  node.getValue());
    }

    public void caseAPreconditionSubstitution(APreconditionSubstitution node)
    {
        printStdOut_twoChildren(node, node.getPredicate(),  node.getSubstitution());
    }


    public void caseAAssertionSubstitution(AAssertionSubstitution node)
    {
        printStdOut_twoChildren(node, node.getPredicate(),  node.getSubstitution());
    }


    public void caseAIfElsifSubstitution(AIfElsifSubstitution node)
    {
        printStdOut_twoChildren(node,  node.getCondition(),  node.getThenSubstitution());
    }


    public void caseASelectWhenSubstitution(ASelectWhenSubstitution node)
    {
        printStdOut_twoChildren(node,  node.getCondition(),  node.getSubstitution());
    }


    public void caseAIntervalExpression(AIntervalExpression node)
    {
        printStdOut_twoChildren(node,  node.getLeftBorder(),  node.getRightBorder());
    }


    public void caseARestrictFrontExpression(ARestrictFrontExpression node)
    {
        printStdOut_twoChildren(node, node.getLeft(), node.getRight());
    }


    public void caseARestrictTailExpression(ARestrictTailExpression node)
    {
        printStdOut_twoChildren(node, node.getLeft(), node.getRight());
    }


    public void caseAPartialFunctionExpression(APartialFunctionExpression node)
    {
        printStdOut_twoChildren(node, node.getLeft(), node.getRight());
    }


    public void caseAConcatExpression(AConcatExpression node)
    {
        printStdOut_twoChildren(node, node.getLeft(), node.getRight());
    }


    public void caseATotalFunctionExpression(ATotalFunctionExpression node)
    {
        printStdOut_twoChildren(node, node.getLeft(), node.getRight());
    }


    public void caseAPartialInjectionExpression(APartialInjectionExpression node)
    {
        printStdOut_twoChildren(node, node.getLeft(), node.getRight());
    }


    public void caseAPartialSurjectionExpression(APartialSurjectionExpression node)
    {
        printStdOut_twoChildren(node, node.getLeft(), node.getRight());
    }


    public void caseATotalSurjectionExpression(ATotalSurjectionExpression node)
    {
        printStdOut_twoChildren(node, node.getLeft(), node.getRight());
    }


    public void caseATotalBijectionExpression(ATotalBijectionExpression node)
    {
        printStdOut_twoChildren(node, node.getLeft(), node.getRight());
    }


    public void caseATotalInjectionExpression(ATotalInjectionExpression node)
    {
        printStdOut_twoChildren(node, node.getLeft(), node.getRight());
    }


    public void caseAPartialBijectionExpression(APartialBijectionExpression node)
    {
        printStdOut_twoChildren(node, node.getLeft(), node.getRight());
    }


    public void caseARelationsExpression(ARelationsExpression node)
    {
        printStdOut_twoChildren(node, node.getLeft(), node.getRight());
    }


    public void caseAAddExpression(AAddExpression node)
    {
        printStdOut_twoChildren(node, node.getLeft(), node.getRight());
    }


    public void caseAMinusOrSetSubtractExpression(AMinusOrSetSubtractExpression node)
    {
        printStdOut_twoChildren(node, node.getLeft(), node.getRight());
    }


    public void caseASetSubtractionExpression(ASetSubtractionExpression node)
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


    public void caseAInsertFrontExpression(AInsertFrontExpression node)
    {
        printStdOut_twoChildren(node, node.getLeft(), node.getRight());
    }


    public void caseAInsertTailExpression(AInsertTailExpression node)
    {
        printStdOut_twoChildren(node, node.getLeft(), node.getRight());
    }


    public void caseAIterationExpression(AIterationExpression node)
    {
        printStdOut_twoChildren(node, node.getLeft(), node.getRight());
    }


    public void caseATransFunctionExpression(ATransFunctionExpression node)
    {
        printStdOut_oneChild(node, node.getExpression());
    }


    public void caseATransRelationExpression(ATransRelationExpression node)
    {
        printStdOut_oneChild(node, node.getExpression());
    }


    public void caseABlockSubstitution(ABlockSubstitution node)
    {
        printStdOut_oneChild(node, node.getSubstitution());
    }


    public void caseAChoiceOrSubstitution(AChoiceOrSubstitution node)
    {
        printStdOut_oneChild(node, node.getSubstitution());
    }


    public void caseAUnaryExpression(AUnaryExpression node)
    {
        printStdOut_oneChild(node, node.getExpression());
    }


    public void caseAConvertBoolExpression(AConvertBoolExpression node)
    {
        printStdOut_oneChild(node, node.getPredicate());
    }


    public void caseAGeneralConcatExpression(AGeneralConcatExpression node)
    {
        printStdOut_oneChild(node, node.getExpression());
    }


    public void caseAReflexiveClosureExpression(AReflexiveClosureExpression node)
    {
        printStdOut_oneChild(node, node.getExpression());
    }


    public void caseAClosureExpression(AClosureExpression node)
    {
        printStdOut_oneChild(node, node.getExpression());
    }


    public void caseAGeneralUnionExpression(AGeneralUnionExpression node)
    {
        printStdOut_oneChild(node, node.getExpression());
    }


    public void caseAGeneralIntersectionExpression(AGeneralIntersectionExpression node)
    {
        printStdOut_oneChild(node, node.getExpression());
    }


    public void caseAConstraintsMachineClause(AConstraintsMachineClause node)
    {
        printStdOut_oneChild(node, node.getPredicates());
    }


    public void caseAPropertiesMachineClause(APropertiesMachineClause node)
    {
        printStdOut_oneChild(node, node.getPredicates());
    }


    public void caseAFirstExpression(AFirstExpression node)
    {
        printStdOut_oneChild(node, node.getExpression());
    }


    public void caseALastExpression(ALastExpression node)
    {
        printStdOut_oneChild(node, node.getExpression());
    }


    public void caseATailExpression(ATailExpression node)
    {
        printStdOut_oneChild(node, node.getExpression());
    }


    public void caseAFrontExpression(AFrontExpression node)
    {
        printStdOut_oneChild(node, node.getExpression());
    }


    public void caseACardExpression(ACardExpression node)
    {
        printStdOut_oneChild(node, node.getExpression());
    }


    public void caseASizeExpression(ASizeExpression node)
    {
        printStdOut_oneChild(node, node.getExpression());
    }


    public void caseARevExpression(ARevExpression node)
    {
        printStdOut_oneChild(node, node.getExpression());
    }


    public void caseASeqExpression(ASeqExpression node)
    {
        printStdOut_oneChild(node, node.getExpression());
    }


    public void caseASeq1Expression(ASeq1Expression node)
    {
        printStdOut_oneChild(node, node.getExpression());
    }


    public void caseAIseqExpression(AIseqExpression node)
    {
        printStdOut_oneChild(node, node.getExpression());
    }


    public void caseAIseq1Expression(AIseq1Expression node)
    {
        printStdOut_oneChild(node, node.getExpression());
    }


    public void caseAPermExpression(APermExpression node)
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


    public void caseAInitialisationMachineClause(AInitialisationMachineClause node)
    {
        printStdOut_oneChild(node, node.getSubstitutions());
    }


    public void caseAInvariantMachineClause(AInvariantMachineClause node)
    {
        printStdOut_oneChild(node, node.getPredicates());
    }


    public void caseANegationPredicate(ANegationPredicate node)
    {
        printStdOut_oneChild(node, node.getPredicate());
    }


    public void caseADomainExpression(ADomainExpression node)
    {
        printStdOut_oneChild(node, node.getExpression());
    }


    public void caseARangeExpression(ARangeExpression node)
    {
        printStdOut_oneChild(node, node.getExpression());
    }


    public void caseAIdentityExpression(AIdentityExpression node)
    {
        printStdOut_oneChild(node, node.getExpression());
    }


    public void caseAPowSubsetExpression(APowSubsetExpression node)
    {
        printStdOut_oneChild(node, node.getExpression());
    }


    public void caseAPow1SubsetExpression(APow1SubsetExpression node)
    {
        printStdOut_oneChild(node, node.getExpression());
    }


    public void caseAFinSubsetExpression(AFinSubsetExpression node)
    {
        printStdOut_oneChild(node, node.getExpression());
    }


    public void caseAFin1SubsetExpression(AFin1SubsetExpression node)
    {
        printStdOut_oneChild(node, node.getExpression());
    }


    public void caseAMinExpression(AMinExpression node)
    {
        printStdOut_oneChild(node, node.getExpression());
    }


    public void caseAMaxExpression(AMaxExpression node)
    {
        printStdOut_oneChild(node, node.getExpression());
    }


    public void caseAReverseExpression(AReverseExpression node)
    {
        printStdOut_oneChild(node, node.getExpression());
    }


    public void caseAPredicateParseUnit(APredicateParseUnit node)
    {
        printStdOut_oneChild(node, node.getPredicate());
        out += "root = id"+(idCounter-1)+ "\n";
    }


    public void caseAOverwriteExpression(AOverwriteExpression node)
    {
        printStdOut_twoChildren(node, node.getLeft(), node.getRight());
    }


    public void caseADirectProductExpression(ADirectProductExpression node)
    {
        printStdOut_twoChildren(node, node.getLeft(), node.getRight());
    }


    public void caseAParallelProductExpression(AParallelProductExpression node)
    {
        printStdOut_twoChildren(node, node.getLeft(), node.getRight());
    }


    public void caseAFirstProjectionExpression(AFirstProjectionExpression node)
    {
        printStdOut_twoChildren(node, node.getExp1(), node.getExp2());
    }


    public void caseASecondProjectionExpression(ASecondProjectionExpression node)
    {
        printStdOut_twoChildren(node, node.getExp1(), node.getExp2());
    }


    public void caseAImageExpression(AImageExpression node)
    {
        printStdOut_twoChildren(node, node.getLeft(), node.getRight());
    }


    public void caseACompositionExpression(ACompositionExpression node)
    {
        printStdOut_twoChildren(node, node.getLeft(), node.getRight());
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


    public void caseADomainRestrictionExpression(ADomainRestrictionExpression node)
    {
        printStdOut_twoChildren(node, node.getLeft(), node.getRight());
    }


    public void caseADomainSubtractionExpression(ADomainSubtractionExpression node)
    {
        printStdOut_twoChildren(node, node.getLeft(), node.getRight());
    }


    public void caseARangeRestrictionExpression(ARangeRestrictionExpression node)
    {
        printStdOut_twoChildren(node, node.getLeft(), node.getRight());
    }


    public void caseARangeSubtractionExpression(ARangeSubtractionExpression node)
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


    // visits and prints the node-List first
    private void printStdOut_manyChildren(Node node, List<Node> children)
    {
        String[] ids = new String[children.size()];
        int i=0;
        for(Node n : children)
        {
            n.apply(this);
            ids[i++] = "" + (idCounter-1);
        }

        String nodeid = "" + idCounter;
        out += "id" + nodeid + "=";
        out += getClassName(node) +"()\n";
        idCounter++;

        for(i=0; i<ids.length; i++)
            out += "id"+nodeid+".children.append(id"+ids[i]+")\n";
    }
}
