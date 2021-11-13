import pytest
from pathlib import Path
import hassembler.hassembler
from mockparser import MockParser

@pytest.mark.parametrize('instruction,expected', [
        ({'instruction_type': 'A', 'value': '0'},    '0000000000000000'),
        ({'instruction_type': 'A', 'value': '1001'}, '0000001111101001'),
        ({'instruction_type': 'C', 'dest': 'M', 'comp': '1'}, '1110111111001000'),
        ({'instruction_type': 'C', 'dest': 'M', 'comp': 'M+1'}, '1111110111001000'),
        ({'instruction_type': 'C', 'comp': 'D', 'jump': 'JGT'}, '1110001100000001'),
        ({'instruction_type': 'C', 'comp': '0', 'jump': 'JMP'}, '1110101010000111'),
        ({'instruction_type': 'C', 'dest': 'M', 'comp': 'D'}, '1110001100001000'),
        ({'instruction_type': 'C', 'dest': 'D', 'comp': 'D+1', 'jump': 'JLT'}, '1110011111010100')
    ])
def test_encode(instruction, expected):
    assert hassembler.hassembler.encode(instruction) == expected

def test_make_symbol_table():
    reference_instructions = [
        {'instruction_line': 0, 'instruction_type': 'A', 'value': '0'},
        {'instruction_line': 1, 'instruction_type': 'A', 'symbol': 'first_symbol'},
        {'instruction_line': 2, 'instruction_type': 'LABEL', 'label': 'SECOND_SYMBOL'},
        {'instruction_line': 2, 'instruction_type': 'A', 'value': '0'},
        {'instruction_line': 3, 'instruction_type': 'A', 'symbol': 'SECOND_SYMBOL'},
    ]
    mparser = MockParser(reference_instructions)

    symbol_table = hassembler.hassembler.make_symbol_table(mparser)
    assert symbol_table['R0'] == 0
    assert symbol_table['R1'] == 1
    assert symbol_table['R15'] == 15
    assert symbol_table['SCREEN'] == 16384
    assert symbol_table['first_symbol'] == 16
    assert symbol_table['SECOND_SYMBOL'] == 2


def test_main():
    assert True
