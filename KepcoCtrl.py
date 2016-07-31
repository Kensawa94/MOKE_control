# -*- coding: utf-8 -*-
"""
Created on Sat Mar 12 16:48:33 2016

@author: stanescu
"""

import os
import time
import visa
from scipy.interpolate import interp1d,interp2d
from numpy import loadtxt

ResMan = visa.ResourceManager()

try:
    KepcoInstr = ResMan.open_resource("GPIB0::1::INSTR",read_termination="\n",write_termination="\n")
except visa.VisaIOError:
    print "KEPCO not ON! Hint: switch it ON!"
    pass
    exit()

class KepcoCtrl:
    def __init__(self,pole_type,gap_value,max_current):
        self.FieldCtrl = KepcoInstr
        self.FieldCtrl.write("*RST")
        self.FieldCtrl.write("FUNC:MODE CURR")
        self.FieldCtrl.write("OUTP ON")
        self.FieldCtrl.write("VOLT 50.0")
        self.my_pole = pole_type
        self.my_gap = float(gap_value)
        self.max_current = max_current
        if self.my_pole == "pole_20":
            self.my_table = os.getcwd()+'\\CALIBRATION_GMW\\magn_table_20poles.txt'
        elif self.my_pole == "pole_40":
            self.my_table = os.getcwd()+'\\CALIBRATION_GMW\\magn_table_40poles.txt'
        self.aa = loadtxt(self.my_table,skiprows=1)
        self.table_gaps = self.aa[0,1:]
        self.table_currents = self.aa[1:,0]
        self.table_fields = [self.aa[1:,ii] for ii in range(1,len(self.table_gaps)+1)]


    def get_current(self):
        self.readCurrent = float(self.FieldCtrl.query("MEAS:CURR?"))
        return self.readCurrent
    def get_field(self):
        self.readCurrent = self.get_current()
        self.readField = self.curr2field(self.readCurrent)
        return round(self.readField,2)
    def set_field(self,writeField):
        self.writeCurrent = self.field2curr(writeField)
        if self.writeCurrent >= self.max_current:
            print "CURRENT TO HIGH, DECREASE YOUR FIELD VALUE!!!"
            self.FieldCtrl.write("CURR 0.0")
        else:
            self.FieldCtrl.write("CURR %f"%(self.writeCurrent))
    def field2curr(self,writeField):
        writeField = float(writeField)/1000
        dict_gaps={}
        for temp_gap,temp_field in zip(self.table_gaps,self.table_fields):
            dict_gaps[temp_gap] = temp_field
        curr_interp = interp1d(dict_gaps[self.my_gap],self.table_currents)
        if writeField >= 0:
            self.theWriteCurrent = curr_interp(abs(writeField))
        else:
            self.theWriteCurrent = (-1)*curr_interp(abs(writeField))
        return self.theWriteCurrent
    def curr2field(self,readCurrent):
        field_interp = interp2d(self.table_currents,self.table_gaps,self.table_fields)
        if readCurrent >= 0:
            self.theReadField = field_interp(abs(readCurrent),self.my_gap)[0]
        else:
            self.theReadField = (-1)*field_interp(abs(readCurrent),self.my_gap)[0]
        return self.theReadField*1000
