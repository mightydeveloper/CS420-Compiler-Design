	AREA 	R
	AREA	MEM

LAB		START

	READI	R(0)
	WRITE	" "
	MOVE	1	R(1)					// I = 1
	
LAB 	LOOPROW
	MOVE	1	R(2)					// J = 1
LAB		LOOPCOL

	ADD		R(1)@ 	R(2)@ 	R(30)	// R3 = I + J
	SUB		R(30)@	1		R(40)	// R4 = R3 - 1 = (I+J-1)
	DIV		R(0)@	2		R(50)	// R5 = N / 2
	ADD		R(40)@	R(50)@	R(50)	// R5 = R4 + R5 = (I+J-1+N/2)
	DIV		R(50)@ 	R(0)@	R(30)	// R3 =	R5 / N
	MUL		R(30)@	R(0)@	R(30)	// R3 = R3 * N
	SUB		R(50)@	R(30)@	R(60) 	// R6 = R5 - R3 = (I+J-1+N/2) mod N
	MUL		R(60)@	R(0)@	R(60)	// R6 = R6 * N
	ADD		R(40)@	R(2)@ 		R(40)	// R4 = R4 + J
	SUB		R(40)@	1		R(40) 	// R4 = R4 - 1
	DIV		R(40)@	R(0)@	R(30)	// R3 = R4 / N
	MUL		R(30)@	R(0)@	R(30)	// R3 = R3 * N
	SUB		R(40)@	R(30)@	R(70)	// R7 = R4 - R3 = (I+2J-2) mod N
	ADD 	R(60)@	R(70)@	R(30)	// R3 = R6 + R7
	ADD 	R(30)@	1		R(80)	// R8 = R3 + 1
	
	WRITE	R(80)@

	SUB		R(2)@ 	R(0)@	R(4)	// R4 = J - N
	ADD 	R(2)@ 	1	R(2) 		// J = J + 1
	JMPZ	R(4)@	CONTINUE		// if R2 = 0, JUMP to CONTINUE
	JMP 	LOOPCOL

LAB		CONTINUE
	SUB 	R(1)@	R(0)@	R(3)	// R3 = I - N
	ADD 	R(1)@ 	1	R(1)		// I = I + 1
	WRITE	" "
	JMPZ	R(3)@	END				// if R1 = 0, Jump to END
	JMP 	LOOPROW

LAB 	END
