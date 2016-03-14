# -*- coding: utf-8 -*-
"""
Created on Sat Mar 12 16:48:33 2016

@author: stanescu
"""

import time
import visa
from scipy.interpolate import interp1d,interp2d
from numpy import loadtxt

ResMan = visa.ResourceManager()

try:
    KepcoCtrl = ResMan.open_resource("GPIB0::1::INSTR",term_chars="\n")
except visa.VisaIOError:
    print "KEPCO not ON! Hint: switch it ON!"
    pass
    exit()

class KepcoCtrl:
    def __init__(self,pole_type,gap_value):
        self.FieldCtrl = KepcoCtrl
        self.FieldCtrl.write("*RST")
        self.FieldCtrl.write("FUNC:MODE CURR")
        self.FieldCtrl.write("VOLT 5.0e1")
        self.FieldCtrl.write("OUTP ON")
        #self.myKepcoIdentity = self.FieldCtrl.query("*IDN?")
        #print "%s model %s is now connected!"%(self.KepcoStr(self.myKepcoIdentity).split(',')[0],self.KepcoStr(self.myKepcoIdentity).split(',')[1])
        #self.KepcoTest = self.FieldCtrl.query("*TST?")
        #if self.KepcoStr(self.KepcoTest) == '0':
        #    print "INTERNAL TEST OK >>> KEPCO power supply functionning properly!"
        #else:
        #    print "INTERNAL TEST NOT OK >>> check the KEPCO power supply!"
        self.my_pole = pole_type
        self.my_gap = float(gap_value)
        if self.my_pole == "pole_20":
            self.my_table = '/Users/stanescu/Documents/PyThoN_SCRIPTS/PyMOKE/SOLMOKE/CALIBRATION_GMW/magn_table_20poles.txt'
        elif self.my_pole == "pole_40":
            self.my_table = '/Users/stanescu/Documents/PyThoN_SCRIPTS/PyMOKE/SOLMOKE/CALIBRATION_GMW/magn_table_40poles.txt'
        self.aa = loadtxt(self.my_table,skiprows=1)
        self.table_gaps = self.aa[0,1:]
        self.table_currents = self.aa[1:,0]
        self.table_fields = [self.aa[1:,ii] for ii in range(1,len(self.table_gaps)+1)]

    def get_field(self):
        readCurrent = float(self.FieldCtrl.query("MEAS:CURR?"))
        readField = self.curr2field(readCurrent)        
        return readField
        
    def set_field(self,theWriteField):
        writeCurrent = self.field2curr(self.theWriteField)
        self.FieldCtrl.write("CURR %f"%(writeCurrent))
        
    def field2curr(self,theWriteField):
        dict_gaps={}
        for temp_gap,temp_field in zip(self.table_gaps,self.table_fields):
            dict_gaps[temp_gap] = temp_field
        curr_interp = interp1d(dict_gaps[self.my_gap],self.table_currents)
        if self.theWriteField >= 0:
            self.theWriteCurrent = curr_interp(abs(self.theWriteField))
        else: 
            self.theWriteCurrent = (-1)*curr_interp(abs(self.theWriteField))
        return self.theWriteCurrent
    
    def curr2field(self,theReadCurrent):
        field_interp = interp2d(self.table_currents,self.table_gaps,self.table_fields)
        if self.theReadCurrent >= 0:
            self.theReadField = field_interp(abs(self.theReadCurrent),self.my_gap)[0]
        else: 
            self.theReadField = (-1)*field_interp(abs(self.theReadCurrent),self.my_gap)[0]
        return self.theReadField
