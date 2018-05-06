from collections import deque, namedtuple
import sys

from PIL import Image, ImageFont, ImageDraw

ROW_SIZE = 50
SPACE_SIZE = 10
COL_SIZE = 50

# Number of stalls inserted between an instruction and an
# immediately depedent instruction
RAW_LATENCY = 2

# Number of stalls inserted after a branch
B_LATENCY = 2

NIBBLE_TABLE = {
    # Opcodes
    'NOP':      0x0,
    'LW':       0x1,
    'SW':       0x2,
    'ADD':      0x3,
    'AND':      0x4,
    'OR':       0x5,
    'XOR':      0x6,
    'SR':       0x7,
    'MOV':      0x8,
    'MOVI':     0x9,
    'BNZ':     0xA,

    # Registers
    'R0':       0x0,
    'R1':       0x1,
    'R2':       0x2,
    'R3':       0x3,
    'R4':       0x4,
    'R5':       0x5,
    'R6':       0x6,
    'R7':       0x7,
    'R8':       0x8,
    'R9':       0x9,
    'R10':      0xA,
    'R11':      0xB,
    'R12':      0xC,
    'R13':      0xD,
    'R14':      0xE,
    'R15':      0xF,

    # Immediates
    '0':       0x0,
    '1':       0x1,
    '2':       0x2,
    '3':       0x3,
    '4':       0x4,
    '5':       0x5,
    '6':       0x6,
    '7':       0x7,
    '8':       0x8,
    '9':       0x9,
    '10':      0xA,
    '11':      0xB,
    '12':      0xC,
    '13':      0xD,
    '14':      0xE,
    '15':      0xF
}


COLOR_TABLE = {
        0x0: '#E9ECEC',
        0x1: '#F07613',
        0x2: '#BD44B3',
        0x3: '#3AAFD9',
        0x4: '#F8C627',
        0x5: '#70B919',
        0x6: '#ED8DAC',
        0x7: '#3E4447',
        0x8: '#8E8E86',
        0x9: '#158991',
        0xA: '#792AAC',
        0xB: '#35399D',
        0xC: '#724728',
        0xD: '#546D1B',
        0xE: '#A12722',
        0xF: '#141519'
}


Instruction = namedtuple('Instruction',
        ['instruction', 'reg_dest', 'reg_src_a', 'reg_src_b', 'immediate',
         'type', 'human_readable', 'stall'])
Instruction.__new__.__defaults__ = (None,) * len(Instruction._fields)

def Stall():
    return Instruction('NOP', type=0, human_readable='NOP', stall=True)


def parse_file(p):
    lines = []
    with open(p) as f:
        for line in f:
            lines.append(line.rstrip())
    return lines


def init_instr(instr):
    # Type 0
    if instr[0] == 'NOP':
        return Instruction(instruction=instr[0], type=0,
                           human_readable=' '.join(instr))

    # Type 1
    elif instr[0] == 'LW':
        return Instruction(instruction=instr[0],
                           reg_dest=instr[1],
                           reg_src_a=instr[2],
                           immediate=instr[3],
                           type=1, human_readable=' '.join(instr))

    # Type 2
    elif instr[0] in ['ADD', 'AND', 'OR', 'XOR', 'SR']:
        return Instruction(instruction=instr[0],
                           reg_dest=instr[1],
                           reg_src_a=instr[2],
                           reg_src_b=instr[3],
                           type=2, human_readable=' '.join(instr))

    # Type 3
    elif instr[0] == 'MOV':
        return Instruction(instruction=instr[0],
                           reg_dest=instr[1],
                           reg_src_a=instr[2],
                           type=3, human_readable=' '.join(instr))

    # Type 4
    elif instr[0] == 'MOVI':
        return Instruction(instruction=instr[0],
                           reg_dest=instr[1],
                           immediate=instr[2],
                           type=4, human_readable=' '.join(instr))

    # Type 5
    elif instr[0] == 'SW':
        return Instruction(instruction=instr[0],
                           reg_src_a=instr[1],
                           reg_src_b=instr[2],
                           immediate=instr[3],
                           type=5, human_readable=' '.join(instr))

    # Type 6
    elif instr[0] == 'BNZ':
        return Instruction(instruction=instr[0],
                           reg_src_a=instr[1],
                           reg_src_b=instr[2],
                           type=6, human_readable=' '.join(instr))

    raise Exception('Unknown instruction %s' % instr[0])


def create_instructions(lines):
    instructions = []
    for line in lines:
        instr = line.upper().replace(',', '').split(' ')
        instructions.append(init_instr(instr))
    return instructions


def insert_stalls_hazards(instructions):
    """
    Check for RAW hazards by scanning instructions
    in reverse order, and if any reads are preceeded
    by any writes of the same register in the last 3 instructions,
    insert stalls to prevent RAW hazard.
    """
    i = len(instructions) - 1
    while i > -1:
        instr = instructions[i]

        if instr.instruction == 'NOP':
            i -= 1
            continue

        reg_reads = [instructions[i].reg_src_a, instructions[i].reg_src_b]

        # check last LATENCY instructions
        for j in range(1, RAW_LATENCY+1):
            if i-j < 0:
                break

            reg_write = instructions[i-j].reg_dest

            if reg_write in reg_reads and reg_write != None:
                print('found RAW hazard from %d to %d, register %s' % (
                    i+1, i-j+1, reg_write))
                num_stalls = RAW_LATENCY+1-j
                print('inserting %d stalls' % num_stalls)
                stalls = [Stall() for _ in range(num_stalls)]
                instructions[i-j+1:i-j+1] = stalls
                break

        i -= 1

    return instructions


def insert_stalls_branchs(instructions):
    i = 0
    while i < len(instructions):
        instr = instructions[i]
        if instr.instruction == 'BNZ':
            stalls = [Stall() for _ in range(B_LATENCY)]
            instructions[i+1:i+1] = stalls
        i += 1

    return instructions


def encode(instr):
    word = 0
    word |= (NIBBLE_TABLE[instr.instruction] << (3 << 2))

    # Type 0
    if instr.type == 0:
        pass

    # Type 1
    elif instr.type == 1:
        word |= (NIBBLE_TABLE[instr.reg_dest]  << (2 << 2))
        word |= (NIBBLE_TABLE[instr.reg_src_a] << (1 << 2))
        word |= (NIBBLE_TABLE[instr.immediate] << (0 << 2))

    # Type 2
    elif instr.type == 2:
        word |= (NIBBLE_TABLE[instr.reg_dest]  << (2 << 2))
        word |= (NIBBLE_TABLE[instr.reg_src_a] << (1 << 2))
        word |= (NIBBLE_TABLE[instr.reg_src_b] << (0 << 2))

    # Type 3
    elif instr.type == 3:
        word |= (NIBBLE_TABLE[instr.reg_dest]  << (2 << 2))
        word |= (NIBBLE_TABLE[instr.reg_src_a] << (1 << 2))

    # Type 4
    elif instr.type == 4:
        word |= (NIBBLE_TABLE[instr.reg_dest]  << (2 << 2))
        word |= (NIBBLE_TABLE[instr.immediate] << (0 << 2))

    # Type 5
    elif instr.type == 5:
        word |= (NIBBLE_TABLE[instr.immediate] << (2 << 2))
        word |= (NIBBLE_TABLE[instr.reg_src_a] << (1 << 2))
        word |= (NIBBLE_TABLE[instr.reg_src_b] << (0 << 2))

    # Type 6
    elif instr.type == 6:
        word |= (NIBBLE_TABLE[instr.reg_src_a] << (1 << 2))
        word |= (NIBBLE_TABLE[instr.reg_src_b] << (0 << 2))

    else:
        raise Exception('Unknown instruction %s, type %d' % (
            instr.instruction, instr.type))

    return word


def write(path, encodings):
    with open(p, 'w') as f:
        for encoding in encodings:
            f.write('0x%04x\n' % encoding)


def draw(path, encodings, instructions, row_size=ROW_SIZE,
         col_size=COL_SIZE, space_size=SPACE_SIZE):
    num_i = len(instructions)

    img = Image.new('RGB', (500, row_size*(num_i+2)), 'white')

    draw = ImageDraw.Draw(img)

    for i, word in enumerate(encodings, 1):
        a = (word & 0xF000) >> 12
        b = (word & 0x0F00) >> 8
        c = (word & 0x00F0) >> 4
        d = (word & 0x000F)

        draw.rectangle(
                ((col_size,   row_size*i), (col_size+col_size, row_size*i+row_size)),
                fill=COLOR_TABLE[a])
        draw.rectangle(
                ((col_size*2, row_size*i), (col_size*2+col_size, row_size*i+row_size)),
                fill=COLOR_TABLE[b])

        draw.rectangle(
                ((col_size*3, row_size*i), (col_size*3+col_size, row_size*i+row_size)),
                fill=COLOR_TABLE[c])

        draw.rectangle(
                ((col_size*4, row_size*i), (col_size*4+col_size, row_size*i+row_size)),
                fill=COLOR_TABLE[d])

        draw.text((25, row_size*i+20), str(i), fill='black')

        draw.text((col_size*6, row_size*i+20), instructions[i-1].human_readable,
                  fill='black')

    img.save(path, 'JPEG', quality=95)


if __name__ == '__main__':
#    if len(sys.argv) < 4:
#        print('Usage: encode.py instructions-path output-path visual-path')
#        exit(1)

    lines = parse_file(sys.argv[1])
    instructions = create_instructions(lines)
    instructions = insert_stalls_hazards(instructions)
    instructions = insert_stalls_branchs(instructions)
    encodings = [encode(i) for i in instructions]
    draw(sys.argv[2], encodings, instructions)

#    write(sys.argv[2], wool)
#    draw(sys.argv[3], wool, instructions, ROW_SIZE, COL_SIZE, SPACE_SIZE)
