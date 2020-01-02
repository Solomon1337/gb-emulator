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
            "C": 0,
            "IME": 0
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

    def __str__(self):
        return """
        A  = {}
        BC = {}
        DE = {}
        HL = {}
        SP = {}
        PC = {}
        """.format(hex(self.A),
                    hex((self.B << 8) + self.C),
                    hex((self.D << 8) + self.E),
                    hex((self.H << 8) + self.L),
                    hex(self.SP),
                    hex(self.PC))

    # TEST
    def set_starting_values(self):
        self.A = 0x00
        self.B = 0x00
        self.C = 0x13
        self.D = 0x00
        self.E = 0xd8
        self.H = 0x01
        self.L = 0x4d
        
        self.SP = 0xfffe

        self.PC = 0x0100

        self.flag["Z"] = 1
        self.flag["N"] = 0
        self.flag["H"] = 0
        self.flag["C"] = 0
        self.flag["IME"] = 0


class Stack():
    def __init__(self):
        self.stack = []

    def push(self, val):
        self.stack.append(val)

    def pop(self):
        return self.stack.pop()

    def __str__(self):
        return self.stack


class Cpu():
    def __init__(self, cartridge):
        self.screen_cycles = int((4.194304*1e6 / 59.7) / 144)
        self.done = False
        self.all_cycles = 0
        self.cartridge = cartridge
        self.register = Registers()
        self.stack = Stack()
        self.g = Graphic(160, 144)
        self.memory = Memory()
        self.gpu = Gpu(self.memory)
        self.codes = {
            0x00: ("NOP", 1, 4, self.nop),
            0x01: ("LD BC,d16", 3, 12, self.ld_bc_d16),
            0x06: ("LD B,d8", 2, 8, self.ld_b_d8),
            0x0e: ("LD C,d8", 2, 8, self.ld_c_d8),
            0x11: ("LD DE,d16", 3, 12, self.ld_de_d16),
            0x16: ("LD D,d8", 2, 8, self.ld_d_d8),
            0x1a: ("LD A,(DE)", 1, 8, self.ld_a_de),
            0x1e: ("LD E,d8", 2, 8, self.ld_e_d8),
            0x21: ("LD HL,d16", 3, 12, self.ld_hl_d16),
            0x22: ("LD (HL+),A", 1, 8, self.ld_hl_p_a),
            0x2a: ("LD A,(HL+)", 1, 8, self.ld_a_hl_p),
            0x2e: ("LD L,d8", 2, 8, self.ld_l_d8),
            0x31: ("LD SP,d16", 3, 12, self.ld_sp_d16),
            0x32: ("LD (HL-),A", 1, 8, self.ld_hl_m_a),
            0x36: ("LD (HL),d8", 1, 8, self.ld_hl_d8),
            0x3e: ("LD A,d8", 2, 8, self.ld_a_d8),
            0x46: ("LD B,(HL)", 1, 8, self.ld_b_hl),
            0x47: ("LD B,A", 1, 4, self.ld_b_a),
            0x4f: ("LD C,A", 1, 4, self.ld_c_a),
            0x56: ("LD D,(HL)", 1, 8, self.ld_d_hl),
            0x57: ("LD D,A", 1, 4, self.ld_d_a),
            0x5e: ("LD E,(HL)", 1, 8, self.ld_e_hl),
            0x5f: ("LD E,A", 1, 4, self.load_e_a),
            0x67: ("LD H,A", 1, 4, self.ld_h_a),
            0x77: ("LD (HL),A", 1, 8, self.ld_hl_a),
            0x78: ("LD A,B", 1, 4, self.ld_a_b),
            0x79: ("LD A,C", 1, 4, self.ld_a_c),
            0x7b: ("LD A,E", 1, 4, self.ld_a_e),
            0x7c: ("LD A,H", 1, 4, self.ld_a_h),
            0x7d: ("LD A,L", 1, 4, self.ld_a_l),
            0x7e: ("LD A,(HL)", 1, 8, self.ld_a_hl),
            0xe2: ("LD (C),A", 1, 8, self.ld_c_a),
            0xea: ("LD (a16),A", 3, 16, self.ld_a16_a),
            0xe0: ("LDH (a8),A", 2, 12, self.ldh_a8_a),
            0xf0: ("LDH A,(a8)", 2, 12, self.ldh_a_a8),

            0x04: ("INC B", 1, 4, self.inc_b),
            0x0c: ("INC C", 1, 4, self.inc_c),
            0x13: ("INC DE", 1, 8, self.inc_de),
            0x23: ("INC HL", 1, 8, self.inc_hl),
            0x24: ("INC H", 1, 4, self.inc_h),

            0x05: ("DEC B", 1, 4, self.dec_b),
            0x0b: ("DEC BC", 1, 8, self.dec_bc),
            0x0d: ("DEC C", 1, 4, self.dec_c),
            0x15: ("DEC D", 1, 4, self.dec_d),
            0x1d: ("DEC E", 1, 4, self.dec_e),
            0x3d: ("DEC A", 1, 4, self.dec_a),

            0x18: ("JR r8", 2, 12, self.jr_r8),
            0x20: ("JR NZ,r8", 2, 12, self.jr_nz_r8),
            0x28: ("JR Z,r8", 2, 12, self.jr_z_r8),
            0xc3: ("JP d16", 3, 16, self.jp_d16),
            0xe9: ("JP (HL)", 1, 4, self.jp_hl),

            0x17: ("RLA", 1, 4, self.rla),
            0x19: ("ADD HL,DE", 1, 8, self.add_hl_de),
            0x2f: ("CPL", 1, 4, self.cpl),
            0x86: ("ADD A,(HL)", 1, 8, self.add_a_hl),
            0x87: ("ADD A,A", 1, 8, self.add_a_a),
            0x90: ("SUB B", 1, 4, self.sub_b),
            0xa0: ("AND B", 1, 4, self.and_b),
            0xa1: ("AND C", 1, 4, self.and_c),
            0xa9: ("XOR C", 1, 4, self.xor_c),
            0xaf: ("XOR A", 1, 4, self.xor_a),
            0xb0: ("OR B", 1, 4, self.or_b),
            0xb1: ("OR C", 1, 4, self.or_c),
            0xe6: ("AND d8", 2, 8, self.and_d8),
            0xbe: ("CP (HL)", 1, 8, self.cp_hl),
            0xc1: ("POP BC", 1, 12, self.pop_bc),
            0xc5: ("PUSH BC", 1, 16, self.push_bc),
            0xc9: ("RET", 1, 16, self.ret),
            0xd5: ("PUSH DE", 1, 16, self.push_de),
            0xcd: ("CALL a16", 3, 24, self.call_a16),
            0xd6: ("SUB d8", 2, 8, self.sub_d8),
            0xe1: ("POP HL", 1, 12, self.pop_hl),
            0xf3: ("DI", 1, 4, self.di),
            0xfb: ("EI", 1, 4, self.ei),
            0xfe: ("CP d8", 2, 8, self.cp_d8),
            0xef: ("RST_28H", 1, 16, self.rst_28h),
            0xff: ("RST_38H", 1, 16, self.rst_38h),
            

            0xcb37: ("SWAP A", 2, 8, self.swap_a),
            0xcb3f: ("SRL A", 2, 8, self.srl_a),
            0xcb7c: ("BIT 7,H", 2, 8, self.cb_bit_7_h),
            0xcb11: ("RL C", 2, 8, self.cb_rl_c)
        }

    def process(self):
        self.g.show()
        self.memory.load_rom_bank_0(self.cartridge)
        self.register.set_starting_values()
        # self.memory.load_bios_rom()
        start1 = time.time()
        cycles = 0
        while not self.done:
            self.check_flags()
            opc = self.memory.mem[self.register.PC]
            if opc == 0xcb:
                opc = 0xcb00 + self.memory.mem[self.register.PC + 1]
            try:
                op = self.codes[opc]
            except KeyError:
                print("OPCODE ", hex(opc), " NOT FOUND!!")
                exit()
            #print("Executing:\t", op[0], "\tat address: ", hex(self.register.PC), "\tOPCODE: ", hex(opc))
            #print(self.memory.mem[0x27a1 - 2 : 0x27a1 + 3])
            op[3]()
            self.all_cycles += op[2]
            cycles += op[2] / 4
            if cycles > 456:
                cycles %= 456
                self.gpu.step(op[2])
            if "call" not in op[0].lower():
                self.register.PC += op[1]
            # if self.register.PC > 0xff:
            #     self.done = True
            if self.register.PC >= len(self.memory.mem):
                self.register.PC &= 0xffff
        end = time.time()
        print("TIME USED FOR ", self.all_cycles, " CYCLES: ", end-start1)

    def check_flags(self):
        if self.memory.mem[0xff50] == 0x01:
            self.register.PC = 0x100
            self.memory.mem[0xff50] = 0x00

    def nop(self):
        pass

    def ld_sp_d16(self):
        self.register.SP = (self.memory.mem[self.register.PC + 2] << 8) + self.memory.mem[self.register.PC + 1]
    
    def xor_a(self):
        self.register.A = 0x0
        self.register.flag["Z"] = 1

    def ld_hl_d16(self):
        # print("LOADING: ", hex(self.memory.mem[self.register.PC + 2]), hex(self.memory.mem[self.register.PC + 1]))
        self.register.H = self.memory.mem[self.register.PC + 2]
        self.register.L = self.memory.mem[self.register.PC + 1]
        if self.register.PC == 0x2795:
            pass
    
    def ld_hl_m_a(self):
        tmp = (self.register.H << 8) + self.register.L
        #print("WRITING TO: ", hex(tmp))
        #print(self.register)
        self.memory.mem[tmp] = self.register.A
        tmp -= 1
        self.register.H = tmp >> 8
        self.register.L = tmp & 0xff

    def jr_nz_r8(self):
        if self.register.flag["Z"] == 0:
            tmp = self.register.PC >> 8
            last = (self.register.PC + self.memory.mem[self.register.PC + 1]) & 0xff
            print(self.memory.mem[0x27a1 - 2 : 0x27a1 + 3])
            self.register.PC = (tmp << 8) + last

    def ld_c_d8(self):
        self.register.C = self.memory.mem[self.register.PC + 1]

    def ld_a_d8(self):
        self.register.A = self.memory.mem[self.register.PC + 1]

    def ld_c_a(self):
        self.memory.mem[0xff00 + self.register.C] = self.register.A

    def inc_c(self):
        if (self.register.C & 0xf) == 0b1111: self.register.flag["H"] = 1
        self.register.C = (self.register.C + 1) & 0xff
        if self.register.C == 0: self.register.flag["Z"] = 1

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
        self.memory.mem[tmp] = self.register.A
        tmp = (tmp + 1) & 0xffff
        self.register.H = tmp >> 8
        self.register.L = tmp & 0xff

    def ld_a_hl_p(self):
        tmp = (self.register.H << 8) + self.register.L
        self.register.A = self.memory.mem[tmp]
        tmp = (tmp + 1) & 0xffff
        self.register.H = tmp >> 8
        self.register.L = tmp & 0xff

    def inc_hl(self):
        tmp = (self.register.H << 8) + self.register.L
        tmp = (tmp + 1) & 0xffff
        self.register.H = tmp >> 8
        self.register.L = tmp & 0xff

    def dec_b(self):
        if (self.register.B % 0xf) == 0b0000: self.register.flag["H"] = 1
        self.register.B -= 1
        if self.register.B < 0:
            self.register.B = 255
        if self.register.B == 0:
            self.register.flag["Z"] = 1
        else:
            self.register.flag["Z"] = 0

    def ld_a16_a(self):
        tmp = (self.memory.mem[self.register.PC + 2] << 8) + self.memory.mem[self.register.PC + 1]
        self.memory.mem[tmp] = self.register.A

    def dec_a(self):
        if (self.register.A % 0xf) == 0b0000: self.register.flag["H"] = 1
        self.register.A -= 1
        if self.register.A < 0:
            self.register.A = 0xff
        if self.register.A == 0:
            self.register.flag["Z"] = 1
        else:
            self.register.flag["Z"] = 0

    def dec_c(self):
        if (self.register.C % 0xf) == 0b0000: self.register.flag["H"] = 1
        self.register.C -= 1
        if self.register.C < 0:
            self.register.C = 255
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
        if (self.register.B & 0xf) == 0b1111: self.register.flag["H"] = 1
        self.register.B = (self.register.B + 1) & 0xff
        if self.register.B == 0: self.register.flag["Z"] = 1

    def ld_e_d8(self):
        self.register.E = self.memory.mem[self.register.PC + 1]
    
    def ldh_a_a8(self):
        self.register.A = self.memory.mem[0xFF00 + self.memory.mem[self.register.PC + 1]]

    def dec_e(self):
        if (self.register.E % 0xf) == 0b0000: self.register.flag["H"] = 1
        self.register.E -= 1
        if self.register.E < 0:
            self.register.E = 0xff
        if self.register.E == 0:
            self.register.flag["Z"] = 1
        else:
            self.register.flag["Z"] = 0

    def inc_h(self):
        if (self.register.H & 0xf) == 0b1111: self.register.flag["H"] = 1
        self.register.H = (self.register.H + 1) & 0xff
        if self.register.H == 0: self.register.flag["Z"] = 1

    def ld_a_h(self):
        self.register.A = self.register.H

    def jr_z_r8(self):
        if self.register.flag["Z"] != 0:
            self.register.PC = (self.register.PC + self.memory.mem[self.register.PC + 1]) & 0xff

    def sub_b(self):
        self.register.A = (self.register.A - self.register.B) % 0x100
        if self.register.A == 0:
            self.register.flag["Z"] = 1
        else:
            self.register.flag["Z"] = 0

    def sub_d8(self):
        val = self.memory.mem[self.register.PC + 1]
        tmp = self.register.A
        self.register.A = (self.register.A - val) % 0x100
        self.register.flag["N"] = 1
        if self.register.A == 0:
            self.register.flag["Z"] = 1
        else:
            self.register.flag["Z"] = 0
        if self.register.A < tmp:
            self.register.flag["C"] = 1
        else:
            self.register.flag["C"] = 0

    def dec_d(self):
        if (self.register.D % 0xf) == 0b0000: self.register.flag["H"] = 1
        self.register.D -= 1
        if self.register.D < 0:
            self.register.D = 255
        if self.register.D == 0:
            self.register.flag["Z"] = 1
        else:
            self.register.flag["Z"] = 0

    def ld_d_d8(self):
        self.register.D = self.memory.mem[self.register.PC + 1]

    def push_bc(self):
        tmp = (self.register.B << 8) + self.register.C
        self.stack.push(tmp)

    def push_de(self):
        tmp = (self.register.D << 8) + self.register.E
        self.stack.push(tmp)

    def rla(self):
        self.register.flag["C"] = (self.register.A & (1<<7)) >> 7
        self.register.A <<= 1
        self.register.A |= self.register.flag["C"]
        self.register.flag["Z"] = self.register.A == 0

    def pop_bc(self):
        tmp = self.stack.pop()
        self.register.B = (tmp >> 8)
        self.register.C = tmp & 0xff

    def pop_hl(self):
        print(self.stack.stack)
        tmp = self.stack.pop()
        self.register.H = (tmp >> 8)
        self.register.L = tmp & 0xff
        print("HL = ", tmp)

    def ret(self):
        self.register.PC = self.stack.pop() + 2
        pass

    def cp_d8(self):
        result = (self.register.A - self.memory.mem[self.register.PC + 1]) & 0xff
        if result == 0:
            self.register.flag["Z"] = 1
        else:
            self.register.flag["Z"] = 0
        if self.register.A < result:
            self.register.flag["C"] = 1
        else:
            self.register.flag["C"] = 0

    def cp_hl(self):
        tmp = (self.register.H << 8) + self.register.L
        # print("Comparing: ", str(hex(self.register.A)) + "==" + str(hex(self.memory.mem[tmp])))
        result = (self.register.A - self.memory.mem[tmp]) % 0x100
        if result == 0:
            self.register.flag["Z"] = 1
        else:
            self.register.flag["Z"] = 0
        if self.register.A < result: self.register.flag["C"] = 1

    def ld_a_l(self):
        self.register.A = self.register.L

    def ld_a_b(self):
        print("LOADING ", hex(self.register.B), " into ", hex(self.register.A))
        self.register.A = self.register.B

    def add_a_hl(self):
        tmp = (self.register.H << 8) + self.register.L
        self.register.A = (self.register.A + self.memory.mem[tmp]) & 0xff
        if self.register.A == 0: self.register.flag["Z"] = 1

    def add_a_a(self):
        self.register.A = self.register.A + self.register.A
        if self.register.A > 0xff:
            self.register.flag["C"] = 1
            self.register.A &= 0xff
        else:
            self.register.flag["C"] = 0
        if self.register.A == 0:
            self.register.flag["Z"] = 1
        else:
            self.register.flag["Z"] = 0

    def jp_d16(self):
        tmp = (self.memory.mem[self.register.PC + 2] << 8) + self.memory.mem[self.register.PC + 1]
        self.register.PC = tmp - 3

    def jp_hl(self):
        tmp = (self.register.H << 8) + self.register.L
        self.register.PC = tmp
        # exit()

    def load_e_a(self):
        self.register.E = self.register.A

    def add_hl_de(self):
        tmp_de = (self.register.D << 8) + self.register.E
        tmp_hl = (self.register.H << 8) + self.register.L
        tmp_hl += tmp_de
        if tmp_hl > 0xffff:
            tmp_hl &= 0xffff
            self.register.flag["C"] = 1
        else:
            self.register.flag["C"] = 0
        self.register.H = tmp_hl >> 8
        self.register.L = tmp_hl & 0xff

    def rst_38h(self):
        self.stack.push(self.register.PC)
        self.register.PC = 0x38
        exit()

    def rst_28h(self):
        self.stack.push(self.register.PC)
        self.register.PC = 0x28
        self.register.PC -= 1
        # exit()

    def and_d8(self):
        self.register.A &= self.memory.mem[self.register.PC + 1]
        if self.register.A == 0:
            self.register.flag["Z"] = 1
        else:
            self.register.flag["Z"] = 0
        self.register.flag["C"] = 0

    def ld_b_hl(self):
        tmp = (self.register.H << 8) + self.register.L
        self.register.B = self.memory.mem[tmp]

    def ld_d_hl(self):
        tmp = (self.register.H << 8) + self.register.L
        self.register.D = self.memory.mem[tmp]

    def ld_e_hl(self):
        tmp = (self.register.H << 8) + self.register.L
        self.register.E = self.memory.mem[tmp]

    def ld_a_hl(self):
        tmp = (self.register.H << 8) + self.register.L
        self.register.A = self.memory.mem[tmp]

    def and_b(self):
        self.register.A &= self.register.B
        if self.register.A == 0:
            self.register.flag["Z"] = 1
        else:
            self.register.flag["Z"] = 0
        self.register.flag["C"] = 0

    def and_c(self):
        self.register.A &= self.register.C
        if self.register.A == 0:
            self.register.flag["Z"] = 1
        else:
            self.register.flag["Z"] = 0
        self.register.flag["C"] = 0

    def di(self):
        self.register.flag["IME"] = 0

    def ei(self):
        self.register.flag["IME"] = 1

    def ld_hl_d8(self):
        address = (self.register.H << 8) + self.register.L
        self.memory.mem[address] = self.memory.mem[self.register.PC + 1]

    def ld_bc_d16(self):
        self.register.B = self.memory.mem[self.register.PC + 2]
        self.register.C = self.memory.mem[self.register.PC + 1]

    def dec_bc(self):
        tmp = (self.register.B << 8) + self.register.C
        tmp = (tmp - 1) & 0xffff
        self.register.B = tmp >> 8
        self.register.C = tmp & 0xff

    def or_b(self):
        self.register.A |= self.register.B
        if self.register.A == 0:
            self.register.flag["Z"] = 1
        else:
            self.register.flag["Z"] = 0
        self.register.flag["C"] = 0

    def or_c(self):
        self.register.A |= self.register.C
        if self.register.A == 0:
            self.register.flag["Z"] = 1
        else:
            self.register.flag["Z"] = 0
        self.register.flag["C"] = 0

    def cpl(self):
        # exit()
        self.register.A = ~self.register.A & 0xff

    def ld_b_a(self):
        self.register.B = self.register.A

    def xor_c(self):
        self.register.A ^= self.register.C
        self.register.flag["C"] = 0
        if self.register.A == 0:
            self.register.flag["Z"] = 1
        else:
            self.register.flag["Z"] = 0

    def ld_a_c(self):
        self.register.A = self.register.C


    def swap_a(self):
        (self.register.A >> 4) + ((self.register.A & 0xf) << 4)
        self.register.flag["C"] = 0
        if self.register.A == 0:
            self.register.flag["Z"] = 1
        else:
            self.register.flag["Z"] = 0

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

    def srl_a(self):
        self.register.flag["C"] = self.register.A & 0b00000001
        self.register.A >>= 1
        if self.register.A == 0:
            self.register.flag["Z"] = 1
        else:
            self.register.flag["Z"] = 0
    