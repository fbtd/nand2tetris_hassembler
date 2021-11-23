from hassembler.parser import VmParser
import pathlib
import sys

_segment_to_registers = dict(local='LCL', argument='ARG', this='THIS', that='THAT')
_pointer_index_to_register = {'0': 'THIS', '1': 'THAT'}

def encode_target_address_to_R13(segment, index, static_prefix=None):
    register = None
    if segment in _segment_to_registers:
        register = _segment_to_registers[segment]
        return f'@{index}, D=A, @{register}, A=M, A=A+D, D=A, @R13, M=D'.split(', ')
    return []

def encode_segment_to_d(segment, index, static_prefix=None):
    register = None
    if segment in _segment_to_registers:
        register = _segment_to_registers[segment]
        return f'@{index}, D=A, @{register}, A=M, A=A+D, D=M'.split(', ')
    if segment == 'pointer':
        register = _pointer_index_to_register[index]
    if segment == 'temp':
        register = f'R{int(index) + 5}'
    if segment == 'static':
        if static_prefix is None:
            raise RuntimeError('missing static prefix')
        register = f'{static_prefix}.{index}'
    return [f'@{register}', 'D=M']

def encode_constant_to_d(constant):
    return [f'@{constant}', 'D=A']

_push_d = '@SP, A=M, M=D, @SP, M=M+1'.split(', ')
_pop_to_d = '@SP, M=M-1, A=M, D=M'.split(', ')
_pop_to_a = '@SP, M=M-1, A=M, A=M'.split(', ')
_jump_conditions = dict(eq='NE', gt='LE', lt='GE')

def encode(vm_instruction, static_prefix=None):
    asm_instruction = [f'// {vm_instruction}']
    operator = vm_instruction['operation']
    segment = vm_instruction.get('segment')
    index = vm_instruction.get('index')
    line = vm_instruction.get('instruction_line')
##################################### PUSH #####################################
    if operator == 'push':
        if 'constant' in vm_instruction:
            asm_instruction.extend(encode_constant_to_d(vm_instruction['constant']))
        elif segment is not None:
            asm_instruction.extend(encode_segment_to_d(segment, index, static_prefix))
        asm_instruction.extend(_push_d)

##################################### POP ######################################
    elif operator == 'pop':
        if segment in _segment_to_registers:
            asm_instruction.extend(encode_target_address_to_R13(segment, index, static_prefix))
            asm_instruction.extend(_pop_to_d)
            asm_instruction.extend(['@R13', 'A=M', 'M=D'])
        else:
            register = None
            asm_instruction.extend(_pop_to_d)
            if segment == 'pointer':
                register = _pointer_index_to_register[index]
            elif segment == 'temp':
                register = f'R{int(index) + 5}'
            elif segment == 'static':
                if static_prefix is None:
                    raise RuntimeError('missing static prefix')
                register = f'{static_prefix}.{index}'
            asm_instruction.extend([f'@{register}', 'M=D'])

################################### ARITHMETIC #################################
    elif operator == 'add':
        asm_instruction.extend(_pop_to_d)
        asm_instruction.extend(_pop_to_a)
        asm_instruction.append('D=A+D')
        asm_instruction.extend(_push_d)
    elif operator == 'sub':
        asm_instruction.extend(_pop_to_d)
        asm_instruction.extend(_pop_to_a)
        asm_instruction.append('D=A-D')
        asm_instruction.extend(_push_d)
    elif operator == 'and':
        asm_instruction.extend(_pop_to_d)
        asm_instruction.extend(_pop_to_a)
        asm_instruction.append('D=A&D')
        asm_instruction.extend(_push_d)
    elif operator == 'or':
        asm_instruction.extend(_pop_to_d)
        asm_instruction.extend(_pop_to_a)
        asm_instruction.append('D=A|D')
        asm_instruction.extend(_push_d)
    elif operator == 'neg':
        asm_instruction.extend('@SP, M=M-1, A=M, M=-M, @SP, M=M+1'.split(', '))
    elif operator == 'not':
        asm_instruction.extend('@SP, M=M-1, A=M, M=!M, @SP, M=M+1'.split(', '))
################################### COMPARISON #################################
    elif operator in _jump_conditions:
        asm_instruction.extend(_pop_to_d)
        asm_instruction.extend(_pop_to_a)
        asm_instruction.extend(
            f'D=A-D, @SKIP1.{line}, D;J{_jump_conditions[operator]}, D=-1, '
            f'@SKIP2.{line}, 0;JMP, (SKIP1.{line}), D=0, (SKIP2.{line})'.split(', '))
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
            for encoded_instruction in encode(instruction, basename):
                fout.write(encoded_instruction)
                fout.write('\n')

if __name__ == '__main__':
    main()
