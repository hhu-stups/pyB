MACHINE Scope /*modified Schnieder book page 115*/
SETS S
PROPERTIES card(S)=4 
VARIABLES f
INVARIANT f:S --> 0..6 
INITIALISATION f:=S*{0}
OPERATIONS
op1(rr, nn) = PRE rr:S & nn:1..6 & f(rr)=0 
		  THEN f(rr):= nn
		  END;
nn <-- op2 = nn:= SIGMA(zz).(zz:S | f(zz))
END

