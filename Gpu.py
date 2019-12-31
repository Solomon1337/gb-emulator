from Graphic import Graphic
import time


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
        self.tile_offset = 0
        self.memory = memory
        self.set_tile_offset()

        self.window = Graphic()
        # self.tile_window = Graphic(height=128)
        self.window.show()
        self.window.clear(0x474741)
        # self.tile_window.clear(0x474741)

        self.window.update()
        # self.tile_window.update()

        self.palette = {
            0: 0xffffff,
            1: 0xaaaaaa,
            2: 0x555555,
            3: 0x000000,
        }

        self.pixels = {0: [], 1: [], 2: [], 3: []}
        # self.tile_pixels = {0: [], 1: [], 2: [], 3: []}

    def step(self, cycles):
        if self.write_ly():
            self.render_full_background()
            self.flush_pixels()
            self.draw_window()
            self.window.update()

    def write_ly(self):
        self.line = (1 + self.line) % 145
        self.memory.mem[0xff44] = self.line
        return self.line == 0
    
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

    def set_tile_offset(self):
        if self.get_lcdc()["BGTILEMAPDSP"] == "0":
            self.tile_offset = 0x9800
        else:
            self.tile_offset = 0x9c00

    def flush_pixels(self):
        for color, positions in self.pixels.items():
            color = self.palette[color]
            self.window.put_pixels(positions, color)
        self.pixels = {0: [], 1: [], 2: [], 3: []}

    def draw_bg(self):
        pass
        # self.draw_all_tiles()
        # self.render_line(int(self.line))

    def convert_to_bits(self, tiles):
        tmp = []
        for i in range(0, len(tiles), 32):
            tmp.append(tiles[i:i+32])

    def draw_all_tiles(self):
        a = set(self.memory.mem[0x9800:0x9a00])
        for i in a:
            self.draw_tile(i)
        # print(a)

    def draw_tile(self, loc):
        tile = self.memory.mem[0x8000+(loc*16):0x8000+(loc*16) + 16]
        line = 0
        for i in range(0, 16, 2):
            a = tile[i]
            b = tile[i+1]
            colors = (
                ((a & 0b10000000) >> 7) | ((b & 0b10000000) >> 6),
                ((a & 0b01000000) >> 6) | ((b & 0b01000000) >> 5),
                ((a & 0b00100000) >> 5) | ((b & 0b00100000) >> 4),
                ((a & 0b00010000) >> 4) | ((b & 0b00010000) >> 3),
                ((a & 0b00001000) >> 3) | ((b & 0b00001000) >> 2),
                ((a & 0b00000100) >> 2) | ((b & 0b00000100) >> 1),
                ((a & 0b00000010) >> 1) | ((b & 0b00000010)     ),
                ((a & 0b00000001)     ) | ((b & 0b00000001) << 1))
            line += 1
            for n, color in enumerate(colors):
                self.pixels[color] += [n + loc*8, line]

    def render_line(self, line):
        # Read the tile table
        bitmap = 0x8000
        table = self.tile_offset

        # Draw one scanline from the tiles. We do this by calculating the tile
        # index and y-position

        # For the given y line, find which tile number it is when the screen is
        # divided up in 32x32 tiles that are 8x8 pixels each.
        ypos = line & 0b11111000
        index_offset = ypos << 2

        # Position whithin this tile
        yoff = line - ypos
        bitmap += yoff*2
        x = 0

        # The background consists of 32x32 tiles, so find the tile index.
        for index in range(32):
            tile = 16*self.memory.mem[table + index_offset + index]

            a = self.memory.mem[bitmap + tile]
            b = self.memory.mem[bitmap + tile + 1]

            colors = (
                ((a & 0b10000000) >> 7) | ((b & 0b10000000) >> 6),
                ((a & 0b01000000) >> 6) | ((b & 0b01000000) >> 5),
                ((a & 0b00100000) >> 5) | ((b & 0b00100000) >> 4),
                ((a & 0b00010000) >> 4) | ((b & 0b00010000) >> 3),
                ((a & 0b00001000) >> 3) | ((b & 0b00001000) >> 2),
                ((a & 0b00000100) >> 2) | ((b & 0b00000100) >> 1),
                ((a & 0b00000010) >> 1) | ((b & 0b00000010)     ),
                ((a & 0b00000001)     ) | ((b & 0b00000001) << 1))

            for n, color in enumerate(colors):
                self.pixels[color] += [x+n, line]
            x += 8

    def render_full_background(self):
        for line in range(32):
            for tile in range(32):
                loc = line * 32 + tile
                loc = self.memory.mem[0x9800 + line * 32 + tile]
                tiles = self.memory.mem[0x8000 + (loc * 16):0x8000 + (loc * 16) + 16]
                lines = line * 8
                for i in range(0, 16, 2):
                    a = tiles[i]
                    b = tiles[i+1]
                    colors = (
                        ((a & 0b10000000) >> 7) | ((b & 0b10000000) >> 6),
                        ((a & 0b01000000) >> 6) | ((b & 0b01000000) >> 5),
                        ((a & 0b00100000) >> 5) | ((b & 0b00100000) >> 4),
                        ((a & 0b00010000) >> 4) | ((b & 0b00010000) >> 3),
                        ((a & 0b00001000) >> 3) | ((b & 0b00001000) >> 2),
                        ((a & 0b00000100) >> 2) | ((b & 0b00000100) >> 1),
                        ((a & 0b00000010) >> 1) | ((b & 0b00000010)     ),
                        ((a & 0b00000001)     ) | ((b & 0b00000001) << 1))
                    lines += 1
                    for n, color in enumerate(colors):
                        self.pixels[color] += [n + tile*8, lines]

    def draw_window(self):
        self.set_scroll()
        self.window.box(self.scrollX, self.scrollY, self.scrollX+144, self.scrollY+160)