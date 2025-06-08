import pandas as pd
from  math import isnan
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import csv

lat = []
lon = []
contador = []
u = 0


def tipo(menos, mas):
    #print("*",menos,mas,end="")
    if abs(menos) == mas:
        return "6" # EQUILIBRADAS LLEGADAS Y SALIDAS"
    elif abs(menos) < 0.25 and mas < 0.25:
        return "1" # POCO USO"
    elif abs(menos) < 0.25 and mas >= 0.25:
        return "2" # LLEGADA"
    elif abs(menos) >= 0.25 and mas < 0.25:
        return "3" # SALIDA"
    elif abs(menos) >= 0.25 and mas >= 0.25 and (abs(menos) - mas) > 0:
        return "4" # MAS SALIDA QUE LLEGADAS"
    elif abs(menos) >= 0.25 and mas >= 0.25 and (abs(menos) - mas) < 0:
        return "5" # MAS LLEGADAS QUE SALIDAS"   
    else:
        print("***********",menos," ",mas,"****")
        return "7" # OTRO TIPO"


nombreArch = "cdmx_data_series"
#df = pd.read_csv(nombreArch+'.csv', encoding='UTF8')
#columnas = df.columns
#tipos = df.dtypes

with open(nombreArch+".csv", encoding="UTF-8", newline='') as File:  
    archivo = csv.reader(File)
    cuenta = 0     
    for reg in archivo:
        if cuenta == 0:
            cuenta += 1 # SALTA EL ENCABEZADO
            continue
        vlat = reg[1]
        vlon = reg[0]
        dia = reg[7]
        festivo = reg[8]
        esta = False
        #print(cuenta,vlat,vlon, u)
    
        cuenta += 1
        if cuenta % 100000 == 0:
            print(cuenta)
        
        i = 0
        while i < u and esta == False:
            if vlat == lat[i] and vlon == lon[i]: # ESTACIÓN EXISTENTE
                contador[i] += 1
                esta = True
            i += 1    
        if esta == False: # ESTACIÓN NUEVA
            lat.append(vlat)
            lon.append(vlon)
            contador.append(1)           
            u += 1
print("Hay ",u,"estaciones")
for i in range(u):
    print(i,lat[i],lon[i],contador[i])
File.close()

print("VUELVO A ABRIR EL DATASET")  
pocupa = np.zeros((u,7),dtype=np.float64)
nocupa = np.zeros((u,7),dtype=np.float64)

upocupa = np.zeros((u,7))
unocupa = np.zeros((u,7))

with open(nombreArch+".csv", encoding="UTF-8", newline='') as File:  
    archivo = csv.reader(File)
    cuenta = 0
        
    for reg in archivo:
        if cuenta == 0:
            cuenta += 1 # SALTA EL ENCABEZADO
            continue
        cuenta += 1
        if cuenta % 25000 == 0:
            print(cuenta)

        vlat = reg[1]
        vlon = reg[0]
        dia = int(reg[7])
        festivo = reg[8]
        esta = False
        cual = 0
        while cual < u and esta == False:
            if vlat == lat[cual] and vlon == lon[cual]: # ESTACIÓN 
                esta = True
                break
            cual += 1
        # SE TIENE EL ÍNDICE DE LA ESTACIÓN, AHORA SE ACUMULA EN LA MATRIZ SEGÚN EL DÍA DE LA SEMANA
        for ihora in range(9,9+24):
            #print("LA HORA",ihora)
            if reg[ihora] == None:
                continue
            if float(reg[ihora]) > 0: # ACUMULAR A POSITIVOS
                if float(reg[ihora]) > 1:
                    reg[ihora] = 1
                #print("ESTACION",cual,"DIA",dia,"HORA",ihora)
                pocupa[cual][dia] += float(reg[ihora])
                upocupa[cual][dia] += 1
            elif float(reg[ihora]) < 0: # ACUMULAR A NEGATIVOS
                #print("ESTACION",cual,"DIA",dia,"HORA",ihora)
                if float(reg[ihora]) < -1:
                    reg[ihora] = -1
                nocupa[cual][dia] += float(reg[ihora])
                unocupa[cual][dia] += 1                    
File.close()
print("\nSe muestran ",u,"estaciones de CDMX")
aEstacion = open("estaciones.csv", "w")
aEstacion.write("idestacion,lat,lon,uso,luns,lune,lunt,mars,mare,mart,mies,miee,miet,jues,juee,juet,vies,viee,viet,sabs,sabt,sabe,doms,dome,domt,totals,totale,tipoestacion\n")
for iestacion in range(u):
    print(str(iestacion)+","+str(lat[iestacion])+","+str(lon[iestacion])+","+str(contador[iestacion]),end="")
    aEstacion.write(str(iestacion)+","+str(lat[iestacion])+","+str(lon[iestacion])+","+str(contador[iestacion]))
    menos = 0
    umenos = 0
    mas = 0
    umas = 0
    for idia in range(7):
        dato1 = int(100*nocupa[iestacion][idia]/unocupa[iestacion][idia])/100
        dato2 = int(100*pocupa[iestacion][idia]/upocupa[iestacion][idia])/100
        print(","+str(dato1)+","+str(dato2)+","+str(tipo(dato1,dato2)),end="")
        aEstacion.write(","+str(dato1)+","+str(dato2)+","+str(tipo(dato1,dato2)))
        if dato1 < 0:
            menos += dato1
            umenos += 1
        if dato2 > 0:
            mas += dato2          
            umas += 1
    fmas = int(100*mas/umas)/100
    fmenos = int(100*menos/umenos)/100
    print(","+str(fmenos)+","+str( fmas ),end=",")
    aEstacion.write(","+str(fmenos)+","+str( fmas )+",")
    print(tipo(fmenos,fmas))
    aEstacion.write(tipo(fmenos,fmas)+"\n")
aEstacion.close()