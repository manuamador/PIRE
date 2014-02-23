# -*- coding: utf-8 -*-
"""
Created on Wed Apr 24 12:53:46 2013

Calibration of the fully anechoic room 
"""
from __future__ import division
import scipy
from numpy import *
import os
import time
import visa


#Instrument modules
import Spectrum
import SignalGenerator

nom_test = raw_input('Enter the name of the calibration?')   
if os.path.isdir('Calibration_'+nom_test)==False:            #verify if the folder exists
   os.mkdir('Calibration_'+nom_test)						#create the folder
    
os.chdir('Calibration_'+nom_test)


###############################################
##########   Testing parameters  ##############
###############################################

fstart=2.5e9      #start frequency
fstop=2.7e9       #stop frequency
fcenter=0.5*(fstart+fstop)   #center frequency        
fspan=fstop-fstart   #Span
RBW=1e6      #RBW size in Hz
VBW=100e3       #VBW size in Hz
SwpPt=1001       #number of points
f=linspace(fstart,fstop,SwpPt) #frequency points

Pol=2       #Number of polarizations (vertical + horizontal = 2)
CableLoss=2.7 # Cable loss in dB
P_gene=0+CableLoss #Signal generator power to get 0 dBm at the antenna input



#Antenna gain (from calibration) interpolation for our measurement frequencies
Logper_AH=array([4.62,5.85,5.92,6.43,6.81,6.86,7.58,7.35,7.54,7.73,8.28,8.16,7.93,8.07,8.38,8.06,8.11,8.57,7.98,8.25,8.06,7.80,8.10,7.63])
G_ant_lin=transpose(array([linspace(1e9,12.5e9,24),10**(Logper_AH / 20)]))    # frequency | Antenna gain (linear values)
G_ant_inter_lin=scipy.interp(f,G_ant_lin[:,0],G_ant_lin[:,1])   # interpolated gain (linear vlaues)
G_ant_inter_db=transpose(array([f,20*log10(G_ant_inter_lin)]))  # interpolated gain (dB)   


print '__________________________\nInstruments initializations\n'
print '\nSpectrum analyzer:'
Spectre=Spectrum.FSV30()
Spectre.reset()
#Spectre.startFreq(fstart)    #Réglage de la fréquence de départ
#Spectre.stopFreq(fstop)      #Réglage de la fréquence de fin
Spectre.RBW(RBW)             #Réglage du RBW
Spectre.SweepPoint(SwpPt)    #Réglage du nombre de pts
Spectre.UnitDBM()            #Réglage en de l'unité en dBm
Spectre.SPAN(fspan)
Spectre.centerFreq(fcenter)


print '\nSignalGenerator:'
gene=SignalGenerator.RS_SMF100A()
gene.reset()
gene.arret() #RF OFF
gene.setPower(P_gene)
gene.setFreq(fcenter)



print '________________________________\nCalibration of the fully anechoic room\n'

           
Calibration=empty([Pol,len(f),2])

for l in range (0,Pol):
	SyntheseCal=empty([0,2])  
    if l==0:
        raw_input ('\nVertical polarization, press Enter to continue')
        Polarization='V'     
    else:
        raw_input ('\nHorizontal polarization, press Enter to continue')
        Polarization='H'
    for i in range(0,len(f)):
        gene.setFreq(f[i])
        gene.marche()
        time.sleep(0.1)       
        Niveau = Spectre.getTrace(SwpPt)
        MarkerValue=Spectre.MarkerMax(f[i])
        Correction=(0+G_ant_inter_db[i,1]-float(MarkerValue))
        SyntheseCal=vstack([SyntheseCal,array([f[i],Correction])])
        Calibration[l,i,:]=array([f[i],Correction])
        print ("f=2.3%f MHz, C=%2.2f dB") %(f[i]/1e6,Correction)
    fname = ('SynthCal_Pol_%s.txt')  %(Polarization) 
    savetxt(fname,SyntheseCal[0:,:])
fnamez = 'Calibration_%s.npz' %nom_test
savez(fnamez,Calibration=Calibration)        
      
gene.arret() 

