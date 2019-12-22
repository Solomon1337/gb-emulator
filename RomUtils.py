
def read_file(file):
    bindata = []
    f = open(file, 'rb')
    singlebyte = f.read(1)
    while singlebyte:
        bindata.append(ord(singlebyte))
        singlebyte = f.read(1)
    return bindata
