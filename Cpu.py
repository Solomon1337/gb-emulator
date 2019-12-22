from Memory import Memory


class Registers():
    def __init__(self):
        self.A = 0x0000
        self.B = 0x0000
        self.C = 0x0000
        self.D = 0x0000
        self.E = 0x0000
        self.H = 0x0000
        self.L = 0x0000

        self.AF = 0x0000
        self.BC = 0x0000
        self.DE = 0x0000
        self.HL = 0x0000

        self.SP = 0x0000
        self.PC = 0x0100


class Opcode():
    def __init__(self, name, length, asm):
        self.name = name
        self.length = length
        self.asm = asm


class Cpu():
    def __init__(self):
        self.register = Registers()

    def load_bn(self, n):
        self.register.B = n

    def load_cn(self, n):
        self.register.C = n

    def load_dn(self, n):
        self.register.D = n

    def load_en(self, n):
        self.register.E = n

    def load_hn(self, n):
        self.register.H = n

    def load_ln(self, n):
        self.register.L = n
