from hassembler.parser import VmParser
import pathlib
import sys

_segment_to_registers = dict(local='LCL', argument='ARG', this='THIS', that='THAT')

def encode_segment_to_d(segment, index, static_prefix=None):
    register = None
    if segment in _segment_to_registers:
        register = _segment_to_registers[segment]
        return f'@{index}, D=A, @{register}, A=M, A=A+D, D=M'.split(', ')
    if segment == 'pointer':
        if index == '0': register='THIS'
        elif index == '1': register='THAT'
        else: raise ValueError(f'index {index} invalid for "pointer" segment')
    if segment == 'temp':
        register = f'R{int(index) + 5}'
    if segment == 'static':
        if static_prefix is None:
            raise RuntimeError('missing static prefix')
        register = f'{static_prefix}.{index}'
    return [f'@{register}', 'D=A']

def encode_constant_to_d(constant):
    return [f'@{constant}', 'D=A']

_push_d = '@SP, A=M, M=D, @SP, M=M+1'.split(', ')

def encode(vm_instruction, static_prefix=None):
    asm_instruction = [f'// {vm_instruction}']
    if vm_instruction['operation'] == 'push':
        if 'constant' in vm_instruction:
            asm_instruction.extend(encode_constant_to_d(vm_instruction['constant']))
        elif 'segment' in vm_instruction:
            asm_instruction.extend(encode_segment_to_d(vm_instruction['segment'],
                vm_instruction['index'], static_prefix))
        asm_instruction.extend(_push_d)
    asm_instruction.append('/////////////')
    asm_instruction.append('')
    return asm_instruction


def main(source_file=None):
    if source_file is None:
        source_file = sys.argv[1]
    parser = VmParser(source_file)

    dest_file = pathlib.Path(source_file).with_suffix('.asm')
    basename = pathlib.Path(source_file).with_suffix('')
    with open(dest_file, 'w') as fout:
        for instruction in parser:
            encoded_instruction = encode(instruction, basename)
            fout.write(encoded_instruction)
            fout.write('\n')

if __name__ == '__main__':
    main()
