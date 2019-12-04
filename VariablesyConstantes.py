# -*- coding: utf-8 -*-
"""
Created on Tue Jul 16 08:31:15 2019

@author: 2IO
"""
import numpy as np
import Funciones as func

BBDD='BBDDFerroxcube.xlsx'                             # DataBase file name
BBDDMaterial="Material"                                # DataBase materials page name
BBDDNucleo="Núcleo"                                    # DataBase nucleos page name

RutaOutput=r'C:\Users\2IO\Desktop\Prueba1.xlsx'        #Results path
DCM=0    
Steinmetz=1

OptimizacionPerdidas=1
Noptimizaciones=0

CopperResistivity=0.0171/1e6                           #Copper Resistivity (Ohm*mm2/m)
mu0=4*np.pi*1e-7                                       #Air Permeability

Ploteo=0  

#%% Theoretical data of Flyback generic design

OutputPower=12.5                               #Output Power (W)                                      
OutputVoltage=5                             #Output Voltage (V)
SwitchingFrecuency=150e3                    #Switching Frequency (Hz)
PrimaryVoltage=48                          #Input Voltage (V)
Vsec=6                                      #??????????????????????????????????????????????????
PercentageDutyCycle=50                      #Maximum Duty Cycle (%)
InductanceValue=220e-6                                      #Inductance Value (H)
GridFrecuency=0                             #Grid Line Frequency (Hz)

#%% Transformer Maximum Parameters

J=5                                         #Maximum Current density (A/mm2)
PercentageMaximumBsat=60                    #Maximum Permeability Rate (%)
MaximumWindowRate=30                        #Maximum Window Ocuppation Rate (%)
MaximumAirGap=10e-3                         #Maximum Airgap (m)   
NArmonicos=pow(2,3)                         #Number of armonics calculated in fourier spectrum 2^3=8

#%% Additional Calculus (From Rated parameters to Absolutes values)

AbsoluteDutyCycle=PercentageDutyCycle/100
AbsoluteMaximumBsat=PercentageMaximumBsat/100
AbsoluteWindowRate=MaximumWindowRate/100

TurnsRatio=PrimaryVoltage/(OutputVoltage)*AbsoluteDutyCycle/(1-AbsoluteDutyCycle)                #Turns Ratio

#%% Current Calculation

MeanPrimaryCurrent, PrimaryCurrentRipple, MaximumPrimaryCurrent, MinimumPrimaryCurrent =(
        func.CurrentCalculation(PrimaryVoltage, OutputPower, 
                           AbsoluteDutyCycle, InductanceValue, SwitchingFrecuency))

MeanSecondaryCurrent, SecondaryCurrentRipple, MaximumSecondaryCurrent, MinimumSecondaryCurrent =(
        func.CurrentCalculation(Vsec, OutputPower, 
                           AbsoluteDutyCycle, InductanceValue, SwitchingFrecuency))

"""
PrimaryMeanCurrent=OutputPower/(OutputVoltage*TurnsRatio)                                       #Primary mean current (A)
SecondaryMeanCurrent=PrimaryMeanCurrent*TurnsRatio                                              #Secondary mean current (A)
PrimaryCurrentRipple=PrimaryVoltage*AbsoluteDutyCycle/(InductanceValue*SwitchingFrecuency)            #Primary Current Ripple (A)

MaximumPrimaryCurrent=PrimaryMeanCurrent+PrimaryCurrentRipple/2                 #Maximum Primary Current
MinimumPrimaryCurrent=PrimaryMeanCurrent-PrimaryCurrentRipple/2                 #Minimum Primary Current

MaximumSecondaryCurrent=MaximumPrimaryCurrent*TurnsRatio                                #Maximum Secondary Current
MinimumSecondaryCurrent=MinimumPrimaryCurrent*TurnsRatio                                #Minimum Secondary Current
"""

#%% Wire Parameters

PrimaryWireMaximumWidth=2                                                               #Primary Wire Maximum Width (mm)
PrimaryWireMinimumWidth=float(round(np.sqrt(MeanPrimaryCurrent/J/np.pi),1))             #Primary Wire Minimum Width (mm)
PrimaryMaximumParallels=1                                                               #Primary Maximum Parallels
PrimaryMinimumParallels=1                                                               #Primary Minimum Parallels

SecondaryWireMaximumWidth=2                                                             #Secondary Wire Maximum Width (mm)
SecondaryWireMinimumWidth=float(round(np.sqrt(MeanSecondaryCurrent/J/np.pi),1))         #Secondary Wire Minimum Width (mm)
SecondaryMaximumParallels=2                                                             #Secondary Maximum Parallels
SecondaryMinimumParallels=1                                                             #Secondary Minimum Parallels