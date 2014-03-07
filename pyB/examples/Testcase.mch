MACHINE Testcase
        VARIABLES xx
        INVARIANT xx:NAT
        INITIALISATION xx:=42
        OPERATIONS
          op1 = xx::{1,2,3};
	  op2(zz) = xx::{1,2,zz};
          rr <-- op3 = rr::{1,2,3};
          rr <-- op4(zz) = rr::{1,2,zz}
        END