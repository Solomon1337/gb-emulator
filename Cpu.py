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


class Stack():
    def __init__(self):
        self.stack = []

    def push(self, val):
        self.stack.append(val)

    def pop(self):
        return self.stack.pop()


class Opcode():
    def __init__(self, name, length, cycles, function):
        self.name = name
        self.length = length
        self.cycles = cycles
        self.function = function


class Cpu():
    def __init__(self):
        self.register = Registers()
        self.stack = Stack()
        self.memory = Memory()
        self.codes = {
            0x06: Opcode("LD B,d8", 2, 8, self.ld_b_d8),
            0x0e: Opcode("LD C,d8", 2, 8, self.ld_c_d8),
            0x11: Opcode("LD DE,d16", 3, 12, self.ld_de_d16),
            0x16: Opcode("LD D,d8", 2, 8, self.ld_d_d8),
            0x1a: Opcode("LD A,(DE)", 1, 8, self.ld_a_de),
            0x1e: Opcode("LD E,d8", 2, 8, self.ld_e_d8),
            0x21: Opcode("LD HL,d16", 3, 12, self.ld_hl_d16),
            0x22: Opcode("LD (HL+),A", 1, 8, self.ld_hl_p_a),
            0x2e: Opcode("LD L,d8", 2, 8, self.ld_l_d8),
            0x31: Opcode("LD SP,d16", 3, 12, self.ld_sp_d16),
            0x32: Opcode("LD (HL-),A", 1, 8, self.ld_hl_m_a),
            0x3e: Opcode("LD A,d8", 2, 8, self.ld_a_d8),
            0x4f: Opcode("LD C,A", 1, 4, self.ld_c_a),
            0x57: Opcode("LD D,A", 1, 4, self.ld_d_a),
            0x67: Opcode("LD H,A", 1, 4, self.ld_h_a),
            0x77: Opcode("LD (HL),A", 1, 8, self.ld_hl_a),
            0x78: Opcode("LD A,B", 1, 4, self.ld_a_b),
            0x7b: Opcode("LD A,E", 1, 4, self.ld_a_e),
            0x7c: Opcode("LD A,H", 1, 4, self.ld_a_h),
            0x7d: Opcode("LD A,L", 1, 4, self.ld_a_l),
            0xe2: Opcode("LD (C),A", 2, 8, self.ld_c_a),
            0xea: Opcode("LD (a16),A", 3, 16, self.ld_a16_a),
            0xe0: Opcode("LDH (a8),A", 2, 12, self.ldh_a8_a),
            0xf0: Opcode("LDH A,(a8)", 2, 12, self.ldh_a_a8),

            0x04: Opcode("INC B", 1, 4, self.inc_b),
            0x0c: Opcode("INC C", 1, 4, self.inc_c),
            0x13: Opcode("INC DE", 1, 8, self.inc_de),
            0x23: Opcode("INC HL", 1, 8, self.inc_hl),
            0x24: Opcode("INC H", 1, 4, self.inc_h),

            0x05: Opcode("DEC B", 1, 4, self.dec_b),
            0x0d: Opcode("DEC C", 1, 4, self.dec_c),
            0x15: Opcode("DEC D", 1, 4, self.dec_d),
            0x1d: Opcode("DEC E", 1, 4, self.dec_e),
            0x3d: Opcode("DEC A", 1, 4, self.dec_a),

            0x18: Opcode("JR r8", 2, 12, self.jr_r8),
            0x20: Opcode("JR NZ,r8", 2, 12, self.jr_nz_r8),
            0x28: Opcode("JR Z,r8", 2, 12, self.jr_z_r8),

            0x17: Opcode("RLA", 1, 4, self.rla),
            0x86: Opcode("ADD A,(HL)", 1, 8, self.add_a_hl),
            0x90: Opcode("SUB B", 1, 4, self.sub_b),
            0xaf: Opcode("XOR A", 1, 4, self.xor_a),
            0xbe: Opcode("CP (HL)", 1, 8, self.cp_hl),
            0xc1: Opcode("POP BC", 1, 12, self.pop_bc),
            0xc5: Opcode("PUSH BC", 1, 16, self.push_bc),
            0xc9: Opcode("RET", 1, 16, self.ret),
            0xcd: Opcode("CALL a16", 3, 24, self.call_a16),
            0xfe: Opcode("CP d8", 2, 8, self.cp_d8),
            


            0xcb7c: Opcode("BIT 7,H", 2, 8, self.cb_bit_7_h),
            0xcb11: Opcode("RL C", 2, 8, self.cb_rl_c)

        }

    def nop(self):
        pass

    def ld_sp_d16(self):
        pass
    
    def xor_a(self):
        pass

    def ld_hl_d16(self):
        pass
    
    def ld_hl_m_a(self):
        pass

    def jr_nz_r8(self):
        pass

    def ld_c_d8(self, location):
        self.register.C = self.memory.read(location)[0]

    def ld_a_d8(self):
        pass

    def ld_c_a(self):
        pass

    def inc_c(self):
        self.register.C += 1

    def ld_hl_a(self):
        pass

    def ldh_a8_a(self):
        pass

    def ld_de_d16(self, location):
        self.register.DE = self.memory.read(location)[0:2]

    def ld_a_de(self):
        self.register.A = self.memory.read(self.register.DE)[0]

    def call_a16(self):
        pass

    def inc_de(self):
        self.register.DE += 1

    def ld_a_e(self):
        pass

    def cp_d8(self):
        pass

    def ld_b_d8(self, location):
        self.register.B = self.memory.read(location)[0]

    def ld_hl_p_a(self):
        pass

    def inc_hl(self):
        self.register.HL += 1

    def dec_b(self):
        self.register.B -= 1

    def ld_a16_a(self):
        pass

    def dec_a(self):
        self.register.A -= 1

    def dec_c(self):
        self.register.C -= 1

    def ld_l_d8(self):
        pass

    def jr_r8(self):
        pass

    def ld_h_a(self):
        pass

    def ld_d_a(self):
        pass

    def inc_b(self):
        self.register.B += 1

    def ld_e_d8(self):
        pass
    
    def ldh_a_a8(self):
        pass

    def dec_e(self):
        self.register.E -= 1

    def inc_h(self):
        self.register.H += 1

    def ld_a_h(self):
        pass

    def jr_z_r8(self):
        pass

    def sub_b(self):
        pass

    def dec_d(self):
        self.register.D -= 1

    def ld_d_d8(self, location):
        self.register.D = self.memory.read(location)[0]

    def push_bc(self):
        self.stack.push(self.register.BC)

    def rla(self):
        pass

    def pop_bc(self):
        self.register.BC = self.stack.pop()

    def ret(self):
        pass

    def cp_hl(self):
        pass

    def ld_a_l(self):
        pass

    def ld_a_b(self):
        pass

    def add_a_hl(self):
        pass



    def cb_bit_7_h(self):
        pass

    def cb_rl_c(self):
        pass
    