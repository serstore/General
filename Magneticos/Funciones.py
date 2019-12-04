# -*- coding: utf-8 -*-
"""
Created on Mon Nov 18 10:47:56 2019

@author: 2IO
"""
import pandas as pd
import numpy as np
import scipy.signal as sig
import scipy.fftpack as fourier
import matplotlib.pyplot as plt

#%% INDUCTANCE CURRENT CALCULATION
def CurrentCalculation(InductanceVoltage, PowerProcessed, AbsoluteDutyCycle,
                       InductanceValue, SwitchingFrecuency):
    
    MeanCurrent=PowerProcessed/InductanceVoltage                                #Primary mean current (A)
    CurrentRipple=(InductanceVoltage*AbsoluteDutyCycle/
                   (InductanceValue*SwitchingFrecuency))                        #Primary Current Ripple (A)
    
    MaximumCurrent=MeanCurrent+CurrentRipple/2                                  #Maximum Primary Current
    MinimumCurrent=MeanCurrent-CurrentRipple/2                                  #Minimum Primary Current
    
    return MeanCurrent, CurrentRipple, MaximumCurrent, MinimumCurrent

#%% LOAD DATABASE
def LoadNucleos(BBDD, CoreBBDD):


    Core=pd.read_excel(BBDD,sheet_name=CoreBBDD)                                #Load Nucleos from Nucleo Sheet
    return Core

def LoadMaterials(BBDD, MaterialBBDD):
    Materials=pd.read_excel(BBDD,sheet_name=MaterialBBDD)                       #Load Materials from Material Sheet           
    return Materials
    
#%% EXTRACT MATERIALS DATA FROM DDBB
def ExtractMaterials(MaterialsDDBB, MaterialsRow, AbsoluteMaximumBsat=0.7):
    if MaterialsDDBB.iloc[MaterialsRow,1] is not None:
        Material={
                "Material":MaterialsDDBB.iloc[MaterialsRow,1],
                "Bsat":MaterialsDDBB.iloc[MaterialsRow,3]*1e-3,
                "K":MaterialsDDBB.iloc[MaterialsRow,7],
                "Alpha":MaterialsDDBB.iloc[MaterialsRow,8],
                "Beta":MaterialsDDBB.iloc[MaterialsRow,9],
                "muR":MaterialsDDBB.iloc[MaterialsRow,2],
                "MinimumFrequency": MaterialsDDBB.iloc[MaterialsRow,11],
                "MaximumFrequency": MaterialsDDBB.iloc[MaterialsRow,12]
                  }
        Material["BMax"]=AbsoluteMaximumBsat*Material["Bsat"]
                  
    return Material

#%% EXTRACT CORE DATA FROM DDBB
def ExtractCore(CoreDDBB, CoreRow):
    if ((type(CoreDDBB.iloc[CoreRow,1]) is int) or 
        (type(CoreDDBB.iloc[CoreRow,1]) is float) and ()):
        
        Core={
                "Core":CoreDDBB.iloc[CoreRow,0],
                "EffectiveVolume":CoreDDBB.iloc[CoreRow,1]*1e-9,
                "CoreEffectiveArea":CoreDDBB.iloc[CoreRow,2]*1e-6,
                "ColumnDiameter":CoreDDBB.iloc[CoreRow,30]*1e-3,
                "XWindow":CoreDDBB.iloc[CoreRow,31]*1e-3,
                "YWindow":CoreDDBB.iloc[CoreRow,32]*1e-3,
                "WindowArea":CoreDDBB.iloc[CoreRow,33]*1e-6,
                "XCore":str(CoreDDBB.iloc[CoreRow,7]),
                "YCore":str(CoreDDBB.iloc[CoreRow,8]),
                "ZCore":str(CoreDDBB.iloc[CoreRow,9]),
                "ThermalResistance":CoreDDBB.iloc[CoreRow,35]
            }
        
        Core["CoreEffectiveLengh"]=(Core["EffectiveVolume"]/
            Core["CoreEffectiveArea"])
        Core["XCore"]=float(Core["XCore"].replace(",","."))
        Core["YCore"]=float(Core["YCore"].replace(",","."))*2
        Core["ZCore"]=float(Core["ZCore"].replace(",","."))
            
    return Core

#%% INDUCTANCE PARAMETERS CALCULATION 
def Inductance(InductanceValue, BMax, CoreEffectiveArea, 
               MaximumPrimaryCurrent, rt):
    """
    CÁLCULO INDUCTANCIA
    """
    CurrentInductanceValue=0
    PrimaryTurns=0
    Precision=0.1                                                               #Inductance Precision
    BMaxint=BMax
    while (InductanceValue*Precision<=
           abs(CurrentInductanceValue-InductanceValue)):                 #Loop while InductanceValue different than InductanceValue required
        PrimaryTurns=(round((MaximumPrimaryCurrent*InductanceValue
                          /(BMaxint*CoreEffectiveArea))*2,0)/2)                 #Primary Turns
        CurrentInductanceValue=((PrimaryTurns*BMaxint*CoreEffectiveArea)
        /MaximumPrimaryCurrent)                                                 #Real Inductance
        BMaxint=BMaxint*0.9                                                     #Change Turns Number 
        if BMaxint<0.01:
            return
    InductanceValue=CurrentInductanceValue
    SecondaryTurns=round(PrimaryTurns/rt*2)/2                                   #Secondary Inductance and Round
    PrimaryTurns=SecondaryTurns*rt                                              #Rounding Primary Turns
    
    return InductanceValue, PrimaryTurns, SecondaryTurns          

#%% WINDOW PARAMETERS CALCULATION
def Window(WindowArea, AbsoluteWindowRate, PrimaryWireDiameter, 
            PrimaryParallels, PrimaryTurns, SecondaryWireDiameter=0, 
            SecondaryParallels=0, SecondaryTurns=0):
    """
    CÁLCULO Window
    """
    WireArea=(pow(PrimaryWireDiameter,2)*PrimaryParallels*PrimaryTurns+
                pow(SecondaryWireDiameter,2)*SecondaryParallels*
                SecondaryTurns)                                                 #Wires Area
    if WireArea>WindowArea*AbsoluteWindowRate:                                  #If not fit break out
        return 
    WindowRate=(WireArea)/WindowArea                                            #If fit extract the window ratio
    return WindowRate

#%% AIRGAP PARAMETERS CALCULATION
def AirGap(PrimaryTurns, CoreEffectiveLengh, MaximumAirGap, 
           CoreEffectiveArea, InductanceValue, muR, mu0=4*np.pi*1e-7):
    """
    CÁLCULO ENTREHIERRO
    """
    TotalReluctance=pow(PrimaryTurns,2)/InductanceValue                         #Total Reluctance
    CoreReluctance=CoreEffectiveLengh/(mu0*muR*CoreEffectiveArea)               #Core Reluctance
    AirGapReluctance=TotalReluctance-CoreReluctance                             #Airgap Reluctance
    AirGapLengh=round(AirGapReluctance*mu0*CoreEffectiveArea,5)                 #Airgap Length
    if AirGapLengh<0 or AirGapLengh>MaximumAirGap:                              #If not fit
        return
    return AirGapLengh

#%% WINDING LOSSES CALCULATION
def WindingLosses(ColumnWidth, MaximumCurrent, MeanCurrent, Turns, 
                  NumberOfParallels, Response, WireDiameter, SkinDepth, 
                  CopperResistivity=0.0171/1e6):
    """
    PÉRDIDAS DEVANADOS 
    """
    WireLength=ColumnWidth*np.pi*Turns                                          #Winding lenght
    FrequencyFourierCurrent=MaximumCurrent*Response/NumberOfParallels           #Fourier Current Spectrum
    RealWireRadio=np.array([None]*len(SkinDepth))                               #Real Wire Radium
    for x in range (0,len(SkinDepth)):
        if SkinDepth[x]<WireDiameter/2:
            RealWireRadio[x]=SkinDepth[x]
        else:
            RealWireRadio[x]=WireDiameter/2
    RealWireArea=(pow(RealWireRadio,2))*np.pi                                   #Real Wire Area 
    AC_Resistance=(CopperResistivity*WireLength)/RealWireArea                   #AC Resistance
    AC_Losses=pow(FrequencyFourierCurrent,2)*AC_Resistance                      #AC Power
    DC_Losses=(pow(MeanCurrent/NumberOfParallels,2)*CopperResistivity*
    WireLength/(pow(WireDiameter/2,2)*np.pi))                                   #DC Winding Losses
    TotalWindingLosses=(DC_Losses+np.sum(AC_Losses))*NumberOfParallels          #Total Winding Losses
    return TotalWindingLosses

#%% CORE LOSSES CALCULATION
def CoreLosses(InductanceValue, CoreEffectiveArea, Turns, MaximumCurrent, 
               MinimumCurrent, SwitchingFrecuency, EffectiveVolume, 
               K, Alpha, Beta):
    """
    CÁLCULO STEINMETZ
    """
    #BBiasMax=InductanceValue*IBiasMaxPrimario/(CoreEffectiveArea*PrimaryTurns)
    B_Max=InductanceValue*MaximumCurrent/(CoreEffectiveArea*Turns)                                #Beta Maximum
    B_Min=InductanceValue*MinimumCurrent/(CoreEffectiveArea*Turns)                                #Beta Minimum
    Delta_B=B_Max-B_Min                                                         #Delta Beta
    #IncrementoBBias=BBiasMax
    CoreLosses=(K*pow(SwitchingFrecuency,Alpha)*
             pow(Delta_B,Beta)*EffectiveVolume)                                 #Core Losses
    return CoreLosses

#%% UPDATE OUTPUT DATA
def UpdateExcelData(DatosExcel,Resultados):
    DatosExcel['Núcleo']=DatosExcel['Núcleo']+Resultados['Núcleo']
    DatosExcel['Material']=DatosExcel['Material']+Resultados['Material']
    DatosExcel['Diámetro del Cable Primario (mm)']=DatosExcel['Diámetro del Cable Primario (mm)']+Resultados['DiámetroCable Primario']
    DatosExcel['Número de Paralelos Primario']=DatosExcel['Número de Paralelos Primario']+Resultados['Número de Paralelos Primario']
    DatosExcel['Diámetro del Cable Secundario (mm)']=DatosExcel['Diámetro del Cable Secundario (mm)']+Resultados['DiámetroCable Secundario']
    DatosExcel['Número de Paralelos Secundario']=DatosExcel['Número de Paralelos Secundario']+Resultados['Número de Paralelos Secundario']
    DatosExcel['Longitud del Entrehierro (mm)']=DatosExcel['Longitud del Entrehierro (mm)']+Resultados['Longitud del Entrehierro']
    DatosExcel['Pérdidas del Núcleo (W)']=DatosExcel['Pérdidas del Núcleo (W)']+Resultados['Pérdidas del Núcleo']
    DatosExcel['Pérdidas de Devanados (W)']=DatosExcel['Pérdidas de Devanados (W)']+Resultados['Pérdidas de Devanados']
    DatosExcel['Pérdidas Totales (W)']=DatosExcel['Pérdidas Totales (W)']+Resultados['Pérdidas Totales']
    DatosExcel['Porcentaje de Ocupación (%)']=DatosExcel['Porcentaje de Ocupación (%)']+Resultados['Porcentaje de Ocupación']
    DatosExcel['Número de Vueltas Primario']=DatosExcel['Número de Vueltas Primario']+Resultados['Número de Vueltas Primario']
    DatosExcel['Número de Vueltas Secundario']=DatosExcel['Número de Vueltas Secundario']+Resultados['Número de Vueltas Secundario']
    DatosExcel['Incremento de Temperatura (ºC)']=DatosExcel['Incremento de Temperatura (ºC)']+Resultados['Temperatura']
    return DatosExcel
                            
#%% FOURIER SPECTRUM ANALISYS
def Fourier(MaximumSecondaryCurrent, MaximumPrimaryCurrent, 
            SwitchingFrecuency, NArmonicos=8, ResistividadCobre=0.0171/1e6, 
            mu0=4*np.pi*1e-7, DCM=0, Ploteo=0):
    Window=sig.triang(NArmonicos*2+1)                                           #Generating a triangular Waveform
    Window=(Window-Window[0])                                                   #Normalizing Window
    Window=Window/max(Window)-0.5                                               #Normalizing Window
    WindowFlyback=(Window*MaximumSecondaryCurrent)                              #Denormalizing Window
    if DCM==1:                                                                  #If DCM is 1, Negative Current will be 0A
        WindowFlyback=(Window*2*MaximumPrimaryCurrent)
        for h in range(0,len(WindowFlyback)):
            if WindowFlyback[h]<0:
                WindowFlyback[h]=0
    
    #plt.plot(Window)
    if Ploteo==1:
        plt.figure("Corriente del Inductor")
        plt.clf()
        plt.plot(WindowFlyback)
        plt.title("Corriente en la Bobina")
        plt.ylabel("Corriente [A]")
        plt.xlabel("2 x Nº de Armónicos")
    
    
    Resolution=2*NArmonicos+1                                                   #Nyquist Minimum Aliasing NO CHANGE
    Fourier=fourier.fft(WindowFlyback, Resolution)                              # / (len(WindowFlyback)/2.0)
    Freq = (np.linspace(-NArmonicos*SwitchingFrecuency, 
                        NArmonicos*SwitchingFrecuency, len(Fourier)))           #Denormalizing Frequency
    Response = np.abs(fourier.fftshift(Fourier / abs(Fourier).max()))           #Frequency Response
    
    Response=Response[int((len(Response)+1)/2):int(len(Response))]              #Solo Frecuencias Positivas
    Freq=Freq[int((len(Freq)+1)/2):int(len(Freq))]                              #Solo Frecuencias Positivas
    
    if Ploteo==1:
        plt.figure("Espectro de Fourier")
        plt.clf()
        plt.plot(Freq*1e-3,Response)
        plt.title("Respuesta en Frecuencia de la Corriente")
        plt.ylabel("Corriente [A]")
        plt.xlabel("Frecuencia [kHz]")
        
    SkinDepth=np.sqrt(ResistividadCobre/(np.pi*mu0*Freq))   
    return SkinDepth, Response
#%%
