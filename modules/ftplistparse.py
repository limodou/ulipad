#ftplistparse

import re
import common

re_ymd = [
        re.compile(r'(?P<ymd>^\d{1,4}.*?\d{1,2}.*?\d{1,2}.*?\s+)'),
        re.compile(r'(?P<mdt>^\d{1,2}.*?\d{1,2}.*?\s*\d{1,2}:\d{1,2}\s+)'),
        re.compile(r'(?P<smdt>^(?i)(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)\s*\d{1,2}\s*\d{1,2}:\d{1,2}\s+)'),
        re.compile(r'(?P<smdy>^(?i)(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)\s*\d{1,2}\s*\d{1,4}\s+)'),
        ]

def ftplistparse(lines, Unicode=False, callback=None):
    dirs = []
    files = []
    for line in lines:
        t = analyseline(line)
        if not t:
            continue
        dir, perm, size, filename = t
        if Unicode:
            filename = encodestring(filename)
        if filename in ('.', '..'):
            continue
        if dir:
            dirs.append((filename, '', perm, 0))
        else:
            if callback:
                if not callback(filename):
                    files.append((filename, size, perm, 1))
            else:
                files.append((filename, size, perm, 1))

    dirs.sort()
    files.sort()

    return dirs, files

months = ["jan", "feb", "mar", "apr", "may", "jun", "jul", "aug", "sep", "oct", "nov", "dec"]

def encodestring(s, encoding=None):
    if encoding:
        s = common.decode_string(s, encoding)
    return s

def getmonth(month):
    if len(month) == 3:
        month = month.lower()
        if month in months:
            return months.index(month) + 1
    return -1

def analyseline(line):
    trydir = 0
    tryfile = 0
    if line and line[0] in ('c', 'd', 'l', 'p', 's', '-'):
        if line[0] == 'd':
            trydir = 1

        state = 1
        i = 0
        for j in range(0, len(line)):
            ch = line[j]
            if ch == ' ' and line[j + 1] != ' ':
                s = line[i:j].strip()
                if state == 1:          #get perm
                    perm = s
                    state = 2
                elif state == 2:        #skip nlink
                    state = 3
                    if (j - i == 6) and (line[i] == 'f'):
                        state = 4
                elif state == 3:        #skip uid
                    state = 4
                elif state == 4:        #skip gid
                    state = 5
                elif state == 5:        #get size
                    size = int(s)
                    flag = False
                    filename = ''
                    text = line[j+1:].strip()
                    for r in re_ymd:
                        result = r.search(text)
                        if result:
                            flag = True
                            filename = text[result.end():]
                            break
                    state = 6
                elif state == 6:
                    continue

                i = j + 1
                while i < len(line) and line[i] == ' ':
                    i = i + 1

        if state != 6:
            return False

        if line[0] == 'l':
            pos = filename.find('->')
            if pos > -1:
                filename = filename[:pos-1]

        return trydir, perm, size, filename

if __name__ == '__main__':
    lists = [
            'drwxr-xr-x   18 179      666          4096 Oct 10 15:38 Python-2.3.4',
            '-rw-r--r--    1 501      501       8502738 Oct 10 15:31 Python-2.3.4.tgz',
            'srwxrwxr-x    1 500      500             0 Sep 15 22:31 MQSeries.1147',
            "-rw-r--r--   1 root     other        531 Jan 29 03:26 README",
            "dr-xr-xr-x   2 root     other        512 Apr  8 1994  etc",
            "dr-xr-xr-x   2 root     other        512 Apr  8  1994 lib",
            "lrwxrwxrwx   1 root     other          7 Jan 25 00:17 bin -> usr/bin",
            "----------   1 owner    group         1803128 Jul 10 10:18 ls-lR.Z",
            "d---------   1 owner    group               0 May  9 19:45 Softlib",
            "-rwxrwxrwx   1 noone    nogroup      322 Aug 19  1996 message.ftp",
            ]
    dirs, files = ftplistparse(lists)
    print 'dirs-------------------'
    for v in dirs:
        print v
    print 'files------------------'
    for v in files:
        print v
