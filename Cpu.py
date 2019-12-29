from Memory import Memory
from Graphic import Graphic
from Gpu import Gpu

import time


class Registers():
    def __init__(self):
        self.A = 0x00
        self.B = 0x00
        self.C = 0x00
        self.D = 0x00
        self.E = 0x00
        self.H = 0x00
        self.L = 0x00

        self.SP = 0x0000
        self.PC = 0x0000

        self.F = 0x00
        self.flag = {
            "Z": 1,
            "N": 0,
            "H": 0,
            "C": 0
        }

    def reset(self):
        self.A = 0x00
        self.B = 0x00
        self.C = 0x00
        self.D = 0x00
        self.E = 0x00
        self.H = 0x00
        self.L = 0x00

        self.SP = 0xfffe
        self.PC = 0x0100

    # TEST
    def set_starting_values(self):
        self.AF = 0x01 #Für GB Typ anpassen
        self.AF += 0xb0

        self.BC = 0x0013
        self.DE = 0x00d8
        self.HL = 0x014d
        
        self.SP = 0xfffe


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
    def __init__(self, cartridge):
        self.cartridge = cartridge
        self.register = Registers()
        self.stack = Stack()
        self.g = Graphic(160, 144)
        self.memory = Memory()
        self.gpu = Gpu(self.memory)
        self.codes = {
            0x00: Opcode("NOP", 1, 4, self.nop),

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
            0xe2: Opcode("LD (C),A", 1, 8, self.ld_c_a),
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

    def process(self):
        self.g.show()
        self.memory.load_rom_bank_0(self.cartridge)
        self.memory.load_bios_rom()
        done = False
        while not done:
            self.check_flags()
            op = self.memory.mem[self.register.PC]
            if op == 0xcb:
                op = 0xcb00 + self.memory.mem[self.register.PC + 1]
            self.codes[op].function()
            self.gpu.step(self.codes[op].cycles)
            # print(self.codes[op].name + " : " + hex(op))
            # print(hex(self.register.PC))
            if "call" not in self.codes[op].name.lower():
                self.register.PC += self.codes[op].length
            if self.register.PC <= len(self.memory.mem):
                self.register.PC &= 0xffff

    def check_flags(self):
        if self.memory.mem[0xff50] == 0x01:
            self.register.PC = 0x100
            self.memory.mem[0xff50] = 0x0

    def nop(self):
        # self.memory.print_ram(self.memory.mem[0x9800:0x9bff])
        # print(self.memory.mem[0x8000:0x82ff])
        while True:
            continue
        exit()

    def ld_sp_d16(self):
        self.register.SP = (self.memory.mem[self.register.PC + 2] << 8) + self.memory.mem[self.register.PC + 1]
    
    def xor_a(self):
        self.register.A ^= self.register.A

    def ld_hl_d16(self):
        self.register.H = self.memory.mem[self.register.PC + 2]
        self.register.L = self.memory.mem[self.register.PC + 1]
    
    def ld_hl_m_a(self):
        tmp = (self.register.H << 8) + self.register.L
        self.memory.mem[tmp] = self.register.A
        tmp -= 1
        self.register.H = tmp >> 8
        self.register.L = tmp & 0xff

    def jr_nz_r8(self):
        if self.register.flag["Z"] == 0:
            "JUMPING"
            self.register.PC = (self.register.PC + self.memory.mem[self.register.PC + 1]) & 0xff
        if self.register.PC == 0xe7:
            exit()

    def ld_c_d8(self):
        self.register.C = self.memory.mem[self.register.PC + 1]

    def ld_a_d8(self):
        self.register.A = self.memory.mem[self.register.PC + 1]

    def ld_c_a(self):
        self.memory.mem[0xff00 + self.register.C] = self.register.A

    def inc_c(self):
        self.register.C = (self.register.C + 1) & 0xff

    def ld_hl_a(self):
        tmp = (self.register.H << 8) + self.register.L
        self.memory.mem[tmp] = self.register.A

    def ldh_a8_a(self):
        self.memory.mem[0xff00 + (self.memory.mem[self.register.PC + 1])] = self.register.A

    def ld_de_d16(self):
        self.register.D = self.memory.mem[self.register.PC + 2]
        self.register.E = self.memory.mem[self.register.PC + 1]

    def ld_a_de(self):
        tmp = (self.register.D << 8) + self.register.E
        self.register.A = self.memory.mem[tmp]

    def call_a16(self):
        self.stack.push(self.register.PC)
        tmp = (self.memory.mem[self.register.PC + 2] << 8) + self.memory.mem[self.register.PC + 1]
        self.register.PC = tmp

    def inc_de(self):
        tmp = (self.register.D << 8) + self.register.E
        tmp = (tmp + 1) & 0xffff
        self.register.D = tmp >> 8
        self.register.E = tmp & 0xff

    def ld_a_e(self):
        self.register.A = self.register.E

    def ld_b_d8(self):
        self.register.B = self.memory.mem[self.register.PC + 1]

    def ld_hl_p_a(self):
        tmp = (self.register.H << 8) + self.register.L
        # print("LOADING: ", hex(self.register.A), " INTO ", hex(tmp))
        self.memory.mem[tmp] = self.register.A
        tmp = (tmp + 1) & 0xffff
        self.register.H = tmp >> 8
        self.register.L = tmp & 0xff

    def inc_hl(self):
        tmp = (self.register.H << 8) + self.register.L
        tmp = (tmp + 1) & 0xffff
        self.register.H = tmp >> 8
        self.register.L = tmp & 0xff

    def dec_b(self):
        self.register.B -= 1
        if self.register.B == 0:
            self.register.flag["Z"] = 1
        else:
            self.register.flag["Z"] = 0

    def ld_a16_a(self):
        tmp = (self.memory.mem[self.register.PC + 2] << 8) + self.memory.mem[self.register.PC + 1]
        self.memory.mem[tmp] = self.register.A

    def dec_a(self):
        self.register.A -= 1
        if self.register.A == 0:
            self.register.flag["Z"] = 1
        else:
            self.register.flag["Z"] = 0

    def dec_c(self):
        self.register.C -= 1
        if self.register.C == 0:
            self.register.flag["Z"] = 1
        else:
            self.register.flag["Z"] = 0

    def ld_l_d8(self):
        self.register.L = self.memory.mem[self.register.PC + 1]

    def jr_r8(self):
        self.register.PC = (self.register.PC + self.memory.mem[self.register.PC + 1]) & 0xff

    def ld_h_a(self):
        self.register.H = self.register.A

    def ld_d_a(self):
        self.register.D = self.register.A

    def inc_b(self):
        self.register.B = (self.register.B + 1) & 0xff

    def ld_e_d8(self):
        self.register.E = self.memory.mem[self.register.PC + 1]
    
    def ldh_a_a8(self):
        self.register.A = self.memory.mem[0xFF00 + self.memory.mem[self.register.PC + 1]]

    def dec_e(self):
        self.register.E -= 1
        if self.register.E == 0:
            self.register.flag["Z"] = 1
        else:
            self.register.flag["Z"] = 0

    def inc_h(self):
        self.register.H += 1

    def ld_a_h(self):
        self.register.A = self.register.H

    def jr_z_r8(self):
        if self.register.flag["Z"] != 0:
            self.register.PC = (self.register.PC + self.memory.mem[self.register.PC + 1]) & 0xff

    def sub_b(self):
        tmp = self.register.A - self.register.B
        if tmp == 0:
            self.register.flag["Z"] = 1
        else:
            self.register.flag["Z"] = 0

    def dec_d(self):
        self.register.D -= 1
        if self.register.D == 0:
            self.register.flag["Z"] = 1
        else:
            self.register.flag["Z"] = 0

    def ld_d_d8(self):
        self.register.D = self.memory.mem[self.register.PC + 1]

    def push_bc(self):
        tmp = (self.register.B << 8) + self.register.C
        self.stack.push(tmp)

    def rla(self):
        lastbit = int(format(self.register.A, '#010b')[2])
        self.register.A = ((self.register.A << 1) & 0xfe) + lastbit

    def pop_bc(self):
        tmp = self.stack.pop()
        self.register.B = (tmp >> 8)
        self.register.C = tmp & 0xff

    def ret(self):
        self.register.PC = self.stack.pop() + 2
        pass

    def cp_d8(self):
        val = self.memory.mem[self.register.PC + 1]
        if val > self.register.A:
            self.register.flag["C"] = 1
        else:
            self.register.flag["C"] = 0

#        if ((self.register.A & 0xF) > (val & 0xF)):
#            self.register.flag["H"] = 1
#        else:
#            self.register.flag["H"] = 0

        if val == self.register.A:
            self.register.flag["Z"] = 1
        else:
            self.register.flag["Z"] = 0

    def cp_hl(self):
        tmp = (self.register.H << 8) + self.register.L
        # print("Comparing: ", str(hex(self.register.A)) + "==" + str(hex(self.memory.mem[tmp])))
        if self.register.A == self.memory.mem[tmp]:
            self.register.flag["Z"] = 1
        else:
            self.register.flag["Z"] = 0

    def ld_a_l(self):
        self.register.A = self.register.L

    def ld_a_b(self):
        self.register.A = self.register.B

    def add_a_hl(self):
        tmp = (self.register.H << 8) + self.register.L
        # print(self.register.A)
        # print(self.memory.mem[tmp])
        self.register.A += self.memory.mem[tmp]



    def cb_bit_7_h(self):
        tmp = (self.register.H << 8) + self.register.L
        binary = format(tmp, '#018b')
        if binary[2] != '1':
            self.register.flag["Z"] = 1
        else:
            self.register.flag["Z"] = 0

    def cb_rl_c(self):
        lastbit = int(format(self.register.C, '#010b')[2])
        self.register.C = ((self.register.C << 1) & 0xfe) + lastbit
    