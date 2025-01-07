#! /usr/bin/python3
import os
import subprocess
import re
import sys
from kubernetes import client, config
import asyncio
from pysnmp.hlapi.v3arch.asyncio import *
import time
import datetime
import asciichartpy as ace
config.load_kube_config()
v1=client.CoreV1Api()

list = v1.list_pod_for_all_namespaces(watch=False)
for i in list.items:
 if i.metadata.name.startswith("r1"):
  print('\nSERIE')
  print('\nRouter: r1')
  print('Interfaz: 1')

  print('Métrica: Tasa media (Bytes/s)')
  print('Granularidad: 0.25s')
  print('Número de muestras: 40')
  


  ip=i.status.pod_ip

name=ObjectType(ObjectIdentity('1.3.6.1.2.1.1.5.0'))
strname='Nombre'
stat1=ObjectType(ObjectIdentity('1.3.6.1.2.1.2.2.1.7.1'))
strstat1='Estado interfaz 1 (1:activa, 2:inactiva)'
stat2=ObjectType(ObjectIdentity('1.3.6.1.2.1.2.2.1.7.11'))
strstat2='Estado interfaz 2 (1:activa, 2:inactiva)'

memtot=ObjectType(ObjectIdentity('1.3.6.1.2.1.25.2.3.1.5.100'))
mtot=0
memused=ObjectType(ObjectIdentity('1.3.6.1.2.1.25.2.3.1.6.100'))
muse=0
cpuused=ObjectType(ObjectIdentity('1.3.6.1.2.1.25.3.3.1.2.1'))
cpu='Uso medio de CPU por nucleo (%)'



bwint1=ObjectType(ObjectIdentity('1.3.6.1.2.1.2.2.1.5.1'))
bwint11=ObjectType(ObjectIdentity('1.3.6.1.2.1.2.2.1.5.11'))
strbwint1='Ancho de banda interfaz 1 (bps)'
strbwint11='Ancho de banda interfaz 2 (bps)'
inint1=ObjectType(ObjectIdentity('1.3.6.1.2.1.2.2.1.10.1'))
inint11=ObjectType(ObjectIdentity('1.3.6.1.2.1.2.2.1.10.11'))
inint11=ObjectType(ObjectIdentity('1.3.6.1.2.1.2.2.1.10.11'))
dts=[]
async def run(obj,st):


 iterator = get_cmd(
   SnmpEngine(),
   CommunityData('public', mpModel=0),
   await UdpTransportTarget.create((ip, 161)),
   ContextData(),
   obj,)
 errorIndication, errorStatus, errorIndex, varBinds= await iterator
 if errorIndication:
      print(errorIndication)

 elif errorStatus:
  print(errorStatus.prettyPrint())
 else:
      for varBind in varBinds:
  #     print('hola')
       #print(' = '.join([x.prettyPrint() for x in varBind]))
       tim=datetime.datetime.now()
#       print(str(tim)+' || '+str(varBind[1]))    
       mes=[tim,varBind[1]]
       
       dts.append(mes)

 SnmpEngine().close_dispatcher()

n=0
while n < 40:
 asyncio.run(run(inint1,''))
 time.sleep(0.25)
 n=n+1

dts2=[]
ind=0
print('\nSerie:')
while ind<len(dts)-1:
  print(str(dts[ind][0])+' || '+str(round(((dts[ind+1][1])-(dts[ind][1]))/1)))
  dts2.append([(dts[ind][0]),round((dts[ind+1][1])-(dts[ind][1]))/0.25])

  ind=ind+1

print('\nGráfica:')
plo=[]
for i in dts2:
 plo.append(int(i[1]))
print(ace.plot(plo,{ 'height': 10,'format':'{:8.0f}' }))
