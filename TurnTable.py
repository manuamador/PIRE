# -*- coding: utf-8 -*-
"""
Created on Fri Jan 03 10:26:57 2014
TurnTable control module
"""
import time
from visa import instrument

class PlateauCA():
    def __init__(self,address=7):
        self.ctrl = instrument("GPIB::%s" %address)
        self.anglemax=400
        self.anglemin=-200
        
    def reset(self):
        """ RESET """
        time.sleep(0.5)
        self.ctrl.write("?IDN*")
        self.ctrl.write("*RST")
        self.ctrl.write("LD 0 DG NP")
        self.ctrl.write("GO")
        s='1'
        while s=='1':
            time.sleep(0.5)
            s=self.ctrl.ask("BU")
        return True
    
    def getPosition(self):
        """ RF OFF """
        return self.ctrl.ask("CP")
    
    def setPosition(self,value):
        time.sleep(0.5)
        if value<=self.anglemax and value>=self.anglemin:
            self.ctrl.write("LD %s DG NP" %value)
            self.ctrl.write("GO")
            s='1'
            while s=='1':
                time.sleep(0.5)
                s=self.ctrl.ask("BU")
                
        else:
            print('Angle non valide')
        return True
