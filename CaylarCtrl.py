# -*- coding: utf-8 -*-
"""
Created on Sat Mar 12 16:48:33 2016

@author: stanescu
"""

import socket
import time
from scipy.interpolate import interp1d,interp2d
from numpy import loadtxt

HOST = '169.254.21.200'
PORT = 1234

try:
    caylar = socket.create_connection((HOST,PORT))
    caylar.close()
except socket.error:
    print "CAYLAR PS not ON! Hint: switch it ON!"
    pass
    exit()

class CaylarCtrl:
    def __init__(self,gap_value):
        self.socket_cmd('SET_POWER_ON')
        self.socket_cmd('REGUL_MODE_1')
        self.socket_cmd('SETREGUL_AMP')

        self.my_gap = float(gap_value)
        #self.my_table = '/usr/Local/mokeConfig/Python_scripts/CALIBRATION_CAYLAR/magn_table_CAYLAR.txt'
        #self.aa = loadtxt(self.my_table,skiprows=1)
        #self.table_gaps = self.aa[0,1:]
        #self.table_currents = self.aa[1:,0]
        #self.table_fields = [self.aa[1:,ii] for ii in range(1,len(self.table_gaps)+1)]

    def socket_cmd(self,command):
        self.caylar = socket.create_connection((HOST,PORT))
        socket_reply = self.caylar.recv(self.caylar.send(str(command)))
        self.caylar.close()
        return socket_reply
    def caylar_off(self):
        self.socket_cmd('SET_POWEROFF')
    def get_Hall(self):
        readField = float(self.socket_cmd('READMAGFIELD').strip('mFG'))/1e4
        return readField
    def set_field(self, theCurrent):
        theCurrent = float(theCurrent)
        if theCurrent >= 0:
            caylarCurrent = '+'+str(theCurrent*1e6)
        elif theCurrent < 0:
            caylarCurrent = str(theCurrent*1e6)
        setCurrent = float(self.socket_cmd('SA%s'%caylarCurrent).strip('I'))
        currTest = True
        while currTest:
            readCURRone = float(self.socket_cmd('READ_CURRENT').strip('uA'))/1e6
            time.sleep(0.1)
            readCURRtwo = float(self.socket_cmd('READ_CURRENT').strip('uA'))/1e6
            if abs(readCURRone - readCURRtwo) >= 0.5:
                time.sleep(0.1)
            else:
                currTest = False
        return setCurrent
    def get_field(self):
        readCurrent = float(self.socket_cmd('READ_CURRENT').strip('uA'))/1e6
        return round(readCurrent,2)

"""

--->>> use if needed with tables calibration
--->>> big hysteresis => need to use MP and PM tables, to be implemented ...

    def get_field(self):
        self.open_socket()
        readCurrent = float(self.caylar.recv(self.caylar.send('READ_CURRENT')).strip('uA'))/1e6
        self.close_socket()
        readField = self.curr2field(readCurrent)
        return readField
    def set_field(self,theWriteField):
        writeCurrent = self.field2curr(self.theWriteField)
        self.open_socket()
        
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
"""


