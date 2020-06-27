
# The following program has a load-use hazard.
# After completing the execution, 
# x30 = 1, x31 = 2

    .text
    .align  2
    .globl  _start
_start:                         # code entry point
    li x31, 0
    addi x31, x31, 1
    addi x31, x31, 2
    addi x31, x31, 3
    addi x31, x31, 4
    addi x31, x31, 5

    ecall
    


