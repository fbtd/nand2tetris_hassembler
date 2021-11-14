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
        '@THIS, D=A, @SP, A=M, M=D, @SP, M=M+1'),
    ({'operation': 'push', 'segment': 'pointer', 'index': '1'},
        '@THAT, D=A, @SP, A=M, M=D, @SP, M=M+1'),
    ({'operation': 'push', 'segment': 'temp', 'index': '3'},
        '@R8, D=A, @SP, A=M, M=D, @SP, M=M+1'),
    ({'operation': 'push', 'segment': 'static', 'index': '3'},
        '@prog.3, D=A, @SP, A=M, M=D, @SP, M=M+1'),
# pop
    ({'operation': 'pop', 'segment': 'local', 'index': '3'},
        '@3, D=A, @LCL, A=M, A=A+D, D=A, @R13, M=D, @SP, A=M, D=M, @SP M=M-1, @R13, M=D'),
         ########## &target to R13 ###############  ###### --stack to D ####  ## set ##
    ({'operation': 'pop', 'segment': 'pointer', 'index': '0'},
        '@SP, A=M, D=M, @SP M=M-1, @THIS, M=D'),
         ##### --stack to D ##### 
    ({'operation': 'pop', 'segment': 'pointer', 'index': '1'},
        '@SP, A=M, D=M, @SP M=M-1, @THAT, M=D'),
    ({'operation': 'pop', 'segment': 'temp', 'index': '3'},
        '@SP, A=M, D=M, @SP M=M-1, @R8, M=D'),
    ({'operation': 'pop', 'segment': 'static', 'index': '3'},
        '@SP, A=M, D=M, @SP M=M-1, @prog.3, M=D'),
    ])
def test_encode(instruction, expected):
    expected_list = expected.split(', ')
    translated_list = [l for l in t.encode(instruction, 'prog') if (not l.startswith('//') and l)]
    assert translated_list == expected_list
