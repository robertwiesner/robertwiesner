#!/usr/bin/env python3

import sys
import math
from pcbnew import *

filename=sys.argv[1]

pcb = LoadBoard(filename)
small_comp = []
large_comp = []
idx = 0

for module in pcb.GetModules():
    name = module.GetReference()
    if name[0] == "U": #  or name[0] == "J"
        large_comp.append([module, []])

    if name[0] == "C" or name[0] == "R":
        small_comp.append(module)

if False:
    for c in small_comp:
        s = c.GetReference() + ":"
        for p in c.Pads():
            s = s + " " + p.GetNetname()
        print(s);

if False:
    for lc in large_comp:
        c = lc[0]
        s = c.GetReference() + ":"
        for p in c.Pads():
            s = s + " " + p.GetNetname() + ""
        print(s);

for sc in small_comp:
    netName = ""
    padOff = 0
    pos = []
    siz = []
    # determin the pad size delta to move the CAP/Resistor to a distance from the SoC pad
    for p in sc.Pads():
        pos.append(p.GetPosition())
        siz.append(p.GetBoundingBox().GetSize())

        if p.GetNetname() != "GND":
            netName = p.GetNetname()

    dx = pos[1][0] - pos[0][0] if pos[0][0] <= pos[1][0] else pos[0][0] - pos[1][0]
    dy = pos[1][1] - pos[0][1] if pos[0][1] <= pos[1][1] else pos[0][1] - pos[1][1]

    # calculate the offset from the pad
    delta = (dx + siz[0][0]) if dy == 0 else (dy + siz[0][1])
    delta = 2500000 + delta // 2

    compPlaced = False; # will be true if placed
    for lc in large_comp:
        chip = lc[0]
        modpos = chip.GetPosition()
        for pad in chip.Pads():
            if pad.GetNetname() == netName:
                if not (pad.GetName() in lc[1]):
                    pos = pad.GetPosition()
                    box = pad.GetBoundingBox().GetSize()
                    # determnin the pad orientation by checking the pad size
                    # the short size determins the Cap/Res direction (top/bottom or left/right)
                    # the distance to the SoC mid point i used to determin if the pos and rotation
                    # with the non GND pin towards the SoC
                    if box[0] > box[1]:
                        if pos[0] < modpos[0]:
                            rot = 1800
                            pos[0] = pos[0] - delta;
                        else:
                            rot = 0
                            pos[0] = pos[0] + delta;
                    else:
                        if pos[1] < modpos[1]:
                            rot = 900
                            pos[1] = pos[1] - delta;
                        else:
                            rot = 2700
                            pos[1] = pos[1] + delta;
    
                    sc.SetOrientation(rot)
                    sc.SetPosition(pos);
                    lc[1].append(pad.GetName())
                    idx = idx + 1
                    compPlaced = True;
                    break;
            if compPlaced:
                break;

print("Components Found:", len(small_comp), "Components placed :", idx);

pcb.Save(filename);
