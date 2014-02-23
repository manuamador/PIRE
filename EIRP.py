# -*- coding: utf-8 -*-
"""
Created on Tue Apr 16 15:15:55 2013

@author: J89950
"""

from __future__ import division
import time
import visa
import scipy
import os
from numpy import *
import matplotlib.pyplot as plt



#Instruments modules
import Spectrum
import TurnTable


nom=raw_input('Enter the name of the equipment?')
if (os.path.isdir('Results_'+nom)==False):
    os.mkdir('Results_'+nom)
    
#Calibration files
Correction_H=loadtxt('SynthCal_Pol_H.txt')   
Correction_V=loadtxt('SynthCal_Pol_V.txt')

os.chdir('Resultats_'+nom)

f=Correction_H[0,:]

###############################################
##########   Testing parameters  ##############
###############################################

fstart=f[0]      #Start frequency
fstop=f[len[f]]       #Stop frequency
fcenter=0.5*(fstart+fstop)   #Center frequency       
fspan=fstop-fstart   #Span
RBW=1e6       #RBW size in Hz
VBW=100e3       #VBW size in Hz
SwpPt=len(f)       #Number of points

N=37      #Number of incident angles
Angles=linspace(0,360,N) 
Pol=2       #Number of polarizations
Exp=3    #Number of cutting planes
Tmes=5     #dwell time



###Stop criterion
###channels center frequencies (european wifi)
##f0=2.412e9
##fn=2.472e9
##n=13 #number of channels
##fc=linspace(f0,fn,n)
###channel center frequencies indexes
##peaksindx=zeros(len(fc))
##for i in range(len(fc)):
#    peaksindx[i]=argmin(abs(f-fc[i]))


Level_criterion=-35


print '___________________________\n Instruments initializations\n'
print '\nSpectrum analyzer:'
Spectre=Spectrum.FSV30()
Spectre.reset()
Spectre.startFreq(fstart)    
Spectre.stopFreq(fstop)      
Spectre.RBW(RBW)             
Spectre.SweepPoint(SwpPt)    
Spectre.MaxHold()            
Spectre.UnitDBM()            

print '\nTurn table:'
TTable=TurnTable.PlateauCA()
TTable.reset()


print '____________________\nMeasurement\n'                 
Measurement=empty([Pol,Exp,N,2])
Raw_Traces=empty([Pol,Exp,N,2,SwpPt])

for l in range (0,Pol):
    if l==0:
        print 'Vertical Polarization'
        Polarization='V'
        
    else:
        print 'Horizontal Polarization'
        Polarization='H'
        
        
    for k in range(Exp):
        print ("Exposition %s " %k)
        raw_input("\n Antenna polarization : %s, Cutting plane : %i \n Press Enter to continue...\n" %(Polarization,k))
        for j in range(0,len(Angles)):              
            print ("Angle de %s " %(Angles [j]))
            TTable.setPosition(Angles [j])
            Spectre.readwrite()
            Spectre.MaxHold()                   
            time.sleep(Tmes)                    
            raw_input("\n Press Enter to validate the measurement\n")
            Level = Spectre.getTrace(SwpPt)    
            if Polarization=='V':
                cLevel=Level+Correction_V[:,1]
            else:                    
                cLevel=Level+Correction_H[:,1]
            #criterion automatic stop
            #while (min(cLevel[peaksindx])<Level_criterion): #every channel
            #while (min(cLevel[peaksindx])<Level_criterion): #one channel
            #while (mean(cLevel[peaksindx]<Level_criterion))<p/n: #p channels among n
            #	Level = Spectre.getTrace(SwpPt)    
            #	if Polarization=='V':
            #    	cLevel=Level+Correction_V[:,1]
            #	else:                    
            #    	cLevel=Level+Correction_H[:,1]
            #	time.sleep(0.5)
            Trace=array((Frequence,Level))     
            MaxLevel=max(cLevel)           
            MaxIdx =cLevel.argmax()             
            Measurement[l,k,j,:]=array([f[MaxIdx],MaxLevel])
            Raw_Traces[l,k,j,:]=Trace
            print 'Max EIRP = %2.2f mW/MHz' %(10**(Measurement[l,k,j,1]/10))
            
        r=(10**((Measurement[l,k,:,1])/10))           
        plt.polar((Angles*pi/180),r)
        Graphlin= 'Graph_Pol_%s_Exp%s' %(Polarization,k)
        plt.ylabel('Puissance max mW')
        plt.title("Diagramme de rayonnement en mW")
        plt.savefig(Graphlin+'.pdf',bbox='tight')
        plt.savefig(Graphlin+'.png',bbox='tight')
        plt.clf()

    
        plt.plot(Angles,Measurement[l,k,:,1])                 
        plt.ylabel('Puissance max en dBm')
        plt.xlabel("Angles en degres")
        plt.title("Diagramme de rayonnement en dBm")
        plt.xlim(0,360)
        plt.grid(True)
        GraphdBm= 'Graph_lin_%s_Exp%s' %(Polarisation,k) 
        plt.savefig(GraphdBm+'pdf',bbox='tight')
        plt.savefig(GraphdBm+'png',bbox='tight')
        plt.clf()

        fname = ( '%s_Exp%s.txt')  %(Polarization,k)
        savetxt(fname,Measurement[l,k,:])               

savez('Bin_Results.npz',Measurement=Measurement,Raw_Traces=Raw_Traces)
