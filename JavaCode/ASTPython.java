// AST Walker
package de.be4.classicalb.core.parser.analysis.python;

import de.be4.classicalb.core.parser.analysis.DepthFirstAdapter;
import de.be4.classicalb.core.parser.node.*;
import java.util.ArrayList;
import java.util.List;
// walks the tree and prints a pythonlike AST

public class ASTPython extends DepthFirstAdapter{
    public StringBuilder out;
    private int idCounter = 0;
    
    public ASTPython()
    {
        out = new StringBuilder();
    }

    private String getClassName(Node node)
    {
        String clsname = node.getClass().getName();
        int mid= clsname.lastIndexOf ('.') + 1;
        return clsname.substring(mid);
    }



    public void outAIntegerExpression(AIntegerExpression node)
    {
        out.append("id"+ (idCounter++) +"=");
        out.append("AIntegerExpression(");
        out.append(node.getLiteral().toString() + ")\n");
    }


    public void outAIdentifierExpression(AIdentifierExpression node)
    {
        // FIXME: some bug with a space at the end
        out.append("id"+ (idCounter++) +"=");
        out.append("AIdentifierExpression(\"");
        out.append(node.getIdentifier().toString().replace("[","").replace("]","") + "\")\n");
    }


    public void caseAStringExpression(AStringExpression node)
    {
        out.append("id"+ (idCounter++) +"=");
        out.append("AStringExpression(\"");
        out.append(node.getContent().getText()+ "\")\n");
    }


    public void caseAStringSetExpression(AStringSetExpression node)
    {
        out.append("id"+ (idCounter++) +"=");
        out.append("AStringSetExpression()\n");
    }


    public void outAEmptySetExpression(AEmptySetExpression node)
    {
        out.append("id"+ (idCounter++) +"=");
        out.append("AEmptySetExpression()\n");
    }


    public void caseAEmptySequenceExpression(AEmptySequenceExpression node)
    {
        out.append("id"+ (idCounter++) +"=");
        out.append("AEmptySequenceExpression()\n");
    }


    public void caseAIntegerSetExpression(AIntegerSetExpression node)
    {
        out.append("id"+ (idCounter++) +"=");
        out.append("AIntegerSetExpression()\n");
    }

    public void caseANatSetExpression(ANatSetExpression node)
    {
        out.append("id"+ (idCounter++) +"=");
        out.append("ANatSetExpression()\n");
    }

    public void caseANaturalSetExpression(ANaturalSetExpression node)
    {
        out.append("id"+ (idCounter++) +"=");
        out.append("ANaturalSetExpression()\n");
    }


    public void caseAIntSetExpression(AIntSetExpression node)
    {
        out.append("id"+ (idCounter++) +"=");
        out.append("AIntSetExpression()\n");
    }
    
        
    public void caseANatural1SetExpression(ANatural1SetExpression node)
    {
        out.append("id"+ (idCounter++) +"=");
        out.append("ANatural1SetExpression()\n");
    }
    
    
    public void caseANat1SetExpression(ANat1SetExpression node)
    {
        out.append("id"+ (idCounter++) +"=");
        out.append("ANat1SetExpression()\n");
    }


    public void caseATrueExpression(ATrueExpression node)
    {
        out.append("id"+ (idCounter++) +"=");
        out.append("ATrueExpression()\n");
    }


    public void caseABoolSetExpression(ABoolSetExpression node)
    {
        out.append("id"+ (idCounter++) +"=");
        out.append("ABoolSetExpression()\n");
    }


    public void caseAFalseExpression(AFalseExpression node)
    {
        out.append("id"+ (idCounter++) +"=");
        out.append("AFalseExpression()\n");
    }


    public void caseASkipSubstitution(ASkipSubstitution node)
    {
        out.append("id"+ (idCounter++) +"=");
        out.append("ASkipSubstitution()\n");
    }


    public void caseAMinIntExpression(AMinIntExpression node)
    {
        out.append("id"+ (idCounter++) +"=");
        out.append("AMinIntExpression()\n");
    }


    public void caseAMaxIntExpression(AMaxIntExpression node)
    {
        out.append("id"+ (idCounter++) +"=");
        out.append("AMaxIntExpression()\n");
    }


    public void caseASuccessorExpression(ASuccessorExpression node)
    {
        out.append("id"+ (idCounter++) +"=");
        out.append("ASuccessorExpression()\n");
    }


    public void caseAPredecessorExpression(APredecessorExpression node)
    {
        out.append("id"+ (idCounter++) +"=");
        out.append("APredecessorExpression()\n");
    }


    public void outStart(Start node)
    {
        // dont add a start node now
        // dont call defaultOut(Node)
    }


    public void caseAPredicateParseUnit(APredicateParseUnit node)
    {
        printStdOut_oneChild(node, node.getPredicate());
        out.append("root = id"+(idCounter-1)+ "\n");
    }
    

    public void caseAExpressionParseUnit(AExpressionParseUnit node)
    {
        printStdOut_oneChild(node, node.getExpression());
        out.append("root = id"+(idCounter-1)+ "\n");
    }


    public void caseAAbstractMachineParseUnit(AAbstractMachineParseUnit node)
    {
        List<Node> children = new ArrayList<Node>();
        if(node.getHeader()!=null)
            children.add(node.getHeader());
        if(node.getMachineClauses()!=null)
            children.addAll(node.getMachineClauses());
        printStdOut_manyChildren(node, children);

        String mtype="";
        if(node.getType() != null)
        {
            mtype = node.getType().toString();
        }
        out.append("id"+(idCounter-1)+".type = \""+mtype+"\"\n");

        out.append("root = id"+(idCounter-1)+ "\n");
    }


    public void caseARefinementMachineParseUnit(ARefinementMachineParseUnit node)
    {
        List<Node> children = new ArrayList<Node>();
        if(node.getHeader()!=null)
            children.add(node.getHeader());
        if(node.getMachineClauses()!=null)
            children.addAll(node.getMachineClauses());
        printStdOut_manyChildren(node, children);

        String refines="";
        if(node.getRefMachine() != null)
        {
            refines = node.getRefMachine().toString();
        }
        out.append("id"+(idCounter-1)+".refines = \""+refines+"\"\n");

        out.append("root = id"+(idCounter-1)+ "\n");
    }


    public void caseAMachineHeader(AMachineHeader node)
    {
        List<Node> children = new ArrayList<Node>();
        if(node.getParameters()!=null)
            children.addAll(node.getParameters());
        printStdOut_manyChildren(node, children);

        String idName = "";
        for(TIdentifierLiteral e : node.getName())
        {
            // XXX
            e.apply(this);
            idName = idName + e.toString();
        }
        out.append("id"+(idCounter-1)+".idName = \""+idName+"\"\n");
    }



    public void caseASubstitutionDefinition(ASubstitutionDefinition node)
    {
        List<Node> children = new ArrayList<Node>();
        if(node.getParameters()!=null)
            children.addAll(node.getParameters());
        if(node.getRhs()!=null)
            children.add(node.getRhs());
        printStdOut_manyChildren(node, children);

        String idName = "";
        if(node.getName() != null)
        {
            idName = node.getName().toString();
        }
        out.append("id"+(idCounter-1)+".idName = \""+idName+"\"\n");
        if (node.getParameters()!=null)
            out.append("id"+(idCounter-1)+".paraNum = "+node.getParameters().size()+"\n");
        else
            out.append("id"+(idCounter-1)+".paraNum = 0");
    }


    public void caseAPredicateDefinition(APredicateDefinition node)
    {
        List<Node> children = new ArrayList<Node>();
        if(node.getParameters()!=null)
            children.addAll(node.getParameters());
        if(node.getRhs()!=null)
            children.add(node.getRhs());
        printStdOut_manyChildren(node, children);

        String idName = "";
        if(node.getName() != null)
        {
            idName = node.getName().toString();
        }
        out.append("id"+(idCounter-1)+".idName = \""+idName+"\"\n");
        if (node.getParameters()!=null)
            out.append("id"+(idCounter-1)+".paraNum = "+node.getParameters().size()+"\n");
        else
            out.append("id"+(idCounter-1)+".paraNum = 0");
    }


    public void caseAExpressionDefinition(AExpressionDefinition node)
    {
        List<Node> children = new ArrayList<Node>();
        if(node.getParameters()!=null)
            children.addAll(node.getParameters());
        if(node.getRhs()!=null)
            children.add(node.getRhs());
        printStdOut_manyChildren(node, children);

        String idName = "";
        if(node.getName() != null)
        {
            idName = node.getName().toString();
        }
        out.append("id"+(idCounter-1)+".idName = \""+idName+"\"\n");
        if (node.getParameters()!=null)
            out.append("id"+(idCounter-1)+".paraNum = "+node.getParameters().size()+"\n");
        else
            out.append("id"+(idCounter-1)+".paraNum = 0");
    }


    public void caseADefinitionExpression(ADefinitionExpression node)
    {
        List<Node> children = new ArrayList<Node>();
        if(node.getParameters()!=null)
            children.addAll(node.getParameters());
        printStdOut_manyChildren(node, children);

        String idName = "";
        if(node.getDefLiteral() != null)
        {
            idName = node.getDefLiteral().toString();
        }
        out.append("id"+(idCounter-1)+".idName = \""+idName+"\"\n");
    }


    public void caseADefinitionPredicate(ADefinitionPredicate node)
    {
        List<Node> children = new ArrayList<Node>();
        if(node.getParameters()!=null)
            children.addAll(node.getParameters());
        printStdOut_manyChildren(node, children);

        String idName = "";
        if(node.getDefLiteral() != null)
        {
            idName = node.getDefLiteral().toString();
        }
        out.append("id"+(idCounter-1)+".idName = \""+idName+"\"\n");
    }


    public void caseADefinitionSubstitution(ADefinitionSubstitution node)
    {
        List<Node> children = new ArrayList<Node>();
        if(node.getParameters()!=null)
            children.addAll(node.getParameters());
        printStdOut_manyChildren(node, children);

        String idName = "";
        if(node.getDefLiteral() != null)
        {
            idName = node.getDefLiteral().toString();
        }
        out.append("id"+(idCounter-1)+".idName = \""+idName+"\"\n");
    }


    public void caseAAssignSubstitution(AAssignSubstitution node)
    {
        List<Node> children = new ArrayList<Node>();
        if(node.getLhsExpression()!=null)
            children.addAll(node.getLhsExpression());
        if(node.getRhsExpressions()!=null)
            children.addAll(node.getRhsExpressions());
        printStdOut_manyChildren(node, children);

        out.append("id"+(idCounter-1)+".lhs_size = \""+node.getLhsExpression().size()+"\"\n");
        out.append("id"+(idCounter-1)+".rhs_size = \""+node.getRhsExpressions().size()+"\"\n");
    }


    public void caseAEnumeratedSet(AEnumeratedSet node)
    {
        List<Node> children = new ArrayList<Node>();
        if(node.getElements()!=null)
            children.addAll(node.getElements());
        printStdOut_manyChildren(node, children);

        String idName = "";
        for(TIdentifierLiteral e : node.getIdentifier())
        {
            // XXX
            e.apply(this);
            idName = idName + e.toString();
        }
        out.append("id"+(idCounter-1)+".idName = \""+idName+"\"\n");
    }


    public void caseADeferredSet(ADeferredSet node)
    {
        String idName = "";
        for(TIdentifierLiteral e : node.getIdentifier())
        {
            // XXX
            e.apply(this);
            idName = idName + e.toString();
        }

        String nodeid = ""+ idCounter;
        out.append("id" + nodeid + "=");
        out.append(getClassName(node) +"()\n");
        idCounter++;
        out.append("id"+nodeid+".idName = \""+idName+"\"\n");
    }


    public void caseAOperation(AOperation node)
    {
        List<Node> children = new ArrayList<Node>();
        if(node.getReturnValues()!=null)
            children.addAll(node.getReturnValues());
        if(node.getParameters()!=null)
            children.addAll(node.getParameters());
        if(node.getOperationBody()!=null)
            children.add(node.getOperationBody());
        printStdOut_manyChildren(node, children);

        String idName = "";
        for(TIdentifierLiteral e : node.getOpName())
        {
            e.apply(this);
            idName = idName + e.toString();
        }
        out.append("id"+(idCounter-1)+".opName = \""+idName+"\"\n");
        out.append("id"+(idCounter-1)+".return_Num = "+node.getReturnValues().size()+"\n");
        out.append("id"+(idCounter-1)+".parameter_Num = "+node.getParameters().size()+"\n");
    }


    public void caseAPrimedIdentifierExpression(APrimedIdentifierExpression node)
    {
        List<Node> children = new ArrayList<Node>(node.getIdentifier());
        printStdOut_manyChildren(node, children);

        if(node.getGrade() != null)
            out.append("id"+(idCounter-1)+".grade = "+node.getGrade()+"\n");
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

        out.append("id"+(idCounter-1)+".expNum = "+node.getEitherExpr().size()+"\n");
    }


    public void caseACaseOrSubstitution(ACaseOrSubstitution node)
    {
        List<Node> children = new ArrayList<Node>(node.getExpressions());
        if(node.getSubstitution()!=null)
            children.add(node.getSubstitution());
        printStdOut_manyChildren(node, children);

        out.append("id"+(idCounter-1)+".expNum = "+node.getExpressions().size()+"\n");
    }


    public void caseAVarSubstitution(AVarSubstitution node)
    {
        List<Node> children = new ArrayList<Node>(node.getIdentifiers());
        if(node.getSubstitution()!=null)
            children.add(node.getSubstitution());
        printStdOut_manyChildren(node, children);

        out.append("id"+(idCounter-1)+".idNum = "+node.getIdentifiers().size()+"\n");
    }


    public void caseAAnySubstitution(AAnySubstitution node)
    {
        List<Node> children = new ArrayList<Node>(node.getIdentifiers());
        if(node.getWhere()!=null)
            children.add(node.getWhere());
        if(node.getThen()!=null)
            children.add(node.getThen());
        printStdOut_manyChildren(node, children);

        out.append("id"+(idCounter-1)+".idNum = "+node.getIdentifiers().size()+"\n");
    }



    public void caseALetSubstitution(ALetSubstitution node)
    {
        List<Node> children = new ArrayList<Node>(node.getIdentifiers());
        if(node.getPredicate()!=null)
            children.add(node.getPredicate());
        if(node.getSubstitution()!=null)
            children.add(node.getSubstitution());
        printStdOut_manyChildren(node, children);

        out.append("id"+(idCounter-1)+".idNum = "+node.getIdentifiers().size()+"\n");
    }


    public void caseAQuantifiedUnionExpression(AQuantifiedUnionExpression node)
    {
        List<Node> children = new ArrayList<Node>(node.getIdentifiers());
        if(node.getPredicates()!=null)
            children.add(node.getPredicates());
        if(node.getExpression()!=null)
            children.add(node.getExpression());
        printStdOut_manyChildren(node, children);

        out.append("id"+(idCounter-1)+".idNum = "+node.getIdentifiers().size()+"\n");
    }


    public void caseAQuantifiedIntersectionExpression(AQuantifiedIntersectionExpression node)
    {
        List<Node> children = new ArrayList<Node>(node.getIdentifiers());
        if(node.getPredicates()!=null)
            children.add(node.getPredicates());
        if(node.getExpression()!=null)
            children.add(node.getExpression());
        printStdOut_manyChildren(node, children);

        out.append("id"+(idCounter-1)+".idNum = "+node.getIdentifiers().size()+"\n");
    }


    public void caseAMachineReference(AMachineReference node)
    {
        List<Node> children = new ArrayList<Node>();
        if(node.getParameters()!=null)
            children.addAll(node.getParameters());
        printStdOut_manyChildren(node, children);

        String idName = "";
        for(TIdentifierLiteral e : node.getMachineName())
        {
            // XXX
            e.apply(this);
            idName = idName + e.toString();
        }
        out.append("id"+(idCounter-1)+".idName = \""+idName+"\"\n");
    }


    public void caseAOpSubstitution(AOpSubstitution node)
    {
        List<Node> children = new ArrayList<Node>();
        if(node.getParameters()!=null)
            children.addAll(node.getParameters());
        printStdOut_manyChildren(node, children);

        String idName="";
        if(node.getName() != null)
        {
            idName = node.getName().toString();
        }
        out.append("id"+(idCounter-1)+".idName = \""+idName+"\"\n");
    }


    public void caseAPromotesMachineClause(APromotesMachineClause node)
    {
        List<Node> children = new ArrayList<Node>();
        if(node.getMachineNames()!=null)
            children.addAll(node.getMachineNames());
        printStdOut_manyChildren(node, children);
    }

    public void caseAIncludesMachineClause(AIncludesMachineClause node)
    {
        List<Node> children = new ArrayList<Node>();
        if(node.getMachineReferences()!=null)
            children.addAll(node.getMachineReferences());
        printStdOut_manyChildren(node, children);
    }


    public void caseAExtendsMachineClause(AExtendsMachineClause node)
    {
        List<Node> children = new ArrayList<Node>();
        if(node.getMachineReferences()!=null)
            children.addAll(node.getMachineReferences());
        printStdOut_manyChildren(node, children);
    }

    
    public void caseASeesMachineClause(ASeesMachineClause node)
    {
        List<Node> children = new ArrayList<Node>();
        if(node.getMachineNames()!=null)
            children.addAll(node.getMachineNames());
        printStdOut_manyChildren(node, children);
    }
    
    
    public void caseAUsesMachineClause(AUsesMachineClause node)
    {
        outAUsesMachineClause(node);
        List<Node> children = new ArrayList<Node>();
        if(node.getMachineNames()!=null)
            children.addAll(node.getMachineNames());
        printStdOut_manyChildren(node, children);
    }
    

    public void caseADefinitionsMachineClause(ADefinitionsMachineClause node)
    {
        List<Node> children = new ArrayList<Node>(node.getDefinitions());
        printStdOut_manyChildren(node, children);
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
    	String hasElse = "False";
        List<Node> children = new ArrayList<Node>();
        if(node.getCondition()!=null)
            children.add(node.getCondition());
        if(node.getThen()!=null)
            children.add(node.getThen());
        if(node.getElsifSubstitutions()!=null)
            children.addAll(node.getElsifSubstitutions());
        if(node.getElse()!=null)
        {
            children.add(node.getElse());
            hasElse = "True";
        }
        printStdOut_manyChildren(node, children);
        out.append("id"+(idCounter-1)+".hasElse = \""+hasElse+"\"\n");
    }


    public void caseASelectSubstitution(ASelectSubstitution node)
    {
    	String hasElse = "False";
        List<Node> children = new ArrayList<Node>();
        if(node.getCondition()!=null)
            children.add(node.getCondition());
        if(node.getThen()!=null)
            children.add(node.getThen());
        if(node.getWhenSubstitutions()!=null)
            children.addAll(node.getWhenSubstitutions());
        if(node.getElse()!=null)
        {
            children.add(node.getElse());
            hasElse = "True";
        }
        printStdOut_manyChildren(node, children);
        out.append("id"+(idCounter-1)+".hasElse = \""+hasElse+"\"\n");
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


    public void caseAAssertionsMachineClause(AAssertionsMachineClause node)
    {
        List<Node> children = new ArrayList<Node>(node.getPredicates());
        printStdOut_manyChildren(node, children);
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
 
    
    public void caseAWhileSubstitution(AWhileSubstitution node)
    {
        List<Node> children = new ArrayList<Node>();
        if(node.getCondition() != null)
            children.add(node.getCondition());
        if(node.getDoSubst() != null)
            children.add(node.getDoSubst());
        if(node.getInvariant() != null)
            children.add(node.getInvariant());
        if(node.getVariant() != null)
            children.add(node.getVariant());
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


    private void printStdOut_oneChild(Node node, Node cnode)
    {
        String nodeid, childid;

        if(cnode != null)
        {
            cnode.apply(this);
            childid = ""+(idCounter-1);
            nodeid = ""+idCounter;
            out.append("id"+ nodeid +"=");
            out.append(getClassName(node) +"()\n");
            idCounter++;
            out.append("id"+nodeid+".children.append(id"+childid+")\n");
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
        out.append("id" + nodeid + "=");
        out.append(getClassName(node) +"()\n");
        idCounter++;

        if(left != null)
            out.append("id"+nodeid+".children.append(id"+childid1+")\n");

        if(right != null)
            out.append("id"+nodeid+".children.append(id"+childid2+")\n");
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
        out.append("id" + nodeid + "=");
        out.append(getClassName(node) +"()\n");
        idCounter++;

        for(i=0; i<ids.length; i++)
            out.append("id"+nodeid+".children.append(id"+ids[i]+")\n");
    }
}
