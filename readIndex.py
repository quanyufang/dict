import sys
from array import array
import socket
from os import stat


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print('Usage:')
        print('\tpython ', sys.argv[0], ' indexFilename')
        exit(-1)
    
    idxFilename  = sys.argv[1]
    
    statResult = stat(idxFilename)
    idxFilesize = statResult[6]

    ret = {}
    with open(idxFilename, 'rb') as f:

        current = ''
        while f.tell() <=  idxFilesize - 1:
            byte = f.read(1)
            key = byte
            while byte != '\0':
                byte = f.read(1)
                if byte != '\0':
                    key += byte

            re = array('L')
            re.fromfile(f, 2)
            offset = socket.ntohl(re.tolist()[0])
            length = socket.ntohl(re.tolist()[1])

            (leading1, leading2, leading3) = ('', '', '')
            leading1 = key[0:1].lower()
            #if not leading1.isalpha():
            #    continue
            if len(key) > 2:
                leading2 = key[1:2].lower()
            if len(key) > 3:
                leading3 = key[2:3].lower()

            leading = leading1 + leading2 + leading3
            #print 'leading=', leading, 'current=', current
            if current == leading:#in section
                continue
            elif current != leading and current != '':#section change and not first time

                c = ret[current]
                c['end'] = f.tell() - len(key) -  10
                ret[current] = c
                c = {}
                c['begin'] = f.tell() -len(key) - 9
                ret[leading] = c
                #print ret
                current = leading
            else :#section change and is first time
                current = leading
                c = {}
                c['begin'] = f.tell() -len(key) - 9
                ret[leading]= c
                #print ret

    for i in (sorted(ret.iteritems())):
        print(i[0], (i[1]['end'] - i[1]['begin']))
        #print i
