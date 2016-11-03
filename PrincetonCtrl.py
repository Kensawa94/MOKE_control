# -*- coding: utf-8 -*-
"""
Created on Mon Mar 07 10:38:14 2016

@author: stanescu
"""

import time
import visa
import numpy as np

ResMan = visa.ResourceManager()

try:
    LockinCtrl = ResMan.open_resource("GPIB0::12::INSTR")
    print "Princeton 5210 connected!"
except visa.VisaIOError:
    print "Princetion LockIn not ON! Hint: switch it ON!"
    pass
    exit()

class PrincetonCtrl:
    def __init__(self):
        self.LockInCtrl = LockinCtrl

    def auto_lockin(self):
        self.LockInCtrl.clear()
        print "performing auto-measure"
        time.sleep(1)
        self.LockInCtrl.write("ie 0")
        time.sleep(1)
        self.LockInCtrl.write("lf 0")
        time.sleep(1)
        self.LockInCtrl.write("asm")
        time.sleep(1)
        self.LockInCtrl.write("axo")
        time.sleep(1)
        self.LockInCtrl.write("tc 5")
        time.sleep(1)
    def auto_offset(self):
        print "performing auto-offset"
        self.LockInCtrl.write("axo")
        time.sleep(1)
    def get_magnitude(self):
        xStr = self.LockInCtrl.query("x")
        yStr = self.LockInCtrl.query("y")
        magnitude = np.sqrt(float(xStr.replace(" ",""))**2 + float(yStr.replace(" ",""))**2)
        return magnitude
    def get_phase(self):
        xStr = self.LockInCtrl.query("x")
        yStr = self.LockInCtrl.query("y")
        phase = float(xStr.replace(" ",""))
        return phase
    def get_lockin(self):
        mpStr = self.LockInCtrl.query("mp")
    #    print ">>>>>>>>> characters from GPIB:  ",gpib_read
    #    sign=gpib_read.split()[0]
    #    value=gpib_read.split()[1]
    #    outX = float(sign+value)
        magnitude,phase = float(mpStr[0].replace(" ","")),float(mpStr[1].replace(" ",""))
        return magnitude, phase
