	area	A
	AREA	STACK
	AREA	SP

LAB		SWAP	// swap first argument and second argument
	WRITE		"STACK"
	WRITE		STACK(SP@(-1))@@	// Print First Argument
	WRITE		STACK(SP@)@@		// Print Second Argument

	move		STACK(SP@)@@	STACK(SP@(1))
					// SP@(1)is local(stack) valiable
	MOVE		STACK(SP@(-1))@@	STACK(SP@)@
	MOVE		STACK(SP@(1))@	STACK(SP@(-1))@
	JMP		STACK(SP@(-2))@	// Label	which is return location

LAB		START			// program start 
	MOVE		0	SP
	MOVE		10	A(0)
	MOVE		20	A(1)
	write		"Original Data"
	Write		A(0)@
	WRITE		A(1)@
	MOVE		RET1	STACK(SP@)	// push return address
	ADD		SP@	1	SP	// SP is stack pointer
	MOVE		A(0) 	STACK(SP@)	// push first argument
	ADD		SP@	1	SP
	MOVE		A(1) 	STACK(SP@)	// push second argument
	JMP		SWAP
LAB		RET1
	WRITE	"RESULT"
	WRITE	A(0)@
	WRITE	A(1)@
LAB		END	//  End of Program
