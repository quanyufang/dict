import sys
from array import array
import socket
import struct
from os import stat

langdao_ec_gb_special={"con":"","int":"","pro":"","com":"","tra":"","par":"","sta":"","dis":"","per":"","ant":"","pre":"","car":"","ele":"","met":"","str":"","tri":"","pol":"","for":"","col":"","pri":"","sub":"","res":"","cor":"","ind":"","mul":"","bac":"","cha":"","hyp":"","be":"","non":"","the":"","rec":"","aut":"","ext":"","acc":"","pla":"","sup":"","ste":"","hyd":"","art":"","rad":"","spe":"","mon":"","gra":"","mic":"","cal":"","ins":"","man":"","pho":"","uni":"","pos":"","iso":"","fre":"","ope":"","gen":"","act":"","all":"","in":"","che":"","sel":"","mar":"","inc":"","dec":"","exp":"","app":"","lin":"","imp":"","ret":"","sec":"","lig":"","ben":"","hem":"","qua":"","hea":"","ove":"","chr":"","spi":"","sto":"","cap":"","hig":"","cat":"","chl":"","bro":"","mag":"","lea":"","dia":"","air":"","inf":"","bas":"","cou":"","cas":"","cho":"","cer":"","thr":"","syn":"","ven":"","sin":"","thi":"","sal":"","gas":"","fin":"","rea":"","reg":"","inv":"","ter":"","mus":"","eth":"","des":"","ser":"","sem":"","ass":"","cen":"","end":"","phe":"","clo":"","sch":"","und":"","flo":"","sod":"","cro":"","to":"","sul":"","liq":"","min":"","rel":"","bar":"","neu":"","dir":"","mat":"","ace":"","ver":"","ang":"","epi":"","sho":"","bra":"","chi":"","out":"","gro":"","dou":"","ana":"","pse":"","tel":"","rep":"","fun":"","wor":"","cla":"","bla":"","abs":"","pot":"","exc":"","def":"","mac":"","tet":"","mer":"","dep":"","hav":"","equ":"","bal":"","flu":"","nat":"","pul":"","pen":"","fla":"","off":"","ref":"","fil":"","cur":"","cri":"","fac":"","sol":"","can":"","low":"","har":"","mak":"","mal":"","aci":"","bri":"","opt":"","cos":"","ent":"","dip":"","rat":"","pha":"","bur":"","spa":"","med":"","blo":"","dif":"","nor":"","sca":"","bre":"","del":"","hom":"","oil":"","mor":"","tak":"","red":"","wat":"","sim":"","cir":"","cre":"","rev":"","not":"","lon":"","lan":"","loc":"","den":"","mas":"","mes":"","sur":"","cyc":"","fir":"","sha":"","mai":"","cry":"","pyr":"","sil":"","tub":"","fra":"","cel":"","mol":"","nit":"","vol":"","fer":"","mod":"","cle":"","qui":"","sym":"","ban":"","wit":"","der":"","dat":"","ple":"","lat":"","cop":"","but":"","hol":"","her":"","het":"","spo":"","cra":"","law":"","rig":"","val":"","leg":"","bil":"","nuc":"","tim":"","phy":"","pan":"","sen":"","add":"","por":"","hal":"","tur":"","amm":"","hor":"","put":"","pat":"","pur":"","han":"","alu":"","net":"","ful":"","lim":"","ner":"","bea":"","shi":"","lab":"","fas":"","alk":"","men":"","gly":"","mec":"","lym":"","mil":"","amp":"","lit":"","ram":"","mem":"","sti":"","mis":"","dig":"","hex":"","coa":"","gal":"","pas":"","die":"","fib":"","tem":"","alt":"","pac":"","glo":"","num":"","eff":"","ost":"","on":"","ten":"","gla":"","pal":""}
oxford_gb_special={"con":"","dis":"","the":"","pro":"","int":"","com":"","pre":"","per":"","tra":"","sta":""}
if __name__ == '__main__':
    if len(sys.argv) != 4:
        print('Usage:')
        print('\tpython ', sys.argv[0], ' indexFilename dictName idxidxOutputFileName')
        exit(-1)
    
    idxFilename  = sys.argv[1]
    dictName     = sys.argv[2]
    idxidxOutputFileName = sys.argv[3]
    
    special = {}
    if dictName == 'oxford-gb':
        special = oxford_gb_special
    elif dictName == 'langdao-ec-gb':
        special = langdao_ec_gb_special
    
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

            (leading1, leading2, leading3, leading4) = ('', '', '', '')
            leading1 = key[0:1].lower()
            if len(key) >= 2:
                leading2 = key[1:2].lower()
            if len(key) >= 3:
                leading3 = key[2:3].lower()

            
            
            leading = leading1 + leading2 + leading3
            if special.has_key(leading) and len(key)>=4:
                leading4 = key[3:4].lower()
                leading += leading4

            #leading = leading.strip()
            if current == leading:#in section
                c = ret[leading]
                c['end'] = f.tell() - 1
            elif current != leading and current != '':#section change and not first time
                c = ret[current]
                c['end'] = f.tell() - len(key) -  9
                ret[current] = c
                c = {}
                c['begin'] = f.tell() -len(key) - 9
                c['end'] = f.tell() - 1
                ret[leading] = c
                current = leading
            else :#section change and is first time
                c = {}
                c['begin'] = f.tell() -len(key) - 9
                c['end'] = f.tell() - 1
                ret[leading]= c
                current = leading

    with open(idxidxOutputFileName, 'wb') as idxidxf:
        for i in (sorted(ret.iteritems())):
            #print (i[1]['end'] - i[1]['begin']), i[0]
            key = i[0]
            offset = i[1]['begin']
            length = i[1]['end'] - i[1]['begin']
            print(key, offset, length)
            idxidxf.write("{0}{1}{2}{3}".format(key, '\0', struct.pack('!I',offset), struct.pack('!I',length)))
                           
