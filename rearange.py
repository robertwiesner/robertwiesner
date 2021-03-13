#!/usr/bin/env python3

import sys
import math
from pcbnew import *

filename=sys.argv[1]

pcb = LoadBoard(filename)
small_comp = []
large_comp = []
idx = 0

srcList = ["J7", "R7", "Q7"]
dstList = [["J6" ,"R6", "Q6"], ["J9", "R9", "Q9"]]

srcMod = dict();
dstMod = [dict(), dict()];
dstPos = [[0,0], [0,0]]

for module in pcb.GetModules():
    name = module.GetReference()
    if name[0:2] in srcList:
        srcMod[name[0] + name[2:]] = module
    for i in range(len(dstList)):
        if name[0:2] in dstList[i]:
            dstMod[i][name[0] + name[2:]] = module

s = ""
d = ["", ""]
for i in srcMod:
    s += i + " "
for i in range(len(dstList)):
    for j in dstMod[i]:
        d[i] += j + " ";

print(len(srcMod), s);
print(len(dstMod[0]), d[0])
print(len(dstMod[1]), d[1])


idxList = []
for sm in srcMod:
    idxList.append(sm);


# adjust orientation
for dstIdx in range(len(dstMod)):
    for idx in idxList:
        dstMod[dstIdx][idx].SetOrientation(srcMod[idx].GetOrientation());

#adjust location based on the 1st object
idx0 = idxList[0];
startSrcPos = srcMod[idx0].GetPosition();
for dstIdx in range(len(dstMod)):
    startDstPos = dstMod[dstIdx][idx0].GetPosition();

    for i in range(1,len(idxList)):
        idx = idxList[i]
        # adjust the position relative to the first element
        srcPos = srcMod[idx].GetPosition();
        dstPos = dstMod[dstIdx][idx].GetPosition();
        dstPos[0] = startDstPos[0] + srcPos[0] - startSrcPos[0];
        dstPos[1] = startDstPos[1] + srcPos[1] - startSrcPos[1];
        dstMod[dstIdx][idx].SetPosition(dstPos);
    


pcb.Save(filename);

