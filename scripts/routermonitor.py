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



bwint1=ObjectType(ObjectIdentity('1.3.6.1.2.1.2.2.1.5.1'))
bwint11=ObjectType(ObjectIdentity('1.3.6.1.2.1.2.2.1.5.11'))
strbwint1='Ancho de banda interfaz 1 (bps)'
strbwint11='Ancho de banda interfaz 2 (bps)'
inint1=ObjectType(ObjectIdentity('1.3.6.1.2.1.2.2.1.10.1'))
inint11=ObjectType(ObjectIdentity('1.3.6.1.2.1.2.2.1.10.11'))
inint11=ObjectType(ObjectIdentity('1.3.6.1.2.1.2.2.1.10.11'))

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
asyncio.run(run(stat1,strstat1))
asyncio.run(run(stat2,strstat2))

asyncio.run(run(bwint1,strbwint1))
asyncio.run(run(bwint11,strbwint11))
asyncio.run(run(cpuused,cpu))

mt= asyncio.run(runw(memtot))
mu= asyncio.run(runw(memused))
print('Memoria utilizada (%): '+str(round(mu*100/mt)))


to= asyncio.run(runw(inint1))
to1= asyncio.run(runw(inint11))
time.sleep(5)
t1= asyncio.run(runw(inint1))
t11= asyncio.run(runw(inint11))

t000=to+to1
t333=t1+t11
tin3=t333-t000
print('Tráfico entrante medio (avg 5s) (bps): '+ str(round(((tin3)*8)/5)))


