# -*- coding: utf-8 -*-
"""
Created on Mon Mar 07 10:38:14 2016

@author: stanescu
"""

import time
import visa

ResMan = visa.ResourceManager()

try:
    TempCtrl = ResMan.open_resource("GPIB0::12::INSTR")
except visa.VisaIOError:
    print "Lakeshore not ON! Hint: switch it ON!"
    pass
    exit()

class LakeshoreCtrl:
    def __init__(self):
        self.TempCtrl = TempCtrl
        #self.TempCtrl.write("*CLS")
        #self.TempCtrl.write("*RST")
        self.myTempIdentity = self.TempCtrl.query("*IDN?")
        print "%s model %s is now connected!"%(self.LakeStr(self.myTempIdentity).split(',')[0],self.LakeStr(self.myTempIdentity).split(',')[1])
        self.LakeTest = self.TempCtrl.query("*TST?")
        if self.LakeStr(self.LakeTest) == '0':
            print "INTERNAL TEST OK >>> temperature controller functionning properly!"
        else:
            print "INTERNAL TEST NOT OK >>> check the temperature controller!"

    def get_temp(self):
        theTemp = self.TempCtrl.query("CRDG? A")
        return self.LakeStr(theTemp)
    def get_heaterOut(self):
        heatPow = self.TempCtrl.query("HTR? 1")
        return self.LakeStr(heatPow)
    def set_temp(self, spTemp):
        self.TempCtrl.write("SETP 1,%f"%spTemp)
        print "Temperature set to >>> ...",spTemp
    def set_tempRamp(self,rampTemp):
        self.TempCtrl.write("RAMP 1,1,%f"%rampTemp)
    def LakeStr(self,theLakeAnswer):
        return theLakeAnswer.strip("\r\n")
