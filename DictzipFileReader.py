from array import array
if __name__ == '__main__':
    import sys
class DictzipFileReader:
    # For gzip-compatible header, as defined in RFC 1952

    #Magic for GZIP
    GZ_MAGIC1 = 0x1f
    GZ_MAGIC2 = 0x8b

    # FLaGs (bitmapped)
    GZ_FTEXT =     0x01  # Set for ASCII text
    GZ_FHCRC =     0x02  # Header CRC16
    GZ_FEXTRA =    0x04  # Optional field (random access index)
    GZ_FNAME =     0x08  # Original name
    GZ_COMMENT =   0x10  # Zero-terminated, human-readable comment
    GZ_MAX =          2  # Maximum compression
    GZ_FAST =         4  # Fasted compression


    GZ_OS_FAT =       0  # FAT filesystem (MS-DOS, OS/2, NT/Win32)
    GZ_OS_AMIGA =     1  # Amiga
    GZ_OS_VMS =       2  # VMS (or OpenVMS)
    GZ_OS_UNIX =      3      # Unix
    GZ_OS_VMCMS =     4      # VM/CMS
    GZ_OS_ATARI =     5      # Atari TOS
    GZ_OS_HPFS =      6      # HPFS filesystem (OS/2, NT)
    GZ_OS_MAC =       7      # Macintosh
    GZ_OS_Z =         8      # Z-System
    GZ_OS_CPM =       9      # CP/M
    GZ_OS_TOPS20 =   10      # TOPS-20
    GZ_OS_NTFS =     11      # NTFS filesystem (NT)
    GZ_OS_QDOS =     12      # QDOS
    GZ_OS_ACORN =    13      # Acorn RISCOS
    GZ_OS_UNKNOWN = 255      # unknown

    GZ_RND_S1 =      'R' # First magic for random access format
    GZ_RND_S2 =      'A' # Second magic for random access format

    GZ_ID1 =          0  # GZ_MAGIC1
    GZ_ID2 =          1  # GZ_MAGIC2
    GZ_CM =           2  # Compression Method (Z_DEFALTED)
    GZ_FLG =          3  # FLaGs (see above)
    GZ_MTIME =        4  # Modification TIME
    GZ_XFL =          8  # eXtra FLags (GZ_MAX or GZ_FAST)
    GZ_OS =           9  # Operating System
    GZ_XLEN =        10  # eXtra LENgth (16bit)
    GZ_FEXTRA_START = 12  # Start of extra fields
    GZ_SI1 =         12  # Subfield ID1
    GZ_SI2 =         13      # Subfield ID2
    GZ_SUBLEN =      14  # Subfield length (16bit)
    GZ_VERSION =     16      # Version for subfield format
    GZ_CHUNKLEN =    18  # Chunk length (16bit)
    GZ_CHUNKCNT =    20  # Number of chunks (16bit)
    GZ_RNDDATA =     22  # Random access data (16bit)

    
    def __init__(self, filename):
        self.pos = 0
        self.file = open(filename)
        self.read_header()

    def pos_internal(self):
        return self.file.tell()

    def set_pos_internal(self, pos):
        self.file.seek(pos)

    def read_header(self):
        self.header_length = DictzipFileReader.GZ_XLEN - 1

        id1 = self.read_byte_internal()
        id2 = self.read_byte_internal()

        #print '%#X\t%#X' % (id1, id2)
        if id1 != DictzipFileReader.GZ_MAGIC1 or id2 != DictzipFileReader.GZ_MAGIC2:
            raise Exception('Not gzip')

        self.method = self.read_byte_internal()
        self.flags  = self.read_byte_internal()
        self.mtime  = self.read_le32()
        self.extra_flags = self.read_byte_internal()
        self.os = self.read_byte_internal()

        if (self.flags & DictzipFileReader.GZ_FEXTRA) != 0:
            extra_length = self.read_le16()
            self.header_length += (extra_length + 2)
            print('now header_length=%d' % self.header_length)
            si1 = self.read_char_internal()
            si2 = self.read_char_internal()

            if (si1 != DictzipFileReader.GZ_RND_S1) or (si2 != DictzipFileReader.GZ_RND_S2):
                print('%c%c' % (si1,si2))
                raise Exception('Not a dictzip file')
            else:
                sub_length   = self.read_le16()
                self.version = self.read_le16()

                if self.version != 1:
                    raise Exception('dzip header version %d not supported' % self.version)

                self.chunk_length = self.read_le16()
                self.chunk_count  = self.read_le16()

                print('chunk_length=%d,chunk_count=%d' % (self.chunk_length, self.chunk_count))
                if self.chunk_count <= 0:
                    raise Exception('No chunks found')

                self.chunks = []
                for i in range(self.chunk_count):
                    self.chunks.append(self.read_le16())

        else:
            raise Exception('This file is a plain gz file!')

        if (self.flags & DictzipFileReader.GZ_FNAME) != 0:
            self.orig_filename = self.read_null_terminated_string()
            print('orig_filename=%s, header_length=%d' % (self.orig_filename, self.header_length))
            self.header_length += len(self.orig_filename) + 1
        else:
            self.orig_filename = ''

        if (self.flags & DictzipFileReader.GZ_COMMENT) != 0:
            self.comment = self.read_null_terminated_string()
            self.header_length += len(self.comment) + 1
        else:
            self.comment = ''

        if(self.flags & DictzipFileReader.GZ_FHCRC) != 0:
            self.read_byte_internal()
            self.read_byte_internal()
            self.header_length += 2

        if self.pos_internal() != self.header_length + 1:
            raise Exception('File position (%d) != header length + 1 (%d)' %
                            (self.pos_internal(), self.header_length))
        
        
        
    def read_byte_internal(self):
        b = array('B')
        b.fromfile(self.file, 1)
        return b.tolist()[0]

    def read_char_internal(self):
        b = array('c')
        b.fromfile(self.file, 1)
        return b.tolist()[0]

    def read_le16(self):
        val = self.read_byte_internal()
        val |= self.read_byte_internal() << 8
        return val
        
    def read_le32(self):
        val = self.read_byte_internal()
        val |= self.read_byte_internal() << 8
        val |= self.read_byte_internal() << 16
        val |= self.read_byte_internal() << 24
        return val

    def read_null_terminated_string(self):
        retstr = ''
        while True:
            c = self.read_byte_internal()
            if c == 0: # or self.file.eof (impl later)
                break
            retstr += str(c)
        return retstr

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print('Usage:')
        print('\tpython ', sys.argv[0], ' dictzipFilename')
        exit(-1)

    filename = sys.argv[1]

    reader = DictzipFileReader(filename)
