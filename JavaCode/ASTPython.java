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
        out += "id"+ (idCounter++) +"=";
        out += "AIdentifierExpression(\"";
        out += node.getIdentifier().toString().replace("[","").replace("]","") + "\")\n";
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

    public void outStart(Start node)
    {
        // dont add a start node now
        // dont call defaultOut(Node)
    }


    public void caseAGeneralSumExpression(AGeneralSumExpression node)
    {
        List<PExpression> copy = new ArrayList<PExpression>(node.getIdentifiers());
        String[] ids = new String[copy.size()+2];
        int i=0;
        for(PExpression e : copy)
        {
            e.apply(this);
            ids[i++] = ""+(idCounter-1);
        }
        if(node.getPredicates() != null)
        {
            node.getPredicates().apply(this);
            ids[copy.size()] = ""+(idCounter-1);
        }
        if(node.getExpression() != null)
        {
            node.getExpression().apply(this);
            ids[copy.size()+1] = ""+(idCounter-1);
        }

        String nodeid = ""+ idCounter;
        out += "id" + nodeid + "=";
        out += getClassName(node) +"()\n";
        idCounter++;

        for(i=0; i<ids.length-2; i++)
            out += "id"+nodeid+".children.append(id"+ids[i]+")\n";
        if(node.getPredicates() != null)
            out += "id"+nodeid+".children.append(id"+ids[copy.size()]+")\n";
        if(node.getExpression() != null)
            out += "id"+nodeid+".children.append(id"+ids[copy.size()+1]+")\n";
    }


    public void caseAGeneralProductExpression(AGeneralProductExpression node)
    {
        List<PExpression> copy = new ArrayList<PExpression>(node.getIdentifiers());
        String[] ids = new String[copy.size()+2];
        int i=0;
        for(PExpression e : copy)
        {
            e.apply(this);
            ids[i++] = ""+(idCounter-1);
        }
        if(node.getPredicates() != null)
        {
            node.getPredicates().apply(this);
            ids[copy.size()] = ""+(idCounter-1);
        }
        if(node.getExpression() != null)
        {
            node.getExpression().apply(this);
            ids[copy.size()+1] = ""+(idCounter-1);
        }

        String nodeid = ""+ idCounter;
        out += "id" + nodeid + "=";
        out += getClassName(node) +"()\n";
        idCounter++;

        for(i=0; i<ids.length-2; i++)
            out += "id"+nodeid+".children.append(id"+ids[i]+")\n";
        if(node.getPredicates() != null)
            out += "id"+nodeid+".children.append(id"+ids[copy.size()]+")\n";
        if(node.getExpression() != null)
            out += "id"+nodeid+".children.append(id"+ids[copy.size()+1]+")\n";
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


    public void caseAExistentialQuantificationPredicate(AExistentialQuantificationPredicate node)
    {
        printStdOut_manyChildren(node, new ArrayList<PExpression>(node.getIdentifiers()), node.getPredicate());
    }


    public void caseAComprehensionSetExpression(AComprehensionSetExpression node)
    {
        printStdOut_manyChildren(node, new ArrayList<PExpression>(node.getIdentifiers()), node.getPredicates());
    }


    public void caseAUniversalQuantificationPredicate(AUniversalQuantificationPredicate node)
    {
        printStdOut_manyChildren(node, new ArrayList<PExpression>(node.getIdentifiers()), node.getImplication());
    }


    public void caseASetExtensionExpression(ASetExtensionExpression node)
    {
        printStdOut_manyChildren(node, new ArrayList<PExpression>(node.getExpressions()),null);
    }


    public void caseACoupleExpression(ACoupleExpression node)
    {
        printStdOut_manyChildren(node, new ArrayList<PExpression>(node.getList()),null);
    }


    public void caseASequenceExtensionExpression(ASequenceExtensionExpression node)
    {
        printStdOut_manyChildren(node, new ArrayList<PExpression>(node.getExpression()),null);
    }


    public void caseAConstantsMachineClause(AConstantsMachineClause node)
    {
        printStdOut_manyChildren(node, new ArrayList<PExpression>(node.getIdentifiers()),null);
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


    // sp. case: PPredicate
    public void caseAAssertionsMachineClause(AAssertionsMachineClause node)
    {
        List<PPredicate> copy = new ArrayList<PPredicate>(node.getPredicates());
        String[] ids = new String[copy.size()];
        int i=0;
        for(PPredicate e : copy)
        {
            e.apply(this);
            ids[i++] = ""+(idCounter-1);
        }

        String nodeid = ""+ idCounter;
        out += "id" + nodeid + "=";
        out += getClassName(node) +"()\n";
        idCounter++;

        for(i=0; i<copy.size(); i++)
            out += "id"+nodeid+".children.append(id"+ids[i]+")\n";
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
        List<PExpression> copy = new ArrayList<PExpression>(node.getIdentifiers());

        String[] ids = new String[copy.size()];
        int i=0;
        for(PExpression e : copy)
        {
            e.apply(this);
            ids[i++] = ""+(idCounter-1);
        }

        String nodeid = ""+ idCounter;
        out += "id" + nodeid + "=";
        out += getClassName(node) +"()\n";
        idCounter++;

        for(i=0; i<copy.size(); i++)
            out += "id"+nodeid+".children.append(id"+ids[i]+")\n";
    }


    public void caseASetsMachineClause(ASetsMachineClause node)
    {
        List<PSet> copy = new ArrayList<PSet>(node.getSetDefinitions());

        String[] ids = new String[copy.size()];
        int i=0;
        for(PSet e : copy)
        {
            e.apply(this);
            ids[i++] = ""+(idCounter-1);
        }

        String nodeid = ""+ idCounter;
        out += "id" + nodeid + "=";
        out += getClassName(node) +"()\n";
        idCounter++;

        for(i=0; i<copy.size(); i++)
            out += "id"+nodeid+".children.append(id"+ids[i]+")\n";
    }


    public void caseAFunctionExpression(AFunctionExpression node)
    {
        printStdOut_manyChildren2(node, new ArrayList<PExpression>(node.getParameters()), node.getIdentifier());
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
    private void printStdOut_manyChildren(Node node, List<PExpression> copy, Node extra)
    {
        String[] ids = new String[copy.size()+1];
        int i=0;
        for(PExpression e : copy)
        {
            e.apply(this);
            ids[i++] = ""+(idCounter-1);
        }
        if(extra!=null)
        {
            extra.apply(this);
            ids[copy.size()] = ""+(idCounter-1);
        }

        String nodeid = ""+ idCounter;
        out += "id" + nodeid + "=";
        out += getClassName(node) +"()\n";
        idCounter++;

        for(i=0; i<ids.length-1; i++)
            out += "id"+nodeid+".children.append(id"+ids[i]+")\n";
        if(extra!=null)
            out += "id"+nodeid+".children.append(id"+ids[copy.size()]+")\n";
    }


    // visits and prints the extra-Node first
    // TODO: refactor ids
    private void printStdOut_manyChildren2(Node node, List<PExpression> copy, Node extra)
    {
        String[] ids = new String[copy.size()+1];
        int i=0;
        if(extra!=null)
        {
            extra.apply(this);
            ids[i++] = ""+(idCounter-1);
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

        if(extra!=null)
            out += "id"+nodeid+".children.append(id"+ids[0]+")\n";
        for(i=1; i<ids.length; i++)
            out += "id"+nodeid+".children.append(id"+ids[i]+")\n";

    }
}
