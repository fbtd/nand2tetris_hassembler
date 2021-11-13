from hassembler.parser import AsmParser
import pathlib
import sys

_binary_codes_comp = {
    '0': '0101010',
    '1': '0111111',
    '-1': '0111010',
    'D': '0001100',
    'A': '0110000', 'M': '1110000',
    '!D': '0001101',
    '!A': '0110001', '!M': '1110001',
    '-D': '0001111',
    '-A': '0110011', '-M': '1110011',
    'D+1': '0011111',
    'A+1': '0110111', 'M+1': '1110111',
    'D-1': '0001110',
    'A-1': '0110010', 'M-1': '1110010',
    'D+A': '0000010', 'D+M': '1000010',
    'A+D': '0000010', 'M+D': '1000010',
    'D-A': '0010011', 'D-M': '1010011', 
    'A-D': '0000111', 'M-D': '1000111',
    'D&A': '0000000', 'D&M': '1000000',
    'A&D': '0000000', 'M&D': '1000000',
    'D|A': '0010101', 'D|M': '1010101',
    'A|D': '0010101', 'M|D': '1010101'}

_binary_codes_dest = {
    'null': '000',
    'M': '001',
    'D': '010',
    'DM': '011', 'MD': '011',
    'A': '100',
    'AM': '101', 'MA': '101',
    'AD': '110', 'DA': '110',
    'ADM': '111', 'AMD': '111', 'DAM': '111',
    'DMA': '111', 'MAD': '111', 'MDA': '111'}

_binary_codes_jump = {
    'null': '000',
    'JGT': '001',
    'JEQ': '010',
    'JGE': '011',
    'JLT': '100',
    'JNE': '101',
    'JLE': '110',
    'JMP': '111'}

def encode(instruction):
    if instruction['instruction_type'] == 'A':
        bin_value = format(int(instruction['value']), '015b')
        return '0' + bin_value

    if instruction['instruction_type'] == 'C':
        comp = instruction.get('comp', 'null')
        dest = instruction.get('dest', 'null')
        jump = instruction.get('jump', 'null')
        return f'111{_binary_codes_comp[comp]}{_binary_codes_dest[dest]}{_binary_codes_jump[jump]}'

    raise ValueError(f'invalid instruction type: {instruction["instruction_type"]}')

default_symbol_table = {
    'R0': 0, 'R1': 1, 'R2': 2, 'R3': 3, 'R4': 4, 'R5': 5, 'R6': 6, 'R7': 7,
    'R8': 8, 'R9': 9, 'R10': 10, 'R11': 11, 'R12': 12, 'R13': 13, 'R14': 14,
    'R15': 15, 'SP': 0, 'LCL': 1, 'ARG': 2, 'THIS': 3, 'THAT': 4,
    'SCREEN': 16384, 'KBD': 24576}

def make_symbol_table(parser):
    symbol_table = default_symbol_table
    next_index = 16
    for instruction in parser:
        symbol = instruction.get('symbol', None)
        if symbol is not None and symbol not in symbol_table:
            symbol_table[symbol] = next_index
            next_index += 1
        label = instruction.get('label', None)
        if label is not None:
            symbol_table[label] = instruction['instruction_line']
            
    parser.rewind()
    return symbol_table


def main(source_file=None):
    if source_file is None:
        source_file = sys.argv[1]
    parser = AsmParser(source_file)
    symbol_table = make_symbol_table(parser)

    dest_file = pathlib.Path(source_file).with_suffix('.hack')
    with open(dest_file, 'w') as fout:
        for instruction in parser:
            if instruction['instruction_type'] == 'LABEL': continue
            if 'symbol' in instruction:
                instruction['value'] = symbol_table[instruction['symbol']]
            encoded_instruction = encode(instruction)
            fout.write(encoded_instruction)
            fout.write('\n')

if __name__ == '__main__':
    main()
