import re
import struct
import sys
from os import path

PNG_HEADER = "\x89PNG\r\n\x1a\n"

def find_pngs(contents, outdir):
    outfile = path.join(outdir, "{}.png")
    fileid = 0
    for match in re.finditer(PNG_HEADER, contents):
        fileid += 1

        header_start = match.start()
        chunks_start = match.end()
        
        pos = chunks_start
        typ = "NONE"
        while typ != "IEND":
            length, typ = struct.unpack("!I4s", contents[pos:pos+8])
            pos += 8
            data = contents[pos:pos+length]
            pos += length
            crc = struct.unpack("!4s", contents[pos:pos+4])
            pos += 4

        filename = outfile.format(fileid)
        print "Writing {} [ {} : {} ]".format(filename, header_start, pos)
        with open(filename, "wb") as f1:
            f1.write(contents[header_start:pos])

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print "usage: python pngfinder.py <file> <outdir>"
    
    infile = sys.argv[1]
    outdir = sys.argv[2]
    with open(infile, "rb") as f:
        find_pngs(f.read(), outdir)
    