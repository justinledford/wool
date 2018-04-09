import sys

from PIL import Image, ImageFont, ImageDraw

ROW_SIZE = 50
SPACE_SIZE = 10
COL_SIZE = 50


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
    'BNEQ':     0xA,

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

def encode(s):
    s = s.upper().replace(',', '').split(' ')
    nibbles = [NIBBLE_TABLE[t] for t in s]

    shift = 3
    word = 0
    for nibble in nibbles:
        word |= (nibble << (shift << 2))
        shift -= 1

    return word


def parse_file(p):
    wool = []
    instructions = []
    with open(p) as f:
        for line in f:
            wool.append(encode(line.rstrip()))
            instructions.append(line.rstrip())
    return wool, instructions


def write(p, wool):
    with open(p, 'w') as f:
        for word in wool:
            f.write('0x%04x\n' % word)

def draw(p, wool, instructions, row_size, col_size, space_size):
    num_i=len(wool)

    img = Image.new('RGB', (500, ROW_SIZE*(num_i+2)), 'white')

    draw = ImageDraw.Draw(img)

    for i, word in enumerate(wool, 1):
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

        draw.text((col_size*6, row_size*i+20), instructions[i-1], fill='black')
    img.save(p, 'JPEG', quality=95)

if __name__ == '__main__':
    if len(sys.argv) < 4:
        print('Usage: encode.py instructions-path output-path visual-path')
        exit(1)

    wool, instructions = parse_file(sys.argv[1])
    write(sys.argv[2], wool)
    draw(sys.argv[3], wool, instructions, ROW_SIZE, COL_SIZE, SPACE_SIZE)
