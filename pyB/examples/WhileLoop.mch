MACHINE WhileLoop
VARIABLES sum, i, n
INVARIANT
  sum:NAT & i:NAT & n:NAT
INITIALISATION 	
  BEGIN 
       BEGIN 
           n := 100 ;
           sum := 0 ; 
           i := 0
       END;
       WHILE i<n DO
           sum := sum + i;
	   i := i+1 
       INVARIANT
           i : NAT & i<=n & sum:NAT & sum = ((i-1) * (i))/2
       VARIANT 
           n - i
       END
   END
END