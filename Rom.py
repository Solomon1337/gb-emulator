
class Rom():
    def __init__(self, binarydata):
        self.binarydata = binarydata

        self.rst00 = binarydata[0x0000]
        self.rst08 = binarydata[0x0008]
        self.rst10 = binarydata[0x0010]
        self.rst18 = binarydata[0x0018]
        self.rst20 = binarydata[0x0020]
        self.rst28 = binarydata[0x0028]
        self.rst30 = binarydata[0x0030]
        self.rst38 = binarydata[0x0038]

        self.vert_blank_int = binarydata[0x0040]
        self.lcdc_start_int = binarydata[0x0048]
        self.timer_overflow_int = binarydata[0x0050]
        self.serial_transfer_cmplt_int = binarydata[0x0058]
        self.htl_p10_int = binarydata[0x0060]

        self.begin_exec = binarydata[0x0100:0x0103]
        self.scroll_graphic = binarydata[0x0104: 0x0133]
        self.title = binarydata[0x0134:0x0142]
        self.color_gb = binarydata[0x0143]
        self.high_license_code = binarydata[0x0144]
        self.low_license_code = binarydata[0x0145]
        self.gb_sgb = binarydata[0x0146]
        self.cartridge_type = binarydata[0x0147]
        self.rom_size = binarydata[0x0148]
        self.ram_size = binarydata[0x0149]
        self.dest_code = binarydata[0x014a]
        self.license_code = binarydata[0x014b]
        self.mask_rom_version = binarydata[0x014c]
        self.complement_check = binarydata[0x014d]
        self.checksum = binarydata[0x014e:0x014f]

    def get_title(self):
        return ''.join([chr(f) for f in self.title])
