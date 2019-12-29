from Graphic import Graphic
import time
import numpy as np


class Gpu():
    def __init__(self, memory):
        self.mode = 0
        # Mode 0 = HBlank (VRAM accessible)
        # Mode 1 = VBlank (VRAM accessible)
        # Mode 2 = OAM used (OAM not accessible)
        # Mode 3 = OAM & VRAM used (OAM + VRAM not accessible)

        # Representation of modes on full cycle:
        # One full refresh should in theory take ~16.6 ms
        # because 60hz * 16.6ms = 1sec
        #
        #  ____ 144 of these lineupdates
        # |    |
        # 000233000233000233000233000233000233...111111111111
        # |_|     Takes 48.6 uS                  |          |
        #    |    Takes 19   uS                  |          |
        #     ||  Takes 41   uS                  |          |
        # |____|  Takes 109  uS        Takes 1ms_|__________|

        # A full screen refresh takes 70224 cycles. From these there are
        # 4560 Cycles reserved for VBlank(1). The remaining 65664 Cycles are
        # used for 144 line updates, each taking 456 cycles to complete.
        # Of these 456 cycles
        # Mode 0 takes 201-207 cycles
        # Mode 2 takes   77-83 cycles
        # Mode 3 takes 169-175 cycles
        # The vague cycle duration is because of instructions taking multiple cycles (1-6)
        # |  lines  |  VBlank
        # (144 * 456) + 4560 = 70224

        self.scrollX = 0
        self.scrollY = 0

        self.line = 0
        self.lcdc = 0
        self.cycles = 0
        self.seconds = 0
        self.memory = memory

        self.window = Graphic()
        self.tile_window = Graphic(height=128)
        self.window.show()
        self.window.clear(0x474741)
        self.tile_window.clear(0x474741)

        self.window.update()
        self.tile_window.update()

        self.palette = {
            0: 0xffffff,
            1: 0xaaaaaa,
            2: 0x555555,
            3: 0x000000,
        }

        self.pixels = {0: [], 1: [], 2: [], 3: []}
        self.tile_pixels = {0: [], 1: [], 2: [], 3: []}

    def step(self, cycles):
        self.cycles += (cycles / 4)
        if self.cycles > 70224:
            self.draw_bg()
            self.cycles -= 70224
            self.line = 0
            self.seconds += 1
            if self.cycles == 60:
                print("FULL SECOND!!!")

        currline = self.cycles // 456
        if currline <= 144:
            if currline != self.line:
                self.line = currline
                self.write_ly()
            mod = self.cycles % 456
            if mod < 207:
                self.mode = 0
            elif mod < 207 + 77:
                self.mode = 2
            else:
                self.mode = 3
        else:
            self.mode = 1

    def write_ly(self):
        self.memory.mem[0xff44] = self.line
    
    def update_stat(self):
        self.memory.mem[0xff41] = self.mode

    def get_lcdc(self):
        tmp = format(self.memory.mem[0xff40], "#010b")
        return {
            "LCD": tmp[2],
            "TILE": tmp[3],
            "DSP": tmp[4],
            "BGTILEDATA": tmp[5],
            "BGTILEMAPDSP": tmp[6],
            "SIZE": tmp[7],
            "SPRITE": tmp[8],
            "BGWINDOW": tmp[9],
        }

    def get_window_x(self):
        return self.memory.mem[0xff4b]

    def get_window_y(self):
        return self.memory.mem[0xff4a]

    def set_scroll(self):
        self.scrollX = self.memory.mem[0xff43]
        self.scrollY = self.memory.mem[0xff42]

    def draw_bg(self):
        lcdc = self.get_lcdc()
        if lcdc["BGWINDOW"] == "0": return
        if lcdc["BGTILEMAPDSP"] == "0":
            tiles = self.memory.mem[0x9800:0x9c00]
        else:
            tiles = self.memory.mem[0x9c00:0xa000]
        # tilemap = self.memory.get_bg_tile_map()
        tilemap = self.convert_to_bits(tiles)

    def convert_to_bits(self, tiles):
        tmp = []
        # alltiles = [list(tiles[n:n+32]) for n in range(0, len(tiles), 32)]
        # tiles = [self.memory.mem[0x8000 + (a * 16):0x8000 + (a * 16) + 16] for a in tiles]
        # test = [tiles[n:n+32] for n in range(0, len(tiles), 32)]
        # t = time.time()
        # print(tiles)
        # t2 = time.time()
        # print(t, t2)
        # print(test)
        # a = [self.memory.mem[0x8000 + (a * 16):0x8000 + (a * 16) + 16] for a in test]
        # trans = [self.memory.mem[0x8000 + (a * 16):0x8000 + (a * 16) + 16] for a in [tiles[n:n+32] for n in range(0, len(tiles), 32)]]
        # print(trans)
        # for line in alltiles:
        #     tmp.append(self.convert_tile_to_color(line))
        return tmp

    def convert_tile_to_color(self, line):
        tmpline = []
        for tile in line:
            # if tile == 0: continue
            # print("CIRREMT: ", tile)
            begin = 0x8000 + (16 * tile)
            tmp = []
            a = self.memory.mem[begin:begin+16]
            # print(a)
            for i in range(8):
                b = format(a[i], '#010b')[2:]
                c = format(a[i+1], '#010b')[2:]
                for cnt, bit in enumerate(b):
                    if bit == c[cnt]:
                        tmp.append(255)
                    elif bit == '1' and c[cnt] == '0':
                        tmp.append(70)
                    elif bit == '0' and c[cnt] == '1':
                        tmp.append(160)
            # print(tmp)
            # tmp = [format(a, '#010b')[2:] for a in self.memory.mem[begin:begin+16]]
            # print(tmp)
            tmpline.append(tmp)
        # print("", len(tmpline), " : ", len(tmpline[0]))
        return tmpline