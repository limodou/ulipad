# PyM3u.py
import os
import re
from modules import common
__doc__='Pym3u Class'

class LoadMusicListException(Exception):
    message = tr("Can't load the music list file")
class SaveMusicListException(Exception):
    message = tr("Can't save the music list file")
class M3u:
    def __init__(self,filepath=None):
        self.filepath=filepath
        self.data=[]
        self.ismodify=False
        self.template='#EXTINF:%s,%s\n%s\n'
        
    def Load(self,filepath=None):
        if filepath:
            self.filepath=filepath
        if not self.filepath or not os.path.isfile(self.filepath) or not self.filepath.lower().endswith('.m3u'):
            raise LoadMusicListException()
        lines=open(self.filepath,'r').readlines()
        if lines[0].upper().strip()!='#EXTM3U':
            raise LoadMusicListException()
        p=re.compile('#EXTINF:(?P<time>\d*?),(?P<titleauthor>.*?)$')
        for i in range(1,len(lines),2):
            if not lines[i].startswith('#EXTINF'):
                continue
            result=p.search(lines[i].strip())
            path = common.decode_string(lines[i+1].strip(), common.defaultfilesystemencoding)
            title = common.decode_string(result.group('titleauthor'), common.defaultfilesystemencoding)
            self.data.append({'Author-Title':title,'Time':result.group('time'),'Path':path})
        return True
    
    def SaveToFile(self,filepath=None):
        if filepath:
            self.filepath=filepath
        fout=None
        try:
            fout=open(self.filepath,'w')
        except:
            if fout:
                fout.close()
            raise SaveMusicListException()
        fout.write('#EXTM3U\n')
        for data in self.data:
            title = common.encode_string(data['Author-Title'], common.defaultfilesystemencoding)
            path = common.encode_string(data['Path'], common.defaultfilesystemencoding)
            fout.write(self.template%(data['Time'], title, path))
        return True
    
    def isExists(self, filename):
        for d in self.data:
            if d['Path'] == filename:
                return True
        return False
    
    def Append(self,record):
        if not isinstance(record,dict):
            return False
        self.data.append(record)
        self.ismodify=True
        
    def Insert(self,record,index=0):
        if not isinstance(record,dict):
            return False
        self.data.insert(index,record)
        self.ismodify=True
    def Delete(self,index=0):
        del self.data[index]
        self.ismodify=True
    def GetFilePath(self):
        return self.filepath
    def IsModify(self):
        return self.ismodify
    def __getitem__(self,key):
        if key=='filepath':
            return self.filepath
        if key=='ismodify':
            return self.ismodify
        return self.data[key]
    def ClearAll(self):
        self.filepath=None
        self.ismodify=False
        del self.data[:]
def test():
    mym3u=M3u('c:\\1.m3u')
    mym3u.Load()
#    for i in mym3u.data:
#        for k,v in i.items():
#            print k,':',v,'  ',
#        print ''
    mym3u.SaveToFile('c:\\2.m3u')
if __name__=='__main__':
    test()
