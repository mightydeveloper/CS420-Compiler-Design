	AREA	A
	AREA	S
// 사용자로부터 한 숫자를 받아들여 0에서 그 숫자까지의 합을 구하는 프로그램

LAB		START		// 프로그램의 시작

	WRITE "Number::"
	READI	A
	MOVE	0		S	// 결과가 저장될 장소의 초기화

LAB		LOOP

	ADD		S@	A@	S	
	SUB		A@	1	A	// A는 loop variable
	JMPZ	A@  EXIT	// A주소의 내용이 0이면 EXIT로 jump
	JMP		LOOP

LAB		EXIT

	WRITE  "SUM::"
	WRITE	S@

LAB		END		// 프로그램의 끝
