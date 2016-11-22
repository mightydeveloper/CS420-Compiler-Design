	area	R
	AREA	B
LAB		START
        move -4 B(0)
        move 1 R(0)
        move -1 R(1)
        add R(1)@ -4 R(2)
        move 1 R(3)
        write B(0)@
        write R(0)@
        write R(2)@
LAB		END
