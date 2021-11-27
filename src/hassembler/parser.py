import re

class Parser:
    def __init__(self, source_file, remove_spaces = True, use_line_number = False):
        self.source_file = source_file
        self.f = open(self.source_file)
        self.instruction_line = 0
        self.patterns = tuple()
        self.remove_spaces = remove_spaces
        self.use_line_number = use_line_number # instead of instruction number


    def __len__(self):
        length = 0
        if self.use_line_number:
            for _ in self.f:
                length += 1
        else:
            for _ in self:
                length += 1
        self.rewind()
        return length

    def __iter__(self):
        return self


    def __next__(self):
        while True:
            original_line = next(self.f)
            line = original_line
            if self.use_line_number:
                self.instruction_line += 1
            if self.remove_spaces:
                line = line.replace(' ', '')
            line = line.replace('\t', '')
            line = line.replace('\n', '')
            if not line: continue
            if re.search('^//', line) is not None: continue

            instruction = {'instruction_line': self.instruction_line}

            for pattern, instruction_type, instruction_increment in self.patterns:
                m = re.search(pattern, line)
                if m is None: continue
                if None in m.groups(): continue
                gd = m.groupdict()
                instruction.update(gd)
                instruction.update({'instruction_type': instruction_type})
                if not self.use_line_number:
                    self.instruction_line += instruction_increment;
                return instruction
            raise RuntimeError(f'instruction "{original_line[:-1]}" could not be parsed')


    def rewind(self):
        self.f.seek(0)
        self.instruction_line = 0

    def close(self):
        self.f.close()

_symbol = '[a-zA-Z_.$:][a-zA-Z0-9_.$:]*'

class AsmParser(Parser):
    def __init__(self, source_file):
        super().__init__(source_file)
        valid_chars = '[-+|&!01ADMJGTEQLNP]'
        self.patterns = (
        #   (pattern, instruction_type, instruction_increment)
            (f'^@(?P<symbol>{_symbol})', 'A', 1),
            (r'^@(?P<value>[0-9]+)', 'A', 1),
            (r'^@(?P<value>[0-9]+)', 'A', 1),
            (rf'^(?P<dest>{valid_chars}+)=(?P<comp>{valid_chars}+);(?P<jump>{valid_chars}+)', 'C', 1),
            (rf'^(?P<comp>{valid_chars}+);(?P<jump>{valid_chars}+)', 'C', 1),
            (rf'^(?P<dest>{valid_chars}+)=(?P<comp>{valid_chars}+)', 'C', 1),
            (rf'^\((?P<label>[^)]+)\)', 'LABEL', 0),
        )


class VmParser(Parser):
    def __init__(self, source_file):
        super().__init__(source_file, remove_spaces=False, use_line_number=True)
        arithmetic_commands='add|sub|neg|eq|gt|lt|and|not|or'
        arithmetic_patterns = (f'(?P<operation>{arithmetic_commands})', 'VM', None)

        segments = 'argument|local|static|this|that|pointer|temp'
        stack_operation = f'(?P<operation>push|pop) +(?P<segment>{segments}) +(?P<index>\\d+)'
        stack_pattern = (stack_operation, 'VM', None)
        stack_constant_pattern = ('(?P<operation>push|pop) +constant +(?P<constant>\\d+)', 'VM', None)

        label_pattern = (f'(?P<operation>label) +(?P<label>{_symbol})', 'VM', None)
        goto_pattern = (f'(?P<operation>(?:if-)?goto) +(?P<destination>{_symbol})', 'VM', None)

        function_pattern = ('(?P<operation>function) +(?P<name>\\S+) +(?P<nvars>\\d+)', 'VM', None)
        call_pattern = ('(?P<operation>call) +(?P<name>\\S+) +(?P<nargs>\\d+)', 'VM', None)
        return_pattern = (f'(?P<operation>return)', 'VM', None)

        self.patterns = (arithmetic_patterns, stack_pattern, stack_constant_pattern,
                label_pattern, goto_pattern, function_pattern, call_pattern, return_pattern)
