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
from scipy.interpolate import interp1d,interp2d


imagePath = "/usr/Local/mokeConfig/Python_scripts/IMAGES/"
onLEDpxm = imagePath+"ledON_patrat.gif"
offLEDpxm = imagePath+"ledOFF_patrat.gif"

class demagObj(QtCore.QObject):
    demagMessage = QtCore.pyqtSignal(str)
    endRun = QtCore.pyqtSignal()
    fieldValue = QtCore.pyqtSignal(float)
    dataValues = QtCore.pyqtSignal(list)
    def __init__(self,field,motor,max_field,step_field,fieldFrequency,rotCheck,rotFrequency):
        QtCore.QObject.__init__(self)
        self.max_field = max_field
        self.step_field = step_field
        self.fieldFrequency = fieldFrequency
        self.rotCheck = rotCheck
        self.field = field
        self.motor = motor
        self.rotFrequency = rotFrequency
    def demagnetize(self):
        myMessage = "RUNNING ..."
        self.demagMessage.emit(myMessage)
        list_fields = np.linspace(self.max_field,0,self.max_field/self.step_field+1)
        TT = []
        fieldValues = []
        if not self.rotCheck:
            for fieldIndex,my_field in enumerate(list_fields):
                self.field.set_field(my_field)
                TT.append(time.time())
                time.sleep(1/(self.fieldFrequency/2))
                readField = self.field.get_field()
                fieldValues.append(readField)
                self.fieldValue.emit(readField)
                self.dataValues.emit([TT,fieldValues])
                if my_field == list_fields[-1]:
                    pass
                else:
                    my_back_field = my_field-self.step_field/2
                    self.field.set_field((-1)*my_back_field)
                    TT.append(time.time())
                    time.sleep(1/(self.fieldFrequency/2))
                    readField = self.field.get_field()
                    fieldValues.append(readField)
                    self.fieldValue.emit(readField)
                    self.dataValues.emit([TT,fieldValues])
            self.field.set_field(0)
        else:
            self.motor.set_vel(float(360*self.rotFrequency))
            self.motor.set_acc(float(3*360*self.rotFrequency))
            self.motor.set_dec(float(3*360*self.rotFrequency))
            motPos = 10e+6
            self.motor.reset_mot()
            self.motor.set_pos(motPos)
            for fieldIndex,my_field in enumerate(list_fields):
                self.field.set_field(my_field)
                TT.append(time.time())
                time.sleep(1/(self.fieldFrequency/2))
                readField = self.field.get_field()
                fieldValues.append(readField)
                self.fieldValue.emit(readField)
                self.dataValues.emit([TT,fieldValues])
                if my_field == list_fields[-1]:
                    pass
                else:
                    my_back_field = my_field-self.step_field/2
                    self.field.set_field((-1)*my_back_field)
                    TT.append(time.time())
                    time.sleep(1/(self.fieldFrequency/2))
                    readField = self.field.get_field()
                    fieldValues.append(readField)
                    self.fieldValue.emit(readField)
                    self.dataValues.emit([TT,fieldValues])
            self.field.set_field(0)
            self.motor.halt_mot()
        myMessage = "FINISHED!"
        self.demagMessage.emit(myMessage)
        self.endRun.emit()
        print "sample demagnetized!"

#---------------------------------------------

class hysteresisObject(QtCore.QObject):
    endRun = QtCore.pyqtSignal()
    endCycle = QtCore.pyqtSignal(str)
    dataValues = QtCore.pyqtSignal(list)
    dataValuesCorr = QtCore.pyqtSignal(list)
    def __init__(self,fileHystName,fieldCtrl,lockinCtrl,max_field,step_field,no_cycles):
        QtCore.QObject.__init__(self)
        self.fileHystName = fileHystName
        self.max_field = max_field
        self.step_field = step_field
        self.no_cycles = no_cycles
        self.fieldCtrl = fieldCtrl
        self.lockinCtrl = lockinCtrl
    def multi_hyst(self):
        try:
            os.stat(self.fileHystName)
        except:
            os.mkdir(self.fileHystName)
        steps1 = np.linspace(0,self.max_field,self.max_field/self.step_field+1)
        steps2 = np.linspace(self.max_field,(-1)*self.max_field,2*self.max_field/self.step_field+1)
        steps3 = np.linspace((-1)*self.max_field+self.step_field,self.max_field,2*self.max_field/self.step_field)
        steps = list(steps1)+list(steps2)+list(steps3)
        print list(steps2)+list(steps3)
        for val in steps1:
            self.fieldCtrl.set_field(val)
            time.sleep(0.1)
            readField = self.fieldCtrl.get_field()
            magn = self.lockinCtrl.get_magnitude()
            phase = self.lockinCtrl.get_phase()
            self.dataValues.emit([readField,magn,phase])
        NN = len(list(steps2)+list(steps3))
        fieldTable = np.zeros((self.no_cycles,NN),float)
        magnitudeTable = np.zeros((self.no_cycles,NN),float)
        phaseTable = np.zeros((self.no_cycles,NN),float)
        magnitudeTable_LIN = np.zeros((self.no_cycles,NN),float)
        for scan in range(self.no_cycles):
            self.endCycle.emit(str(scan+1))
            with open(self.fileHystName+"/"+"hyst_"+str(scan+1).zfill(4)+".txt","w") as outFile:
                for index,my_field in enumerate(list(steps2)+list(steps3)):
                    self.fieldCtrl.set_field(my_field)
                    time.sleep(0.1)
                    readField = self.fieldCtrl.get_field()
                    magn = self.lockinCtrl.get_magnitude()
                    phase = self.lockinCtrl.get_phase()
                    fieldTable[scan][index] = readField
                    magnitudeTable[scan][index] = magn
                    phaseTable[scan][index] = phase
                    print "FIELD --> %f \t MAGN --> %f \t PHASE --> %f"%(readField,magn,phase)
                    outFile.writelines(str(my_field)+'\t'+str(readField)+'\t'+str(magn)+'\t'+str(phase)+'\n')
                    self.dataValues.emit([readField,magn,phase])
            with open(self.fileHystName+"/"+"hyst_"+str(scan+1).zfill(4)+"_LIN.txt","w") as outFile:
                magn_N = magnitudeTable[scan][NN-1]
                magn_0 = magnitudeTable[scan][0]
                delta_magn = magn_N-magn_0
                for ii in range(NN):
                    magnitudeTable_LIN[scan][ii] = magnitudeTable[scan][ii] - delta_magn/(NN-1)*ii
                    outFile.writelines(str(fieldTable[scan][ii])+'\t'+str(magnitudeTable_LIN[scan][ii])+'\n')
            print "FINISHED HYST NO. >>> ",scan+1
            magnitudeTable_sum = np.zeros(NN,float)
            magnitudeTable_mean = np.zeros(NN,float)
            if scan == 0:
                self.dataValuesCorr.emit([fieldTable[scan],magnitudeTable_LIN[scan]])
            elif scan != 0:
                for index in range(scan):
                    magnitudeTable_sum = [(magnitudeTable_sum[ii]+magnitudeTable_LIN[index][ii]) for ii in range(NN)]
                magnitudeTable_mean = [(magnitudeTable_sum[ii]/scan) for ii in range(NN)]
                self.dataValuesCorr.emit([fieldTable[scan],magnitudeTable_mean])
        with open(self.fileHystName+"/"+"HYST_MEAN.txt","w") as outFile:
            for index,my_field in enumerate(list(steps2)+list(steps3)):
                outFile.writelines(str(my_field)+'\t'+str(magnitudeTable_mean[index])+'\n')
        print "SEQUENCE FINISHED ! CHECK YOUR FILES!!!!!!!!!"
        self.fieldCtrl.set_field(0.0)
        self.endRun.emit()


class myGUIapp(QtGui.QMainWindow,SolMOKE_GUI.Ui_MainWindow):
    def __init__(self,parent=None):
        super(myGUIapp,self).__init__(parent)
        self.setupUi(self)
        self.readPalette = QtGui.QPalette()
        self.readPalette.setColor(QtGui.QPalette.Background,QtCore.Qt.black)
        self.readPalette.setColor(QtGui.QPalette.Foreground,QtCore.Qt.yellow)
        self.readTempSetup.setPalette(self.readPalette)
        self.readFieldGMWSetup.setPalette(self.readPalette)
        self.readFieldCAYLARSetup.setPalette(self.readPalette)
        self.readMotPosSetup.setPalette(self.readPalette)
        self.readSRSxSetup.setPalette(self.readPalette)
        self.readSRSySetup.setPalette(self.readPalette)
        self.readPrincexSetup.setPalette(self.readPalette)
        self.readPrinceySetup.setPalette(self.readPalette)
        self.readTempControl.setPalette(self.readPalette)
        self.readMotPosControl.setPalette(self.readPalette)
        self.readFieldControl.setPalette(self.readPalette)
        self.readFieldMagn.setPalette(self.readPalette)

# ---> timers section
        self.readTempTimer = QtCore.QTimer()
        self.readTempTimer.timeout.connect(self.update_temp)
        self.readFieldTimer = QtCore.QTimer()
        self.readFieldTimer.timeout.connect(self.update_field)
        self.readLockinTimer = QtCore.QTimer()
        self.readLockinTimer.timeout.connect(self.update_lockin)
        self.readPosTimer = QtCore.QTimer()
        self.readPosTimer.timeout.connect(self.update_pos)
        self.timeTimer = QtCore.QTimer()
        self.timeTimer.timeout.connect(self.updateTimescanGraph)

# ---> init LED states section
        self.pixmapONled = QtGui.QPixmap(onLEDpxm)
        self.pixmapOFFled = QtGui.QPixmap(offLEDpxm)

        self.ledLakeshore.setPixmap(self.pixmapOFFled)
        self.ledLakeshore.show()
        self.ledGMW.setPixmap(self.pixmapOFFled)
        self.ledGMW.show()
        self.ledCAYLAR.setPixmap(self.pixmapOFFled)
        self.ledCAYLAR.show()
        self.ledMotor.setPixmap(self.pixmapOFFled)
        self.ledMotor.show()
        self.ledSRS.setPixmap(self.pixmapOFFled)
        self.ledSRS.show()
        self.ledPrinceton.setPixmap(self.pixmapOFFled)
        self.ledPrinceton.show()

# ---> standard init for the GUI components
# ---> ---> SETUP tab
        self.connectLakeshoreBtn.clicked.connect(self.connectLakeshore)
        self.connectGMWBtn.clicked.connect(self.connectGMW)
        self.connectCAYLARBtn.clicked.connect(self.connectCAYLAR)
        self.connectMotorBtn.clicked.connect(self.connectMotor)
        self.setMotPosSetup.returnPressed.connect(self.set_MotPosSetup)
        self.setMotVelocitySetup.returnPressed.connect(self.set_MotVelocity)
        self.setMotAccSetup.returnPressed.connect(self.set_MotAcc)
        self.setMotDecSetup.returnPressed.connect(self.set_MotDec)
        self.setFieldGMWSetup.returnPressed.connect(self.set_fieldSetup)
        self.setFieldCAYLARSetup.returnPressed.connect(self.set_fieldSetup)

        self.stopMotSetup.clicked.connect(self.stop_motor)
        self.resetMotSetup.clicked.connect(self.reset_motor)
        self.connectSRSBtn.clicked.connect(self.connectSRS)
        self.autoMeasSRS.clicked.connect(self.autoMeasureLockin)
        self.resetSRS.clicked.connect(self.reset_lockin)
        self.autoOffsetSRS.clicked.connect(self.autoPhaseLockin)
        self.autoSensSRS.clicked.connect(self.autoSensLockin)
        self.connectPrincetonBtn.clicked.connect(self.connectPrince)

        self.setTempSetup.returnPressed.connect(self.setTemperature)
        self.startTimescan.clicked.connect(self.startTimescanGraph)
        self.stopTimescan.clicked.connect(self.stopTimescanGraph)

# ---> ---> CONTROL tab
        self.workDirControl.clicked.connect(self.chooseWorkDir)
        self.magnitudeRadioBtn.setChecked(True)
        self.poleTypeGMWSetup.addItems(['pole_20','pole_40'])
        self.gapValueGMWSetup.addItems(['0.5','7.5','10','15','20','25','30','40'])
        self.setFieldControl.returnPressed.connect(self.set_FieldControl)
        self.gapValueCAYLARSetup.addItems(['20','25','30','35'])
        self.setMotPosControl.returnPressed.connect(self.set_MotPosControl)

# ---> ---> MAGNETIC MEASUREMENTS tab
        self.workDirMagn.clicked.connect(self.chooseWorkDir)
        self.startHyst.clicked.connect(self.hyst_scan)
        self.demagBtn.clicked.connect(self.demagnetize)
        self.rotateYES.setChecked(False)
        self.rotateNO.setChecked(True)
        self.demagLabel.setText("status ...")
        self.myLag = 100



    def connectLakeshore(self):
        import LakeshoreCtrl
        self.temperature = LakeshoreCtrl.LakeshoreCtrl()
        self.ledLakeshore.setPixmap(self.pixmapONled)
        self.ledLakeshore.show()
        self.readTempTimer.start()

    def connectGMW(self):
        self.max_current = float(self.setMaxCurrentGMW.text())
        self.GMWpole = str(self.poleTypeGMWSetup.currentText())
        self.GMWgap = str(self.gapValueGMWSetup.currentText())
        print "GMW >>>>>>> pole: %s >>>>>>> gap: %s "%(self.GMWpole,self.GMWgap)
        import KepcoCtrl
        self.field = KepcoCtrl.KepcoCtrl(self.GMWpole,self.GMWgap,self.max_current)
        self.ledGMW.setPixmap(self.pixmapONled)
        self.ledGMW.show()
        self.startFieldTimer()
        self.field_controler_flag = 'GMW'

    def connectCAYLAR(self):
        import CaylarCtrl
        #gap value to be implemented if using tables, now using current control
        self.caylarGapValue = str(self.gapValueCAYLARSetup.currentText())
        self.field = CaylarCtrl.CaylarCtrl(self.caylarGapValue)
        self.ledCAYLAR.setPixmap(self.pixmapONled)
        self.ledCAYLAR.show()
        self.startFieldTimer()
        self.field_controler_flag = 'CAYLAR'

    def connectMotor(self):
        import MotorCtrl
        self.motor = MotorCtrl.MotorCtrl()
        self.ledMotor.setPixmap(self.pixmapONled)
        self.ledMotor.show()
        self.readPosTimer.start()

    def connectSRS(self):
        import SRSCtrl
        self.lockin = SRSCtrl.SRSCtrl()
        #self.lockin.auto_lockin()
        self.ledSRS.setPixmap(self.pixmapONled)
        self.ledSRS.show()
        self.readLockinTimer.start()

    def connectPrince(self):
#        import PrincetonCtrl
#        self.lockin = PrincetonCtrl.PrincetonCtrl()
        self.ledPrinceton.setPixmap(self.pixmapONled)
        self.ledPrinceton.show()

    def chooseWorkDir(self):
        self.workDir = str(QtGui.QFileDialog.getExistingDirectory(self,"Select your working directory","/home/solmoke/Documents/DATA_MOKE/2016/TESTS"))+'/'
               
# ----> timescans section
    def startTimescanGraph(self):
        if self.magnitudeRadioBtn.isChecked():
            self.graphicsViewTime.setLabel('left', "Magnitude", units='a. u.')
        elif self.phaseRadioBtn.isChecked():
            self.graphicsViewTime.setLabel('left', "Phase", units='a. u.')
        elif self.tempRadioBtn.isChecked():
            self.graphicsViewTime.setLabel('left', "Temperature", units='K')
        self.Xdatabuffer = []
        self.Ydatabuffer = []
        self.graphicsViewTime.setLabel('bottom', "Time", units='sec.')
        self.graphicsViewTime.showGrid(x=True,y=True)
        self.graphicsViewTime.clear()
        self.xx0 = pg.ptime.time()
        
        self.fileTimescanName = self.workDir+self.saveTimescanFileName.text()
        print "SAVE FILE >>>>>> ",self.fileTimescanName
        with open(self.fileTimescanName,'w') as outFile:
            outFile.writelines("Timescan started @ %s\n\n"%(time.ctime()))
        self.readLockinTimer.stop()
        self.timeTimer.start(self.myLag)
    def stopTimescanGraph(self):
        self.timeTimer.stop()
    def updateTimescanGraph(self):
        self.xx = pg.ptime.time()
        if self.magnitudeRadioBtn.isChecked():
            self.y = self.lockin.get_magnitude()
        elif self.phaseRadioBtn.isChecked():
            self.y = self.lockin.get_phase()
        elif self.tempRadioBtn.isChecked():
            self.y = self.temperature.get_temp()
        self.Xdatabuffer.append(self.xx-self.xx0-self.myLag/1000)
        self.Ydatabuffer.append(self.y)
        self.graphicsViewTime.plot(x=self.Xdatabuffer ,y=self.Ydatabuffer,clear=True, pen=None,symbol='o',symbolSize=5,symbolPen=(255,255,0))
        self.fileTimescanName = self.workDir+self.saveTimescanFileName.text()
        with open(self.fileTimescanName,'a') as outFile:
            outFile.writelines(str(self.xx-self.xx0-self.myLag/1000)+"\t"+str(self.y)+"\n")
        self.readLockinTimer.start()

# ----> temperature control functions
    def setTemperature(self):
        self.spTemp = self.setTempSetup.text()
        self.rampTemp = self.setTempRampSetup.text()
        self.temperature.set_tempRamp(self.rampTemp)
        self.temperature.set_temp(self.spTemp)
    def update_temp(self):
        read_temp = self.temperature.get_temp()
        self.readTempSetup.setText(read_temp)
        self.readTempControl.setText(read_temp)
        
# ----> magnetic field control functions
    def update_field(self):
        read_field = str(self.field.get_field())
        self.updateField(read_field)
    def set_fieldSetup(self):
        if self.field_controler_flag == 'GMW':
            theField = self.setFieldGMWSetup.text()
        elif self.field_controler_flag == 'CAYLAR':
            theField = self.setFieldCAYLARSetup.text()
        self.field.set_field(theField)
    def set_FieldControl(self):
        theFieldControl = self.setFieldControl.text()
        self.field.set_field(theFieldControl)
    def demagnetize(self):
        self.stopFieldTimer()
        self.tt0 = time.time()
        max_field = int(self.setFieldMagn.text())
        step_field = int(self.setDemagRamp.text())
        fieldFrequency = float(self.demagFrequency.text())
        rotCheck = self.rotateYES.isChecked()
        rotFrequency = float(self.rotFrequency.text())
        self.demagObj = demagObj(self.field,self.motor,max_field,step_field,fieldFrequency,rotCheck,rotFrequency)
        self.demagThread = QtCore.QThread()
        self.demagObj.moveToThread(self.demagThread)
        self.demagThread.started.connect(self.demagObj.demagnetize)
        self.demagObj.demagMessage.connect(self.updateDemagLabel)
        self.demagObj.endRun.connect(self.demagThread.quit)
        self.demagObj.endRun.connect(self.startFieldTimer)
        self.demagObj.fieldValue.connect(self.updateField)
        self.demagObj.dataValues.connect(self.updateDemagGraph)
        self.demagThread.start()
    def updateDemagLabel(self,myMessage):
        self.demagLabel.setText(myMessage)
    def startFieldTimer(self):
        self.readFieldTimer.start()
    def stopFieldTimer(self):
        self.readFieldTimer.stop()
    def updateField(self,read_field):
        if self.field_controler_flag == 'GMW':
            self.readFieldGMWSetup.setText(str(read_field))
        elif self.field_controler_flag == 'CAYLAR':
            self.readFieldCAYLARSetup.setText(str(read_field))
        self.readFieldControl.setText(str(read_field))
        self.readFieldMagn.setText(str(read_field))
    def updateDemagGraph(self,theData):
        self.graphicsViewFieldSingle.showGrid(x=True,y=True)
        self.graphicsViewFieldSingle.setLabel('bottom', "Time", units='sec.')
        self.graphicsViewFieldSingle.setLabel('left', "Field", units='mT')
        tt = np.array(theData[0])-self.tt0
        yy = np.array(theData[1])
        #print type(tt)
        #print type(yy)
        self.graphicsViewFieldSingle.plot(tt,yy,clear=True,symbol='o',symbolSize=5,symbolPen=(255,255,0),pen=(255,255,0))
        
    def hyst_scan(self):
        self.stopLockinTimer()
        fileHystName = self.workDir+self.saveHystFileName.text()
        max_field = float(self.maxFieldMagn.text())
        step_field = float(self.stepFieldMagn.text())
        no_cycles = int(self.noHystCyclesMagn.text())
        self.hystObj = hysteresisObject(fileHystName,self.field,self.lockin,max_field,step_field,no_cycles)
        self.hystThread = QtCore.QThread()
        self.hystObj.moveToThread(self.hystThread)
        self.hystThread.started.connect(self.hystObj.multi_hyst)
        self.cancelHyst.clicked.connect(self.hystThread.quit)
        self.hystObj.endRun.connect(self.hystThread.quit)
        self.hystObj.endRun.connect(self.startLockinTimer)
        self.hystObj.endCycle.connect(self.clearGraph)
        self.hystObj.dataValues.connect(self.updateHystGraph)
        self.hystObj.endCycle.connect(self.updateGraphTitle)
        self.hystObj.dataValuesCorr.connect(self.updateHystMeanGraph)
        self.graphicsViewFieldSingle.clear()
        self.graphicsViewFieldSingle.showGrid(x=True,y=True)
        self.graphicsViewFieldSingle.setLabel('bottom', "Field", units='Amp')
        self.graphicsViewFieldSingle.setLabel('left', "MAGNITUDE", units='a.u.')
        self.graphicsViewFieldMulti.showGrid(x=True,y=True)
        self.graphicsViewFieldMulti.setTitle('HYSTERESIS MEAN + LIN')
        self.graphicsViewFieldMulti.setLabel('bottom', "Field", units='Amp')
        self.graphicsViewFieldMulti.setLabel('left', "MAGNITUDE", units='a.u.')
        self.hystThread.start()
        
    def stopLockinTimer(self):
        self.readLockinTimer.stop()
    def startLockinTimer(self):
        self.readLockinTimer.stop()
    def updateHystGraph(self,theData):
        theReadField = []
        theMagnitude = []
        thePhase = []
        theReadField.append(np.array(theData[0]))
        theMagnitude.append(np.array(theData[1]))
        thePhase.append(np.array(theData[2]))
        self.graphicsViewFieldSingle.plot(theReadField,theMagnitude,symbol='s',symbolSize=5,symbolPen=(0,255,255),pen=(0,255,255))
    def updateHystMeanGraph(self,theData):
        theReadField = np.array(theData[0])
        theMagnitudeMean = np.array(theData[1])
        self.graphicsViewFieldMulti.plot(theReadField,theMagnitudeMean,clear=True,symbol='o',symbolSize=5,symbolPen=(0,255,0),pen=(0,255,0))
    def clearGraph(self):
        self.graphicsViewFieldSingle.clear()
        #self.graphicsViewFieldMulti.clear()
    def updateGraphTitle(self,title):
        self.graphicsViewFieldSingle.setTitle('SCAN NO. ---> '+title)

# ----> motor position control functions
    def set_MotVelocity(self):
        theVelocity = self.setMotVelocitySetup.text()
        self.motor.set_vel(theVelocity)
    def set_MotAcc(self):
        theAcc = self.setMotAccSetup.text()
        print 'acc = ',theAcc
        self.motor.set_acc(theAcc)
    def set_MotDec(self):
        theDec = self.setMotDecSetup.text()
        self.motor.set_dec(theDec)
    def set_MotPosSetup(self):
        thePosition = self.setMotPosSetup.text()
        self.motor.set_pos(thePosition)
    def set_MotPosControl(self):
        thePosition = self.setMotPosControl.text()
        self.motor.set_pos(thePosition)
    def update_pos(self):
        read_pos = str(self.motor.get_pos())
        self.readMotPosSetup.setText(read_pos)
        self.readMotPosControl.setText(read_pos)
    def stop_motor(self):
        self.motor.halt_mot()
    def reset_motor(self):
        self.motor.reset_mot()

# ----> LockIn control functions
    def update_lockin(self):
        read_magnitude = str(round(self.lockin.get_magnitude(),3))
        read_phase = str(round(self.lockin.get_phase(),3))
        self.updateLockinLabels(read_magnitude,read_phase)
    def updateLockinLabels(self,read_magnitude,read_phase):
        self.readSRSxSetup.setText(read_magnitude)
        self.readSRSySetup.setText(read_phase)
    def startLockinTimer(self):
        self.readLockinTimer.start()
    def stopLockinTimer(self):
        self.readLockinTimer.stop()
    def autoMeasureLockin(self):
        self.lockin.auto_lockin()
    def autoPhaseLockin(self):
        self.lockin.auto_phase()
    def reset_lockin(self):
        self.lockin.reset_lockin()
    def autoSensLockin(self):
        self.lockin.auto_sensitivity()



#----------------------------------------------------------------------------------------------------#

def main():
    app = QtGui.QApplication(sys.argv)
    win = myGUIapp()
    win.show()
    #win.update_temp()
    app.exec_()

if __name__=='__main__':
    main()
