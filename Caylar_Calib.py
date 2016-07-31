# -*- coding: utf-8 -*-
"""
Created on Tue Oct 13 15:38:14 2015

@author: stanescu
"""

import os
import numpy as np
import sys
from PyQt4 import QtGui, QtCore
import pyqtgraph as pg
import CAYLAR_GUI
import time
import CaylarCtrl
from scipy.interpolate import interp1d,interp2d

class caylarScan(QtCore.QObject):
    endRun = QtCore.pyqtSignal()
    dataValues = QtCore.pyqtSignal(list)
    def __init__(self,caylar,start_field,end_field,dwellTime,fileName,gap_value):
        QtCore.QObject.__init__(self)
        self.start_field = start_field
        self.end_field = end_field
        self.dwellTime = dwellTime
        self.caylar = caylar
        self.fileName = fileName
        self.gap_value = gap_value
    def start_scanCaylar(self):
        self.caylar.set_field(self.start_field)
        while abs(self.caylar.get_field()) < abs(self.start_field*(1-0.01)) or abs(self.caylar.get_field()) > abs(self.start_field*(1+0.01)):
           time.sleep(0.1)
        currBuffer = []
        fieldBuffer = []
        if self.start_field == self.end_field:
            self.currents = np.ones(200)*self.start_field
        else:
            self.currents = np.linspace(self.start_field,self.end_field,np.abs(self.start_field)+np.abs(self.end_field)+1)
        #print self.currents            
        with open(self.fileName,'w') as outFile:
            outFile.writelines('Time : %s \t GAP VALUE (mm): %i\n\n'%(time.ctime(),int(self.gap_value)))
            outFile.writelines('CURRENT (Amp) \t FIELD (T)\n')
            for curr in self.currents:
                self.caylar.set_field(curr)
                time.sleep(self.dwellTime)
                readCurr = self.caylar.get_field()
                readField = self.caylar.get_Hall()
                outFile.writelines(str(readCurr) +'\t'+ str(readField)+'\n')
                currBuffer.append(readCurr)
                fieldBuffer.append(readField)
                print "%f\t%f"%(readCurr,readField)
                self.dataValues.emit([currBuffer,fieldBuffer])
        self.endRun.emit()
        print "FINI !!!!"



class myGUIapp(QtGui.QMainWindow,CAYLAR_GUI.Ui_MainWindow):
    def __init__(self,parent=None):
        super(myGUIapp,self).__init__(parent)
        self.setupUi(self)
        self.chooseDir.clicked.connect(self.chooseWorkDir)
        self.startFieldScan.clicked.connect(self.start_scan)
        self.initCaylarPS.clicked.connect(self.init_caylarPS)
        self.zeroCaylar.clicked.connect(self.zero_caylarPS)
        self.offCaylar.clicked.connect(self.off_caylarPS)
        self.plotField.setLabel('left', "Hall probe", units='mT')
        self.plotField.setLabel('bottom','Current',units='Amp')
        self.plotField.showGrid(x=True,y=True)
        self.click_flag = None
    def init_caylarPS(self):
        self.gap_value = self.gapValue.text()        
        self.caylar = CaylarCtrl.CaylarCtrl(self.gap_value)
    def zero_caylarPS(self):
        self.caylar.set_field(0.0)
    def off_caylarPS(self):
        self.caylar.caylar_off()
        
    def chooseWorkDir(self):
        self.workDir = str(QtGui.QFileDialog.getExistingDirectory(self,"Select save directory: ","/home/solmoke/Documents/DATA_MOKE/2016/TESTS"))+'/'
        self.click_flag = 'clicked'

        
    def start_scan(self):
        scan_start = float(self.startField.text())
        scan_end = float(self.endField.text())
        wait_time = float(self.lineEdit.text())
        if self.click_flag == None:
            self.workDir = '/home/solmoke/Documents/DATA_MOKE/2016/TESTS/'
        elif self.click_flag == 'clicked':
            pass
        file_name = self.workDir+self.outFileName.text()
        self.scanObj = caylarScan(self.caylar,scan_start,scan_end,wait_time,file_name,self.gap_value)
        self.scanThread = QtCore.QThread()
        self.scanObj.moveToThread(self.scanThread)
        self.scanThread.started.connect(self.scanObj.start_scanCaylar)
        self.scanObj.endRun.connect(self.scanThread.quit)
        self.scanObj.endRun.connect(self.zero_caylarPS)
        self.scanObj.dataValues.connect(self.updateCaylarGraph)
        self.scanThread.start()
    def updateCaylarGraph(self,theData):
        realCurrent = np.array(theData[0])
        realField = np.array(theData[1])
        self.plotField.plot(x=realCurrent ,y=realField,clear=True, pen=(255,255,0),symbol='o',symbolSize=8,symbolPen=(255,255,0))
                
#----------------------------------------------------------------------------------------------------#

def main():
    app = QtGui.QApplication(sys.argv)
    win = myGUIapp()
    win.show()
    #win.update_temp()
    app.exec_()

if __name__=='__main__':
    main()
