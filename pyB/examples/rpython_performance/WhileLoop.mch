MACHINE WhileLoop
VARIABLES sum, i, n
INVARIANT
  sum:NATURAL & i:NATURAL & n:NATURAL & i:{0,n}
INITIALISATION 	
  BEGIN 
       BEGIN 
           n := 10 ;
           sum := 0 ; 
           i := 0
       END;
       WHILE i<n DO
           sum := sum + i;
           i := i+1 
       INVARIANT
           i:NATURAL & sum:NATURAL & sum = ((i-1) * (i))/2
       VARIANT 
           n - i
       END /* ;i:=-1 */
   END

OPERATIONS    
   rr <-- op = rr:=sum /* avoid deadlock */
END

