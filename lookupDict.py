import sys
from array import array
import socket
from os import stat


if __name__ == '__main__':
    if len(sys.argv) != 4:
        print('Usage:')
        print('\tpython ', sys.argv[0], ' dictFilename indexFilename outputXmlFilename')
        exit(-1)
    
    idxFilename  = sys.argv[2]
    dictFilename = sys.argv[1]
    outputXmlFilename = sys.argv[3]
    
    statResult = stat(idxFilename)
    idxFilesize = statResult[6]
    with open(idxFilename, 'rb') as f:

        resultXml = '<xml version="1.0" encoding="utf-8">\n'
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
            content = ''
            with open(dictFilename , 'rb') as dictFile:
                dictFile.seek(offset)
                content = dictFile.read(length)
            resultXml += '\t<item>\n'
            resultXml += '\t\t<key>' + key +'</key>\n'
            resultXml += '\t\t<content>' + content + '\n\t\t</content>\n'
            resultXml += '\t</item>\n'
        resultXml += '</xml>\n'
        with open(outputXmlFilename, 'w') as xmlFile:
            xmlFile.write(resultXml)
            

            
