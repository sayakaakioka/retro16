from retro16sim.assembler import asm_addi, asm_cmpi, asm_jmp, asm_jz, asm_jnz, asm_halt


def prog_infinite_loop_r1_add():
    return [
        asm_addi(rd=1, rs=1, imm=1),  # 0000    ADDI R1, R1, #1
        asm_jmp(off_words=-2),  # 0002  JMP -2
    ]


def prog_add_two_then_halt():
    return [
        asm_addi(rd=1, rs=1, imm=1),  # 0000 ADDI R1, R1, #1
        asm_addi(rd=1, rs=1, imm=1),  # 0002  ADDI R1, R1, #1
    ]


def prog_countdown():
    return [
        asm_addi(rd=1, rs=1, imm=3),  # 0000  ADDI R1, R1, #3
        asm_cmpi(rd=1, rs=1, imm=0),  # 0002  CMPI R1, #0
        asm_jz(off_words=3),  # 0004  JZ end
        asm_addi(rd=1, rs=1, imm=-1),  # 0006  ADDI R1, R1, #-1
        asm_jnz(off_words=-4),  # 0008  JNZ -4
        asm_halt(),  # 000A  HALT
    ]
