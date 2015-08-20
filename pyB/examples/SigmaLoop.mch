/* johnwitulski$ ./probcli -mc 2 -p MAXINT 10000000 ../pyB/examples/SigmaLoop.mch */

MACHINE SigmaLoop
VARIABLES sum,  n
INVARIANT
  sum:NAT & n:NAT
INITIALISATION 	n:=5 ; sum:=(SIGMA i. (i:0..n | i))
OPERATIONS 

rr <-- op = rr:=sum /* avoid deadlock */
  
END