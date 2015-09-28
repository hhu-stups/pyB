MACHINE PyB_C_Features
VARIABLES f
INVARIANT 1+1=2
        & {1,2}\/{3,4}={1,2,3,4} 
        & {1,2,3,4}/\{4}={4}
        & {1,2,3,4}-{4}={1,2,3} 
        & {1,2}:POW({1,2,3}) & {1,1}:POW({1,2,3}) 
        & {2,1}:POW1({1,2,3}) & {}/:POW1({1,2,3}) 
		& {(1,TRUE)}:f & card(f)=64
	/*	& {1}={x|x=1} */
INITIALISATION f:={1,2,3}<->{TRUE,FALSE}
OPERATIONS
 avoid_deadlock = skip
END