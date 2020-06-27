/*------------------------------------------------------------------------------
 * 4190.308 Computer Architecture                                    Spring 2020
 *
 * Compute Lab
 *
 * Handout:    April  8, 2020
 * Due:        April 20, 2020 11:00
 *
 * compute.c - implement the functions in this file. Push to your CSAP GitLab
 *             account when done. You can push as many times as you want, the
 *             last submission will be graded.
 *             The date/time of the last submission counts as the submission
 *             date.
 *
 * WARNING:    You should use only 32-bit interger operations inside the
 *             Uadd64(), Usub64(), Umul64(), and Udiv64() functions.
 */

#include <stdio.h>
#include "compute.h"


/* Uadd64() implements the addition of two 64-bit unsigned integers.
 * Assume that A and B are the 64-bit unsigned integer represented by
 * a and b, respectively. Uadd64() should return x, where x.hi and x.lo
 * contain the upper and lower 32 bits of (A + B), respectively.
 */
HL64 Uadd64 (HL64 a, HL64 b)
{ 
  /* Compute the sum of lower 32 bits, then the sum of upper 32 bits.
   * If overflow occured when computing the lower 32 bits sum, 
   * add 1 when computing the upper 32 bits sum.
   */
  HL64 r = {0, 0};
  int overflow = 0;

  r.lo = a.lo + b.lo;
  /* overflow occured if the result is smaller than either operand */
  if(r.lo < a.lo || r.lo < b.lo){ 
    overflow = 1;
  }
  r.hi = a.hi + b.hi + overflow;

  return r;
}

/* Usub64() implements the subtraction between two 64-bit unsigned integers.
 * Assume that A and B are the 64-bit unsigned integer represented by
 * a and b, respectively. Usub64() should return x, where x.hi and x.lo
 * contain the upper and lower 32 bits of (A - B), respectively.
 */
HL64 Usub64 (HL64 a, HL64 b)
{
  /* Compute the difference of lower 32 bits, then the difference of upper 32 bits.
   * If underflow occured when computing the lower 32 bits difference, 
   * subtract 1 when computing the upper 32 bits difference.
   */
  HL64 r = {0, 0};
  int underflow = 0;

  r.lo = a.lo - b.lo;
  /* underflow occured if the result is bigger than minuend*/
  if(r.lo > a.lo){ 
    underflow = 1;
  }
  r.hi = a.hi - underflow - b.hi;

  return r;
}


/* Umul64() implements the multiplication of two 64-bit unsigned integers.
 * Assume that A and B are the 64-bit unsigned integer represented by
 * a and b, respectively.  Umul64() should return x, where x.hi and x.lo
 * contain the upper and lower 32 bits of (A * B), respectively.
 */
HL64 Umul64 (HL64 a, HL64 b)
{
  /* Starting from the LSB of multiplier(b) to the MSB,
   * if the bit is 1, add the multiplcand to the result.
   * On each step, multiplicand is shifted left by one bit.
   */
  HL64 r = {0, 0};
  for(int i=0; i<64; i++){
    if(bitVal(b, i)){
      r = Uadd64(r, a);
    }
    a = shiftLeft(a);
  }
  return r;
}


/* Udiv64() implements the division of two 64-bit unsigned integers.
 * Assume that A and B are the 64-bit unsigned integer represented by
 * a and b, respectively.  Udiv64() should return x, where x.hi and x.lo
 * contain the upper and lower 32 bits of the quotient of (A / B),
 * respectively.
 */
HL64 Udiv64 (HL64 a, HL64 b)
{
  /* For each 64 iteration, remainder gets one bit from a, starting from MSB.
   * If remainder is larger than b, b is subtracted from remainder
   * and quotient is incremented by 1.
   * On each step, quotient and remainder are shifted left by one bit.
   */
  HL64 q = {0, 0};
  HL64 rem = {0, 0};
  if(b.hi == 0 && b.lo == 0) return q;

  for(int i=0; i<64; i++){
    q = shiftLeft(q);
    rem = shiftLeft(rem);
    /* Copy the bit value of a to remainder */
    if(bitVal(a, 63-i)){
      rem.lo += 1;
    }
    if(compare(rem, b) >= 0){
      rem = Usub64(rem, b);
      q.lo += 1;
    }
  }
  return q;
}

/* shiftLeft() logically shifts a 64-bit unsigned integer(a) left by one bit. */
HL64 shiftLeft(HL64 a){
  /* First, shift left each of a.hi and a.lo.
   * Then, if the MSB of a.lo is 1, add 1 to the LSB of upper 32 bits of result.
   */
  HL64 r = {a.hi << 1, a.lo << 1};
  if(bitVal(a,31)){
    r.hi += 1;
  }
  return r;
}

/* shiftRight() logically shifts a 64-bit unsigned integer(a) right by one bit. */
HL64 shiftRight(HL64 a){
  /* First, shift right each of a.hi and a.lo.
   * Then, if the LSB of a.hi is 1, add 1 to the MSB of lower 32 bits of result.
   */
  HL64 r = {a.hi >> 1, a.lo >> 1};
  if(bitVal(a,32)){
    r.lo |= 1<<31;
  }
  return r;
}


/* compare() compares the value of two 64-bit unsigned integers(a,b). It returns... 
 * 1 if a > b
 * 0 if a = b
 * -1 if a < b
 */
int compare(HL64 a, HL64 b){
  /* First, compare upper 32 bits
   * If upper 32 bits are equal, compare lower 32 bits.
   */
  if(a.hi > b.hi){
    return 1;
  } else if (a.hi < b.hi){
    return -1;
  } else{
    if(a.lo > b.lo) return 1;
    else if(a.lo < b.lo) return -1;
    else return 0;
  }
}

/* bitVal() checks specific bit position of a 64-bit unsigned integer(a).
 * It returns 1 if the n-th bit of a is 1, otherwise returns 0. 
 * If illegal argument (n<0 or n>63) is given, it returns -1.
 */
int bitVal(HL64 a, int n){
  /* Checks the n-th bit by ANDing with the constant 
   * which has 1 only in the n-th bit 
   */
  if(0 <= n && n < 32){
    return a.lo & (1<<n) ? 1 : 0;
  } else if(32 <= n && n < 64){
    return a.hi & (1<<(n-32)) ? 1: 0;
  }
  return -1;
}