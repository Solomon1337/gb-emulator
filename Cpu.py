from Memory import Memory


class Registers():
    def __init__(self):
        self.A = 0x00
        self.B = 0x00
        self.C = 0x00
        self.D = 0x00
        self.E = 0x00
        self.H = 0x00
        self.L = 0x00

        self.AF = 0x00
        self.BC = 0x00
        self.DE = 0x00
        self.HL = 0x00

        self.SP = 0x00
        self.PC = 0x00


class Opcode():
    def __init__(self, name, length, asm):
        self.name = name
        self.length = length
        self.asm = asm


class Cpu():
    def __init__(self):
        self.register = Registers()


class Commands():

    def load_bn(n):
        self.B = n

    def load_cn(n):
        self.C = n
