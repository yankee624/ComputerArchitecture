/*------------------------------------------------------------------------------
 * 4190.308 Computer Architecture                                    Spring 2020
 *
 * Assembly Lab
 *
 * Handout:    April 22, 2020
 * Due:        May    4, 2020 11:00
 *
 * multdiv.s - implement the functions in this file. Push to your CSAP GitLab
 *             account when done. You can push as many times as you want, the
 *             last submission will be graded.
 *             The date/time of the last submission counts as the submission
 *             date.
 */

    .text
    .align  2

#----------------------------------------------------------------
#   int mul(int a, int b)
#----------------------------------------------------------------
/* Perform 32bit x 32bit integer multiplication, return lower 32 bit result.
 * Starting from the LSB of multiplier(b) to the MSB,
 * if the bit is 1, add the multiplcand to the result.
 * On each step, multiplicand/multiplier are shifted left/right by one bit.
 * The loop terminates when the multiplier becomes 0.
 * All calculations are done assuming operands are unsigned,
 * but even when the operands are signed(negative), this algorithm works 
 * since lower 32 bits of the result remains same.
 * (This is because "1" in MSB of signed operand means -2^31, but interpreted as 2^31 in this algorithm, 
 * which is 2^32 difference. 2^32 difference doesn't affect lower 32 bit result.)
 */
    .globl  mul
mul:
    #--------------------------------------------
    # a0:       result
    # a1:       (shifted) a
    # a2:       (shifted) b
    # a3:       counter
    #--------------------------------------------  
    mv      a2, a1  
    mv      a1, a0 
    li      a0, 0 
    li      a3, 0

mul_loop:
    andi    a5, a2, 1               # a5 = LSB of a2
    beq     a5, zero, mul_shift     # if (LSB of a2) == 0, go to .L2
    add     a0, a0, a1              # else, result += a2

mul_shift:
    slli    a1, a1, 1               # a1 = a1 << 1
    srli    a2, a2, 1               # a2 = a2 >> 1
    addi    a3, a3, 1               # counter += 1
    bne     a2, zero, mul_loop      # if a2 == 0, terminate the loop

    ret

#----------------------------------------------------------------
#   int mulh(int a, int b)
#----------------------------------------------------------------
/* Perform 32bit x 32bit integer multiplication, return upper 32 bit result.
 * To calculate upper 32 bit result, we also need the lower 32 bit result, so we calculate both.
 * Before starting, convert negative operands to positive, and remember the number of negative operands.
 * Starting from the LSB of multiplier(b) to the MSB,
 * if the bit is 1, add (counter) bit left shifted multiplcand to the lower result,
 * and (32-counter) bit right shifted multiplicand to the upper result.
 * On each step, multiplier is shifted left by one bit.
 * The loop terminates when the multiplier becomes 0.
 * The result is negated if one of the operands was negative.
 */
    .globl  mulh
mulh:
    #--------------------------------------------
    # a0:       upper 32 bit result
    # a1:       lower 32 bit result
    # a2:       a
    # a3:       (shifted) b
    # a4:       counter
    # a5:       counter for negative operands
    #-------------------------------------------- 
    mv      a2, a0 
    mv      a3, a1           
    li      a0, 0            
    li      a1, 0           
    li      a4, 0            
    li      a5, 0           
                                
mulh_neg1:                          # Convert negative operands to positive
    bge     a2, zero, mulh_neg2     # if a >= 0, skip this part
    xori    a2, a2, 0xffffffff      # else, a2 = -a2 = -a
    addi    a2, a2, 1
    addi    a5, a5, 1               # a5 += 1
mulh_neg2:
    bge     a3, zero, mulh_lower    # if b >= 0, skip this part
    xori    a3, a3, 0xffffffff      # else, a3 = -a3 = -b
    addi    a3, a3, 1      
    addi    a5, a5, 1               # a5 += 1

mulh_lower:                         # Calculating lower 32 bit result
    andi    a6, a3, 1               # a6 = LSB of a3 (shifted b)     
    beq     a6, zero, mulh_shift    # if a6 == 0, skip this part and goto shifting part
    sll     a6, a2, a4              # a6 = a << counter
    add     a1, a1, a6              # lower 32 bit result += a6
    bgeu    a1, a6, mulh_upper      # if a1 < a6, overflow occured

mulh_overflow:
    addi    a0, a0, 1               # Overflow in lower 32 bit result -> Add 1 to upper 32 bit result

mulh_upper:                         # Calculating upper 32 bit result
    beq     a4, zero, mulh_shift    # if first iteration, skip calculation of upper 32 bits
    xori    a6, a4, 0xffffffff      # a6 = 32 - counter
    addi    a6, a6, 33
    srl     a6, a2, a6              # a6 = a >> (32 - counter)
    add     a0, a0, a6              # upper 32 bit result += a6

mulh_shift:
    addi    a4, a4, 1               # counter += 1
    srli    a3, a3, 1               # a3 = a3 >> 1 (shifted b)
    bne     a3, zero, mulh_lower    # if a3 == 0, terminate the loop

mulh_sign:                          # Determine the sign of the result
    andi    a5, a5, 1               # a5 = LSB of a5 (0 if operands have same sign)     
    beq     a5, zero, mulh_exit     # if operands have same sign, return
    xori    a0, a0, 0xffffffff      # else, [a0 a1] = 2s complement of [a0 a1]
    xori    a1, a1, 0xffffffff
    addi    a1, a1, 1 
    bne     a1, zero, mulh_exit     # if a1 == 0, overflow occured

mulh_overflow2:
    addi    a0, a0, 1               # Overflow in lower 32 bit result -> Add 1 to upper 32 bit result

mulh_exit:

    ret


#----------------------------------------------------------------
#   int div(int a, int b)
#----------------------------------------------------------------
/* Performs 32bit / 32bit integer division, returns quotient. (rounding towards zero)
 * First, convert negative operands to positive.
 * For each 32 iteration, remainder gets one bit from a, starting from MSB.
 * If remainder is larger than b, b is subtracted from remainder
 * and quotient is incremented by 1.
 * On each step, quotient and remainder are shifted left by one bit.
 * Quotient is negated if only one of the operands was negative.
 * Two special cases (division by zero, overflow) dealt separately.
 */
    .globl  div
div:

    #--------------------------------------------
    # a0:       quotient (result)
    # a1:       remainder
    # a2:       a
    # a3:       each bit of a (starting from MSB)
    # a4:       b
    # a5        counter
    # a6:       counter for negative operands
    #-------------------------------------------- 
                                
    beq     a1, zero, div_zero       # division by zero: if b == 0, return -1
                                
                                
    li      a2, -1                   # division overflow
    bne     a1, a2, div_start        # if a == 0x80000000 and b==-1, return a    
    li      a2, 0
    lui     a2, 0x80000
    bne     a0, a2, div_start
    jal     zero, div_exit

div_start:
    mv      a2, a0
    mv      a4, a1
    li      a5, 31
    li      a6, 0
    li      a0, 0
    li      a1, 0

div_neg1:    
    bge     a2, zero, div_neg2      # if a >= 0, skip this part
    xori    a2, a2, 0xffffffff      # else, a2 = -a2 (= -a)
    addi    a2, a2, 1
    addi    a6, a6, 1               # a6 += 1
div_neg2:
    bge     a4, zero, div_loop      # if b >= 0, skip this part
    xori    a4, a4, 0xffffffff      # else (b < 0), a4 = -a4 (= -b)
    addi    a4, a4, 1      
    addi    a6, a6, 1               # a6 += 1

div_loop:                           # At each iteration,
    slli    a0, a0, 1               # shift quotient and remainder left
    slli    a1, a1, 1

    srl     a3, a2, a5              # a3 = a >> counter
    andi    a3, a3, 1               # a3 = LSB of a3
    add     a1, a1, a3              # a1 += a3

    bltu    a1, a4, div_loop_test   # if rem < b, skip this part
    sub     a1, a1, a4              # else, rem -= b, quotient += 1
    addi    a0, a0, 1

div_loop_test:
    addi    a5, a5, -1              # counter -= 1
    bge     a5, zero, div_loop      # if counter >= 0, loop again

div_sign:
    andi    a6, a6, 1               # a6 = LSB of a6 (0 if operands have same sign)
    beq     a6, zero, div_exit      # if operands have same sign, return
    xori    a0, a0, 0xffffffff      # else, a0 = -a0   
    addi    a0, a0, 1
    jal     zero, div_exit

div_zero:                           # exit for 'division by zero' case
    li      a0, -1
    ret
div_exit:
    ret

#----------------------------------------------------------------
#   int rem(int a, int b)
#----------------------------------------------------------------
/* Performs 32bit / 32bit integer division, returns remainder.
 * First, convert negative operands to positive.
 * For each 32 iteration, remainder gets one bit from a, starting from MSB.
 * If remainder is larger than b, b is subtracted from remainder
 * and quotient is incremented by 1.
 * On each step, quotient and remainder are shifted left by one bit.
 * Remainder is negated if dividend(a) was negative.
 * Two special cases (division by zero, overflow) dealt separately.
 */
    .globl  rem
rem:
    #--------------------------------------------
    # a0:       quotient
    # a1:       remainder (result)
    # a2:       a
    # a3:       each bit of a (starting from MSB)
    # a4:       b
    # a5        counter
    # a6:       check if dividend(a) is negative
    #-------------------------------------------- 

    beq     a1, zero, rem_exit       # division by zero (b=0): return a

    li      a2, -1                   # division overflow (a=0x80000000, b=-1): return 0
    bne     a1, a2, rem_start
    li      a2, 0
    lui     a2, 0x80000
    bne     a0, a2, rem_start
    li      a0, 0
    jal     zero, rem_exit

rem_start:
    mv      a2, a0
    mv      a4, a1
    li      a5, 31
    li      a6, 0
    li      a0, 0
    li      a1, 0

rem_neg1:    
    bge     a2, zero, rem_neg2      # if a >= 0, skip this part
    xori    a2, a2, 0xffffffff      # else, a2 = -a2 (= -a)
    addi    a2, a2, 1
    addi    a6, a6, 1               # a6 += 1
rem_neg2:
    bge     a4, zero, rem_loop      # if b >= 0, skip this part
    xori    a4, a4, 0xffffffff      # else (b < 0), a4 = -a4 (= -b)
    addi    a4, a4, 1      

rem_loop:                           # At each iteration,
    slli    a0, a0, 1               # shift quotient and remainder left
    slli    a1, a1, 1

    srl     a3, a2, a5              # a3 = a >> counter
    andi    a3, a3, 1               # a3 = LSB of a3
    add     a1, a1, a3              # a1 += a3

    bltu    a1, a4, rem_loop_test   # if rem < b, skip this part
    sub     a1, a1, a4              # else, rem -= b, quotient += 1
    addi    a0, a0, 1

rem_loop_test:
    addi    a5, a5, -1              # counter -= 1
    bge     a5, zero, rem_loop      # if counter >= 0, loop again

rem_sign:
    beq     a6, zero, rem_swap      # if a6==0 (dividend > 0), return
    xori    a1, a1, 0xffffffff      # else, a1 = -a1   
    addi    a1, a1, 1

rem_swap:
    mv      a0, a1                  # remainder is in a1

rem_exit:
    ret
