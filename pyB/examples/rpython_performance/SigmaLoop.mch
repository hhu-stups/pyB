/* johnwitulski$ ./probcli -mc 2 -p MAXINT 10000000 ../pyB/examples/SigmaLoop.mch */

MACHINE SigmaLoop
VARIABLES n
INVARIANT
  n:NAT & 55=(SIGMA i. (i:0..n | i)) 
INITIALISATION 	n:=10
OPERATIONS 

op = skip /* avoid deadlock */
  
END