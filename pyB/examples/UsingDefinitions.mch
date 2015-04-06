MACHINE UsingDefinitions
VARIABLES z, b
INVARIANT z:NAT & b:BOOL
INITIALISATION Assign(z, 1+1) || Assign(b, TRUE)
DEFINITIONS Assign(VarName,Expr) == VarName := Expr;
END