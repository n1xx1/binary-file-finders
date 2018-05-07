import re
import struct
import sys
from os import path

SCALERS = ["true", "\x00\x01\x00\x00", "typ1", "OTTO"]

def try_read_font(contents, header_start):
    pos = header_start
    stype, ntables, srange, esel, rshift = struct.unpack("!IHHHH", contents[pos:pos+12])
    pos += 12

    if ntables == 0 or rshift != ntables*16 - srange:
        return False, 0

    maxoff = 0
    maxlen = 0
    for i in range(ntables):
        tag, chk, off, length = struct.unpack("!4sIII", contents[pos:pos+16])
        pos += 16

        if tag != "head":
            chk1 = get_chunk_checksum(contents, header_start + off, length)
            if chk1 != chk:
                return False, 0
        
        if off > maxoff:
            maxoff = off
            maxlen = length
    
    return True, maxoff + maxlen

def get_chunk_checksum(contents, pos, length):
    chk = 0
    nlongs = (length + 3) / 4
    while nlongs > 0 and pos + 4 < len(contents):
        nlongs -= 1
        chk = (chk + struct.unpack("!I", contents[pos:pos+4])[0]) & 0xffffffff
        pos += 4
    return chk

def find_ttfs(contents, outdir):
    outfile = path.join(outdir, "{}.ttf")
    fileid = 0
    for scaler in SCALERS:
        for match in re.finditer(scaler, contents):
            header_start = match.start()
            res, length = try_read_font(contents, header_start)
            
            if res:
                fileid += 1
                filename = outfile.format(fileid)
                print "Writing {} [ {} : {} ]".format(filename, header_start, header_start+length)
                with open(filename, "wb") as f1:
                    f1.write(contents[header_start:header_start+length])

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print "usage: python ttffinder.py <file> <outdir>"
    
    infile = sys.argv[1]
    outdir = sys.argv[2]
    with open(infile, "rb") as f:
        find_ttfs(f.read(), outdir)
    