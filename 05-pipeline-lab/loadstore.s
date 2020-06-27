
# The following program has a load-use hazard.
# After completing the execution, 
# x30 = 1, x31 = 2

    .text
    .align  2
    .globl  _start
_start:                         # code entry point
    lui     t0, 0x80010
    li      x31, 3
    sw      x31, 0(t0)
    addi    x31, x31, 10
    lw      x31, 0(t0)
    sw      x31, 4(t0)
    lw      x30, 4(t0)

    addi    x30, x30, -2
    addi    x31, x31, -1
    ecall
    


