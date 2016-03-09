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
    def open(self):
        self.TempCtrl.open()
        print "Lakeshore com open!"
    def close(self):
        self.TempCtrl.close()
        print "Lakeshore com close!"

    def reset(self):
        self.TempCtrl.write("*CLS")
        self.TempCtrl.write("*RST")
    def get_temp(self):
        self.theTemp = self.TempCtrl.query("CRDG? A")
        return self.theTemp.strip('\r\n')
    
    def get_heaterOut(self):
        self.heatPow = self.TempCtrl.query("HTR? 1")
        return self.heatPow.strip('\r\n')
        
    def LakeStr(self,theLakeAnswer):
        return theLakeAnswer.strip("\r\n")
    
    def set_temp(self, spTemp):
        print "Temperature set to >>> ...",spTemp
        
