# -*- coding: utf-8 -*-
"""
Created on Sat Apr  4 17:46:08 2020

@author: pepeb
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import cm
import matplotlib.dates as mdates
import io
import os
import sys
import requests
import boto3



def cod_ine(NomCom):

    Comunidades = {
    "ANDA":   1,
    "ARAG":   2,
    "ASTUR":  3,
    "BALE":   4,
    "CANA":   5 ,
    'CANTA':  6,
    'MANCHA':  8,
    'LEON':    7,
    "CATALU":  9,
    "CEUT":  18,
    "VALEN":  10,
    "EXTRE":  11,
    "GALI" :  12,
    "MADRI":  13,
    "MELI":   19,
    "MURC":   14, 
    "NAVARR": 15,
    "VASC":   16,
    "EUSK":   16,
    "RIOJ":   17,
    "ESP":     0

    }
    for key in Comunidades:
    
        if NomCom.upper().find(key)>-1:
            return Comunidades[key]
    
    return -1
   
def ploteame(txt, Comunidad, tipo, densidad):

    print('oli')
    plt.figure()
    fig, ax = plt.subplots()
    df= GetStat(txt)
    
    if densidad:
        df = 1000000*df.div(getPoblacion(), axis = 0, level =0)
    
    df.sort_values(by=df.columns[len(df.columns)-1], ascending = False, inplace = True)
    
    if Comunidad[0] == 'TOP':
        if Comunidad[1]>0:
            #Esp = df.loc[0]
            
            df = df.drop(0, axis = 0, level =0).iloc[range(Comunidad[1])]
            #df = pd.concat([df, Esp])
            Comunidad = df.index.get_level_values(0).tolist()
            
            
        else:
            #Esp = df.loc[0]
            df.drop(0, axis = 0, level =0, inplace = True)
            df = df.iloc[range(len(df)+Comunidad[1], len(df))]
            
            #df = pd.concat([Esp,df])
            Comunidad = df.index.get_level_values(0).tolist()
            
    else:
        df = df.loc[Comunidad]
        
    print(Comunidad)
    
    tipo = diarioortotal(tipo)
    for i in range(len(Comunidad)):
        
        
        NombreComunidad = df.index[i][1]
  
            
        if tipo.upper().find('DIA')>-1:
            ax.bar(df.iloc[i].index, df.iloc[i].diff(), color = cm.tab10(i), label = NombreComunidad, alpha = 0.8)
        
     
        elif tipo.upper().find('TOT')>-1:
            ax.plot(df.iloc[i].index, df.iloc[i], label = NombreComunidad,  color = cm.tab10(i), linewidth=4)
    
    ax.xaxis.set_major_locator(mdates.DayLocator(interval=5))
    ax.xaxis.set_minor_locator(mdates.DayLocator(interval=1))
    fig.autofmt_xdate()
    
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %d'))
    ax.tick_params(labelsize=13)
    if densidad:
        ylab =txt+' '+ diarioortotal(tipo) +' '+ 'POR MILL.'
    else:
        ylab = txt+' '+ diarioortotal(tipo)

     
    ax.set_ylabel(ylab, fontsize = 13)
    plt.legend(loc=2, fontsize = 13, frameon=False)  
    plt.tight_layout()     
    plt.gcf().subplots_adjust(bottom=0.15)
    
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)

    return buf
    
def tipo(txt):
    x = txt.split() 
    for i in x:
        if i.upper().find('MUERT')>-1 or i.upper().find('FALLE')>-1:
            return 'FALLECIDOS'
        if i.upper().find('CONTAG')>-1 or i.upper().find('INFEC')>-1:
            return 'INFECTADOS'
    return 0

def diarioortotal(txt):
    x = txt.split() 
    for i in x:
        if i.upper().find('TOT')>-1 or i.upper().find('ACUM')>-1:
            return 'TOTALES'
        if i.upper().find('DIA')>-1:
            return 'DIARIOS'
    return 0

def comunidad(txt):
    x = txt.split() 
    a = []
    for i in range(len(x)):
        
        if x[i].upper().find('TOP')>-1:
            a = ['TOP', 5]
            
            if x[i+1].isdigit():
                a[1] = int(x[i+1]) 
            elif x[i+1][0] == '-'  and  x[i+1][1:].isdigit():
                a[1] = int(x[i+1]) 
        if a[1]>8:
            a[1]=8
        elif a[1]<-8:
            a[1] = -8
        elif a[1]==0:
            a[1] = 5
        
                
            return a
            
        
        if cod_ine(x[i])>-1:
            
            a.append(cod_ine(x[i]))
        
    return a



def GetStat(txt):
    if txt == 'FALLECIDOS':
        url ="https://raw.githubusercontent.com/datadista/datasets/master/COVID%2019/ccaa_covid19_fallecidos.csv"

    if txt == 'INFECTADOS':
        url ="https://raw.githubusercontent.com/datadista/datasets/master/COVID%2019/ccaa_covid19_casos.csv"
        
    s = requests.get(url).content
    Stat = pd.read_csv(io.StringIO(s.decode('utf-8')))
    
    Stat = Stat.set_index(['cod_ine', 'CCAA'])
    Stat.rename(index ={'Total': 'España'}, inplace = True)
    Stat.columns = pd.to_datetime(Stat.columns)
    
    return Stat

def keywordDetector(txt):
    answer= []
    count = 0
    if txt =='/start':
        resp = 'Hola, soy el coronabot!\n\nTengo datos actualizados del número de contagiados y fallecidos por COVID-19 '+\
            'en cada comunidad española.'+\
            ' Estos datos provienen de fuentes oficiales y son facilitados por Datadista.\n\n'\
            'Usarme es sencillo, tienes que introducir palabras clave. En una misma frase, me escribes lo que quieres saber: \n\n '+\
            '*- Contagiados/fallecidos* \n\n *- Acumulado/diario* \n\n*- Comunidades españolas* en las que quieras conocerlo\n\n '+\
            '\* Además, si dices *"millon"* te daré los *datos normalizados* por cada millón de habitantes. \n\n' + \
            'Ejemplo de frase:\n\n_Numero de infectados acumulados en España, Madrid, Aragon y Andalucia_\n\n' +\
            'No me importa en qué orden me digas las cosas. Simplemente necesito las tres primeras palabras clave y funcionaré!\n\n'+\
            'Muchas gracias por usarme!'
        return resp

    if not tipo(txt): 
        count = count +1
        answer.append('*-Contagiados/fallecidos*\n\n')
    if not diarioortotal(txt):
        count = count +1
        answer.append('*-Acumulado/diario*\n\n')
    if not comunidad(txt): 
        count = count +1
        answer.append('*-Comunidad/es*\n\n')
    


    if count == 0:

        return [tipo(txt), diarioortotal(txt), comunidad(txt), densidadPoblacion(txt)]
    elif count ==1:
        resp = 'Me falta saber el dato de:\n\n' +answer[0]+'Escribelo todo en un mismo mensaje por favor.\n'+\
               'Te recuerdo que si añades *"millon"* te daré los datos estarán normalizados.'

        return resp
    elif count == 2:
        resp = 'Me faltan los siguientes datos:\n\n'+ answer[0] + answer[1]+ 'Escribelo todo en un mismo mensaje, por favor.\n' +\
               'Te recuerdo que si añades *"millon"* te daré los datos estarán normalizados.'
        return resp
    else:
        resp = 'No te he entendido! Recuerda que funciono con palabras clave, así que dime en una misma frase qué quieres saber: \n\n '+\
            '*- Contagiados/fallecidos* \n\n *- Acumulado/diario* \n\n*- Comunidades españolas* en las que quieras conocerlo\n\n '+\
            '\* Además, si dices *"millon"* te daré los *datos normalizados* por cada millón de habitantes. \n\n' + \
            'Ejemplo de frase:\n\n_Numero de infectados acumulados en España, Madrid, Aragon y Andalucia_\n\n' +\
            'No me importa en qué orden me digas las cosas. Simplemente necesito las tres primeras palabras clave y funcionaré!'
            

        return resp

def chatID( number_id, SavedChats):

    SavedChatsList = SavedChats.split(',')
    
    for i in SavedChatsList:
        
        if number_id==i:
            return SavedChats
        
    return SavedChats+','+ number_id 
        
        
    

def getListChats(bucket_name):
    s3 = boto3.client('s3')
    print('bot3cogido')
    response = s3.get_object(Bucket=bucket_name, Key='IdChats.txt')
    print(response)
    return response

def writeListChats(bucket_name, chats):
    s3 = boto3.client('s3')
    
    s3.put_object(Bucket=bucket_name, Key='IdChats.txt', Body =chats )

def densidadPoblacion(txt):

    x = txt.split() 
    for i in x:
        if i.upper().find('DENSID')>-1 or i.upper().find('POBLA')>-1 or  i.upper().find('MILL')>-1 :
            return True
    
    return False        
        
       
   

def Poblacion(cod):
    Df = pd.read_csv('PoblacionEspañola.csv',   sep=';', encoding = 'latin')
    Number = (Df.loc[cod]['Numero'])
    Prev=''
    for x in Number.split('.'):
        print(type(x))
        Prev = Prev + x
    print(float(Prev))
    return float(Prev)

def takeOutDot(Number):
    Prev = ''
    for x in Number.split('.'):
        
        Prev = Prev + x
    return float(Prev)

def getPoblacion():
    Df = pd.read_csv('PoblacionEspañola.csv',   sep=';', encoding = 'latin')
    return Df.set_index('Num')['Numero'].apply(lambda x: takeOutDot(x))
