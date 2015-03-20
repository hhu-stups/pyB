// AST Walker
package pyB;

import de.be4.classicalb.core.parser.analysis.DepthFirstAdapter;
import de.be4.classicalb.core.parser.node.*;
import java.util.ArrayList;
import java.util.List;
// walks the tree and prints a JSON AST

public class ASTJSON extends DepthFirstAdapter{
    public StringBuilder out;

    public ASTJSON()
    {
        out = new StringBuilder();
    }

    private String getClassName(Node node)
    {
        String clsname = node.getClass().getName();
        int mid= clsname.lastIndexOf ('.') + 1;
        return clsname.substring(mid);
    }
    
    public void defaultOut(@SuppressWarnings("unused") Node node)
    {
        if(getClassName(node).equals("AFileDefinition"))
        {   
			out.append("[\"");
            out.append("AFileDefinition\",");
            out.append("{\"idName\":\""+node.toString()+"\"}");
            out.append("]");
		}
		else if (getClassName(node).equals("ADefinitionFileParseUnit"))
        {
			// assumption: last node
            out.append("]");
		}
    }
    
    public void defaultIn(@SuppressWarnings("unused") Node node)
    {
        if (getClassName(node).equals("ADefinitionFileParseUnit"))
        {
            // assumption: first node
        	out.append("[\"");
            out.append("ADefinitionFileParseUnit\",");
        }
    }

    public void outAIntegerExpression(AIntegerExpression node)
    {
        out.append("[\"");
        out.append(getClassName(node));
        out.append("\",");
        out.append("{\"intValue\":"+node.getLiteral().toString()+"}");
        out.append("]");
    }


    public void outAIdentifierExpression(AIdentifierExpression node)
    {
        // FIXME: some bug with a space at the end
        String idName = node.getIdentifier().toString().replace("[","").replace("]","");
        out.append("[\"");
        out.append(getClassName(node));
        out.append("\",");
        out.append("{\"idName\":\""+idName+"\"}");
        out.append("]");
    }


    public void caseAStringExpression(AStringExpression node)
    {
    	String string;
    	if (node.getContent()!=null)
        	string = node.getContent().getText(); 
        else
        	string = ""; //else empty string ""
        out.append("[\"");
        out.append(getClassName(node));
        out.append("\",");
        out.append("{\"string\":\""+string+"\"}");
        out.append("]");
    }


    public void caseAStringSetExpression(AStringSetExpression node)
    {
        out.append("[\"");
        out.append(getClassName(node));
        out.append("\"]");
    }


    public void outAEmptySetExpression(AEmptySetExpression node)
    {
        out.append("[\"");
        out.append(getClassName(node));
        out.append("\"]");
    }


    public void caseAEmptySequenceExpression(AEmptySequenceExpression node)
    {
        out.append("[\"");
        out.append(getClassName(node));
        out.append("\"]");
    }


    public void caseAIntegerSetExpression(AIntegerSetExpression node)
    {
        out.append("[\"");
        out.append(getClassName(node));
        out.append("\"]");
    }

    public void caseANatSetExpression(ANatSetExpression node)
    {
        out.append("[\"");
        out.append(getClassName(node));
        out.append("\"]");
    }

    public void caseANaturalSetExpression(ANaturalSetExpression node)
    {
        out.append("[\"");
        out.append(getClassName(node));
        out.append("\"]");
    }
    
    public void caseAIntSetExpression(AIntSetExpression node)
    {
        out.append("[\"");
        out.append(getClassName(node));
        out.append("\"]");
    }
    
        
    public void caseANatural1SetExpression(ANatural1SetExpression node)
    {
        out.append("[\"");
        out.append(getClassName(node));
        out.append("\"]");
    }

    public void caseANat1SetExpression(ANat1SetExpression node)
    {
        out.append("[\"");
        out.append(getClassName(node));
        out.append("\"]");
    }


    public void caseABooleanTrueExpression(ABooleanTrueExpression node)
    {
        out.append("[\"");
        out.append(getClassName(node));
        out.append("\"]");
    }


    public void caseABoolSetExpression(ABoolSetExpression node)
    {
        out.append("[\"");
        out.append(getClassName(node));
        out.append("\"]");
    }


    public void caseABooleanFalseExpression(ABooleanFalseExpression node)
    {
        out.append("[\"");
        out.append(getClassName(node));
        out.append("\"]");
    }


    public void caseASkipSubstitution(ASkipSubstitution node)
    {
        out.append("[\"");
        out.append(getClassName(node));
        out.append("\"]");
    }


    public void caseAMinIntExpression(AMinIntExpression node)
    {
        out.append("[\"");
        out.append(getClassName(node));
        out.append("\"]");
    }


    public void caseAMaxIntExpression(AMaxIntExpression node)
    {
        out.append("[\"");
        out.append(getClassName(node));
        out.append("\"]");
    }


    public void caseASuccessorExpression(ASuccessorExpression node)
    {
        out.append("[\"");
        out.append(getClassName(node));
        out.append("\"]");
    }


    public void caseAPredecessorExpression(APredecessorExpression node)
    {
        out.append("[\"");
        out.append(getClassName(node));
        out.append("\"]");
    }


    public void outStart(Start node)
    {
        // dont add a start node now
        // dont call defaultOut(Node)
    }


    public void caseAPredicateParseUnit(APredicateParseUnit node)
    {
        printStdOut_oneChild(node, node.getPredicate());
    }
    
    public void caseAExpressionParseUnit(AExpressionParseUnit node)
    {
        printStdOut_oneChild(node, node.getExpression());
    }


    public void caseAAbstractMachineParseUnit(AAbstractMachineParseUnit node)
    {
        out.append("[");
        List<Node> children = new ArrayList<Node>();
        if(node.getHeader()!=null)
            children.add(node.getHeader());
        if(node.getMachineClauses()!=null)
            children.addAll(node.getMachineClauses());
        printStdOut_manyChildren_nb(node, children);
        out.append(",");
        /*
        String mtype="";
        if(node.getType() != null)
        {
            mtype = node.getType().toString();
        }
        out.append("{\"type\":\""+mtype+"\",");*/
        out.append("]");
    }


    public void caseARefinementMachineParseUnit(ARefinementMachineParseUnit node)
    {
        out.append("[");
        List<Node> children = new ArrayList<Node>();
        if(node.getHeader()!=null)
            children.add(node.getHeader());
        if(node.getMachineClauses()!=null)
            children.addAll(node.getMachineClauses());
        printStdOut_manyChildren_nb(node, children);
        out.append(",");

        String refines="";
        if(node.getRefMachine() != null)
        {
            refines = node.getRefMachine().toString();
        }
        out.append("{\"refines\":\""+refines+"\",");
        out.append("]");
    }


    public void caseAMachineHeader(AMachineHeader node)
    {
        out.append("[");
        List<Node> children = new ArrayList<Node>();
        if(node.getParameters()!=null)
            children.addAll(node.getParameters());
        printStdOut_manyChildren_nb(node, children);
        out.append(",");

        String idName = "";
        for(TIdentifierLiteral e : node.getName())
        {
            // XXX
            e.apply(this);
            idName = idName + e.toString();
        }
        out.append("{\"idName\":\""+idName+"\",");
        out.append("]");
    }



    public void caseASubstitutionDefinitionDefinition(ASubstitutionDefinitionDefinition node)
    {
        out.append("[");
        List<Node> children = new ArrayList<Node>();
        if(node.getParameters()!=null)
            children.addAll(node.getParameters());
        if(node.getRhs()!=null)
            children.add(node.getRhs());
        printStdOut_manyChildren_nb(node, children);
        out.append(",");

        String idName = "";
        if(node.getName() != null)
        {
            idName = node.getName().toString();
        }
        out.append("{\"idName\":\""+idName+"\",");
        if (node.getParameters()!=null)
            out.append(" \"paraNum\":"+node.getParameters().size()+"}");
        else
            out.append(" \"paraNum\": 0 }");
        out.append("]");
    }


    public void caseAPredicateDefinitionDefinition(APredicateDefinitionDefinition node)
    {
        out.append("[");
        List<Node> children = new ArrayList<Node>();
        if(node.getParameters()!=null)
            children.addAll(node.getParameters());
        if(node.getRhs()!=null)
            children.add(node.getRhs());
        printStdOut_manyChildren_nb(node, children);
        out.append(",");

        String idName = "";
        if(node.getName() != null)
        {
            idName = node.getName().toString();
        }
        out.append("{\"idName\":\""+idName+"\",");
        if (node.getParameters()!=null)
            out.append(" \"paraNum\":"+node.getParameters().size()+"}");
        else
            out.append(" \"paraNum\": 0 }");
        out.append("]");
    }


    public void caseAExpressionDefinitionDefinition(AExpressionDefinitionDefinition node)
    {
        out.append("[");
        List<Node> children = new ArrayList<Node>();
        if(node.getParameters()!=null)
            children.addAll(node.getParameters());
        if(node.getRhs()!=null)
            children.add(node.getRhs());
        printStdOut_manyChildren_nb(node, children);
        out.append(",");

        String idName = "";
        if(node.getName() != null)
        {
            idName = node.getName().toString();
        }
        out.append("{\"idName\":\""+idName+"\",");
        if (node.getParameters()!=null)
            out.append(" \"paraNum\":"+node.getParameters().size()+"}");
        else
            out.append(" \"paraNum\": 0 }");
        out.append("]");
    }


    public void caseADefinitionExpression(ADefinitionExpression node)
    {
        out.append("[");
        List<Node> children = new ArrayList<Node>();
        if(node.getParameters()!=null)
            children.addAll(node.getParameters());
        printStdOut_manyChildren_nb(node, children);
        out.append(",");

        String idName = "";
        if(node.getDefLiteral() != null)
        {
            idName = node.getDefLiteral().toString();
        }
        out.append("{\"idName\":\""+idName+"\"}");
        out.append("]");
    }


    public void caseADefinitionPredicate(ADefinitionPredicate node)
    {
        out.append("[");
        List<Node> children = new ArrayList<Node>();
        if(node.getParameters()!=null)
            children.addAll(node.getParameters());
        printStdOut_manyChildren_nb(node, children);
        out.append(",");

        String idName = "";
        if(node.getDefLiteral() != null)
        {
            idName = node.getDefLiteral().toString();
        }
        out.append("{\"idName\":\""+idName+"\"}");
        out.append("]");
    }


    public void caseADefinitionSubstitution(ADefinitionSubstitution node)
    {
        out.append("[");
        List<Node> children = new ArrayList<Node>();
        if(node.getParameters()!=null)
            children.addAll(node.getParameters());
        printStdOut_manyChildren_nb(node, children);
        out.append(",");

        String idName = "";
        if(node.getDefLiteral() != null)
        {
            idName = node.getDefLiteral().toString();
        }
        out.append("{\"idName\":\""+idName+"\"}");
        out.append("]");
    }


    public void caseAAssignSubstitution(AAssignSubstitution node)
    {
        out.append("[");
        List<Node> children = new ArrayList<Node>();
        if(node.getLhsExpression()!=null)
            children.addAll(node.getLhsExpression());
        if(node.getRhsExpressions()!=null)
            children.addAll(node.getRhsExpressions());
        printStdOut_manyChildren_nb(node, children);
        out.append(",");


        out.append("{\"lhs_size\":"+node.getLhsExpression().size()+",");
        out.append(" \"rhs_size\":"+node.getRhsExpressions().size()+"}");
        out.append("]");
    }


    public void caseAEnumeratedSetSet(AEnumeratedSetSet node)
    {
        out.append("[");
        List<Node> children = new ArrayList<Node>();
        if(node.getElements()!=null)
            children.addAll(node.getElements());
        printStdOut_manyChildren_nb(node, children);
        out.append(",");

        String idName = "";
        for(TIdentifierLiteral e : node.getIdentifier())
        {
            // XXX
            e.apply(this);
            idName = idName + e.toString();
        } 
        out.append("{\"idName\":\""+idName+"\"}");
        out.append("]");
    }


    public void caseADeferredSetSet(ADeferredSetSet node)
    {
        out.append("[\"");
        out.append(getClassName(node));
        out.append("\"");
        out.append(",");
        String idName = "";
        for(TIdentifierLiteral e : node.getIdentifier())
        {
            // XXX
            e.apply(this);
            idName = idName + e.toString();
        }

        out.append("{\"idName\": \""+idName+"\"}");
        out.append("]");
    }


    public void caseAOperation(AOperation node)
    {
        out.append("[");
        List<Node> children = new ArrayList<Node>();
        if(node.getReturnValues()!=null)
            children.addAll(node.getReturnValues());
        if(node.getParameters()!=null)
            children.addAll(node.getParameters());
        if(node.getOperationBody()!=null)
            children.add(node.getOperationBody());
        printStdOut_manyChildren_nb(node, children);
        out.append(",");

        String idName = "";
        for(TIdentifierLiteral e : node.getOpName())
        {
            e.apply(this);
            idName = idName + e.toString();
        }
        out.append("{\"opName\":\""+idName+"\",");
        out.append(" \"return_Num\":"+node.getReturnValues().size()+",");
        out.append(" \"parameter_Num\":"+node.getParameters().size()+"}");
        out.append("]");
    }


    public void caseAPrimedIdentifierExpression(APrimedIdentifierExpression node)
    {
        out.append("[");
        List<Node> children = new ArrayList<Node>(node.getIdentifier());
        printStdOut_manyChildren_nb(node, children);
        out.append(",");

        out.append("{\"grade\":"+node.getGrade()+"}");
        out.append("]");
    }


    public void caseACaseSubstitution(ACaseSubstitution node)
    {
        out.append("[");
        List<Node> children = new ArrayList<Node>();
        String hasElse = "False";
        if(node.getExpression()!=null)
            children.add(node.getExpression());
        if(node.getEitherExpr()!=null)
            children.addAll(node.getEitherExpr());
        if(node.getEitherSubst()!=null)
            children.add(node.getEitherSubst());
        if(node.getOrSubstitutions()!=null)
            children.addAll(node.getOrSubstitutions());
        if(node.getElse()!=null)
        {
            hasElse = "True";
            children.add(node.getElse());
        }    
        printStdOut_manyChildren_nb(node, children);
        out.append(",");

        out.append("{\"expNum\":"+node.getEitherExpr().size()+"}");
        out.append("{\"hasElse\":"+hasElse+"}");
        out.append("]");
    }


    public void caseACaseOrSubstitution(ACaseOrSubstitution node)
    {
        out.append("[");
        List<Node> children = new ArrayList<Node>(node.getExpressions());
        if(node.getSubstitution()!=null)
            children.add(node.getSubstitution());
        printStdOut_manyChildren_nb(node, children);
        out.append(",");

        out.append("{\"expNum\":"+node.getExpressions().size()+"}");
        out.append("]");
    }


    public void caseAVarSubstitution(AVarSubstitution node)
    {
        out.append("[");
        List<Node> children = new ArrayList<Node>(node.getIdentifiers());
        if(node.getSubstitution()!=null)
            children.add(node.getSubstitution());
        printStdOut_manyChildren_nb(node, children);
        out.append(",");

        out.append("{\"idNum\":"+node.getIdentifiers().size()+"}");
        out.append("]");
    }


    public void caseAAnySubstitution(AAnySubstitution node)
    {
        out.append("[");
        List<Node> children = new ArrayList<Node>(node.getIdentifiers());
        if(node.getWhere()!=null)
            children.add(node.getWhere());
        if(node.getThen()!=null)
            children.add(node.getThen());
        printStdOut_manyChildren_nb(node, children);
        out.append(",");

        out.append("{\"idNum\":"+node.getIdentifiers().size()+"}");
        out.append("]");
    }



    public void caseALetSubstitution(ALetSubstitution node)
    {
        out.append("[");
        List<Node> children = new ArrayList<Node>(node.getIdentifiers());
        if(node.getPredicate()!=null)
            children.add(node.getPredicate());
        if(node.getSubstitution()!=null)
            children.add(node.getSubstitution());
        printStdOut_manyChildren_nb(node, children);
        out.append(",");

        out.append("{\"idNum\":"+node.getIdentifiers().size()+"}");
        out.append("]");
    }


    public void caseAQuantifiedUnionExpression(AQuantifiedUnionExpression node)
    {
        out.append("[");
        List<Node> children = new ArrayList<Node>(node.getIdentifiers());
        if(node.getPredicates()!=null)
            children.add(node.getPredicates());
        if(node.getExpression()!=null)
            children.add(node.getExpression());
        printStdOut_manyChildren_nb(node, children);
        out.append(",");

        out.append("{\"idNum\":"+node.getIdentifiers().size()+"}");
        out.append("]");
    }


    public void caseAQuantifiedIntersectionExpression(AQuantifiedIntersectionExpression node)
    {
        out.append("[");
        List<Node> children = new ArrayList<Node>(node.getIdentifiers());
        if(node.getPredicates()!=null)
            children.add(node.getPredicates());
        if(node.getExpression()!=null)
            children.add(node.getExpression());
        printStdOut_manyChildren_nb(node, children);
        out.append(",");

        out.append("{\"idNum\":"+node.getIdentifiers().size()+"}");
        out.append("]");
    }


    public void caseAMachineReference(AMachineReference node)
    {
        out.append("[");
        List<Node> children = new ArrayList<Node>();
        if(node.getParameters()!=null)
            children.addAll(node.getParameters());
        printStdOut_manyChildren_nb(node, children);
        out.append(",");

        String idName = "";
        for(TIdentifierLiteral e : node.getMachineName())
        {
            // XXX
            e.apply(this);
            idName = idName + e.toString();
        }
        out.append("{\"idName\":\""+idName+"\"}");
        out.append("]");
    }


    public void caseAOpSubstitution(AOpSubstitution node)
    {
        out.append("[");
        List<Node> children = new ArrayList<Node>();
        if(node.getParameters()!=null)
            children.addAll(node.getParameters());
        printStdOut_manyChildren_nb(node, children);
        out.append(",");

        String idName="";
        if(node.getName() != null)
        {
            idName = node.getName().toString();
        }
        out.append("{\"idName\":\""+idName+"\"");
        out.append(" \"parameter_Num\":"+node.getParameters().size()+"}");
        out.append("]");
    }


    public void caseAOperationCallSubstitution(AOperationCallSubstitution node)
    {
    	out.append("[");
        List<Node> children = new ArrayList<Node>();
        if(node.getResultIdentifiers()!=null)
            children.addAll(node.getResultIdentifiers());
        
        String idName = "";
        for(TIdentifierLiteral e : node.getOperation())
        {
            // XXX
            e.apply(this);
            idName = idName + e.toString();
        }
        
        if(node.getParameters()!=null)
            children.addAll(node.getParameters());
        printStdOut_manyChildren(node, children);

        out.append("{\"idName\":\""+idName+"\"");
        out.append(" \"return_Num\":"+node.getResultIdentifiers().size()+",");
        out.append(" \"parameter_Num\":"+node.getParameters().size()+"}");
        out.append("]");
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
        out.append("[");
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
        printStdOut_manyChildren_nb(node, children);
        out.append(",");
        out.append("{\"hasElse\":"+hasElse+"}");
        out.append("]");
    }


    public void caseASelectSubstitution(ASelectSubstitution node)
    {
        out.append("[");
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
        printStdOut_manyChildren_nb(node, children);
        out.append(",");
        out.append("{\"hasElse\":"+hasElse+"}");
        out.append("]");
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


    public void caseAExistsPredicate(AExistsPredicate node)
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
        
        if(node.getIdentifiers()!=null)
        	out.append("{\"idNum\":"+node.getIdentifiers().size()+"}");
    }


    public void caseAForallPredicate(AForallPredicate node)
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


    public void caseAAbstractConstantsMachineClause(AAbstractConstantsMachineClause node)
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


    public void caseAConcreteVariablesMachineClause(AConcreteVariablesMachineClause node)
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
        
        if(node.getIdentifiers()!=null)
        	out.append("{\"idNum\":"+node.getIdentifiers().size()+"}");
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


    public void caseAMemberPredicate(AMemberPredicate node)
    {
        printStdOut_twoChildren(node, node.getLeft(), node.getRight());
    }
    
    
    public void caseANotMemberPredicate(ANotMemberPredicate node)
    {
        printStdOut_twoChildren(node, node.getLeft(), node.getRight());
    }


    public void caseASubsetPredicate(ASubsetPredicate node)
    {
        printStdOut_twoChildren(node, node.getLeft(), node.getRight());
    }
    
    
    public void caseANotSubsetPredicate(ANotSubsetPredicate node)
    {
        printStdOut_twoChildren(node, node.getLeft(), node.getRight());
    }
    
    
    public void caseASubsetStrictPredicate(ASubsetStrictPredicate node)
    {
        printStdOut_twoChildren(node, node.getLeft(), node.getRight());
    }
    
    
    public void caseANotSubsetStrictPredicate(ANotSubsetStrictPredicate node)
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


    public void caseANotEqualPredicate(ANotEqualPredicate node)
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


    public void caseAUnaryMinusExpression(AUnaryMinusExpression node)
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
        out.append("[\"");
        out.append(getClassName(node));
        out.append("\"");
        if(cnode != null)
        {
            out.append(",");
            cnode.apply(this);
        }
        out.append("]");
    }


    private void printStdOut_twoChildren(Node node, Node left, Node right)
    {
        out.append("[\"");
        out.append(getClassName(node));
        out.append("\"");
        if(left != null)
        {
            out.append(",");
            left.apply(this);
        }

        if(right != null)
        {
            out.append(",");
            right.apply(this);
        }
        out.append("]");
    }

    // visits and prints the node-List first
    private void printStdOut_manyChildren(Node node, List<Node> children)
    {
        out.append("[\"");
        out.append(getClassName(node));
        out.append("\"");
        for(Node n : children)
        {
            out.append(",");
            n.apply(this);
        }
        out.append("]");
    }


    // visits and prints the node-List first
    private void printStdOut_manyChildren_nb(Node node, List<Node> children)
    {
        // out.append("[\""); ??
        out.append("\"");
        out.append(getClassName(node));
        out.append("\"");
        for(Node n : children)
        {
            out.append(",");
            n.apply(this);
        }
        out.append("{\"childNum\":\""+children.size()+"\"}");
    }
}
