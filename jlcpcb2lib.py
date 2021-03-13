#!/usr/bin/env python3

import sys

if len(sys.argv) < 3:
    print("jlcbcs2lib.py CVSInput LibOutput")
    print("   CVSInput: JLCPCB library saved as a TAB separated file")
    print("   LibOutput: KiCAD generate library output file")
    print("   Supported symbols are Rs, C, LED, Inductors")
    exit()

aFPdict = dict()
aFPdict["0402"] = "0402_1005"
aFPdict["0603"] = "0603_1608"
aFPdict["0805"] = "0805_2012"
aFPdict["1206"] = "1206_3216"

def genDEF2(prefix, foot_prefix, name, order, part, aDraw):
        aRet = ["#\n"]
        aRet.append("# " + prefix + " " + name + "\n")
        aRet.append("#\n")
        aRet.append("DEF " + name +  " " + prefix + " 0 0 N Y 1 F N\n")
    
        aRet.append('F0 "' + prefix + '" 30 20 50 H V L CNN\n')
        aRet.append('F1 "' + name + '" 30 -40 50 H V L CNN\n')
        aRet.append('F2 "' + foot_prefix + aFPdict[part[0]] + 'Metric" 0 0 50 H I C CNN\n')
        aRet.append('F3 "' + part[2] + '" 0 0 50 H I C CNN\n')
        aRet.append('F4 "' + order + '" 0 0 50 H I C CNN "LCSC"\n')
        aRet.append('F5 "' + part[3] + '" 0 0 50 H I C CNN "Part"\n')
        aRet.append('$FPLIST\n')
        aRet.append(" " + prefix + '_*\n')
        aRet.append('$ENDFPLIST\n')
        aRet.append('DRAW\n')
        aRet += aDraw
        aRet.append('ENDDRAW\n')
        aRet.append('ENDDEF\n')
        aRet.append('\n')
        return aRet

inFile = open(sys.argv[1], "r")
outFile = open(sys.argv[2], "w")

Rs   = dict()
Cs   = dict()
Ls   = dict()
Ds   = dict()
Ys   = dict()
LEDs = dict()
FPtypes = dict()

for line in inFile.readlines():
    aVal = line.split("\t")
    entry = [ aVal[4], aVal[8], aVal[9], aVal[3] ]
    if aVal[7] == "Basic" and aVal[-1] != "0":
        if (aVal[2] in FPtypes):
            if not (aVal[4] in FPtypes[aVal[2]]):
                FPtypes[aVal[2]].append(aVal[4])
        else:
            FPtypes[aVal[2]] = [aVal[4]]
        if aVal[1] == "Resistors" and aVal[4].find("_") == -1:
            Rs[aVal[0]] = entry
        elif aVal[1] == "Capacitors":
            Cs[aVal[0]] = entry
        elif aVal[2] == "Inductors (SMD)":
            Ls[aVal[0]] = entry
        elif aVal[2] == "Beads":
            Ls[aVal[0]] = entry
        elif aVal[1] == "Diodes":
            Ds[aVal[0]] = entry
        elif aVal[1] == "Crystals":
            Ys[aVal[0]] = entry
        elif aVal[4][0:3] == "LED":
            LEDs[aVal[0]] = entry

outFile.writelines(["EESchema-LIBRARY Version 2.4\n", "#encoding utf-8\n", "#\n"])


for i in Rs:
    if Rs[i][0] in aFPdict:
        aVal = Rs[i][1].split(" ")
        aDot = aVal[5].split(".")
        idx = aDot[len(aDot)-1].find("Ohm")
    
        if 0 < idx:
            typ = aDot[len(aDot)-1][idx-1]
            if "MKm".find(typ) != -1:
                idx = idx -1
            else:
                typ = "R"
        else:
            typ = "X"
            print("Error in part:", i)
    
        if len(aDot) == 1:
            name = aDot[0][0:idx] + typ + "_" + Rs[i][0][0:2] 
        else:
            name = aDot[0] + typ + aDot[1][0:idx] + "_" + Rs[i][0][0:2] 

        aOut = genDEF2("R", "Resistor_SMD:R_" , name, i, Rs[i],
                       ['S -30 70 30 -70 0 1 8 N\n',
                        'X ~ 1 0 100 30 D 50 50 1 1 P\n',
                        'X ~ 2 0 -100 30 U 50 50 1 1 P\n'])
        outFile.writelines(aOut)
    else:
        print("Skip part:", i, ", Footprint:", Rs[i][0])

for i in Cs:
    if Cs[i][0] in aFPdict:
        aVal = Cs[i][1].split(" ")
        aDot = aVal[6].split(".")
        volt = aVal[7]
        idx = aDot[len(aDot)-1].find("F")

        if 0 < idx:
            typ = aDot[len(aDot)-1][idx-1]
            if "unpf".find(typ) != -1:
                idx = idx -1
            else:
                typ = "X"
                print("Error in part:", i, dot)
        else:
            typ = "X"
            print("Error in part:", i)

        if len(aDot) == 1:
            name = aDot[0][0:idx] + typ + "_" + volt + "_" + Cs[i][0][0:2]
        else:
            name = aDot[0] + typ + aDot[1][0:idx] + "_" + volt + "_" + Cs[i][0][0:2]

        aOut = genDEF2("C", "Capacitor_SMD:C_" , name, i, Cs[i],
                       ['P 2 0 1 13 -60 -20 60 -20 N\n',
                        'P 2 0 1 12 -60 20 60 20 N\n',
                        'X ~ 1 0 100 80 D 50 50 1 1 P\n',
                        'X ~ 2 0 -100 80 U 50 50 1 1 P\n'])
        outFile.writelines(aOut)
    else:
        print("Skip part:", i, ", Footprint:", Cs[i][0])

for i in Ls:
    if Ls[i][0] in aFPdict:
        name = Ls[i][3]
        if Ls[i][1][0] == "I":
            aDraw = ['A 0 -60 20 -899 899 0 1 0 N 0 -80 0 -40\n',
                     'A 0 -20 20 -899 899 0 1 0 N 0 -40 0 0\n',
                     'A 0 20 20 -899 899 0 1 0 N 0 0 0 40\n',
                     'A 0 60 20 -899 899 0 1 0 N 0 40 0 80\n',
                     'X ~ 1 0 100 20 D 50 50 1 1 P\n',
                     'X ~ 2 0 -100 20 U 50 50 1 1 P\n']
        else:
            aDraw = ['P 2 0 1 0 0 -50 0 -31 N\n',
                     'P 2 0 1 0 0 35 0 51 N\n',
                     'P 5 0 1 0 -72 11 -44 59 72 -8 44 -56 -72 11 N\n',
                     'X ~ 1 0 100 50 D 50 50 1 1 P\n',
                     'X ~ 2 0 -100 50 U 50 50 1 1 P\n']

        aOut = genDEF2("L", "Inductor_SMD:L_" , name, i, Ls[i], aDraw)
        outFile.writelines(aOut)
    else:
        print("Skip part:", i, ", Footprint:", Ls[i][0])

LEDlist = []

for i in LEDs:
    fp = LEDs[i][0]
    if fp[0:4] == "LED_":
        fp = fp[4:]
    if fp in aFPdict:
        aVal = LEDs[i][1].split(" ")
        name = "LED_" + aVal[4] + "_" + fp[0:2]
        if not (name in LEDlist):
            LEDlist.append(name);
            LEDs[i][0] = fp
            aOut = genDEF2("LED", "LED_SMD:LED_" , name, i, LEDs[i],
                           ['P 2 0 1 10 -50 -50 -50 50 N\n',
                            'P 2 0 1 0 -50 0 50 0 N\n',
                            'P 4 0 1 10 50 -50 50 50 -50 0 50 -50 N\n',
                            'P 5 0 1 0 -120 -30 -180 -90 -150 -90 -180 -90 -180 -60 N\n',
                            'P 5 0 1 0 -70 -30 -130 -90 -100 -90 -130 -90 -130 -60 N\n',
                            'X K 1 -150 0 100 R 50 50 1 1 P\n',
                            'X A 2 150 0 100 L 50 50 1 1 P\n'])
            outFile.writelines(aOut)
        else:
            print("Skip part:", i, name, "dupplicate")
    else:
        print("Skip part:", i, ", Footprint:", LEDs[i][0])

for i in Ds:
    print (i, Ds[i])

for i in Ys:
    print (i, Ys[i])

for i in FPtypes:
    print (i, FPtypes[i])
