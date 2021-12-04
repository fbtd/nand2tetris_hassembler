import pytest
from pathlib import Path
import hassembler.vmtranslator as t
from mockparser import MockParser

def keep_only_commands(commands):
    return [l for l in commands if (not l.startswith('//') and l)]

@pytest.mark.parametrize('instruction,expected', [
# push
    ({'operation': 'push', 'constant': '510'},  '@510, D=A, @SP, A=M, M=D, @SP, M=M+1'),
    ({'operation': 'push', 'segment': 'local', 'index': '3'},
        '@3, D=A, @LCL, A=M, A=A+D, D=M, @SP, A=M, M=D, @SP, M=M+1'),
    ({'operation': 'push', 'segment': 'pointer', 'index': '0'},
        '@THIS, D=M, @SP, A=M, M=D, @SP, M=M+1'),
    ({'operation': 'push', 'segment': 'pointer', 'index': '1'},
        '@THAT, D=M, @SP, A=M, M=D, @SP, M=M+1'),
    ({'operation': 'push', 'segment': 'temp', 'index': '3'},
        '@R8, D=M, @SP, A=M, M=D, @SP, M=M+1'),
    ({'operation': 'push', 'segment': 'static', 'index': '3'},
        '@Prog.3, D=M, @SP, A=M, M=D, @SP, M=M+1'),
# pop
    ({'operation': 'pop', 'segment': 'local', 'index': '3'},
        '@3, D=A, @LCL, A=M, A=A+D, D=A, @R13, M=D, @SP, M=M-1, A=M, D=M, @R13, A=M, M=D'),
    ({'operation': 'pop', 'segment': 'pointer', 'index': '0'},
        '@SP, M=M-1, A=M, D=M, @THIS, M=D'),
    ({'operation': 'pop', 'segment': 'pointer', 'index': '1'},
        '@SP, M=M-1, A=M, D=M, @THAT, M=D'),
    ({'operation': 'pop', 'segment': 'temp', 'index': '3'},
        '@SP, M=M-1, A=M, D=M, @R8, M=D'),
    ({'operation': 'pop', 'segment': 'static', 'index': '3'},
        '@SP, M=M-1, A=M, D=M, @Prog.3, M=D'),
# arithmetic
    ({'operation': 'add'},
        '@SP, M=M-1, A=M, D=M, @SP, M=M-1, A=M, A=M, D=A+D, @SP, A=M, M=D, @SP, M=M+1'),
    ({'operation': 'sub'},
        '@SP, M=M-1, A=M, D=M, @SP, M=M-1, A=M, A=M, D=A-D, @SP, A=M, M=D, @SP, M=M+1'),
    ({'operation': 'neg'}, '@SP, M=M-1, A=M, M=-M, @SP, M=M+1'),
# logical
    ({'operation': 'and'},
        '@SP, M=M-1, A=M, D=M, @SP, M=M-1, A=M, A=M, D=A&D, @SP, A=M, M=D, @SP, M=M+1'),
    ({'operation': 'or'},
        '@SP, M=M-1, A=M, D=M, @SP, M=M-1, A=M, A=M, D=A|D, @SP, A=M, M=D, @SP, M=M+1'),
    ({'operation': 'not'}, '@SP, M=M-1, A=M, M=!M, @SP, M=M+1'),
# comparison  commands
    ({'operation': 'eq', 'instruction_line': 6},
        '@SP, M=M-1, A=M, D=M, @SP, M=M-1, A=M, A=M, '
        'D=A-D, @SKIP1.6, D;JNE, D=-1, @SKIP2.6, 0;JMP, (SKIP1.6), D=0, (SKIP2.6), '
        '@SP, A=M, M=D, @SP, M=M+1'),
    ({'operation': 'gt', 'instruction_line': 7},
        '@SP, M=M-1, A=M, D=M, @SP, M=M-1, A=M, A=M, '
        'D=A-D, @SKIP1.7, D;JLE, D=-1, @SKIP2.7, 0;JMP, (SKIP1.7), D=0, (SKIP2.7), '
        '@SP, A=M, M=D, @SP, M=M+1'),
    ({'operation': 'lt', 'instruction_line': 8},
        '@SP, M=M-1, A=M, D=M, @SP, M=M-1, A=M, A=M, '
        'D=A-D, @SKIP1.8, D;JGE, D=-1, @SKIP2.8, 0;JMP, (SKIP1.8), D=0, (SKIP2.8), '
        '@SP, A=M, M=D, @SP, M=M+1'),
# comparison  commands
    ({'operation': 'label', 'label': 'LABEL1'}, '(Prog.fun$LABEL1)'),
    ({'operation': 'goto', 'destination': 'LABEL1'}, '@Prog.fun$LABEL1, 0;JMP'),
    ({'operation': 'if-goto', 'destination': 'LABEL1'},
        '@SP, M=M-1, A=M, D=M, @Prog.fun$LABEL1, D;JNE'),
# return
    ({'operation': 'return'},
        '@LCL, D=M, @R13, M=D, '                 # R13 := LCL
        '@5, A=D-A, D=M, @R12, M=D, '            # R12 := (*LCL) - 5
        '@SP, M=M-1, A=M, D=M, @ARG, A=M, M=D, ' # pop to *ARG
        '@ARG, D=M+1, @SP, M=D, '                # SP = ARG + 1
        '@R13, M=M-1, A=M, D=M, @THAT, M=D, '    # THAT = *(--R13
        '@R13, M=M-1, A=M, D=M, @THIS, M=D, '    # THIS = *(--R13)
        '@R13, M=M-1, A=M, D=M, @ARG, M=D, '     # ARG = *(--R13)
        '@R13, M=M-1, A=M, D=M, @LCL, M=D, '     # LCL = *(--R13)
        '@R12, A=M, 0;JMP'                       # jump to R12
        ),
    ])
def test_encode(instruction, expected):
    vmt = t.VmTranslator(static_prefix='Prog')
    vmt.current_function = 'Prog.fun'
#   vmt.encode({'operation': 'function', 'name': 'f1', 'nargs': '1'})
    expected_list = expected.split(', ')
    assert keep_only_commands(vmt.encode(instruction)) == expected_list

def test_encode_function():
    vmt = t.VmTranslator(static_prefix='Prog')
    instruction_f0 = {'operation': 'function', 'name': 'Prog.f0', 'nvars': '0'}
    assert keep_only_commands(vmt.encode(instruction_f0)) == ['(Prog.f0)']
    assert vmt.current_function == 'Prog.f0'

    instruction_f1 = {'operation': 'function', 'name': 'Prog.f1', 'nvars': '1'}
    assert keep_only_commands(vmt.encode(instruction_f1)) == '(Prog.f1), @SP, A=M, M=0, @SP, M=M+1'.split(', ')
    assert vmt.current_function == 'Prog.f1'

def test_encode_call():
    vmt = t.VmTranslator(static_prefix='Prog')
    vmt.current_function = 'Prog.caller'
    vmt.i = 1
    expected_pattern = (
        '@Prog.caller$ret.{i}, D=A, @SP, A=M, M=D, @SP, M=M+1, ' # push return address
        '@LCL, D=M, @SP, A=M, M=D, @SP, M=M+1, '                 # push LCL, ARG, THIS and THAT
        '@ARG, D=M, @SP, A=M, M=D, @SP, M=M+1, ' 
        '@THIS, D=M, @SP, A=M, M=D, @SP, M=M+1, ' 
        '@THAT, D=M, @SP, A=M, M=D, @SP, M=M+1, ' 
        '@SP, D=M, @{five_plus_nargs}, D=D-A, @ARG, M=D, '       # ARG = SP - 5 - nargs
        '@SP, D=M, @LCL, M=D, '                                  # LS = SP
        '@Prog.callee, 0;JMP, '                                  # goto callee
        '(Prog.caller$ret.{i})')                                 # inject return address

    instruction_call_f0 = {'operation': 'call', 'name': 'Prog.callee', 'nargs': '0'}
    expected = expected_pattern.format(i=1, five_plus_nargs=5).split(', ')
    assert keep_only_commands(vmt.encode(instruction_call_f0)) == expected

    instruction_call_f2 = {'operation': 'call', 'name': 'Prog.callee', 'nargs': '2'}
    expected = expected_pattern.format(i=2, five_plus_nargs=7).split(', ')
    assert keep_only_commands(vmt.encode(instruction_call_f2)) == expected
