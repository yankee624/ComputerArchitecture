#!/usr/bin/python3
#----------------------------------------------------------------
#
#  4190.308 Computer Architecture (Fall 2019)
#
#  Project #4: A 3-Stage Pipelined RISC-V Simulator
#
#  November 19, 2019
#
#  Jin-Soo Kim (jinsoo.kim@snu.ac.kr)
#  Systems Software & Architecture Laboratory
#  Dept. of Computer Science and Engineering
#  Seoul National University
#
#----------------------------------------------------------------

import sys

from consts import *
from isa import *
from components import *
from program import *
from stages import *


#--------------------------------------------------------------------------
#   Configurations
#--------------------------------------------------------------------------

# Memory configurations
#   IMEM: 0x80000000 - 0x8000ffff (64KB)
#   DMEM: 0x80010000 - 0x8001ffff (64KB)

IMEM_START  = WORD(0x80000000)      # IMEM: 0x80000000 - 0x8000ffff (64KB)
IMEM_SIZE   = WORD(64 * 1024)
DMEM_START  = WORD(0x80010000)      # DMEM: 0x80010000 - 0x8001ffff (64KB)
DMEM_SIZE   = WORD(64 * 1024)


#--------------------------------------------------------------------------
#   SNURISC3: Target machine to simulate
#--------------------------------------------------------------------------

class SNURISC3(object):

    def __init__(self):

        stages = [ FD(), EX(), MW() ]
        self.ctl = Control()
        Pipe.set_stages(self, stages, self.ctl)
       
        self.rf = RegisterFile()
        self.alu = ALU()
        self.imem = Memory(IMEM_START, IMEM_SIZE, WORD_SIZE)
        self.dmem = Memory(DMEM_START, DMEM_SIZE, WORD_SIZE)
        self.adder_brtarget = Adder()
        self.adder_pcplus4 = Adder()

    def run(self, entry_point):
        Pipe.run(entry_point)


#--------------------------------------------------------------------------
#   Utility functions for command line parsing
#--------------------------------------------------------------------------

def show_usage(name):
    print("SNURISC3: A 3-stage Pipelined RISC-V ISA Simulator in Python")
    print("Usage: %s [-l n] [-c m] filename" % name)
    print("\tfilename: RISC-V executable file name")
    print("\t-l sets the desired log level n (default: 4)")
    print("\t   0: shows no output message")
    print("\t   1: dumps registers at the end of the execution")
    print("\t   2: dumps registers and memory at the end of the execution")
    print("\t   3: 1 + shows instructions retired from the WB stage")
    print("\t   4: 2 + shows all the instructions in the pipeline")
    print("\t   5: 3 + shows full information for each instruction")
    print("\t   6: 4 + dumps registers for each cycle")
    print("\t   7: 5 + dumps data memory for each cycle")
    print("\t-c shows logs after cycle m (default: 0, only effective for log level 3 or higher)")


def parse_args(args):
    if (not len(args) in [ 2, 4, 6 ]):
        return None

    index = 1
    while True:
        if args[index].startswith('-'):
            if args[index] == '-l':
                try:
                    level = int(args[index + 1])
                except ValueError:
                    level = 999
                if level > Log.MAX_LOG_LEVEL:
                    print("Invalid log level '%s'" % args[index + 1])
                    return None
                index += 2
                Log.level = level
            elif args[index] == '-c':
                try:
                    cycle = int(args[index + 1])
                except ValueError:
                    print("Invalid cycle number '%s'" % args[index + 1])
                    return None
                index += 2
                Log.start_cycle = cycle
            else:
                print("Invalid option '%s'" % args[index])
                return None
        else:
            break;

    if len(args) != index + 1:
        print("Invalid argument '%s'" % args[index + 1:])
        return None

    return args[index]      # executable file name


#--------------------------------------------------------------------------
#   Simulator main
#--------------------------------------------------------------------------

def main():

    filename = parse_args(sys.argv)
    if not filename:
        show_usage(sys.argv[0])
        sys.exit()

    cpu = SNURISC3()
    prog = Program()
    entry_point = prog.load(cpu, filename)
    if not entry_point:
        sys.exit()
    cpu.run(entry_point)
    Stat.show()


if __name__ == '__main__':
    main()

