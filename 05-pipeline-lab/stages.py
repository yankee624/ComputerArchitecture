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
from pipe import *


#--------------------------------------------------------------------------
#   Control signal table
#--------------------------------------------------------------------------

csignals = {
    LW     : [ Y, BR_N  , OP1_RS1, OP2_IMI, OEN_1, OEN_0, ALU_ADD  , WB_MEM, REN_1, MEN_1, M_XRD, MT_W, ],
    SW     : [ Y, BR_N  , OP1_RS1, OP2_IMS, OEN_1, OEN_1, ALU_ADD  , WB_X  , REN_0, MEN_1, M_XWR, MT_W, ],
    AUIPC  : [ Y, BR_N  , OP1_PC,  OP2_IMU, OEN_0, OEN_0, ALU_ADD  , WB_ALU, REN_1, MEN_0, M_X  , MT_X, ],
    LUI    : [ Y, BR_N  , OP1_X,   OP2_IMU, OEN_0, OEN_0, ALU_COPY2, WB_ALU, REN_1, MEN_0, M_X  , MT_X, ],
    ADDI   : [ Y, BR_N  , OP1_RS1, OP2_IMI, OEN_1, OEN_0, ALU_ADD  , WB_ALU, REN_1, MEN_0, M_X  , MT_X, ],

    SLLI   : [ Y, BR_N  , OP1_RS1, OP2_IMI, OEN_1, OEN_0, ALU_SLL  , WB_ALU, REN_1, MEN_0, M_X  , MT_X, ],
    SLTI   : [ Y, BR_N  , OP1_RS1, OP2_IMI, OEN_1, OEN_0, ALU_SLT  , WB_ALU, REN_1, MEN_0, M_X  , MT_X, ],
    SLTIU  : [ Y, BR_N  , OP1_RS1, OP2_IMI, OEN_1, OEN_0, ALU_SLTU , WB_ALU, REN_1, MEN_0, M_X  , MT_X, ],
    XORI   : [ Y, BR_N  , OP1_RS1, OP2_IMI, OEN_1, OEN_0, ALU_XOR  , WB_ALU, REN_1, MEN_0, M_X  , MT_X, ],
    SRLI   : [ Y, BR_N  , OP1_RS1, OP2_IMI, OEN_1, OEN_0, ALU_SRL  , WB_ALU, REN_1, MEN_0, M_X  , MT_X, ],

    SRAI   : [ Y, BR_N  , OP1_RS1, OP2_IMI, OEN_1, OEN_0, ALU_SRA  , WB_ALU, REN_1, MEN_0, M_X  , MT_X, ],
    ORI    : [ Y, BR_N  , OP1_RS1, OP2_IMI, OEN_1, OEN_0, ALU_OR   , WB_ALU, REN_1, MEN_0, M_X  , MT_X, ],
    ANDI   : [ Y, BR_N  , OP1_RS1, OP2_IMI, OEN_1, OEN_0, ALU_AND  , WB_ALU, REN_1, MEN_0, M_X  , MT_X, ],
    ADD    : [ Y, BR_N  , OP1_RS1, OP2_RS2, OEN_1, OEN_1, ALU_ADD  , WB_ALU, REN_1, MEN_0, M_X  , MT_X, ],
    SUB    : [ Y, BR_N  , OP1_RS1, OP2_RS2, OEN_1, OEN_1, ALU_SUB  , WB_ALU, REN_1, MEN_0, M_X  , MT_X, ],

    SLL    : [ Y, BR_N  , OP1_RS1, OP2_RS2, OEN_1, OEN_1, ALU_SLL  , WB_ALU, REN_1, MEN_0, M_X  , MT_X, ],
    SLT    : [ Y, BR_N  , OP1_RS1, OP2_RS2, OEN_1, OEN_1, ALU_SLT  , WB_ALU, REN_1, MEN_0, M_X  , MT_X, ],
    SLTU   : [ Y, BR_N  , OP1_RS1, OP2_RS2, OEN_1, OEN_1, ALU_SLTU , WB_ALU, REN_1, MEN_0, M_X  , MT_X, ],
    XOR    : [ Y, BR_N  , OP1_RS1, OP2_RS2, OEN_1, OEN_1, ALU_XOR  , WB_ALU, REN_1, MEN_0, M_X  , MT_X, ],
    SRL    : [ Y, BR_N  , OP1_RS1, OP2_RS2, OEN_1, OEN_1, ALU_SRL  , WB_ALU, REN_1, MEN_0, M_X  , MT_X, ],

    SRA    : [ Y, BR_N  , OP1_RS1, OP2_RS2, OEN_1, OEN_1, ALU_SRA  , WB_ALU, REN_1, MEN_0, M_X  , MT_X, ],
    OR     : [ Y, BR_N  , OP1_RS1, OP2_RS2, OEN_1, OEN_1, ALU_OR   , WB_ALU, REN_1, MEN_0, M_X  , MT_X, ],
    AND    : [ Y, BR_N  , OP1_RS1, OP2_RS2, OEN_1, OEN_1, ALU_AND  , WB_ALU, REN_1, MEN_0, M_X  , MT_X, ],
    JALR   : [ Y, BR_JR , OP1_RS1, OP2_IMI, OEN_1, OEN_0, ALU_ADD  , WB_PC4, REN_1, MEN_0, M_X  , MT_X, ],   
    JAL    : [ Y, BR_J  , OP1_RS1, OP2_IMJ, OEN_0, OEN_0, ALU_X    , WB_PC4, REN_1, MEN_0, M_X  , MT_X, ],

    BEQ    : [ Y, BR_EQ , OP1_RS1, OP2_IMB, OEN_1, OEN_1, ALU_SEQ  , WB_X  , REN_0, MEN_0, M_X  , MT_X, ],
    BNE    : [ Y, BR_NE , OP1_RS1, OP2_IMB, OEN_1, OEN_1, ALU_SEQ  , WB_X  , REN_0, MEN_0, M_X  , MT_X, ],
    BLT    : [ Y, BR_LT , OP1_RS1, OP2_IMB, OEN_1, OEN_1, ALU_SLT  , WB_X  , REN_0, MEN_0, M_X  , MT_X, ],
    BGE    : [ Y, BR_GE , OP1_RS1, OP2_IMB, OEN_1, OEN_1, ALU_SLT  , WB_X  , REN_0, MEN_0, M_X  , MT_X, ],
    BLTU   : [ Y, BR_LTU, OP1_RS1, OP2_IMB, OEN_1, OEN_1, ALU_SLTU , WB_X  , REN_0, MEN_0, M_X  , MT_X, ],

    BGEU   : [ Y, BR_GEU, OP1_RS1, OP2_IMB, OEN_1, OEN_1, ALU_SLTU , WB_X  , REN_0, MEN_0, M_X  , MT_X, ],
    ECALL  : [ Y, BR_N  , OP1_X  , OP2_X  , OEN_0, OEN_0, ALU_X    , WB_X  , REN_0, MEN_0, M_X  , MT_X, ],
}


#--------------------------------------------------------------------------
#   Control: Control logic (executed in FD stage)
#--------------------------------------------------------------------------

class Control(object):

    def __init__(self):
        super().__init__()

        # Internal signals:----------------------------
        #
        #   self.pc_sel             # Pipe.CTL.pc_sel
        #   self.br_type            # Pipe.CTL.br_type
        #   self.op1_sel            # Pipe.CTL.op1_sel
        #   self.op2_sel            # Pipe.CTL.op2_sel
        #   self.alu_fun            # Pipe.CTL.alu_fun
        #   self.wb_sel             # Pipe.CTL.wb_sel
        #   self.rf_wen             # Pipe.CTL.rf_wen
        #   self.imem_en            # Pipe.CTL.imem_en
        #   self.imem_rw            # Pipe.CTL.imem_rw
        #   self.dmem_en            # Pipe.CTL.dmem_en
        #   self.dmem_rw            # Pipe.CTL.dmem_rw
        
        #   self.fwd_op1            # Pipe.CTL.fwd_op1
        #   self.fwd_op2            # Pipe.CTL.fwd_op2
        #   self.fwd_rs2            # Pipe.CTL.fwd_rs2
        #   self.FD_stall           # Pipe.CTL.FD_stall
        #   self.EX_bubble          # Pipe.CTL.EX_bubble
        #   self.MW_bubble          # Pipe.CTL.MW_bubble
        #
        #----------------------------------------------


        # These signals are used before gen() is called
        self.imem_en        = True
        self.imem_rw        = M_XRD


    def gen(self, inst):
        from stages import FD, EX, MW

        self.MW_bubble      = False

        # DO NOT TOUCH------------------------------------------------
        opcode = RISCV.opcode(inst)
        if opcode == ECALL:
            Pipe.FD.exception |= EXC_ECALL
        elif opcode == ILLEGAL:
            Pipe.FD.exception |= EXC_ILLEGAL_INST
            inst = BUBBLE
            opcode = RISCV.opcode(inst)

        cs = csignals[opcode]

        self.br_type        = cs[CS_BR_TYPE]
        self.op1_sel        = cs[CS_OP1_SEL]
        self.op2_sel        = cs[CS_OP2_SEL]
        self.alu_fun        = cs[CS_ALU_FUN]
        self.wb_sel         = cs[CS_WB_SEL]
        self.rf_wen         = cs[CS_RF_WEN]

        rs1_oen             = cs[CS_RS1_OEN]
        rs2_oen             = cs[CS_RS2_OEN]

        self.dmem_en        = cs[CS_MEM_EN]
        self.dmem_rw        = cs[CS_MEM_FCN]
        #-------------------------------------------------------------

        # Control signal to select the next PC
        self.pc_sel         =   PC_BRJMP    if (EX.reg_c_br_type == BR_NE  and (not Pipe.EX.alu_out)) or    \
                                               (EX.reg_c_br_type == BR_EQ  and Pipe.EX.alu_out) or          \
                                               (EX.reg_c_br_type == BR_GE  and (not Pipe.EX.alu_out)) or    \
                                               (EX.reg_c_br_type == BR_GEU and (not Pipe.EX.alu_out)) or    \
                                               (EX.reg_c_br_type == BR_LT  and Pipe.EX.alu_out) or          \
                                               (EX.reg_c_br_type == BR_LTU and Pipe.EX.alu_out) or          \
                                               (EX.reg_c_br_type == BR_J) else                              \
                                PC_JALR     if  EX.reg_c_br_type == BR_JR else                              \
                                PC_4

        # Control signal for forwarding rs1 value to op1_data
        # The c_rf_wen signal can be disabled when we have an exception during dmem access,
        # so Pipe.MW.c_rf_wen should be used instead of MW.reg_c_rf_wen.
        self.fwd_op1        =   FWD_EX      if (EX.reg_rd == Pipe.FD.rs1) and rs1_oen and   \
                                               (EX.reg_rd != 0) and EX.reg_c_rf_wen else    \
                                FWD_MW      if (MW.reg_rd == Pipe.FD.rs1) and rs1_oen and   \
                                               (MW.reg_rd != 0) and Pipe.MW.c_rf_wen else   \
                                FWD_NONE

        # Control signal for forwarding rs2 value to op2_data
        # Exclude forwarding op2 for branch and sw instruction (do this in rs2 forwarding below)
        self.fwd_op2        =   FWD_EX      if (EX.reg_rd == Pipe.FD.rs2) and               \
                                               (EX.reg_rd != 0) and EX.reg_c_rf_wen and     \
                                               self.op2_sel == OP2_RS2 else                 \
                                FWD_MW      if (MW.reg_rd == Pipe.FD.rs2) and               \
                                               (MW.reg_rd != 0) and Pipe.MW.c_rf_wen and    \
                                               self.op2_sel == OP2_RS2 else                 \
                                FWD_NONE

        # Control signal for forwarding rs2 value to rs2_data
        # Forwarding for branch and sw instruction included (rs2_oen)
        self.fwd_rs2        =   FWD_EX      if (EX.reg_rd == Pipe.FD.rs2) and rs2_oen and   \
                                               (EX.reg_rd != 0) and EX.reg_c_rf_wen  else   \
                                FWD_MW      if (MW.reg_rd == Pipe.FD.rs2) and rs2_oen and   \
                                               (MW.reg_rd != 0) and Pipe.MW.c_rf_wen else   \
                                FWD_NONE

        # Check for load-use data hazard
        EX_opcode = RISCV.opcode(EX.reg_inst)
        EX_cs = csignals[EX_opcode]
        EX_load_inst = EX_cs[CS_MEM_EN] and EX_cs[CS_MEM_FCN] == M_XRD
        # Equivalently...
        # EX_load_inst = EX.reg_c_dmem_en and (EX.reg_c_dmem_rw == M_XRD)

        # store_inst = self.dmem_en and self.dmem_rw == M_XWR
        load_use_hazard     = (EX_load_inst and EX.reg_rd != 0) and             \
                              ((EX.reg_rd == Pipe.FD.rs1 and rs1_oen) or        \
                               (EX.reg_rd == Pipe.FD.rs2 and rs2_oen)) # and not store_inst)) -> load-store forwarding



        # Check for mispredicted branch/jump
        EX_brjmp            = self.pc_sel != PC_4

        self.FD_stall       = load_use_hazard
        self.EX_bubble      = EX_brjmp or load_use_hazard



        # DO NOT TOUCH -----------------------------------------------
        # Any instruction with an exception becomes BUBBLE as it enters the MW stage. (except ECALL)
        # All the following instructions after exception become BUBBLE too.
        self.MW_bubble = (Pipe.EX.exception and (Pipe.EX.exception != EXC_ECALL)) or (Pipe.MW.exception)

        if inst == BUBBLE:
            return False
        else:
            return True
        #-------------------------------------------------------------


#--------------------------------------------------------------------------
#   FD: Instruction fetch and decode stage
#--------------------------------------------------------------------------

class FD(Pipe):

    # Pipeline registers ------------------------------

    reg_pc          = WORD(0)       # FD.reg_pc

    #--------------------------------------------------


    def __init__(self):
        super().__init__()

        # Internal signals:----------------------------
        #
        #   self.pc                 # Pipe.FD.pc
        #   self.inst               # Pipe.FD.inst
        #   self.exception          # Pipe.FD.exception
        #   self.pc_next            # Pipe.FD.pc_next
        #   self.pcplus4            # Pipe.FD.pcplus4
        #
        #   self.rs1                # Pipe.FD.rs1
        #   self.rs2                # Pipe.FD.rs2
        #   self.rd                 # Pipe.FD.rd
        #   self.op1_data           # Pipe.FD.op1_data
        #   self.op2_data           # Pipe.FD.op2_data
        #   self.rs2_data           # Pipe.FD.rs2_data
        #
        #----------------------------------------------

    def compute(self):

        # DO NOT TOUCH -----------------------------------------------
        # Read out pipeline register values
        self.pc     = FD.reg_pc

        # Fetch an instruction from instruction memory (imem)
        self.inst, status = Pipe.cpu.imem.access(Pipe.CTL.imem_en, self.pc, 0, Pipe.CTL.imem_rw)

        # Handle exception during imem access
        if not status:
            self.exception = EXC_IMEM_ERROR
            self.inst = BUBBLE
        else:
            self.exception = EXC_NONE
        #-------------------------------------------------------------



        self.rs1        = RISCV.rs1(self.inst)
        self.rs2        = RISCV.rs2(self.inst)
        self.rd         = RISCV.rd(self.inst)

        imm_i           = RISCV.imm_i(self.inst)
        imm_s           = RISCV.imm_s(self.inst)
        imm_b           = RISCV.imm_b(self.inst)
        imm_u           = RISCV.imm_u(self.inst)
        imm_j           = RISCV.imm_j(self.inst)

        rf_rs1_data     = Pipe.cpu.rf.read(self.rs1)
        rf_rs2_data     = Pipe.cpu.rf.read(self.rs2)

        # Generate control signals
        if not Pipe.CTL.gen(self.inst):
            self.inst = BUBBLE

       # Determine ALU operand 2: R[rs2] or immediate values
        alu_op2 =         rf_rs2_data   if Pipe.CTL.op2_sel == OP2_RS2  else \
                          imm_i         if Pipe.CTL.op2_sel == OP2_IMI  else \
                          imm_s         if Pipe.CTL.op2_sel == OP2_IMS  else \
                          imm_b         if Pipe.CTL.op2_sel == OP2_IMB  else \
                          imm_u         if Pipe.CTL.op2_sel == OP2_IMU  else \
                          imm_j         if Pipe.CTL.op2_sel == OP2_IMJ  else \
                          WORD(0)
        

        # Determine ALU operand 1: PC / R[rs1] / forwarded value 
        # The order matters: EX -> MW 
        self.op1_data = self.pc         if Pipe.CTL.op1_sel == OP1_PC       else \
                        Pipe.EX.alu_out if Pipe.CTL.fwd_op1 == FWD_EX       else \
                        Pipe.MW.wbdata  if Pipe.CTL.fwd_op1 == FWD_MW       else \
                        rf_rs1_data
        # Determine ALU operand 2: alu_op2(imm / R[rs2]) / forwarded value
        self.op2_data = Pipe.EX.alu_out if Pipe.CTL.fwd_op2 == FWD_EX       else \
                        Pipe.MW.wbdata  if Pipe.CTL.fwd_op2 == FWD_MW       else \
                        alu_op2

        # Determine rs2 data, which will be used by branch(EX) / sw(MW) instructions
        # -- in these instructions, op2_data will hold an immediate value (branch / memory offset)
        # -- and rs2_data will hold register 2 value 
        self.rs2_data = Pipe.EX.alu_out if Pipe.CTL.fwd_rs2 == FWD_EX       else \
                        Pipe.MW.wbdata  if Pipe.CTL.fwd_rs2 == FWD_MW       else \
                        rf_rs2_data


        # PC + 4 for jal / jalr instruction
        self.pcplus4    = Pipe.cpu.adder_pcplus4.op(self.pc, 4)

        # Select next PC based on Control signal
        self.pc_next =  self.pcplus4            if Pipe.CTL.pc_sel == PC_4      else \
                        Pipe.EX.brjmp_target    if Pipe.CTL.pc_sel == PC_BRJMP  else \
                        Pipe.EX.jump_reg_target if Pipe.CTL.pc_sel == PC_JALR   else \
                        WORD(0)  

    def update(self):
        if not Pipe.CTL.FD_stall:
            FD.reg_pc               = self.pc_next
        else:   
            pass                    # stall -> don't update PC

        if Pipe.CTL.EX_bubble:
            EX.reg_inst             = WORD(BUBBLE)
            EX.reg_exception        = WORD(EXC_NONE)
            EX.reg_c_br_type        = WORD(BR_N)
            EX.reg_c_rf_wen         = False
            EX.reg_c_dmem_en        = False
        else:
            EX.reg_pc               = self.pc
            EX.reg_inst             = self.inst
            EX.reg_exception        = self.exception
            EX.reg_rd               = self.rd
            EX.reg_op1_data         = self.op1_data
            EX.reg_op2_data         = self.op2_data
            EX.reg_rs2_data         = self.rs2_data
            EX.reg_c_br_type        = Pipe.CTL.br_type
            EX.reg_c_rf_wen         = Pipe.CTL.rf_wen
            EX.reg_c_alu_fun        = Pipe.CTL.alu_fun
            EX.reg_c_wb_sel         = Pipe.CTL.wb_sel
            EX.reg_c_dmem_en        = Pipe.CTL.dmem_en
            EX.reg_c_dmem_rw        = Pipe.CTL.dmem_rw
            EX.reg_pcplus4          = self.pcplus4
            # EX.reg_rs2              = self.rs2

        # DO NOT TOUCH -----------------------------------------------
        Pipe.log(S_FD, self.pc, self.inst, self.log())
        #-------------------------------------------------------------


    # DO NOT TOUCH ---------------------------------------------------
    def log(self):
        if self.inst in [ BUBBLE, ILLEGAL ]:
            return('# -')
        else:
            return("# inst=0x%08x, pc_next=0x%08x, rd=%d rs1=%d rs2=%d op1=0x%08x op2=0x%08x" 
                    % (self.inst, self.pc_next, self.rd, self.rs1, self.rs2, self.op1_data, self.op2_data))
    #-----------------------------------------------------------------


#--------------------------------------------------------------------------
#   EX: Execution stage
#--------------------------------------------------------------------------

class EX(Pipe):

    # Pipeline registers ------------------------------

    reg_pc              = WORD(0)           # EX.reg_pc
    reg_inst            = WORD(BUBBLE)      # EX.reg_inst
    reg_exception       = WORD(EXC_NONE)    # EX.exception
    reg_rd              = WORD(0)           # EX.reg_rd
    reg_c_rf_wen        = False             # EX.reg_c_rf_wen
    reg_c_wb_sel        = WORD(WB_X)        # EX.reg_c_wb_sel
    reg_c_dmem_en       = False             # EX.reg_c_dmem_en
    reg_c_dmem_rw       = WORD(M_X)         # EX.reg_c_dmem_rw
    reg_c_br_type       = WORD(BR_N)        # EX.reg_c_br_type
    reg_c_alu_fun       = WORD(ALU_X)       # EX.reg_c_alu_fun
    reg_op1_data        = WORD(0)           # EX.reg_op1_data
    reg_op2_data        = WORD(0)           # EX.reg_op2_data
    reg_rs2_data        = WORD(0)           # EX.reg_rs2_data
    reg_pcplus4         = WORD(0)           # EX.reg_pcplus4
    # reg_rs2             = WORD(0)           # EX.reg_rs2
    #--------------------------------------------------


    def __init__(self):
        super().__init__()

        # Internal signals:----------------------------
        #
        #   self.pc                 # Pipe.EX.pc
        #   self.inst               # Pipe.EX.inst
        #   self.exception          # Pipe.EX.exception
        #   self.rd                 # Pipe.EX.rd
        #   self.c_rf_wen           # Pipe.EX.c_rf_wen
        #   self.c_wb_sel           # Pipe.EX.c_wb_sel        
        #   self.c_dmem_en          # Pipe.EX.c_dmem_en
        #   self.c_dmem_rw          # Pipe.EX.c_dmem_fcn
        #   self.c_br_type          # Pipe.EX.c_br_type        
        #   self.c_alu_fun          # Pipe.EX.c_alu_fun
        #   self.op1_data           # Pipe.EX.op1_data
        #   self.op2_data           # Pipe.EX.op2_data
        #   self.rs2_data           # Pipe.EX.rs2_data
        #   self.pcplus4            # Pipe.EX.pcplus4
        #
        #   self.alu2_data          # Pipe.EX.alu2_data
        #   self.alu_out            # Pipe.EX.alu_out
        #   self.brjmp_target       # Pipe.EX.brjmp_target
        #   self.jump_reg_target    # Pipe.EX.jump_reg_target
        #
        #----------------------------------------------


    def compute(self):

        # Read out pipeline register values
        self.pc                 = EX.reg_pc
        self.inst               = EX.reg_inst
        self.exception          = EX.reg_exception
        self.rd                 = EX.reg_rd
        self.c_rf_wen           = EX.reg_c_rf_wen
        self.c_wb_sel           = EX.reg_c_wb_sel
        self.c_dmem_en          = EX.reg_c_dmem_en
        self.c_dmem_rw          = EX.reg_c_dmem_rw
        self.c_br_type          = EX.reg_c_br_type        
        self.c_alu_fun          = EX.reg_c_alu_fun
        self.op1_data           = EX.reg_op1_data
        self.op2_data           = EX.reg_op2_data
        self.rs2_data           = EX.reg_rs2_data
        self.pcplus4            = EX.reg_pcplus4
        # self.rs2                = EX.reg_rs2

        # load - store rs2 dependency forwarding
        # load_store      = (self.c_dmem_en and self.c_dmem_rw == M_XWR) and          \
        #                   (MW.reg_c_dmem_en and MW.reg_c_dmem_rw == M_XRD) and      \
        #                   MW.reg_rd != 0 and                                        \
        #                   self.rs2 == MW.reg_rd
        # if load_store: 
        #     self.rs2_data =  Pipe.MW.wbdata

        # The second input to ALU should be put into self.alu2_data for correct log msg.
        self.alu2_data  = self.rs2_data     if self.c_br_type in [ BR_NE, BR_EQ, BR_GE, BR_GEU, BR_LT, BR_LTU ] else \
                          self.op2_data

        # Perform ALU operation
        self.alu_out = Pipe.cpu.alu.op(self.c_alu_fun, self.op1_data, self.alu2_data)

        # Adjust the output for jalr instruction (forwarded to FD)
        self.jump_reg_target    = self.alu_out & WORD(0xfffffffe) 

        # Calculate the branch/jal target address using an adder (forwarded to FD)
        self.brjmp_target       = Pipe.cpu.adder_brtarget.op(self.pc, self.op2_data) 

        # For jal and jalr instructions, pc+4 should be written to the rd
        if self.c_wb_sel == WB_PC4:                   
            self.alu_out        = self.pcplus4


    def update(self):

        MW.reg_pc               = self.pc
        MW.reg_exception        = self.exception

        if Pipe.CTL.MW_bubble:
            MW.reg_inst         = WORD(BUBBLE)
            MW.reg_c_rf_wen     = False
            MW.reg_c_dmem_en    = False
        else:
            MW.reg_inst         = self.inst
            MW.reg_rd           = self.rd
            MW.reg_c_rf_wen     = self.c_rf_wen
            MW.reg_c_wb_sel     = self.c_wb_sel
            MW.reg_c_dmem_en    = self.c_dmem_en
            MW.reg_c_dmem_rw    = self.c_dmem_rw            
            MW.reg_alu_out      = self.alu_out            
            MW.reg_rs2_data     = self.rs2_data


        # DO NOT TOUCH -----------------------------------------------
        Pipe.log(S_EX, self.pc, self.inst, self.log())
        #-------------------------------------------------------------


    # DO NOT TOUCH ---------------------------------------------------
    def log(self):

        ALU_OPS = {
            ALU_X       : f'# -',
            ALU_ADD     : f'# {self.alu_out:#010x} <- {self.op1_data:#010x} + {self.alu2_data:#010x}',
            ALU_SUB     : f'# {self.alu_out:#010x} <- {self.op1_data:#010x} - {self.alu2_data:#010x}',
            ALU_AND     : f'# {self.alu_out:#010x} <- {self.op1_data:#010x} & {self.alu2_data:#010x}',
            ALU_OR      : f'# {self.alu_out:#010x} <- {self.op1_data:#010x} | {self.alu2_data:#010x}',
            ALU_XOR     : f'# {self.alu_out:#010x} <- {self.op1_data:#010x} ^ {self.alu2_data:#010x}',
            ALU_SLT     : f'# {self.alu_out:#010x} <- {self.op1_data:#010x} < {self.alu2_data:#010x} (signed)',
            ALU_SLTU    : f'# {self.alu_out:#010x} <- {self.op1_data:#010x} < {self.alu2_data:#010x} (unsigned)',
            ALU_SLL     : f'# {self.alu_out:#010x} <- {self.op1_data:#010x} << {self.alu2_data & 0x1f}',
            ALU_SRL     : f'# {self.alu_out:#010x} <- {self.op1_data:#010x} >> {self.alu2_data & 0x1f} (logical)',
            ALU_SRA     : f'# {self.alu_out:#010x} <- {self.op1_data:#010x} >> {self.alu2_data & 0x1f} (arithmetic)',
            ALU_COPY1   : f'# {self.alu_out:#010x} <- {self.op1_data:#010x} (pass 1)',
            ALU_COPY2   : f'# {self.alu_out:#010x} <- {self.alu2_data:#010x} (pass 2)',
            ALU_SEQ     : f'# {self.alu_out:#010x} <- {self.op1_data:#010x} == {self.alu2_data:#010x}',
        }
        return('# -' if self.inst == BUBBLE else ALU_OPS[self.c_alu_fun]);
    #-----------------------------------------------------------------


#--------------------------------------------------------------------------
#   MW: Memory access and write back stage
#--------------------------------------------------------------------------

class MW(Pipe):

    # Pipeline registers ------------------------------

    reg_pc              = WORD(0)           # MW.reg_pc
    reg_inst            = WORD(BUBBLE)      # MW.reg_inst
    reg_exception       = WORD(EXC_NONE)    # MW.reg_exception
    reg_rd              = WORD(0)           # MW.reg_rd
    reg_c_rf_wen        = False             # MW.reg_c_rf_wen
    reg_c_wb_sel        = WORD(WB_X)        # MW.reg_c_wb_sel
    reg_c_dmem_en       = False             # MW.reg_c_dmem_en
    reg_c_dmem_rw       = WORD(M_X)         # MW.reg_c_dmem_rw
    reg_alu_out         = WORD(0)           # MW.reg_alu_out
    reg_rs2_data        = WORD(0)           # MW.reg_rs2_data
    #--------------------------------------------------

    def __init__(self):
        super().__init__()

        # Internal signals:----------------------------
        #
        #   self.pc                 # Pipe.MW.pc
        #   self.inst               # Pipe.MW.inst
        #   self.exception          # Pipe.MW.exception
        #   self.rd                 # Pipe.MW.rd
        #   self.c_rf_wen           # Pipe.MW.c_rf_wen
        #   self.c_wb_sel           # Pipe.MW.c_rf_wen
        #   self.c_dmem_en          # Pipe.MW.c_dmem_en
        #   self.c_dmem_rw          # Pipe.MW.c_dmem_rw    
        #   self.alu_out            # Pipe.MW.alu_out
        #   self.rs2_data           # Pipe.MW.rs2_data
        #
        #   self.wbdata             # Pipe.MM.wbdata
        #
        #----------------------------------------------

    def compute(self):

        # Read out pipeline register values
        self.pc             = MW.reg_pc
        self.inst           = MW.reg_inst
        self.exception      = MW.reg_exception
        self.rd             = MW.reg_rd
        self.c_rf_wen       = MW.reg_c_rf_wen
        self.c_wb_sel       = MW.reg_c_wb_sel
        self.c_dmem_en      = MW.reg_c_dmem_en
        self.c_dmem_rw      = MW.reg_c_dmem_rw
        self.alu_out        = MW.reg_alu_out  
        self.rs2_data       = MW.reg_rs2_data 

        # Access data memory (dmem) if needed
        mem_data, status = Pipe.cpu.dmem.access(self.c_dmem_en, self.alu_out, self.rs2_data, self.c_dmem_rw)

        # Handle exception during dmem access
        if not status:
            self.exception |= EXC_DMEM_ERROR
            self.c_rf_wen   = False
    
        # For load instruction, store the value read from dmem
        self.wbdata         = mem_data          if self.c_wb_sel == WB_MEM  else \
                              self.alu_out  



    def update(self):
    
        if self.c_rf_wen:
            Pipe.cpu.rf.write(self.rd, self.wbdata)


        # DO NOT TOUCH -----------------------------------------------
        Pipe.log(S_MW, self.pc, self.inst, self.log())

        if (self.exception):
            return False
        else:
            return True
        # ------------------------------------------------------------


    # DO NOT TOUCH ---------------------------------------------------
    def log(self):
        if self.inst == BUBBLE or (not self.c_rf_wen):
            return('# -')
        else:
            return('# R[%d] <- 0x%08x' % (self.rd, self.alu_out))
    #-----------------------------------------------------------------
