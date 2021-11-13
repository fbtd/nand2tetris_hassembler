import pytest
from pathlib import Path
from hassembler.parser import VmParser

test_prog = Path(__file__).parent / 'Prog.vm'

def test_sample_prog_parse():
    p = VmParser(test_prog)
    reference_instructions = (
        {'instruction_line': 2, 'operation': 'push', 'constant': '510', 'instruction_type': 'VM'},
        {'instruction_line': 3, 'operation': 'pop', 'segment': 'temp', 'index': '6', 'instruction_type': 'VM'},
        {'instruction_line': 5, 'operation': 'push', 'segment': 'that', 'index': '5', 'instruction_type': 'VM'},
        {'instruction_line': 6, 'operation': 'add', 'instruction_type': 'VM'},
    )

    assert len(p) >= len(reference_instructions)

    for instruction, reference_instruction in zip(p, reference_instructions):
        assert instruction == reference_instruction

test_bad_prog = Path(__file__).parent / 'BadProg.vm'

def test_bad_instruction():
    p = VmParser(test_bad_prog)
    _ = next(p)
    with pytest.raises(RuntimeError):
        _ = next(p)


def test_rewind():
    p = VmParser(test_prog)
    _ = next(p)
    _ = next(p)
    _ = next(p)
    p.rewind()
    i = next(p)
    assert i['instruction_line'] == 2
    i = next(p)
    assert i['instruction_line'] == 3
