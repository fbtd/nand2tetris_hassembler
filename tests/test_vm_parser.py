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
        {'instruction_line': 7, 'operation': 'sub', 'instruction_type': 'VM'},
        {'instruction_line': 8, 'operation': 'neg', 'instruction_type': 'VM'},
        {'instruction_line': 9, 'operation': 'eq', 'instruction_type': 'VM'},
        {'instruction_line': 10, 'operation': 'gt', 'instruction_type': 'VM'},
        {'instruction_line': 11, 'operation': 'lt', 'instruction_type': 'VM'},
        {'instruction_line': 12, 'operation': 'and', 'instruction_type': 'VM'},
        {'instruction_line': 13, 'operation': 'or', 'instruction_type': 'VM'},
        {'instruction_line': 14, 'operation': 'not', 'instruction_type': 'VM'},
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


test_branching_prog = Path(__file__).parent / 'BranchingProg.vm'
def test_branching_prog_parse():
    p = VmParser(test_branching_prog)
    reference_instructions = (
        {'instruction_line': 2, 'operation': 'label', 'label': 'SECOND_LINE', 'instruction_type': 'VM'},
        {'instruction_line': 3, 'operation': 'label', 'label': 'Third$line.3', 'instruction_type': 'VM'},
        {'instruction_line': 5, 'operation': 'goto', 'destination': 'SECOND_LINE', 'instruction_type': 'VM'},
        {'instruction_line': 6, 'operation': 'if-goto', 'destination': 'SECOND_LINE', 'instruction_type': 'VM'},
        {'instruction_line': 8, 'operation': 'function', 'name': 'f1', 'nvars': '2', 'instruction_type': 'VM'},
        {'instruction_line': 9, 'operation': 'call', 'name': 'f1', 'nargs': '3', 'instruction_type': 'VM'},
        {'instruction_line': 10, 'operation': 'return', 'instruction_type': 'VM'},
    )

    assert len(p) >= len(reference_instructions)

    for instruction, reference_instruction in zip(p, reference_instructions):
        assert instruction == reference_instruction
