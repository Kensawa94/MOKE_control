# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'CAYLAR_GUI.ui'
#
# Created: Tue Jul 12 07:32:12 2016
#      by: PyQt4 UI code generator 4.11.3
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName(_fromUtf8("MainWindow"))
        MainWindow.resize(940, 648)
        self.centralwidget = QtGui.QWidget(MainWindow)
        self.centralwidget.setObjectName(_fromUtf8("centralwidget"))
        self.plotField = PlotWidget(self.centralwidget)
        self.plotField.setGeometry(QtCore.QRect(290, 10, 631, 591))
        self.plotField.setObjectName(_fromUtf8("plotField"))
        self.gridLayoutWidget = QtGui.QWidget(self.centralwidget)
        self.gridLayoutWidget.setGeometry(QtCore.QRect(30, 260, 241, 91))
        self.gridLayoutWidget.setObjectName(_fromUtf8("gridLayoutWidget"))
        self.gridLayout = QtGui.QGridLayout(self.gridLayoutWidget)
        self.gridLayout.setMargin(0)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.endField = QtGui.QLineEdit(self.gridLayoutWidget)
        self.endField.setObjectName(_fromUtf8("endField"))
        self.gridLayout.addWidget(self.endField, 0, 1, 1, 1)
        self.startField = QtGui.QLineEdit(self.gridLayoutWidget)
        self.startField.setObjectName(_fromUtf8("startField"))
        self.gridLayout.addWidget(self.startField, 0, 0, 1, 1)
        self.lineEdit = QtGui.QLineEdit(self.gridLayoutWidget)
        self.lineEdit.setObjectName(_fromUtf8("lineEdit"))
        self.gridLayout.addWidget(self.lineEdit, 1, 0, 1, 1)
        self.gapValue = QtGui.QLineEdit(self.gridLayoutWidget)
        self.gapValue.setObjectName(_fromUtf8("gapValue"))
        self.gridLayout.addWidget(self.gapValue, 1, 1, 1, 1)
        self.outFileName = QtGui.QLineEdit(self.centralwidget)
        self.outFileName.setGeometry(QtCore.QRect(30, 420, 241, 33))
        self.outFileName.setObjectName(_fromUtf8("outFileName"))
        self.startFieldScan = QtGui.QPushButton(self.centralwidget)
        self.startFieldScan.setGeometry(QtCore.QRect(30, 460, 241, 31))
        self.startFieldScan.setObjectName(_fromUtf8("startFieldScan"))
        self.chooseDir = QtGui.QPushButton(self.centralwidget)
        self.chooseDir.setGeometry(QtCore.QRect(30, 380, 241, 31))
        self.chooseDir.setObjectName(_fromUtf8("chooseDir"))
        self.initCaylarPS = QtGui.QPushButton(self.centralwidget)
        self.initCaylarPS.setGeometry(QtCore.QRect(30, 140, 241, 31))
        self.initCaylarPS.setObjectName(_fromUtf8("initCaylarPS"))
        self.zeroCaylar = QtGui.QPushButton(self.centralwidget)
        self.zeroCaylar.setGeometry(QtCore.QRect(30, 180, 241, 31))
        self.zeroCaylar.setObjectName(_fromUtf8("zeroCaylar"))
        self.offCaylar = QtGui.QPushButton(self.centralwidget)
        self.offCaylar.setGeometry(QtCore.QRect(30, 220, 241, 31))
        self.offCaylar.setObjectName(_fromUtf8("offCaylar"))
        MainWindow.setCentralWidget(self.centralwidget)
        self.statusbar = QtGui.QStatusBar(MainWindow)
        self.statusbar.setObjectName(_fromUtf8("statusbar"))
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow", None))
        self.endField.setPlaceholderText(_translate("MainWindow", "END (Amp)", None))
        self.startField.setPlaceholderText(_translate("MainWindow", "START (Amp)", None))
        self.lineEdit.setPlaceholderText(_translate("MainWindow", "Time wait (sec)", None))
        self.gapValue.setPlaceholderText(_translate("MainWindow", "GAP value (mm)", None))
        self.outFileName.setPlaceholderText(_translate("MainWindow", "FILE NAME", None))
        self.startFieldScan.setText(_translate("MainWindow", "START", None))
        self.chooseDir.setText(_translate("MainWindow", "DIRECTORY", None))
        self.initCaylarPS.setText(_translate("MainWindow", "INIT CAYLAR_PS", None))
        self.zeroCaylar.setText(_translate("MainWindow", "ZERO CAYLAR", None))
        self.offCaylar.setText(_translate("MainWindow", "CAYLAR_PS OFF", None))

from pyqtgraph import PlotWidget
