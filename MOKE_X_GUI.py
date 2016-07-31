# -*- coding: cp1252 -*-
"""
pyvisa module for DEMAG/MOKE HERMES control
GUI Tkinter version
Used to measure lock-in signal from Princeton 5210 and drive the Kepco PS
credits � S. Stanescu
04/12/2103
"""


import matplotlib
matplotlib.use('TkAgg')
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import Tkinter as Tk
import os
from numpy import r_, zeros,loadtxt
import time
from visa import instrument
from scipy.interpolate import interp1d,interp2d
import tkSimpleDialog


LockIn = instrument("GPIB0::12::INSTR")
kepco = instrument("GPIB0::1::INSTR",term_chars="\n")
motor = instrument("ASRL4::INSTR",term_chars="\n")

########
# init motor

motor.write('rbt')
motor.write('svo 1 1')
motor.write('ron 1 0')

def dataPath():
	dataDirPath = 'D:\DEMAG-MOKE\DATA'
	sample_name = sampleNameEntry.get()
	dataPath = dataDirPath + '\\' + sample_name
	return dataPath


def change_SEN(val):
	LockIn.write("sen %i"%(sensitivity[str(val)]))
	LockIn.write("sen")
	tmp_str = LockIn.read()
	for sen in sensitivity:
		if tmp_str == sensitivity[str(sen)]:
			print "You are now on SENSITIVITY %s"%(sen)

def test_motor():
	acc_deg = float(accEntry.get())
	dec_deg = float(decEntry.get())
	vel_deg = float(velEntry.get())
	my_deg = 16.66666667
	acc = acc_deg*my_deg**2
	dec = dec_deg*my_deg**2
	vel = vel_deg*my_deg
	motor.write('svo 1 1')
	motor.write('ron 1 0')
	motor.write('acc 1 %f'%(acc))
	motor.write('dec 1 %f'%(dec))
	motor.write('vel 1 %f'%(vel))
	motor.write('vel?'); print motor.read()
	motor.write('acc?'); print motor.read()
	motor.write('ron?'); print 'RON = ',motor.read()
	motor.write('svo?'); print 'SVO = ',motor.read()
	my_range = tkSimpleDialog.askfloat('MOVE RANGE (degree)','Enter a range value for your move in degrees!')
	print 'asked angular range:',my_range
	motor.write('mvr 1 %f'%(my_range*my_deg))

def LockIn_init():
	print "PLEASE WAIT FOR THE INIT TO FINISH (AUTO red LED off)!!!"
	LockIn.clear()
	time.sleep(3)
	LockIn.write("ie 0")
	time.sleep(3)
	LockIn.write("lf 0")
	time.sleep(3)
	LockIn.write("asm")
	time.sleep(10)
	LockIn.write("axo")
	time.sleep(3)
#	LockIn.write("xdb 1")
#	time.sleep(3)
	LockIn.write("tc 5")
	time.sleep(3)

def LockIn_clear():
	LockIn.clear()
	print "LockIn cleaned!"


def LockIn_measure():
	time.sleep(0.1)
	tt = time.time()
	LockIn.write("x")
	gpib_read = LockIn.read()
#	print ">>>>>>>>> characters from GPIB:  ",gpib_read
#	sign=gpib_read.split()[0]
#	value=gpib_read.split()[1]
#	outX = float(sign+value)
	outX = float(gpib_read.replace(" ",""))
	return outX,tt


##############################
######### field vs current tables ######
##############################


def field2curr(the_field):
	my_pole = pole_type.get()
	my_gap = float(gap_value.get())
	if my_pole == "pole_20":
		my_table = 'D:\DEMAG-MOKE\CALIBRATION_GMW\magn_table_20poles.txt'
	elif my_pole == "pole_40":
		my_table = 'D:\DEMAG-MOKE\CALIBRATION_GMW\magn_table_40poles.txt'

	aa = loadtxt(my_table,skiprows=1)
	table_gaps = aa[0,1:]
	table_currents = aa[1:,0]
	table_fields = [aa[1:,ii] for ii in range(1,len(table_gaps)+1)]

	dict_gaps={}
	for temp_gap,temp_field in zip(table_gaps,table_fields):
		dict_gaps[temp_gap] = temp_field

	curr_interp = interp1d(dict_gaps[my_gap],table_currents)

	if the_field >= 0:
		the_current = curr_interp(abs(the_field))
	else:
		the_current = (-1)*curr_interp(abs(the_field))
	return the_current

def curr2field(the_current):
	my_pole = pole_type.get()
	my_gap = float(gap_value.get())
	if my_pole == "pole_20":
		my_table = 'D:\DEMAG-MOKE\CALIBRATION_GMW\magn_table_20poles.txt'
	elif my_pole == "pole_40":
		my_table = 'D:\DEMAG-MOKE\CALIBRATION_GMW\magn_table_40poles.txt'

	aa = loadtxt(my_table,skiprows=1)
	table_gaps = aa[0,1:]
	table_currents = aa[1:,0]
	table_fields = [aa[1:,ii] for ii in range(1,len(table_gaps)+1)]

	field_interp = interp2d(table_currents,table_gaps,table_fields)

	if the_current >= 0:
		the_field = field_interp(abs(the_current),my_gap)[0]
	else:
		the_field = (-1)*field_interp(abs(the_current),my_gap)[0]
	return the_field

##############################
######### field control section ######
##############################


def set_field():
	field = float(F1.get())
	kepco.write("*RST")
	kepco.write("FUNC:MODE CURR")
	kepco.write("VOLT 5.0e1")
	kepco.write("OUTP ON")

	while (field2curr(field) >= 3.0):
		field = tkSimpleDialog.askfloat('MAGNET OVERLOAD','Choose a new value for the field or decrease the gap!')

	my_write_curr = field2curr(field)
	kepco.write("CURR %f"%(my_write_curr))
	time.sleep(0.1)
	my_read_curr = float(kepco.ask("MEAS:CURR?"))
	my_read_field = curr2field(my_read_curr)
	print "FIELD SET TO: ",my_read_field
	del my_write_curr
	del my_read_curr
	del my_read_field

def kepcoInit():
	kepco.write("*RST")
	kepco.write("FUNC:MODE CURR")
	kepco.write("VOLT 5.0e1")
	kepco.write("OUTP ON")

def set_field_zero():
	field = 0.0
	kepco.write("*RST")
	kepco.write("FUNC:MODE CURR")
	kepco.write("VOLT 5.0e1")
	kepco.write("OUTP ON")
	kepco.write("CURR %f"%(field))
#	kepco.write("OUTP OFF")
	print "FIELD SET TO: ",field

##############################
######### DEMAG section ######
##############################

def demagnetize():
	max_field = float(F1.get())
	steps = int(F2.get())
	kepcoInit()

	while (field2curr(max_field) >= 3.0):
		max_field = tkSimpleDialog.askfloat('MAGNET OVERLOAD','Choose a new value for the field or decrease the gap!')
	step_field = max_field/(steps+1)
	list_fields = r_[max_field:step_field/2-step_field/10:-step_field]

	for my_field in list_fields:
		my_write_curr = field2curr(my_field)
		kepco.write("CURR %f"%(my_write_curr))
		#print "FIELD++ = ",my_val
		time.sleep(0.2)
		my_read_curr = float(kepco.ask("MEAS:CURR?"))
		my_read_field = curr2field(my_read_curr)
		print "MEASURED FIELD:  ",my_read_field
		my_back_field = my_field-step_field/2
		my_back_write_curr = field2curr(my_back_field)
		kepco.write("CURR %f"%(-my_back_write_curr))
		#print "FIELD-- = ",-my_val_back
		time.sleep(0.2)
		my_read_curr = float(kepco.ask("MEAS:CURR?"))
		my_read_field = curr2field(my_read_curr)
		print "MEASURED FIELD:  ",my_read_field
	kepco.write("CURR 0.0")
	kepco.write("OUTP OFF")
	print "sample demagnetized!"
	del my_write_curr
	del my_read_curr
	del my_read_field
	del my_field

##############################
######### SCANS section ######
##############################

def timescan():
	fileName = e1.get()
	pn = int(e2.get())
	delay = float(e3.get())
	OUT = []
	TT = []
	dataPathLoc = dataPath()
	try:
		os.stat(dataPathLoc)
	except:
		os.mkdir(dataPathLoc)
	my_file = open(dataPathLoc+'\\'+fileName+'.txt','w')
	my_head = 'index'+' '+'outX'+'\n'
	my_file.writelines(my_head)
	for step in range(pn):
		outx_tmp,tt = LockIn_measure()
		outx = outx_tmp
		OUT.append(outx)
		TT.append(tt)
		plot_update(TT,OUT)
		my_line = str(step)+' '+str(outx)+'\n'
		my_file.writelines(my_line)
		time.sleep(delay)
	my_file.close()


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
#	with open(m_Path+'\\'+root_fileName+'.txt','w') as outFile:
#		for my_field in steps:
#			my_write_curr = field2curr(float(my_field))
#			kepco.write("CURR %f"%(my_write_curr))
#			outx_tmp,tt = LockIn_measure()
#			outx = outx_tmp
#			my_read_curr = float(kepco.ask("MEAS:CURR?"))
#			my_read_field = curr2field(my_read_curr)
#			print "MEASURED FIELD:   ",my_read_field
#			FIELDS.append(my_read_field)
#			OUT.append(outx)
#			plot_update(FIELDS,OUT)
#			outFile.writelines(str(my_read_field)+" "+str(outx)+"\n")
#			time.sleep(0.01)
#		del my_field
#		del my_write_curr
#		del my_read_curr
#		del my_read_field
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
#	del YY_mean
#	del YY_sum
#	YY_sum = zeros(len(steps),float)
#	for index in range(mm):
#		YY_sum = [(YY_sum[ii]+YY[index][ii]) for ii in range(len(list(steps2)+list(steps3)))]
#	YY_mean = [(YY_sum[ii]/mm) for ii in range(len(list(steps2)+list(steps3)))]
#	plot_update(FIELDS,OUT,'Current [Amp]',FIELDS,YY_mean,'Current [Amp]')
	with open(m_Path+"\\"+root_fileName+"_MEAN.txt","w") as outFile:
		for index,my_field in enumerate(list(steps2)+list(steps3)):
			outFile.writelines(str(my_field)+" "+str(YY_mean[index])+"\n")
		del my_field
	print "SEQUENCE FINISHED ! CHECK YOUR FILES!!!!!!!!!"

#######################
#### GUI section ######
#######################


data1 = []
data2 = []
TT = []

root = Tk.Tk()
root.title('HERMES DEMAGNETIZATION - MOKE SETUP')
fig = Figure()
ax = fig.add_subplot(211)
ax.grid(True)
ax.set_ylabel('Raw Intensity [a.u.]')
#ax.set_title('RAW DATA')
#ax.text(0.85,1.0,'Raw Data')
bx = fig.add_subplot(212)
bx.grid(True)
bx.set_ylabel('Mean Intensity [a.u.]')
bx.set_xlabel('field [T]')
#bx.set_title('LINEARIZED + MEAN DATA')
#bx.text(0.7,1.0,'Linearized + Mean Data')
#fig.tight_layout()
canv = FigureCanvasTkAgg(fig,master=root)
canv.show()
canv.get_tk_widget().pack(fill='both',expand=True,side = 'right')

#--------------------------------------------magnetSetupFrame------------------------------------------------------
magnetSetupFrame = Tk.Frame(root, relief='groove', bd=3)
Tk.Label(magnetSetupFrame,text="MAGNET:\n poles type and gap",font='bold',bg='blue',fg='yellow').pack(fill='x',side='top')
#Tk.Label(magnetSetupFrame,text="pole_type: ").pack(padx=2)
pole_type = Tk.Entry(magnetSetupFrame)
pole_type.insert(Tk.END,'pole_20')
pole_type.pack(side='left')
#Tk.Label(magnetSetupFrame,text="gap value: ").pack(side='top')
gap_value = Tk.Spinbox(magnetSetupFrame,values=(0.5,7.5,10,15,20,25,30,40))
gap_value.pack(side='left')
magnetSetupFrame.pack(fill='x',side='top',padx=5,pady=5)

#------------------------------------------------motorFrame--------------------------------------------------
motorFrame = Tk.Frame(root, relief='groove', bd=3)
Tk.Label(motorFrame, text='MOTOR CONTROL',font='bold', bg='blue',fg='yellow').pack(fill='x',side='top')
accFrame = Tk.Frame(motorFrame,padx=5)
Tk.Label(accFrame, text='ACCELERATION').pack(side='left')
accEntry = Tk.Spinbox(accFrame,from_ = 300, to = 16000, increment = 10)
accEntry.pack(side='right',padx=5)
decFrame = Tk.Frame(motorFrame,padx=5)
Tk.Label(decFrame, text='DECELERATION').pack(side='left')
decEntry = Tk.Spinbox(decFrame,from_ = 300, to = 16000, increment = 10)
decEntry.pack(side='right',padx=5)
velFrame = Tk.Frame(motorFrame,padx=5)
Tk.Label(velFrame, text='VELOCITY').pack(side='left')
velEntry = Tk.Spinbox(velFrame,from_ = 100, to = 10000, increment = 10)
velEntry.pack(side='right',padx=5)

motorFrame.pack(fill='x',side='top',padx=5,pady=5)
accFrame.pack(fill='x',side='top')
decFrame.pack(fill='x',side='top')
velFrame.pack(fill='x',side='top')
Tk.Button(motorFrame,text="MOVE",bd=2,relief='raise',bg='green',command=lambda:test_motor()).pack(fill='x',side='top')

#----------------------------------------------fieldControlFrame----------------------------------------------------
fieldControlFrame = Tk.Frame(root, relief='groove', bd=3)
Tk.Label(fieldControlFrame,text="FIELD CONTROL",font='bold',bg='blue',fg='yellow').pack(fill='x',side='top')
setFieldFrame = Tk.Frame(fieldControlFrame,padx=5)
Tk.Label(setFieldFrame,text="FIELD").pack(side='left')
F1 = Tk.Spinbox(setFieldFrame,from_ = 0.001, to = 2.0, increment = 0.001)
F1.pack(side='right',padx=5)
setStepsFrame = Tk.Frame(fieldControlFrame,padx=5)
Tk.Label(setStepsFrame,text="STEPS").pack(side='left')
F2 = Tk.Spinbox(setStepsFrame,from_ = 1, to = 4000, increment = 10)
F2.pack(side='right',padx=5)
Tk.Button(fieldControlFrame, text='DEMAGNETIZE',bd=2,bg='pink',relief='raise',activebackground='red',command=lambda:demagnetize()).pack(fill='x',side='bottom')
Tk.Button(fieldControlFrame, text='SET FIELD',bd=2,bg='green',relief='raise',activebackground='green',command=lambda:set_field()).pack(fill='x',side='bottom')
fieldControlFrame.pack(fill='x',side='top',padx=5,pady=5)
setFieldFrame.pack(fill='x',side='top')
setStepsFrame.pack(fill='x',side='top')

#------------------------------------------------sampleName--------------------------------------------------
dataPathFrame = Tk.Frame(root, relief='groove', bd=3)
Tk.Label(dataPathFrame,text="SAMPLE NAME",font='bold',bg='blue',fg='yellow').pack(fill='x',side='top')
sampleNameEntry = Tk.Entry(dataPathFrame)
sampleNameEntry.insert(Tk.END,'Your_Sample_Name')
sampleNameEntry.pack(fill='x',side='top')
dataPathFrame.pack(fill='x',side='top',padx=5,pady=5)

#-------------------------------------------------timescanFrame-------------------------------------------------
timescanFrame = Tk.Frame(root,relief='groove',bd=3)
Tk.Label(timescanFrame,text="TIMESCAN",font='bold',bg='blue',fg='yellow').pack(fill='x',side='top')
timescanNameFrame = Tk.Frame(timescanFrame,padx=5)
Tk.Label(timescanNameFrame,text="File Name").pack(side='left')
e1 = Tk.Entry(timescanNameFrame)
e1.insert(Tk.END,'Your_timescan_Name')
e1.pack(side = 'right',padx=5)
setPointsTimescanFrame = Tk.Frame(timescanFrame,padx=5)
Tk.Label(setPointsTimescanFrame,text="No. of points").pack(side='left')
e2 = Tk.Spinbox(setPointsTimescanFrame,from_ = 10, to = 1000, increment = 10)
e2.pack(side = 'right',padx=5)
setDelayTimescanFrame = Tk.Frame(timescanFrame,padx=5)
Tk.Label(setDelayTimescanFrame,text="Delay").pack(side='left')
e3 = Tk.Spinbox(setDelayTimescanFrame, from_ = 0.1, to = 10, increment = 0.1)
e3.pack(side = 'right',padx=5)
timescanFrame.pack(fill='x',side = 'top',padx=5,pady=5)
timescanNameFrame.pack(fill='x',side = 'top')
setPointsTimescanFrame.pack(fill='x',side = 'top')
setDelayTimescanFrame.pack(fill='x',side = 'top')
Tk.Button(timescanFrame, text='TIMESCAN',bd=2,relief='raise',bg='green',activebackground='green',command=lambda:timescan()).pack(fill='x',side = 'bottom')

#------------------------------------------------hystFrame--------------------------------------------------
hystFrame = Tk.Frame(root,relief='groove',bd=3)
Tk.Label(hystFrame,text="HYSTERESIS",font='bold',bg='blue',fg='yellow').pack(fill='x',side='top')
hystNameFrame = Tk.Frame(hystFrame,padx=5)
Tk.Label(hystNameFrame,text="File Name").pack(side='left')
h1 = Tk.Entry(hystNameFrame)
h1.insert(Tk.END,'Your_HYST_Name')
h1.pack(side = 'right',padx=5)
setHystFieldFrame = Tk.Frame(hystFrame,padx=5)
Tk.Label(setHystFieldFrame,text="Field MAX [T]").pack(side='left')
h2 = Tk.Spinbox(setHystFieldFrame,from_ = 0.0001, to = 1.5, increment = 0.0001)
h2.pack(side = 'right',padx=5)
setHystStepFrame = Tk.Frame(hystFrame,padx=5)
Tk.Label(setHystStepFrame,text="Field STEP [T]").pack(side='left')
h3 = Tk.Spinbox(setHystStepFrame,from_ = 0.0001, to = 1.5, increment = 0.0001)
h3.pack(side = 'right',padx=5)
setHystMultiFrame = Tk.Frame(hystFrame,padx=5)
Tk.Label(setHystMultiFrame,text="Number of scans").pack(side='left')
h4 = Tk.Spinbox(setHystMultiFrame, from_ = 2, to = 1000, increment = 1)
h4.pack(side = 'right',padx=5)
hystFrame.pack(fill='x',side = 'top',padx=5,pady=5)
hystNameFrame.pack(fill='x',side = 'top')
setHystFieldFrame.pack(fill='x',side = 'top')
setHystStepFrame.pack(fill='x',side = 'top')
Tk.Button(hystFrame, text='SINGLE SCAN',bd=2,relief='raise',bg='green',activebackground='green',command=lambda:hyst()).pack(fill='x',side = 'top')
setHystMultiFrame.pack(fill='x',side = 'top')
Tk.Button(hystFrame, text='MULTIPLE SCANS',bd=2,relief='raise',bg='green',activebackground='green',command=lambda:m_hyst()).pack(fill='x',side = 'top')

#------------------------------------------------exitButton--------------------------------------------------
exitButton = Tk.Button(root,text="EXIT",bd=2,relief='raise',bg='red',command=lambda:mokeExit())
exitButton.pack(side='bottom')

##############################
######### PLOTTING section ######
##############################

def plot_update(x1,data1):
	ax.clear()
	ax.grid(True)
	ax.set_ylabel('Raw Intensity [a.u.]')
	ax.text(0.85,1.0,'Raw Data')
	ax.plot(x1,data1,'r-o',mfc='w',markersize=8,label='Raw Intensity')
	ax.legend(loc=4)
	canv.draw()
	canv.get_tk_widget().pack(fill='both',expand=True,side = 'right')

def plot_update_multi(x1,data1,scanNo):
	ax.clear()
	ax.grid(True)
	ax.set_ylabel('Raw Intensity [a.u.]')
	ax.text(0.85,1.0,'Raw Data')
	the_label = 'Raw Intensity - scan no. ' + str(scanNo)
	ax.plot(x1,data1,'r-o',mfc='w',markersize=8,label=the_label)
	ax.legend(loc=4)
	canv.draw()
	canv.get_tk_widget().pack(fill='both',expand=True,side = 'right')

def plot_update_mean(x2,data2):
	bx.clear()
	bx.grid(True)
	bx.set_ylabel('Mean Intensity [a.u.]')
	bx.set_xlabel('Field [T]')
	bx.text(0.7,1.0,'Linearized + Mean Data')
	bx.plot(x2,data2,'b-o',mfc='w',markersize=8,label='Linearized + Mean Intensity')
	bx.legend(loc=4)
	canv.draw()
	canv.get_tk_widget().pack(fill='both',expand=True,side = 'right')


def mokeExit(): root.destroy()

kepco.write("*RST")
set_field_zero()


root.after(1, plot_update)
root.after(1, plot_update_mean)
root.mainloop()
