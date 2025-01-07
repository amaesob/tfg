import json
from pprint import pprint
from pprint import pformat

from prometheus_api_client import PrometheusConnect
prom=PrometheusConnect(url="http://localhost:30000",disable_ssl=True)
metrics=prom.all_metrics()
p='sum(rate(container_cpu_usage_seconds_total{container!=""}[5m]))'
z='100*avg(1-rate(node_cpu_seconds_total{mode="idle"}[5m]))by(instance)'
h='sum by (namespace) (kube_pod_status_ready{condition="false"})'
d="sum(machine_cpu_cores)"
q="(irate(node_cpu_seconds_total{job=\"node\",mode=\"idle\"}[5m]))*100"
#for metric in metrics:
w='sum(container_memory_usage_bytes{namespace="kube-system"})by(pod)'
c="topk(10,sum(rate(container_cpu_usage_seconds_total[5m]))by(pod))"
tz="\n %CPU por nodo"
zz=pformat(prom.custom_query(query=z))
#pprint(prom.custom_query(query=d))

#pprint(prom.custom_query(query=c))
th='\n Nº de PODS reiniciados por espacio de nombre'
hh=pformat(prom.custom_query(query=h))

tc="\n Pods con más consumo de CPU"
cc=pformat(prom.custom_query(query=c))

tw="\n Consumo de memoria (Bytes)"
ww=pformat(prom.custom_query(query=w))
f=open("clustermetrics","w")
f.write((tz+"\n"+zz+"\n"+th+"\n"+hh+"\n"+tc+"\n"+cc+"\n"+tw+"\n"+ww))

f.close()
print("Métricas guardadas en ./clustermetrics")
