from modules.Debug import error
from modules import common

def stripnulls(data):
    "strip whitespace and nulls"
    return data.replace("\00", "").strip()

class MP3FileInfo:
    "store ID3v1.0 MP3 tags"
    tagDataMap = {"title"   : (  3,  33, stripnulls),
                  "author"  : ( 33,  63, stripnulls),
                  "album"   : ( 63,  93, stripnulls),
                  "year"    : ( 93,  97, stripnulls),
                  "comment" : ( 97, 126, stripnulls),
                  "genre"   : (127, 128, ord)}
    def __init__(self,filepath=None):
        self.filepath=filepath
        self.info={}
        self.ishasinfo=False

    def parse(self, filepath=None):
        "parse ID3v1.0 tags from MP3 file"
        if filepath:
            self.filepath=filepath
        self.filepath=common.decode_string(self.filepath, common.defaultfilesystemencoding)
        self.info.clear()
        try:
            fsock = open(self.filepath, "rb", 0)
            try:
                fsock.seek(-128, 2)
                tagdata = fsock.read(128)
            finally:
                fsock.close()
            if tagdata[:3] == "TAG":
                for tag, (start, end, parseFunc) in self.tagDataMap.items():
                    self.info[tag] = parseFunc(tagdata[start:end])
                self.ishasinfo=True
            else:
                self.info['title']=self.filepath
                self.info['author']=''
        except IOError:
            error.traceback()
            return False
        return True

    def __setitem__(self, key, item):
        if key == "filepath" and item:
            self.filepath=item
        else:
            self.info[key]=item

    def __getitem__(self,key):
        if key=='filepath':
            return self.filepath
        return self.info[key]
