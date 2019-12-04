# -*- coding: utf-8 -*-
"""
Created on Thu May 30 13:14:46 2019

@author: 2IO
"""
#%% 

import VariablesyConstantes as var
import Funciones as func
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from time import time

Initial_Time=time()

DatosExcel={  "Núcleo":[],                                                      #Dictionary for Data Loaded from DataBase
               "Material":[],
               "Diámetro del Cable Primario (mm)":[],
               "Diámetro del Cable Secundario (mm)":[],
               "Número de Paralelos Primario":[],
               "Número de Paralelos Secundario":[],
               "Longitud del Entrehierro (mm)":[],
               "Pérdidas del Núcleo (W)":[],
               "Pérdidas de Devanados (W)":[],
               "Pérdidas Totales (W)":[],
               'Porcentaje de Ocupación (%)':[],
               "Número de Vueltas Primario":[],
               "Número de Vueltas Secundario":[],
               'Incremento de Temperatura (ºC)':[],
               }
#%%             CÁLCULOS PREVIOS

"""
        IBias (Fline)
"""

"""
IBiasMaxPrimario=IMediaPrimario*np.sqrt(2)        #A
IBiasMinPrimario=0

IBiasMaxSecundario=IBiasMaxPrimario*TurnsRatio*0
IBiasMinSecundario=IBiasMinPrimario*TurnsRatio*0
"""

"""
        I Pequeñas señal (SS 2ºArmónico)
"""

"""
ISSMaxPrimario=IRizadoAbsoluto
ISSMinPrimario=0

ISSMaxSecundario=ISSMaxPrimario*TurnsRatio
ISSMinSecundario=ISSMinPrimario*TurnsRatio
"""

"""
        I total (Bias+SS)
"""

"""
IMaxPrimario=IBiasMaxPrimario+ISSMaxPrimario
IMinPrimario=IBiasMinPrimario+ISSMinPrimario

IMaxSecundario=IMaxPrimario*TurnsRatio
IMinSecundario=IMinPrimario*TurnsRatio
"""
"""

FOURIER ANALISIS

"""
Skindepth, Response=(func.Fourier(var.MaximumSecondaryCurrent, 
                                  var.MaximumPrimaryCurrent, 
                                  var.SwitchingFrecuency))

Nucleos=func.LoadNucleos(var.BBDD, var.BBDDNucleo)

Materiales=func.LoadMaterials(var.BBDD, var.BBDDMaterial)
              #SkinDepth equation

#%%         FUNCIÓN


def MagneticoFerrita(MaterialsRow, CoreRow,InductanceValue,PrimaryWireDiameter, 
                     SecondaryWireDiameter,SkinDepth, Bmax, TurnsRatio, 
                     MaximumPrimaryCurrent, AbsoluteWindowRate, MaximumAirGap, 
                     PrimaryParallels, SecondaryParallels, WindowArea, 
                     CoreEffectiveLengh, CoreEffectiveArea, muR, 
                     ColumnDiameter, Response, EffectiveVolume, K, Alpha, Beta,
                     ThermalResistance):                                        #InductanceValue,Fsw,NArmonicos,IRizado,Pout,Vout,Material,Núcleo,PrimaryParallels,DiametroCable,PrimaryTurns,Ploteo

    if Materiales.iloc[MaterialsRow,1] is None:
        return
    """
    CALCULO DE INDUCTANCIA
    
    """
    InductanceValue, PrimaryTurns, SecondaryTurns =( 
            func.Inductance(InductanceValue, Bmax, CoreEffectiveArea, 
                            var.MaximumPrimaryCurrent, TurnsRatio))                                              
    
    """
    
    CALCULO DE OCUPACION
    
    """
    WindowRate=(
            func.Window(WindowArea, AbsoluteWindowRate, 
                         PrimaryWireDiameter, PrimaryParallels,
                         PrimaryTurns, SecondaryWireDiameter, 
                         SecondaryParallels, SecondaryTurns))
    if WindowRate is None:
        return
    
    """
    
    CALCULO DE ENTREHIERRO
    
    """    
    AirGapLengh=(
            func.AirGap(PrimaryTurns, CoreEffectiveLengh, MaximumAirGap, 
                        CoreEffectiveArea, InductanceValue, muR))
    if AirGapLengh is None:
        return
    
    """
    
    PERDIDAS DEVANADOS
    
    """
    PrimaryWindingLosses=(
            func.WindingLosses(ColumnDiameter, var.MaximumPrimaryCurrent, 
                               var.MeanPrimaryCurrent, PrimaryTurns, 
                               PrimaryParallels, Response, 
                               PrimaryWireDiameter, SkinDepth))
    
    
    SecondaryWindingLosses=(
            func.WindingLosses(ColumnDiameter, var.MaximumSecondaryCurrent, 
                               var.MeanSecondaryCurrent, SecondaryTurns, 
                               SecondaryParallels, Response, 
                               SecondaryWireDiameter, SkinDepth))
             
    TotalWindingLosses=PrimaryWindingLosses+SecondaryWindingLosses                                     #Primary+Secondary Winding Losses
    
    """
    
    PERDIDAS NUCLEO
    
    """
    if var.Steinmetz==1:                                                                               #Core Losses
        PCore=(
            func.CoreLosses(InductanceValue, CoreEffectiveArea, PrimaryTurns, 
                            var.MaximumPrimaryCurrent,
                            var.MinimumPrimaryCurrent, var.SwitchingFrecuency, 
                            EffectiveVolume, K, Alpha, Beta))
        
    PTotal=PCore+TotalWindingLosses                                                                         #Total Losses
    Temperature=PTotal*ThermalResistance                                        #((XNucleo*ZNucleo*2+YNucleo*ZNucleo*2)/100),0.833)        Temperature Raising
    
    """
    
    GUARDADO DE DATOS
    
    """
    #StringPerdidas="PCore="+str(round(PCore,3))+"W", "PWindings="+str(round(PWindings,3))+"W"
    return{"Núcleo":[Nucleos.iloc[CoreRow,0]],                                                      #Return Dictionary
           "Material":[Materiales.iloc[MaterialsRow,1]],
           "DiámetroCable Primario":[round(PrimaryWireDiameter*1e3,1)],
           "DiámetroCable Secundario":[round(SecondaryWireDiameter*1e3,1)],
           "Número de Paralelos Primario":[PrimaryParallels],
           "Número de Paralelos Secundario":[SecondaryParallels],
           "Longitud del Entrehierro":[round(AirGapLengh*1e3,3)],
           "Pérdidas del Núcleo":[round(PCore,2)],
           "Pérdidas de Devanados":[round(TotalWindingLosses,2)],
           "Pérdidas Totales":[round(PTotal,2)],
           "Porcentaje de Ocupación":[round(WindowRate,2)],
           "Número de Vueltas Primario":[PrimaryTurns],
           "Número de Vueltas Secundario":[SecondaryTurns],
           "Temperatura":[round(Temperature,1)],
           #'Relación Pérdidas':[round(PCore,2)/round(PWindings,2)]
           }

#%%

                                               #Core Vector
#def Programa(NHilo, NHilos,DatosExcel):
    
Soluciones=0                                                                    #Solutions Counter
MaxNucleo=Nucleos.last_valid_index()                                            #Core Maximum Row
MaxMateriales=Materiales.last_valid_index()                                     #Materials Maximum Row
FilaMateriales=range(0,MaxMateriales)                                           #Materials Vector
FilaNucleo=range(0,MaxNucleo)    
for MaterialsRow in FilaMateriales:                                             #Extract Materials Parameters
    
    if Materiales.iloc[MaterialsRow,1] is not None:
        Material=func.ExtractMaterials(Materiales, MaterialsRow, 
                                       var.AbsoluteMaximumBsat)
        if (Material["MinimumFrequency"]>=var.SwitchingFrecuency 
        or Material["MaximumFrequency"]<var.SwitchingFrecuency):
            continue
    else:
        continue
    
    print(Materiales.iloc[MaterialsRow,1])
    for CoreRow in FilaNucleo:                                                  #Extracting Core Parameters
        if ((type(Nucleos.iloc[CoreRow,1]) is int) or 
            (type(Nucleos.iloc[CoreRow,1]) is float) and ()):
            Core=func.ExtractCore(Nucleos, CoreRow)
            
        else:
            continue
        print(Nucleos.iloc[CoreRow,0])
        for PrimaryParallels in range(var.PrimaryMinimumParallels,var.PrimaryMaximumParallels+1):
            for SecondaryParallels in range(var.SecondaryMinimumParallels,var.SecondaryMaximumParallels+1):
                for PrimaryWireDiameter in range (int(float(round(np.sqrt(var.MeanPrimaryCurrent/PrimaryParallels/var.J/np.pi)*2,1))*10),var.PrimaryWireMaximumWidth*10):
                    for SecondaryWireDiameter in range (int(float(round(np.sqrt(var.MeanSecondaryCurrent/SecondaryParallels/var.J/np.pi)*2,1))*10),var.SecondaryWireMaximumWidth*10):
                        if PrimaryWireDiameter==0 or SecondaryWireDiameter==0:
                            continue
                        Resultados=MagneticoFerrita(MaterialsRow,CoreRow,var.InductanceValue,PrimaryWireDiameter*1e-4, SecondaryWireDiameter*1e-4,Skindepth, Material["BMax"], var.TurnsRatio, var.MaximumPrimaryCurrent, var.AbsoluteWindowRate, var.MaximumAirGap,  PrimaryParallels, SecondaryParallels, Core["WindowArea"], Core["CoreEffectiveLengh"], Core["CoreEffectiveArea"], Material["muR"], Core["ColumnDiameter"], Response, Core["EffectiveVolume"], Material["K"], Material["Alpha"], Material["Beta"],Core["ThermalResistance"])
                    
                        if Resultados is not None:
                                                   
                            if var.Noptimizaciones==0:
                                #DatosExcel=
                                ResultadoOptimo=Resultados
                                var.Noptimizaciones=var.Noptimizaciones+1
                                print("                          OPTIMO        ")
                            if Resultados["Pérdidas Totales"]<ResultadoOptimo["Pérdidas Totales"]:
                                ResultadoOptimo=Resultados
                                var.Noptimizaciones=var.Noptimizaciones+1
                                print(var.Noptimizaciones)
                                print("                          OPTIMO        ")
                            DatosExcel=func.UpdateExcelData(DatosExcel,Resultados)
                            Soluciones=Soluciones+1
                            

if var.Ploteo==1:
    plt.figure("Pérdidas")
    plt.clf()
    plt.pie([ResultadoOptimo["Pérdidas del Núcleo (W)"][0],ResultadoOptimo["Pérdidas de Devanados (W)"][0]],labels=["PCore","PWindings"],explode=(0.1,0),autopct='%1.1f%%')
    plt.title("PORCENTAJE DE REPARTO DE PÉRDIDAS")
    plt.text(-2,-1.21,"Pérdidas del Núcleo="+str(round(ResultadoOptimo["Pérdidas del Núcleo (W)"][0],3))+"W")
    plt.text(-2,-1.32,"Pérdidas de Devanados="+str(round(ResultadoOptimo["Pérdidas de Devanados (W)"][0],3))+"W")
    plt.text(-2,-1.43,"Pérdidas Totales="+str(round(ResultadoOptimo["Pérdidas Totales (W)"][0],3))+"W")
    plt.figure("Porcentaje de Ocupación")
    plt.clf()
    plt.pie([0.000001,ResultadoOptimo["Porcentaje de Ocupación"][0]],labels=[" ","Ocupado"],explode=(0.1,0),autopct='%1.1f%%')
    plt.title("OCUPACIÓN DE VENTANA")
    plt.text(-2,-1.1,"Núcleo: "+ResultadoOptimo["Núcleo"][0])
    plt.text(-2,-1.21,"Material: "+ResultadoOptimo["Material"][0])
    plt.text(-2,-1.32,"Diámetro Cable: "+str(ResultadoOptimo["Diámetro del Cable (mm)"][0])+"mm")
    plt.text(-2,-1.43,"Número de Paralelos: "+str(ResultadoOptimo["Número de Paralelos"][0]))
    plt.text(-0.8,1.15,"Longitud del Entrehierro: "+str(ResultadoOptimo["Longitud del Entrehierro (mm)"][0])+"mm")
##return DatosExcel



df=pd.DataFrame(DatosExcel)
df=df.sort_values(['Pérdidas Totales (W)','Incremento de Temperatura (ºC)'])
export_excel=df.to_excel(var.RutaOutput,index = None, header=True)
print("Número de Soluciones: "+str(Soluciones))

Final_Time=time()
Total_Execution_Time=Final_Time-Initial_Time
Total_Execution_Time_Hr=np.floor(Total_Execution_Time/3600)
Total_Execution_Time_Min=np.floor(Total_Execution_Time/60-Total_Execution_Time_Hr*60)
Total_Execution_Time_Seg=round(Total_Execution_Time-Total_Execution_Time_Min*60-Total_Execution_Time_Hr*3600)
print("Total Execution Time: ", Total_Execution_Time_Hr, "Hrs:", Total_Execution_Time_Min, "Min:", Total_Execution_Time_Seg, "Seg")

#plt.clf()
#plt.plot(range(0,len(SkinDepth)),SkinDepth,range(0,len(SkinDepth)),[0.5e-3]*8)
