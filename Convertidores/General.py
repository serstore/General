# -*- coding: utf-8 -*-
"""
Created on Fri Nov 22 08:38:00 2019

@author: 2IO
"""

def Flyback(InputVoltage, OutputVoltage, OutputPower, FrequencySwitching, 
            CurrentRipplePercentage, VoltageRipplePercentage):
    TurnsRatio=InputVoltage/OutputVoltage
    DutyCycle=OutputVoltage*TurnsRatio/(InputVoltage+OutputVoltage*TurnsRatio)
    OutputMeanCurrent=OutputPower/OutputVoltage
    InputMeanCurrent=OutputMeanCurrent/TurnsRatio
    Inductance=((InputVoltage*DutyCycle)/
                (InputMeanCurrent*CurrentRipplePercentage*FrequencySwitching))
    Capacitance=((CurrentRipplePercentage*InputMeanCurrent*TurnsRatio*DutyCycle/
                  VoltageRipplePercentage*OutputVoltage))
    
    return TurnsRatio, DutyCycle, Inductance, Capacitance

def Boost(InputVoltage, OutputVoltage, OutputPower, FrequencySwitching, 
            CurrentRipplePercentage, VoltageRipplePercentage):
    DutyCycle=(OutputVoltage-InputVoltage)/OutputVoltage
    OutputMeanCurrent=OutputPower/OutputVoltage
    InputMeanCurrent=OutputMeanCurrent/(1-DutyCycle)
    Inductance=((InputVoltage*DutyCycle)/
                (InputMeanCurrent*CurrentRipplePercentage*FrequencySwitching))
    Capacitance=((CurrentRipplePercentage*InputMeanCurrent*DutyCycle/
                  VoltageRipplePercentage*OutputVoltage))
    
    return DutyCycle, Inductance, Capacitance

def Buck(InputVoltage, OutputVoltage, OutputPower, FrequencySwitching, 
            CurrentRipplePercentage, VoltageRipplePercentage):
    DutyCycle=OutputVoltage/(OutputVoltage-InputVoltage)
    OutputMeanCurrent=OutputPower/OutputVoltage
    InputMeanCurrent=OutputMeanCurrent*(1-DutyCycle)/DutyCycle
    Inductance=((InputVoltage*DutyCycle)/
                (InputMeanCurrent*CurrentRipplePercentage*FrequencySwitching))
    Capacitance=((CurrentRipplePercentage*InputMeanCurrent*DutyCycle/
                  VoltageRipplePercentage*OutputVoltage))
    
    return DutyCycle, Inductance, Capacitance
