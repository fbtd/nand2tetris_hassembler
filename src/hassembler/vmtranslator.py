from hassembler.parser import VmParser
import pathlib
import sys

_segment_to_registers = dict(local='LCL', argument='ARG', this='THIS', that='THAT')
_pointer_index_to_register = {'0': 'THIS', '1': 'THAT'}
_push_d = '@SP, A=M, M=D, @SP, M=M+1'.split(', ')
_push_0_to_stack = '@SP, A=M, M=0, @SP, M=M+1'.split(', ')
_pop_to_d = '@SP, M=M-1, A=M, D=M'.split(', ')
_pop_to_a = '@SP, M=M-1, A=M, A=M'.split(', ')
_jump_conditions = dict(eq='NE', gt='LE', lt='GE')

_push_segment_to_stack_pattern = '@{segment}, D=M, @SP, A=M, M=D, @SP, M=M+1, '

class VmTranslator:
    current_function = ''
    i = 0
    def __init__(self, static_prefix=None):
        self.static_prefix = static_prefix

    @staticmethod
    def encode_target_address_to_R13(segment, index):
        register = None
        if segment in _segment_to_registers:
            register = _segment_to_registers[segment]
            return f'@{index}, D=A, @{register}, A=M, A=A+D, D=A, @R13, M=D'.split(', ')
        return []

    @staticmethod
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

    @staticmethod
    def encode_constant_to_d(constant):
        return [f'@{constant}', 'D=A']

#   def label_with_prefix(self, label):
#       return f'{self.static_prefix}.{self.current_function}${label}'

    def encode(self, vm_instruction):
        asm_instruction = [f'// {vm_instruction}']
        operator = vm_instruction['operation']
        segment = vm_instruction.get('segment')
        index = vm_instruction.get('index')
        line = vm_instruction.get('instruction_line')
        label = vm_instruction.get('label')
        name = vm_instruction.get('name')
        destination = vm_instruction.get('destination')
        nargs = int(vm_instruction.get('nargs') or 0)
        nvars = int(vm_instruction.get('nvars') or 0)
    ##################################### PUSH ##################################
        if operator == 'push':
            if 'constant' in vm_instruction:
                asm_instruction.extend(self.encode_constant_to_d(vm_instruction['constant']))
            elif segment is not None:
                asm_instruction.extend(self.encode_segment_to_d(segment, index, self.static_prefix))
            asm_instruction.extend(_push_d)

    ##################################### POP ###################################
        elif operator == 'pop':
            if segment in _segment_to_registers:
                asm_instruction.extend(self.encode_target_address_to_R13(segment, index))
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
                    if self.static_prefix is None:
                        raise RuntimeError('missing static prefix')
                    register = f'{self.static_prefix}.{index}'
                asm_instruction.extend([f'@{register}', 'M=D'])

    ################################### ARITHMETIC ##############################
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

    ################################### BRANCHING ##############################
        elif operator == 'label':
            asm_instruction.append(f'({self.current_function}${label})')
        elif operator == 'goto':
            asm_instruction.extend(f'@{self.current_function}${destination}, 0;JMP'.split(', '))
        elif operator == 'if-goto':
            asm_instruction.extend(_pop_to_d)
            asm_instruction.extend(f'@{self.current_function}${destination}, D;JNE'.split(', '))

    ################################### FUNCTION ###############################
        elif operator == 'function':
            self.current_function = name
            self.i = 1
            asm_instruction.append(f'({name})')
            for _ in range(int(nvars)):
                asm_instruction.extend(_push_0_to_stack)

        elif operator == 'call':
            asm_instruction.extend(                 # push return address
        f'@{self.current_function}$ret.{self.i}, D=A, @SP, A=M, M=D, @SP, M=M+1'.split(', '))

            for s in ['LCL', 'ARG', 'THIS', 'THAT']:
                asm_instruction.extend(_push_segment_to_stack_pattern.format(segment=s).split(', '))
            asm_instruction.extend((                    # ARG = SP - 5 - nargs
               f'@SP, D=M, @{5+nargs}, D=D-A, @ARG, M=D, '
                '@SP, D=M, @LCL, M=D, '                 # LS = SP
               f'@{name}, 0;JMP, '                      # goto callee
               f'({self.current_function}$ret.{self.i})').split(', '))   # inject return address
            self.i += 1

        elif operator == 'return':
            asm_instruction.extend((
                '@LCL, D=M, @R13, M=D, '                 # R13 := LCL
                '@5, A=D-A, D=M, @R12, M=D, '            # R12 := (*LCL) - 5
                '@SP, M=M-1, A=M, D=M, @ARG, A=M, M=D, ' # pop to ARG
                '@ARG, D=M+1, @SP, M=D, '                # SP = ARG + 1
                '@R13, M=M-1, A=M, D=M, @THAT, M=D, '    # THAT = *(--R13
                '@R13, M=M-1, A=M, D=M, @THIS, M=D, '    # THIS = *(--R13)
                '@R13, M=M-1, A=M, D=M, @ARG, M=D, '     # ARG = *(--R13)
                '@R13, M=M-1, A=M, D=M, @LCL, M=D, '     # LCL = *(--R13)
                '@R12, A=M, 0;JMP'                       # jump to R12
                ).split(', '))


        asm_instruction.append('/////////////')
        asm_instruction.append('')
        return asm_instruction

def get_bootstrap():
#   bootstrap_list = '@256, D=A, @SP, M=D, @Sys.init, 0;JMP'.split(', ')
    bootstrap_list = '@256, D=A, @SP, M=D'.split(', ')
    return '/// BOOTSTRAP\n' + '\n'.join(bootstrap_list) + '\n'

def main(destination_file=None, source_files=None, bootstrap=None):
    if destination_file is None:
        destination_file = sys.argv[1]
    if source_files is None:
        source_files = sys.argv[2:]

    vmt = VmTranslator()
    with open(destination_file, 'w') as fout:
        if bootstrap is True or ('Sys.vm' in source_files and bootstrap is not False):
            vmt.static_prefix = 'bootstrap'
            vmt.current_function = 'bootstrap'
            fout.write(get_bootstrap())
            for instruction in vmt.encode({'operation': 'call', 'name': 'Sys.init', 'nargs': '0'}):
                fout.write(instruction)
                fout.write('\n')
            fout.write('/////////////\n\n')

        for source_file in source_files:
            parser = VmParser(source_file)
            basename = pathlib.Path(source_file).with_suffix('')
            vmt.static_prefix = basename
            for instruction in parser:
                for encoded_instruction in vmt.encode(instruction):
                    fout.write(encoded_instruction)
                    fout.write('\n')

if __name__ == '__main__':
    main()
