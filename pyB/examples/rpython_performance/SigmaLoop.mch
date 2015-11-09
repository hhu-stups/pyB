/* johnwitulski$ time ./probcli -mc 2147483648 -p MAXINT 2147483648 -p MININT -2147483648 
../pyB/examples/rpython_performance/SigmaLoop.mch  */

MACHINE SigmaLoop
VARIABLES n, sum
INVARIANT
  n:NAT & sum=45
  /* (10,55),  (100,5050), (1000, 500500), (10000, 50005000) */
INITIALISATION 	n:=9 ; sum:=(SIGMA i. (i:0..n | i)) 

OPERATIONS op = skip /* avoid deadlock */
  
END