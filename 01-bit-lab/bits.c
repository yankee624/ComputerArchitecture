/*------------------------------------------------------------------------------
 * 4190.308 Computer Architecture                                    Spring 2020
 *
 * Bit Lab
 *
 * Handout: March 30, 2020
 * Due:     April  8, 2020 11:00
 *
 * bits.c - solve the puzzles  by modifying this file.  Push to your CSAP GitLab
 *          account when done.  You can push as many times as you want, the last
 *          submission will be graded.
 *          The date/time of the  last submission counts as the submission date.
 *
 * WARNING: Do not include the  <stdio.h> header;  it confuses the dlc compiler.
 *          You can still use printf for debugging  without including <stdio.h>,
 *          although you might get a compiler warning. In general, it's not good
 *          practice to ignore compiler warnings, but in this case it's OK.
 */

#if 0

/*******************************************************************************
 *                  STEP 1: Read the following instructions carefully.         *
 ******************************************************************************/

CODING RULES:

  Replace the "return" statement in each function with one or more lines of C 
  code that implements the function. Your code must conform to the following 
  style:

  int Funct(arg1, arg2, ...) {
      /*
       * brief description of how your implementation works
       * >>> IMPORTANT: do not leave the description out! <<<
       */

      int var1 = Expr1;
      ...
      int varM = ExprM;

      varJ = ExprJ;
      ...
      varN = ExprN;

      return ExprR;
  }

  Each "Expr" is an expression using ONLY the following:
  1. Integer constants 0 through 255 (0xFF), inclusive. You are not allowed to
     use big constants such as 0xffffffff.
  2. Function arguments and local variables (no global variables).
  3. Unary integer operations ! ~
  4. Binary integer operations & ^ | + << >>

  Some of the problems restrict the set of allowed operators even further. Each
  "Expr" may consist of multiple operators. You are not restricted to one 
  operator per line.

  You are expressly forbidden to:
  1. Use any control constructs such as if, do, while, for, switch, etc.
  2. Define or use any macros.
  3. Define any additional functions in this file.
  4. Call any functions.
  5. Use any other operations, such as &&, ||, -, or ?:
  6. Use any form of casting.
  7. Use any data type other than int. This implies that you cannot use arrays,
     structs, or unions.

  You may assume that your machine:
  1. Uses 2s complement, 32-bit representations of integers.
  2. Performs right shifts arithmetically.
  3. Has unpredictable behavior when shifting an integer by more than the 
     word size.

EXAMPLES OF ACCEPTABLE CODING STYLE:
  /*
   * pow2plus1 - returns 2^x + 1, where 0 <= x <= 31
   */
  int pow2plus1(int x) {
     /* exploit ability of shifts to compute powers of 2 */
     return (1 << x) + 1;
  }

  /*
   * pow2plus4 - returns 2^x + 4, where 0 <= x <= 31
   */
  int pow2plus4(int x) {
     /* exploit ability of shifts to compute powers of 2 */
     int result = (1 << x);
     result += 4;
     return result;
  }

#endif

/*******************************************************************************
 *     STEP 2: Solve the following puzzles according to the coding rules.      *
 ******************************************************************************/

/*
 * isZero - returns 1 if x == 0, 0 otherwise
 *   Examples: isZero(5) = 0, isZero(0) = 1
 *   Legal ops: ! ~ & ^ | + << >>
 *   Max ops: 2
 *   Rating: 1
 */
int isZero(int x) {
  /* Logical operator ! always returns 0 or 1 */
  return !x ;
}
//
//
/*
 * minusOne - return minus one (-1)
 *   Legal ops: ! ~ & ^ | + << >>
 *   Max ops: 2
 *   Rating: 1
 */
int minusOne(void) {
  /* Bit pattern of -1 is 1111...1111 */
  return ~0;
}
//
//
/*
 * bitOr - x|y using only ~ and &
 *   Example: bitOr(8, 5) = 13
 *   Legal ops: ~ &
 *   Max ops: 8
 *   Rating: 1
 */
int bitOr(int x, int y) {
  /* De Morgan's law: NOT (x OR y) = ((NOT x) AND (NOT y)) */
  return ~((~x) & (~y));
}
//
//
/*
 * bitAnd - x&y using only ~ and |
 *   Example: bitAnd(6, 3) = 2
 *   Legal ops: ~ |
 *   Max ops: 8
 *   Rating: 1
 */
int bitAnd(int x, int y) {
  /* De Morgan's law: NOT (x AND y) = ((NOT x) OR (NOT y)) */
  return ~((~x) | (~y));
}
//
//
/* 
 * fitsShort - return 1 if x can be represented as a
 *   16-bit, two's complement integer.
 *   Examples: fitsShort(33003) = 0, fitsShort(-32768) = 1
 *   Legal ops: ! ~ & ^ | + << >>
 *   Max ops: 8
 *   Rating: 1
 */
int fitsShort(int x) {
  /* 
   * If x fits in short, 
   * its actual value is stored in the rightmost 15 bits 
   * Left 17 bits should be all 0 or all 1 (depending on the sign)
   */
  int y = x >> 15;
  int isAllZero = !y;
  int isAllOne = !(~y);
  return isAllZero | isAllOne;
}

//
//
/* 
 * fitsBits - return 1 if x can be represented as an
 *  n-bit, two's complement integer.
 *   1 <= n <= 32
 *   Examples: fitsBits(4,3) = 0, fitsBits(-4,3) = 1
 *   Legal ops: ! ~ & ^ | + << >>
 *   Max ops: 15
 *   Rating: 2
 */
int fitsBits(int x, int n) {
  /* 
   * If x fits in n-bit,
   * its actual value is stored in the rightmost (n-1) bits 
   * Left 32 - (n-1) bits should be all 0 or all 1 (depending on the sign)
   */  
  int n_minus_one = n + ~0;
  int y = x >> (n_minus_one);
  int isAllZero = !y;
  int isAllOne = !(~y);
  return isAllZero | isAllOne;
}


//
//
/*
 * isNegative - return 1 if x < 0, return 0 otherwise
 *   Example: isNegative(-3) = 1.
 *   Legal ops: ! ~ & ^ | + << >>
 *   Max ops: 6
 *   Rating: 2
 */
int isNegative(int x) {
  /* test if MSB is 1 */
  int y = x >> 31; // shift right until MSB becomes LSB
  return !!y;
}
//
//
/*
 * isEqual - return 1 if x == y, and 0 otherwise
 *   Examples: isEqual(5,5) = 1, isEqual(5,4) = 0
 *   Legal ops: ! ~ & ^ | + << >>
 *   Max ops: 5
 *   Rating: 2
 */
int isEqual(int x, int y) {
  /* if x and y are same, x XOR y returns 0 */
  return !(x^y);
}
//
//
/*
 * anyOddBit - return 1 if any odd-numbered bit in word set to 1
 *   Examples anyOddBit(0x4) = 0, anyOddBit(0x6) = 1
 *   Legal ops: ! ~ & ^ | + << >>
 *   Max ops: 12
 *   Rating: 2
 */
int anyOddBit(int x) {
  /* 
   * Test if all odd-numbered bits are 0 
   * with constant 1010...1010 (1s in odd-numbered bits)
   */
  int y = (0xaa << 8) + 0xaa;
  int onesInOdd = y + (y<<16); // 1010...1010 (32 bits long)
  int result = x & onesInOdd; // Result is 0 iff all odd-numbered bits are 0
  return !!result;
}
//
//
/*
 * allEvenBits - return 1 if all even-numbered bits in word set to 1
 *   Examples allEvenBits(0xFFFFFFFB) = 0, allEvenBits(0x55555555) = 1
 *   Legal ops: ! ~ & ^ | + << >>
 *   Max ops: 12
 *   Rating: 2
 */
int allEvenBits(int x) {
  /* 
   * Test if all even-numbered bits are 1 
   * with constant 1010...1010 (0s in even-numbered bits)
   */
  int y = (0xaa << 8) + 0xaa;
  int zerosInEven = y + (y<<16); // 1010...1010 (32 bits long)
  int result = x | zerosInEven; // Result is 1111...1111 iff all even-numbered bits are 1
  return !(~result);
}
//
//
/* 
 * leastBitPos - return a mask that marks the position of the
 *               least significant 1 bit. If x == 0, return 0
 *   Example: leastBitPos(80) = 0x10
 *   Legal ops: ! ~ & ^ | + << >>
 *   Max ops: 6
 *   Rating: 2
 */
int leastBitPos(int x) {
  /* 
   * 2s complement:
   * From LSB to the least significant 1 bit: same
   * From there to the end: negated
   * Original & Complement => only the least significant 1 bit survives
   */
  int complement = ~x + 1;
  return x & complement;
}
//
//
/*
 * addOK - Determine if x+y can be computed without overflow
 *   Example: addOK(0x80000000,0x80000000) = 0,
 *            addOK(0x80000000,0x70000000) = 1,
 *   Legal ops: ! ~ & ^ | + << >>
 *   Max ops: 20
 *   Rating: 3
 */
int addOK(int x, int y) {
  /*
   * If the sign of (x+y) is different from the signs of x and y,
   * (i.e. x>=0, y>=0, x+y<0 or x<0, y<0, x+y>=0)
   * overflow occured
   */
  int x_sign = x >> 31;
  int y_sign = y >> 31;
  int sum_sign = (x+y) >> 31;
  return !((x_sign ^ sum_sign) & (y_sign ^ sum_sign));
}
//
//
/* 
 * subOK - Determine if x-y can be computed without overflow
 *   Example: subOK(0x80000000,0x80000000) = 1,
 *            subOK(0x80000000,0x70000000) = 0,
 *   Legal ops: ! ~ & ^ | + << >>
 *   Max ops: 20
 *   Rating: 3
 */
int subOK(int x, int y) {
  /*
   * If the sign of x is different from the signs of y and (x-y),
   * (i.e. x>=0, y<0, x+y<0 or x<0, y>=0, x+y>=0)
   * overflow occured
   */
  int x_sign = x >> 31;
  int y_sign = y >> 31;
  int y_complement = ~y + 1;
  int sub_sign = (x+y_complement) >> 31;
  return !((y_sign ^ x_sign) & (sub_sign ^ x_sign));
}
//
//
/*
 * conditional - same as x ? y : z
 *   Example: conditional(2,5,4) = 5
 *   Legal ops: ! ~ & ^ | + << >>
 *   Max ops: 16
 *   Rating: 3
 */
int conditional(int x, int y, int z) {
  /*
   * If x is 0, make y 0 by ANDing with zero mask, and leave z as it is
   * If x isn't 0, make z 0 by ANDing with zero mask, and leave y as it is
   */
  int mask = !x; // 1 if x=0, 0 otherwise
  mask = ~mask + 1; // 1111...1111 if x=0, 0 otherwise
  y = ~mask & y;  
  z = mask & z;
  return y+z;
  
}
//
//
/*
 * logicalNeg - implement the ! operator, using all of
 *              the legal operators except !
 *   Examples: logicalNeg(1) = 0, logicalNeg(0) = 1
 *   Legal ops: ~ & ^ | + << >>
 *   Max ops: 12
 *   Rating: 4
 */
int logicalNeg(int x) {
  /* 
   * If x is 0, both x and its complement has MSB 0
   * Otherwise, at least one of x and its complement has MSB 1
   */
  int complement = ~x + 1;
  int msb = (x >> 31) | (complement >> 31); // check if both MSBs are zero
  return msb + 1;
}
