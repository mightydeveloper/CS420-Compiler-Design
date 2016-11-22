	AREA 	R
	AREA 	I
	AREA 	J
	AREA 	N

LAB		START

	MOVE	5	N
	MOVE	1	I
	MOVE	1	J
	
LAB 	LOOPROW
	SUB 	I@	N@	R(1)		// R1 = I - N
	MOVE	1	J
LAB		LOOPCOL
	SUB		J@ 	N@	R(2)		// R2 = J - N
	
LAB		CALC 						
	ADD		I@ 		J@ 		R(3)	// R3 = I + J
	SUB		R(3)@	1		R(4)	// R4 = R3 - 1 = (I+J-1)
	DIV		N@		2		R(5)	// R5 = N / 2
	ADD		R(4)@	R(5)@	R(5)	// R5 = R4 + R5 = (I+J-1+N/2)
	DIV		R(5)@ 	N@		R(3)	// R3 =	R5 / N
	MUL		R(3)@	N@		R(3)	// R3 = R3 * N
	SUB		R(5)@	R(3)@	R(6) 	// R6 = R5 - R3 = (I+J-1+N/2) mod N
	MUL		R(6)@	N@		R(6)	// R6 = R6 * N
	ADD		R(4)@	J@ 		R(4)	// R4 = R4 + J
	SUB		R(4)@	1		R(4) 	// R4 = R4 - 1
	DIV		R(4)@	N@		R(3)	// R3 = R4 / N
	MUL		R(3)@	N@		R(3)	// R3 = R3 * N
	SUB		R(4)@	R(3)@	R(7)	// R7 = R4 - R3 = (I+2J-2) mod N
	ADD 	R(6)@	R(7)@	R(3)	// R3 = R6 + R7
	ADD 	R(3)@	1		R(8)	// R8 = R3 + 1
	
	WRITE	R(8)@

	ADD 	J@ 	1	J 			// J = J + 1
	JMPZ	R(2)@	CONTINUE	// if R2 = 0, JUMP to CONTINUE
	JMP 	LOOPCOL

LAB		CONTINUE
	ADD 	I@ 	1	I		// I = I + 1
	WRITE	" "
	JMPZ	R(1)@	END			// if R1 = 0, Jump to END
	JMP 	LOOPROW

LAB 	END
