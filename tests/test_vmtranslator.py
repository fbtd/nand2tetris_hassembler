import pytest
from pathlib import Path
import hassembler.vmtranslator as t
from mockparser import MockParser

@pytest.mark.parametrize('instruction,expected', [
# push
    ({'operation': 'push', 'constant': '510'}, '@510, D=A, @SP, A=M, M=D, @SP, M=M+1'),
    ({'operation': 'push', 'segment': 'local', 'index': '3'},
        '@3, D=A, @LCL, A=M, A=A+D, D=M, @SP, A=M, M=D, @SP, M=M+1'),
    ({'operation': 'push', 'segment': 'pointer', 'index': '0'},
        '@THIS, D=M, @SP, A=M, M=D, @SP, M=M+1'),
    ({'operation': 'push', 'segment': 'pointer', 'index': '1'},
        '@THAT, D=M, @SP, A=M, M=D, @SP, M=M+1'),
    ({'operation': 'push', 'segment': 'temp', 'index': '3'},
        '@R8, D=M, @SP, A=M, M=D, @SP, M=M+1'),
    ({'operation': 'push', 'segment': 'static', 'index': '3'},
        '@prog.3, D=M, @SP, A=M, M=D, @SP, M=M+1'),
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
        '@SP, M=M-1, A=M, D=M, @prog.3, M=D'),
# arithmetic
    ({'operation': 'add'},
        '@SP, M=M-1, A=M, D=M, @SP, M=M-1, A=M, A=M, D=A+D, @SP, A=M, M=D, @SP, M=M+1'),
    ({'operation': 'sub'},
        '@SP, M=M-1, A=M, D=M, @SP, M=M-1, A=M, A=M, D=A-D, @SP, A=M, M=D, @SP, M=M+1'),
    ({'operation': 'neg'},
        '@SP, M=M-1, A=M, M=-M, @SP, M=M+1'),
# comparison  commands
    ({'operation': 'eq', 'instruction_line': 6},
        '@SP, M=M-1, A=M, D=M, @SP, M=M-1, A=M, A=M, '
        'D=A-D, @SKIP1.6, D;JNE, D=-1, @SKIP2.6, 0;JMP, (SKIP1.6), D=0, (SKIP2.6), '
        '@SP, A=M, M=D, @SP, M=M+1'),
    ({'operation': 'gt', 'instruction_line': 7},
        '@SP, M=M-1, A=M, D=M, @SP, M=M-1, A=M, A=M, '
        'D=A-D, @SKIP1.7, D;JLT, D=-1, @SKIP2.7, 0;JMP, (SKIP1.7), D=0, (SKIP2.7), '
        '@SP, A=M, M=D, @SP, M=M+1'),
    ({'operation': 'lt', 'instruction_line': 8},
        '@SP, M=M-1, A=M, D=M, @SP, M=M-1, A=M, A=M, '
        'D=A-D, @SKIP1.8, D;JGT, D=-1, @SKIP2.8, 0;JMP, (SKIP1.8), D=0, (SKIP2.8), '
        '@SP, A=M, M=D, @SP, M=M+1'),
    ])
def test_encode(instruction, expected):
    expected_list = expected.split(', ')
    translated_list = [l for l in t.encode(instruction, 'prog') if (not l.startswith('//') and l)]
    assert translated_list == expected_list
