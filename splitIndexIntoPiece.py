import sys
from array import array
import socket
from os import stat


if __name__ == '__main__':
    if len(sys.argv) != 4:
        print('Usage:')
        print('\tpython ', sys.argv[0], ' indexFilename dictName outputDictionary')
        exit(-1)
    
    idxFilename      = sys.argv[1]
    dictName         = sys.argv[2]
    outputDictionary = sys.argv[3]
    
    statResult = stat(idxFilename)
    idxFilesize = statResult[6]
    #print 'idxFilesize=%d' %(idxFilesize)
    #sys.exit(0)
    with open(idxFilename, 'rb') as f:

        while f.tell() <=  idxFilesize - 1:
            byte = f.read(1)
            key = byte
            while byte != '\0':
                byte = f.read(1)
                if byte != '\0':
                    key += byte
            key += '\0'
            re = array('L')
            re.fromfile(f, 2)
            
            leading = key[0:1]
            if leading.islower() :
                leading1 = key[1:2]
                if leading1.isalpha():
                    leading += leading1
            
            outputFileName = outputDictionary+'/dict_'+dictName+'_'+leading+'.idx'
            print(outputFileName)
            with open(outputFileName, 'ab', 10240) as idxFile:
                idxFile.write(key)
                re.tofile(idxFile)
                idxFile.close()
            
            

