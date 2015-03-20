package pyB; 

import de.be4.classicalb.core.parser.BParser;
import de.be4.classicalb.core.parser.node.Start;
import de.be4.classicalb.core.parser.exceptions.BException;


import java.io.File;
import java.io.IOException;
import java.io.FileReader;
import java.io.BufferedReader;


public class Main {

private static Start ast;

public static void main(String[] args) {
  try {
      
      String mode = args[0];
      String filename = args[1];
      File file = new File(filename);

      
  	  ast = new BParser().parseFile(file, false);
      if(args[0].contains("-python"))
      {
         ASTPython visitor = new ASTPython();
         ast.apply(visitor);
         System.out.println(visitor.out);
      }
    
      if(args[0].contains("-json"))
      {
          ASTJSON visitor = new ASTJSON();
          ast.apply(visitor);
          System.out.println(visitor.out);
      }
      
    }

    catch (IOException e) {
        e.printStackTrace();
    }
       catch (BException e) {
       e.printStackTrace();
       }
}

}