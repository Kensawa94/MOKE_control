# -*- coding: utf-8 -*-
"""
Created on Mon Mar 07 10:38:14 2016

@author: stanescu
"""

import time
import visa

ResMan = visa.ResourceManager()

try:
    LockinCtrl = ResMan.open_resource("GPIB0::12::INSTR")
except visa.VisaIOError:
    print "Princetion LockIn not ON! Hint: switch it ON!"
    pass
    exit()

class PrincetonCtrl:
    def __init__(self):
        self.LockInCtrl = LockinCtrl


    def auto_lockin(self):
        self.LockInCtrl.clear()
        self.LockInCtrl.write("ie 0")
        self.LockInCtrl.write("lf 0")
        self.LockInCtrl.write("asm")
        self.LockInCtrl.write("axo")
        self.LockInCtrl.write("tc 5")
    def get_lockin(self):
        mpStr = self.LockInCtrl.query("mp")
    #    print ">>>>>>>>> characters from GPIB:  ",gpib_read
    #    sign=gpib_read.split()[0]
    #    value=gpib_read.split()[1]
    #    outX = float(sign+value)
        magnitude,phase = float(mpStr[0].replace(" ","")),float(mpStr[1].replace(" ",""))
        return magnitude, phase
