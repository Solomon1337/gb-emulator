
class Gpu():
    def __init__(self, memory):
        self.mode = 0
        # Mode 0 = HBlank (VRAM accessible)
        # Mode 1 = VBlank (VRAM accessible)
        # Mode 2 = OAM used (OAM not accessible)
        # Mode 3 = OAM & VRAM used (OAM + VRAM not accessible)

        # Representation of modes on full cycle:
        # One full refresh should in theory take 16.6 ms
        # because 60hz * 16.6ms * 1sec
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

        self.line = 0
        self.lcdc = 0x0
        self.cycles = 0
        self.seconds = 0
        self.memory = memory

    def step(self, cycles):
        self.cycles += (cycles / 4)
        if self.cycles > 70224:
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
