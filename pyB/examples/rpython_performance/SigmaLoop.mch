/* johnwitulski$ time ./probcli -mc 2147483648 -p MAXINT 2147483648 -p MININT -2147483648 
../pyB/examples/rpython_performance/SigmaLoop.mch  */

MACHINE SigmaLoop
VARIABLES n, sum
INVARIANT n:NAT & sum=((n+1) * (n))/2
INITIALISATION 	n:=10000 ; sum:=(SIGMA i. (i:0..n | i)) 
OPERATIONS op = skip /* avoid deadlock */  
END