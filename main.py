import sys
from RomUtils import read_file
from Cpu import Cpu


def main():
    cartridge = read_file(sys.argv[1])
    print(len(cartridge))
    cpu = Cpu(cartridge)
    cpu.process()


if __name__ == "__main__":
    main()
