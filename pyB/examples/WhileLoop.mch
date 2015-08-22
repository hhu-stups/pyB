MACHINE WhileLoop
VARIABLES sum, i, n
INVARIANT
  sum>=0 & sum<MAXINT & i>=0 & i<MAXINT & n>=0 & n<MAXINT
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
           i>=0 & i<MAXINT & i<=n & sum>=0 & sum<MAXINT & sum = ((i-1) * (i))/2
       VARIANT 
           n - i
       END
   END

OPERATIONS    
   rr <-- op = rr:=sum /* avoid deadlock */
END

