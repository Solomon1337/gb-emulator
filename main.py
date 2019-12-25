import sys
from RomUtils import read_file
from Memory import Memory
from Cpu import Cpu


def main():
    #romfile = sys.argv[1]
    # read_file(romfile)
    # rom = Rom.Rom(bindata)
    #print(rom.get_title())

    bindata = Memory().bios
    cpu = Cpu()
    a = cpu.codes[0x1a].function()
    print(a)


if __name__ == "__main__":
    main()
