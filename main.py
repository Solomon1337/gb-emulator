import sys
from RomUtils import read_file
import Rom


def main():
    romfile = sys.argv[1]
    bindata = read_file(romfile)
    rom = Rom.Rom(bindata)
    print(rom.get_title())


if __name__ == "__main__":
    main()
