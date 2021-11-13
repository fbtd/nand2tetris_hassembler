class MockParser:
    def __init__(self, l):
        self.l = l
        self.index = 0

    def __iter__(self):
        return iter(self.l)

    def __next__(self):
        self.index += 1
        return self.l[self.index]

    def rewind(self):
        self.index = 0
