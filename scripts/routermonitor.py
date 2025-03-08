#! /usr/bin/python3
import os
import subprocess
import re
import sys
from kubernetes import client, config
import asyncio
from pysnmp.hlapi.v3arch.asyncio import *
import time
config.load_kube_config()
v1=client.CoreV1Api()

list = v1.list_pod_for_all_namespaces(watch=False)
for i in list.items:
 if i.metadata.name.startswith("r1"):
  print('\nMÉTRICAS ROUTER\n')
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
addr=ObjectType(ObjectIdentity('1.3.6.1.2.1.25.3.2.1.3.1'))
addrst='Dispositivo host'
type=ObjectType(ObjectIdentity('1.3.6.1.2.1.25.3.2.1.4.1'))
typest='ID del producto'
esta=ObjectType(ObjectIdentity('1.3.6.1.2.1.25.3.2.1.5.1'))
estast='Estado dispositivo (1:desconocido, 2:activo ,3:aviso ,4:testeo ,5:inactivo)'
error=ObjectType(ObjectIdentity('1.3.6.1.2.1.25.3.2.1.6.1'))
errorst='Nº Errores'

alma=ObjectType(ObjectIdentity('1.3.6.1.2.1.25.2.3.1.3.1'))
almast='Almacenamiento'

ent=ObjectType(ObjectIdentity('1.3.6.1.2.1.47.1.1.1.1.2.1'))
entst='Nombre entidad'
sw=ObjectType(ObjectIdentity('1.3.6.1.2.1.47.1.1.1.1.10.1'))
swst='Software entidad'
ser=ObjectType(ObjectIdentity('1.3.6.1.2.1.47.1.1.1.1.11.1'))
serst='Número de serie entidad'
ven=ObjectType(ObjectIdentity('1.3.6.1.2.1.47.1.1.1.1.12.1'))
venst='Vendedor'




bwint1=ObjectType(ObjectIdentity('1.3.6.1.2.1.2.2.1.5.1'))
bwint11=ObjectType(ObjectIdentity('1.3.6.1.2.1.2.2.1.5.11'))
strbwint1='Ancho de banda interfaz 1 (bps)'
strbwint11='Ancho de banda interfaz 2 (bps)'
inint1=ObjectType(ObjectIdentity('1.3.6.1.2.1.2.2.1.10.1'))
inint11=ObjectType(ObjectIdentity('1.3.6.1.2.1.2.2.1.10.11'))
des1=ObjectType(ObjectIdentity('1.3.6.1.2.1.2.2.1.13.1'))
des11=ObjectType(ObjectIdentity('1.3.6.1.2.1.2.2.1.13.11'))

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
       #print(' = '.join([x.prettyPrint() for x in varBind]))
       print(st+ ': '+str(varBind[1]))

 SnmpEngine().close_dispatcher()

async def runw(obj):
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
       
       return varBind[1]

 SnmpEngine().close_dispatcher()


asyncio.run(run(name,strname))

asyncio.run(run(addr,addrst))
asyncio.run(run(type,typest))
asyncio.run(run(esta,estast))
asyncio.run(run(error,errorst))
asyncio.run(run(ent,entst))
asyncio.run(run(sw,swst))
asyncio.run(run(ser,serst))
asyncio.run(run(ven,venst))

asyncio.run(run(alma,almast))

asyncio.run(run(stat1,strstat1))
asyncio.run(run(stat2,strstat2))

asyncio.run(run(bwint1,strbwint1))
asyncio.run(run(bwint11,strbwint11))
asyncio.run(run(cpuused,cpu))

mt= asyncio.run(runw(memtot))
mu= asyncio.run(runw(memused))
print('Memoria utilizada (%): '+str(round(mu*100/mt)))


to= asyncio.run(runw(inint1))
do= asyncio.run(runw(des1))
do1= asyncio.run(runw(des11))

to1= asyncio.run(runw(inint11))
time.sleep(5)
d1= asyncio.run(runw(des1))
d11= asyncio.run(runw(des11))

t1= asyncio.run(runw(inint1))
t11= asyncio.run(runw(inint11))

t000=to+to1
t333=t1+t11
tin3=t333-t000
print('Tráfico entrante medio (avg 5s) (bps): '+ str(round(((tin3)*8)/5)))
d000=do+do1
d333=d1+d11
din3=d333-d000
print('Tráfico descartado medio (avg 5s) (bps): '+ str(round(((din3)*8)/5)))


