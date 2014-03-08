#!/usr/bin/env python
#coding=utf-8

# /opt/ulipad/modules/PCInfo.py

def memInfo():
    ram = open("/proc/meminfo")
    ramlines = ram.readlines()

    ramInfo = {'cachedRam': 0,
                'freeRam': 0,
                'totalRam': 0
                }
   
    for element in ramlines:
        if element.split(" ")[0] == "MemTotal:":
            ramInfo['totalRam'] = int(element.split(" ")[-2])/1024
        elif element.split(" ")[0] == "MemFree:":
            ramInfo['freeRam'] = int(element.split(" ")[-2])/1024
        elif element.split(" ")[0] == "Cached:":
            ramInfo['cachedRam'] = int(element.split(" ")[-2])/1024
        else:
            pass

    ram.close()
   
    return ramInfo
