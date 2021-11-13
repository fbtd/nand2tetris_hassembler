import pytest
from pathlib import Path
from hassembler.parser import AsmParser

test_prog = Path(__file__).parent / 'prog.asm'

def test_sample_prog_parse():
    p = AsmParser(test_prog)
    reference_instructions = (
        {'instruction_line': 0, 'instruction_type': 'A', 'value': '0'},
        {'instruction_line': 1, 'instruction_type': 'A', 'value': '1000'},
        {'instruction_line': 2, 'instruction_type': 'A', 'symbol': 'first_symbol'},
        {'instruction_line': 3, 'instruction_type': 'C', 'dest': 'D', 'comp': 'M'},
        {'instruction_line': 4, 'instruction_type': 'LABEL', 'label': 'SECOND_SYMBOL'},
        {'instruction_line': 4, 'instruction_type': 'C', 'comp': 'D', 'jump': 'JGT'},
        {'instruction_line': 5, 'instruction_type': 'LABEL', 'label': 'dotty.symbol'},
        {'instruction_line': 5, 'instruction_type': 'C', 'comp': '0', 'jump': 'JMP'},
        {'instruction_line': 6, 'instruction_type': 'LABEL', 'label': 'nummy.0'},
        {'instruction_line': 6, 'instruction_type': 'C', 'dest': 'AM', 'comp': 'M+1'},
        {'instruction_line': 7, 'instruction_type': 'C', 'dest': 'A', 'comp': 'A-1'},
        {'instruction_line': 8, 'instruction_type': 'C', 'dest': 'D', 'comp': 'D+1', 'jump': 'JLT'},
        {'instruction_line': 9, 'instruction_type': 'A', 'symbol': 'SECOND_SYMBOL'},
        {'instruction_line': 10, 'instruction_type': 'C', 'dest': 'M', 'comp': 'D'},
    )

    assert len(p) == len(reference_instructions)

    for instruction, reference_instruction in zip(p, reference_instructions):
        assert instruction == reference_instruction

test_bad_prog = Path(__file__).parent / 'bad_prog.asm'

def test_bad_instruction():
    p = AsmParser(test_bad_prog)
    _ = next(p)
    with pytest.raises(RuntimeError):
        _ = next(p)


def test_rewind():
    p = AsmParser(test_prog)
    _ = next(p)
    _ = next(p)
    _ = next(p)
    p.rewind()
    i = next(p)
    assert i['instruction_line'] == 0
    i = next(p)
    assert i['instruction_line'] == 1
