from hassembler.parser import VmParser
import pathlib
import sys

def encode(instruction):
    return ''

def main(source_file=None):
    if source_file is None:
        source_file = sys.argv[1]
    parser = VmParser(source_file)

    dest_file = pathlib.Path(source_file).with_suffix('.asm')
    with open(dest_file, 'w') as fout:
        for instruction in parser:
            encoded_instruction = encode(instruction)
            fout.write(encoded_instruction)
            fout.write('\n')

if __name__ == '__main__':
    main()
