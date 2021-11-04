import pytest
from pathlib import Path
from hassembler.parser import Parser

test_prog = Path(__file__).parent / 'prog.asm'

def test_sample_prog_parse():
    p = Parser(test_prog)
    reference_instructions = (
        {'instruction_line': 0, 'instruction_type': 'A', 'value': '0'},
        {'instruction_line': 1, 'instruction_type': 'A', 'value': '1000'},
        {'instruction_line': 2, 'instruction_type': 'A', 'symbol': 'first_symbol'},
        {'instruction_line': 3, 'instruction_type': 'C', 'dest': 'D', 'comp': 'M'},
        {'instruction_line': 4, 'instruction_type': 'LABEL', 'label': 'SECOND_SYMBOL'},
        {'instruction_line': 4, 'instruction_type': 'C', 'comp': 'D', 'jump': 'JGT'},
        {'instruction_line': 5, 'instruction_type': 'C', 'comp': '0', 'jump': 'JMP'},
        {'instruction_line': 6, 'instruction_type': 'C', 'dest': 'AM', 'comp': 'M+1'},
        {'instruction_line': 7, 'instruction_type': 'C', 'dest': 'A', 'comp': 'A-1'},
        {'instruction_line': 8, 'instruction_type': 'C', 'dest': 'D', 'comp': 'D+1', 'jump': 'JLT'},
        {'instruction_line': 9, 'instruction_type': 'A', 'symbol': 'SECOND_SYMBOL'},
    )

    for instruction, reference_instruction in zip(p, reference_instructions):
        assert instruction == reference_instruction

def test_rewind():
    p = Parser(test_prog)
    _ = next(p)
    _ = next(p)
    _ = next(p)
    p.rewind()
    i = next(p)
    assert i['instruction_line'] == 0
    i = next(p)
    assert i['instruction_line'] == 1
