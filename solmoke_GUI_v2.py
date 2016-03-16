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
import SolMOKE_GUI
import time
import LakeshoreCtrl
from scipy.interpolate import interp1d,interp2d

#myInstrument = "HermesMOKE"
myInstrument = "SolMOKE"

class myGUIapp(QtGui.QMainWindow,SolMOKE_GUI.Ui_MainWindow):
    def __init__(self,parent=None):
        super(myGUIapp,self).__init__(parent)
        self.setupUi(self)
        
        if myInstrument == "HermesMOKE":
            try:
                self.field = KepcoCtrl.KepcoCtrl()
                time.sleep(3)
            except:
                print "KEPCO not connected!"
                pass
            try:
                self.LockIn = LockInPrincetonCtrl.LockInPrincetonCtrl()
                time.sleep(3)
            except:
                print "LockIn not connected!"
                pass
        elif myInstrument == "SolMOKE":
            try:
                self.temperature = LakeshoreCtrl.LakeshoreCtrl()
                time.sleep(3)
            except:
                print "Lakeshore not connected!"
                pass
            try:
                self.field = CaylarCtrl.CaylarCtrl()
                time.sleep(3)
            except:
                print "Caylar PS not connected!"
                pass
            try:
                self.LockIn = LockInSRSCtrl.LockInSRSCtrl()
                time.sleep(3)
            except:
                print "LockIn not connected!"
                pass
            
        self.readTempTimer = pg.QtCore.QTimer()
        self.readTempTimer.timeout.connect(self.update_temp)        
        self.setTempLine.returnPressed.connect(self.setTemperature)
        self.startTimescanBtn.clicked.connect(self.startTimescanGraph)
        self.stopTimescanBtn.clicked.connect(self.stopTimescanGraph)
        self.timeTimer = pg.QtCore.QTimer()
        self.timeTimer.timeout.connect(self.updateTimescanGraph)
        self.workDirBtn.clicked.connect(self.chooseWorkDir)
        self.workDirBtn_1.clicked.connect(self.chooseWorkDir)
        self.lockInRadioBtn.setChecked(True)
        if myInstrument == "HermesMOKE":
            self.poleTypeCB.addItems(['pole_20','pole_40'])
            self.gapValueCB.addItems(['0.5','7.5','10','15','20','25','30','40'])
        elif myInstrument == "SolMOKE":
            self.gapValueCB.addItems(['20','24','26','28','30','32','34','36'])
        self.myLag = 100

    def chooseWorkDir(self):
        self.workDir = str(QtGui.QFileDialog.getExistingDirectory(self,"Select your working directory","/home/solmoke/Documents/DATA_MOKE"))+'/'
   
#    def readData(self):
#        if self.lockInRadioBtn.isChecked():
#            self.field = self.fieldCtrlSlider.value()
#            self.xx = pg.ptime.time()
#            self.y = 0.1+self.xx**(-0.2*self.field/1000)
#        elif self.tempRadioBtn.isChecked():
#            self.temp = self.tempCtrlSlider.value()
#            self.xx = pg.ptime.time()
#            self.y = 0.1+self.xx**(0.2*self.temp/100)            
        return self.xx,self.y

    def updateTimescanGraph(self):
        self.xx = pg.ptime.time()
        if self.lockInRadioBtn.isChecked():
            self.y = self.LockIn.get_outX()
        elif self.tempRadioBtn.isChecked():
            self.y = self.temperature.get_temp()
        self.Xdatabuffer.append(self.xx-self.xx0-self.myLag/1000)
        self.Ydatabuffer.append(self.y)
        self.graphicsViewTime.plot(x=self.Xdatabuffer ,y=self.Ydatabuffer,clear=True, pen=None,symbol='o',symbolSize=5,symbolPen=(255,255,0))
        self.fileTimescanName = self.workDir+self.saveTimescanFileName.text()
        with open(self.fileTimescanName,'a') as outFile:
            outFile.writelines(str(self.xx-self.xx0-self.myLag/1000)+"\t"+str(self.y)+"\n")

    def startTimescanGraph(self):
        self.Xdatabuffer = []
        self.Ydatabuffer = []
        self.graphicsViewTime.clear()
        self.xx0 = pg.ptime.time()
        if self.lockInRadioBtn.isChecked():
            self.graphicsViewTime.setLabel('left', "LockIn signal", units='a. u.')
            self.graphicsViewTime.setLabel('bottom', "Time", units='sec.')
        elif self.tempRadioBtn.isChecked():
            self.graphicsViewTime.setLabel('left', "Temperature", units='K')
            self.graphicsViewTime.setLabel('bottom', "Time", units='sec.')
        self.graphicsViewTime.showGrid(x=True,y=True)
        self.fileTimescanName = self.workDir+self.saveTimescanFileName.text()
        print "SAVE FILE >>>>>> ",self.fileTimescanName
        with open(self.fileTimescanName,'w') as outFile:
            outFile.writelines("Timescan started @ %s\n\n"%(time.ctime()))
        self.timeTimer.start(self.myLag)

    def stopTimescanGraph(self):
        self.timeTimer.stop()
    
    def setTemperature(self):
        self.spTemp = self.setTempLine.text()
        self.rampTemp = self.setTempRampLine.text()
        print "Ramp is set to >>>> ",self.rampTemp
        self.temperature.set_temp(self.spTemp)

    def update_temp(self):
        read_temp = self.temperature.get_temp()
        self.readTempLabel.setText(read_temp)
        #print "TEMP >>>> ",self.read_temp
        self.readTempTimer.start(self.myLag)

    ##############################
    ###########  SCANS section  #########
    ##############################


    def hyst():
        fileName = h1.get()
        field = float(h2.get())
        step = float(h3.get())
        OUT=[]
        FIELDS=[]
        kepcoInit()
        dataPathLoc = dataPath()
        try:
            os.stat(dataPathLoc)
        except:
            os.mkdir(dataPathLoc)
        while (field2curr(field) >= 3.0):
            field = tkSimpleDialog.askfloat('MAGNET OVERLOAD','Choose a new value for the field or decrease the gap!')

        steps1 = r_[0.0:field:step]
        steps2 = r_[field:-field:-step]
        steps3 = r_[-field:field+step/10:step]
        steps = list(steps1)+list(steps2)+list(steps3)
        print "FIELDS ARE: ", steps
        with open(dataPathLoc+'\\'+fileName+'.txt','w') as outFile:
            outFile.writelines("Hyst started @ %s\n"%(time.ctime()))
            outFile.writelines("Magnet config. is: pole %s and gap %s\n\n"%(pole_type.get(),gap_value.get()))
            for my_field in steps:
                my_write_curr = field2curr(my_field)
                kepco.write("CURR %f"%(my_write_curr))
                time.sleep(0.1)
                outx_tmp,tt = LockIn_measure()
                outx = outx_tmp
                my_read_curr = float(kepco.ask("MEAS:CURR?"))
                my_read_field = curr2field(my_read_curr)
                print "MEASURED FIELD:   ",my_read_field
                FIELDS.append(my_read_field)
                OUT.append(outx)
                plot_update(FIELDS,OUT)
                outFile.writelines(str(my_read_field)+' '+str(outx)+'\n')
                time.sleep(0.01)
        kepco.write("CURR 0.0")
        kepco.write("OUTP OFF")
        print "FINISHED!!!"
        del my_write_curr
        del my_read_curr
        del my_read_field
        del my_field

    
    def m_hyst():
        root_fileName = h1.get()
        Hmax = float(h2.get())
        step = float(h3.get())
        mm = int(h4.get())
        OUT=[]
        FIELDS=[]
        dataPathLoc = dataPath()
        m_Path = dataPathLoc+"\\"+root_fileName
        try:
            os.stat(m_Path)
        except:
            os.mkdir(m_Path)
        while (field2curr(Hmax) >= 3.0):
            Hmax = tkSimpleDialog.askfloat('MAGNET OVERLOAD','Choose a new value for the field or decrease the gap!')
        steps1 = ['%.8f'%elem for elem in r_[0:Hmax+step/10:step]]
        steps2 = ['%.8f'%elem for elem in r_[Hmax:-Hmax:-step]]
        steps3 = ['%.8f'%elem for elem in r_[-Hmax:Hmax+step/10:step]]
        steps = list(steps1)+list(steps2)+list(steps3)
        kepcoInit()
        for val in steps1:
            my_write_curr = field2curr(float(val))
            kepco.write("CURR %f"%(my_write_curr))
            time.sleep(0.1)
        del my_write_curr
        NN = len(list(steps2)+list(steps3))
        YY = zeros((mm,len(steps)),float)
        yy_LIN = zeros((mm,NN),float)
        for scan in range(mm):
            del FIELDS
            del OUT
            FIELDS=[]
            OUT=[]
            with open(m_Path+"\\"+"hyst_"+str(scan+1).zfill(4)+".txt","w") as outFile:
                for index,my_field in enumerate(list(steps2)+list(steps3)):
                    my_write_curr = field2curr(float(my_field))
                    kepco.write("CURR %f"%(my_write_curr))
                    outx_tmp,tt = LockIn_measure()
                    outx = outx_tmp
                    YY[scan][index] = outx
                    my_read_curr = float(kepco.ask("MEAS:CURR?"))
                    my_read_field = curr2field(my_read_curr)
                    print "MEASURED FIELD:   ",my_read_field
                    FIELDS.append(my_read_field)
                    OUT.append(outx)
                    plot_update_multi(FIELDS,OUT,scan+1)
                    outFile.writelines(str(my_read_field)+" "+str(outx)+"\n")
                del my_field
                del my_write_curr
                del my_read_curr
                del my_read_field
            with open(m_Path+"\\"+"hyst_"+str(scan+1).zfill(4)+"_LIN.txt","w") as outFile:
                NN = len(list(steps2)+list(steps3))
                yyN = YY[scan][NN-1]
                yy0 = YY[scan][0]
                delta_yy = yyN-yy0
                for ii in range(NN):
                    yy_LIN[scan][ii] = YY[scan][ii] - delta_yy/(NN-1)*ii
                    outFile.writelines(str(FIELDS[ii])+" "+str(yy_LIN[scan][ii])+"\n")
            print "FINISHED HYST NO. >>> ",scan+1
            YY_sum = zeros(len(steps),float)
            YY_mean = zeros(len(list(steps2)+list(steps3)),float)
            if scan != 0:
                for index in range(scan):
                    YY_sum = [(YY_sum[ii]+yy_LIN[index][ii]) for ii in range(len(list(steps2)+list(steps3)))]
                YY_mean = [(YY_sum[ii]/scan) for ii in range(len(list(steps2)+list(steps3)))]
                plot_update_mean(FIELDS,YY_mean)
            time.sleep(1)
        set_field_zero()
        del index
        with open(m_Path+"\\"+root_fileName+"_MEAN.txt","w") as outFile:
            for index,my_field in enumerate(list(steps2)+list(steps3)):
                outFile.writelines(str(my_field)+" "+str(YY_mean[index])+"\n")
            del my_field
        print "SEQUENCE FINISHED ! CHECK YOUR FILES!!!!!!!!!"

def main():        
    app = QtGui.QApplication(sys.argv)
    win = myGUIapp()
    win.show()
    win.update_temp()
    app.exec_()

if __name__=='__main__':
    main()
