import re


_symbol = '[a-zA-Z_.$:][a-zA-Z0-9_.$:]*'
patterns = (
    (f'^@(?P<symbol>{_symbol})', 'A', 1),
    (r'^@(?P<value>[0-9]+)', 'A', 1),
    (r'^@(?P<value>[0-9]+)', 'A', 1),
    (r'^(?P<dest>.+)=(?P<comp>.+);(?P<jump>.+)', 'C', 1),
    (r'^(?P<comp>.+);(?P<jump>.+)', 'C', 1),
    (r'^(?P<dest>.+)=(?P<comp>.+)', 'C', 1),
    (r'^\((?P<label>.+)\)', 'LABEL', 0),
)


class Parser:
    def __init__(self, source_file):
        self.source_file = source_file
        self.f = open(self.source_file)
        self.instruction_line = 0

    def __iter__(self):
        return self

    def __next__(self):
        while True:
            line = next(self.f)
            line = line.replace(' ', '')
            line = line.replace('\t', '')
            if not line: continue
            if re.search('^//', line) is not None: continue

            instruction = {'instruction_line': self.instruction_line}


            for pattern, instruction_type, instruction_increment in patterns:
                m = re.match(pattern, line)
                if m is None: continue
                if None in m.groups(): continue
                gd = m.groupdict()
                instruction.update(gd)
                instruction.update({'instruction_type': instruction_type})
                self.instruction_line += instruction_increment;
                return instruction


    def rewind(self):
        self.f.seek(0)
        self.instruction_line = 0

    def close(self):
        self.f.close()

