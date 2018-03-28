TABLE = {
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
    'BNZ':      0xA,

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

def encode(s):
    s = s.upper().replace(',', '').split(' ')
    nibbles = [TABLE[c] for c in s]

    shift = 3
    word = 0
    for nibble in nibbles:
        word |= (nibble << (shift << 2))
        shift -= 1

    return word
