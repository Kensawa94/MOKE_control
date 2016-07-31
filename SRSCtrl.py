# -*- coding: utf-8 -*-
"""
Created on Mon Mar 07 10:38:14 2016

@author: stanescu
"""

import time
import visa

ResMan = visa.ResourceManager()

try:
    SRSLockinCtrl = ResMan.open_resource("GPIB0::23::INSTR",read_termination="\n",write_termination="\n")
except visa.VisaIOError:
    print "SRS LockIn not ON! Hint: switch it ON!"
    pass
    exit()

class SRSCtrl:
    def __init__(self):
        self.LockInCtrl = SRSLockinCtrl
    def auto_lockin(self):
        self.LockInCtrl.write("s 2") #S=2 sets the R and Phi as outputs on the 2 channels, S=0 sets X and Y
        self.LockInCtrl.write("ar")
    def auto_phase(self):
        self.LockInCtrl.write("ap")
    def get_magnitude(self):
        #self.auto_phase()
        magnitude = float(self.LockInCtrl.query('Q1'))
        return magnitude
    def get_phase(self):
        #self.auto_lockin()
        phase = float(self.LockInCtrl.query('Q2'))
        return phase
    def reset_lockin(self):
        self.LockInCtrl.write('z')
    def auto_sensitivity(self):
        for sensy in range(24,0,-1):
            self.LockInCtrl.write("g %i"%sensy)
            self.LockInCtrl.write("ar")
            self.LockInCtrl.write("ap")
            time.sleep(1)
            print "BIT4 STATUS >>>>>> ",self.LockInCtrl.query("y 4")
            print "\tSENS >>>>   ",int(self.LockInCtrl.query("g"))
            if int(self.LockInCtrl.query("y 4")) == 1:
                break
        theSensy = int(self.LockInCtrl.query("g"))
        self.LockInCtrl.write("g %i"%(theSensy+1))
        print "SENSITIVITY SET TO ",theSensy+1
    
        
