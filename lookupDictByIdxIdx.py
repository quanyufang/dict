import sys
from array import array
import socket
from os import stat

def loadIdxIdxFile(idxidxFileName):
    statResult = stat(idxidxFileName)
    size = statResult[6]
    secidx = {}
    with open(idxidxFileName) as f:
        while f.tell() <= size - 1:
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
            #print key, offset, length
            c = {}
            c['offset'] = offset
            c['length'] = length
            secidx[key] = c
    return secidx
            

if __name__ == '__main__':
    if len(sys.argv) != 5:
        print('Usage:')
        print('\tpython ', sys.argv[0], ' dictFilename indexFilename idxidxFilename word')
        exit(-1)
    
    dictFilename = sys.argv[1]
    idxFilename  = sys.argv[2]
    idxidxFileName = sys.argv[3]
    word = sys.argv[4]

    secidx = loadIdxIdxFile(idxidxFileName)
    #print secidx
    #sys.exit(0)
    if len(secidx) == 0:
        print('load idxidx fail')
        sys.exit(-1)
        
    section = ''
    info = {}

    idxidxWord = word.lower()
    print('idxidxWord=', idxidxWord)
    if len(idxidxWord) >= 4:
        section = idxidxWord[0:4]
    else:
        section = idxidxWord

    print('section =', section)
    #print secidx.keys()
    if secidx.has_key(section):
        print('section', section, ' find info')
        info = secidx[section]
    else:
        print(section, ' not find info , cont.')
        if len(section) <= 1:
            print('can not find info')
            sys.exit(-1)
        seclen = len(section) - 1
        while seclen > 0 :
            tmpsec = section[0:seclen]
            print('tmpsec=', tmpsec)
            if secidx.has_key(tmpsec):
                print('find idxidx')
                info = secidx[tmpsec]
                break
            else:
                seclen = seclen - 1
    
    if len(info) == 0:
        print('can not find idxidx')
        sys.exit(-1)
    
    statResult = stat(idxFilename)
    idxFilesize = statResult[6]

    print(section, info)
    if info['offset'] + info['length'] > idxFilesize:
        print('wrong sec idx info')
        sys.exit(-1)
    
    with open(idxFilename, 'rb') as f:
        f.seek(info['offset'])
        while f.tell() <= info['offset'] + info['length']:
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
            print(key, offset, length)
            if key == word:
                with open(dictFilename , 'rb') as dictFile:
                    dictFile.seek(offset)
                    content = dictFile.read(length)
                    print(content)
                    sys.exit(0)
            

            
