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
    def __init__(self, name, length, cycles, function):
        self.name = name
        self.length = length
        self.cycles = cycles
        self.function = function


class Cpu():
    def __init__(self):
        self.register = Registers()
        self.codes = {
            0x31: Opcode("LD SP,d16", 3, 12, self.ld_sp_d16),
            0xaf: Opcode("XOR A", 1, 4, self.xor_a),
            0x21: Opcode("LD HL,d16", 3, 12, self.ld_hl_d16),
            0x32: Opcode("LD (HL-),A", 1, 8, self.ld_hl_m_a),
            0x20: Opcode("JR NZ,r8", 2, 12, self.jr_nz_r8),
            0x0e: Opcode("LD C,d8", 2, 8, self.ld_c_d8),
            0x3e: Opcode("LD A,d8", 2, 8, self.ld_a_d8),
            0xe2: Opcode("LD (C),A", 2, 8, self.ld_c_a),
            0x0c: Opcode("INC C", 1, 4, self.inc_c),
            0x77: Opcode("LD (HL),A", 1, 8, self.ld_hl_a),
            0xe0: Opcode("LDH (a8),A", 2, 12, self.ldh_a8_a),
            0x11: Opcode("LD DE,d16", 3, 12, self.ld_de_d16),
            0x1a: Opcode("LD A,(DE)", 1, 8, self.ld_a_de),
            0xcd: Opcode("CALL a16", 3, 24, self.call_a16),
            0x13: Opcode("INC DE", 1, 8, self.inc_de),
            0x7b: Opcode("LD A,E", 1, 4, self.ld_a_e),
            0xfe: Opcode("CP d8", 2, 8, self.cp_d8),
            0x06: Opcode("LD B,d8", 2, 8, self.ld_b_d8),
            0x22: Opcode("LD (HL+),A", 1, 8, self.ld_hl_p_a),
            0x23: Opcode("INC HL", 1, 8, self.inc_hl),
            0x05: Opcode("DEC B", 1, 4, self.dec_b),
            0xea: Opcode("LD (a16),A", 3, 16, self.ld_a16_a),
            0x3d: Opcode("DEC A", 1, 4, self.dec_a),
            0x0d: Opcode("DEC C", 1, 4, self.dec_c),
            0x2e: Opcode("LD L,d8", 2, 8, self.ld_l_d8),
            0x18: Opcode("JR r8", 2, 12, self.jr_r8),
            0x67: Opcode("LD H,A", 1, 4, self.ld_h_a),
            0x57: Opcode("LD D,A", 1, 4, self.ld_d_a),
            0x04: Opcode("INC B", 1, 4, self.inc_b),
            0x1e: Opcode("LD E,d8", 2, 8, self.ld_e_d8),
            0xf0: Opcode("LDH A,(a8)", 2, 12, self.ldh_a_a8),
            0x1d: Opcode("DEC E", 1, 4, self.dec_e),
            0x24: Opcode("INC H", 1, 4, self.inc_h),
            0x7c: Opcode("LD A,H", 1, 4, self.ld_a_h),
            0x28: Opcode("JR Z,r8", 2, 12, self.jr_z_r8),
            0xe2: Opcode("LD (C),A", 2, 8, self.ld_c_a),
            0x90: Opcode("SUB B", 1, 4, self.sub_b),
            0x15: Opcode("DEC D", 1, 4, self.dec_d),
            0x16: Opcode("LD D,d8", 2, 8, self.ld_d_d8),
            0x4f: Opcode("LD C,A", 1, 4, self.ld_c_a),
            0xc5: Opcode("PUSH BC", 1, 16, self.push_bc),
            0x17: Opcode("RLA", 1, 4, self.rla),
            0xc1: Opcode("POP BC", 1, 12, self.pop_bc),
            0xc9: Opcode("RET", 1, 16, self.ret),
            0xbe: Opcode("CP (HL)", 1, 8, self.cp_hl),
            0x7d: Opcode("LD A,L", 1, 4, self.ld_a_l),
            0x78: Opcode("LD A,B", 1, 4, self.ld_a_b),
            0x86: Opcode("ADD A,(HL)", 1, 4, self.add_a_hl),
            


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

    def ld_c_d8(self):
        pass

    def ld_a_d8(self):
        pass

    def ld_c_a(self):
        pass

    def inc_c(self):
        pass

    def ld_hl_a(self):
        pass

    def ldh_a8_a(self):
        pass

    def ld_de_d16(self):
        pass

    def ld_a_de(self):
        pass

    def call_a16(self):
        pass

    def inc_de(self):
        pass

    def ld_a_e(self):
        pass

    def cp_d8(self):
        pass

    def ld_b_d8(self):
        pass

    def ld_hl_p_a(self):
        pass

    def inc_hl(self):
        pass

    def dec_b(self):
        pass

    def ld_a16_a(self):
        pass

    def dec_a(self):
        pass

    def dec_c(self):
        pass

    def ld_l_d8(self):
        pass

    def jr_r8(self):
        pass

    def ld_h_a(self):
        pass

    def ld_d_a(self):
        pass

    def inc_b(self):
        pass

    def ld_e_d8(self):
        pass
    
    def ldh_a_a8(self):
        pass

    def dec_e(self):
        pass

    def inc_h(self):
        pass

    def ld_a_h(self):
        pass

    def jr_z_r8(self):
        pass

    def sub_b(self):
        pass

    def dec_d(self):
        pass

    def ld_d_d8(self):
        pass

    def push_bc(self):
        pass

    def rla(self):
        pass

    def pop_bc(self):
        pass

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
    
