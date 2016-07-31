# -*- coding: utf-8 -*-
"""
Created on Sat Mar 12 16:48:33 2016

@author: stanescu
"""

import time
import visa
from numpy import loadtxt

ResMan = visa.ResourceManager()

try:
    MotorInstr = ResMan.open_resource("ASRL4::INSTR",read_termination="\n",write_termination="\n")
except visa.VisaIOError:
    print "MERCURY CONTROLLER not ON! Hint: switch it ON!"
    pass
    exit()

class MotorCtrl:
    def __init__(self):
        self.RotCtrl = MotorInstr
        self.conversionDeg = 16.66667
        self.reset_mot()

    def init_mot(self):
        self.RotCtrl.write("svo 1 1")
        self.RotCtrl.write("ron 1 0")
    def stop_mot(self):
        self.RotCtrl.write("stp")
    def halt_mot(self):
        self.RotCtrl.write("hlt 1")
    def reset_mot(self):
        self.RotCtrl.write("svo 1 1")
        self.RotCtrl.write("ron 1 0")
        self.RotCtrl.write("pos 1 0")
    def home_mot(self):
        self.RotCtrl.write("goh 1")
    def get_pos(self):
        MotPosStr = self.RotCtrl.query("pos? 1")
        MotPos = float(MotPosStr.split("=")[1])
        return round(MotPos/self.conversionDeg,2)
    def set_pos(self,posDeg):
        writeMotPos = float(posDeg)*self.conversionDeg
        self.RotCtrl.write("mvr 1 %f"%(writeMotPos))
        #print "motor sent to >>>>> ",self.get_pos()
    def set_acc(self,motAcc):
        writeMotAcc = float(motAcc)*self.conversionDeg**2
        self.RotCtrl.write("acc 1 %f"%writeMotAcc)
    def set_dec(self,motDec):
        writeMotDec = float(motDec)*self.conversionDeg**2
        self.RotCtrl.write("dec 1 %f"%writeMotDec)
    def set_vel(self,motVel):
        writeMotVel = float(motVel)*self.conversionDeg
        self.RotCtrl.write("vel 1 %f"%writeMotVel)
