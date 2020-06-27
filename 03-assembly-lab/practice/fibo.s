/*------------------------------------------------------------------------------
 * 4190.308 Computer Architecture                                    Spring 2020
 *
 * Assembly Lab
 *
 * fibo.s - A simple fibonacci exercise for students
 *
 */

    .text
    .align  2
    .globl  _start
_start:
    lui     sp, 0x80020
    call    fibo
    ecall


fibo:
    li a0, 0x1
    slli a0, a0, 32
    # slli a1, a0, 1
    # slli a2, a1, 1
    # slli a3, a2, 1
    # slli a0, a0, 1





    ret

