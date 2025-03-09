# GUÍA DE DESPLIEGUE DEL ESCENARIO
## Instalación VMs
	
Software de virtualización: Oracle VM VirtualBox 7.0.14 r161095 (Qt5.15.2)<br>
Sistema operativo (imagen ISO): Ubuntu Server 22.04.4 LTS (web oficial)<br>
Almacenamiento nodo master: 42,57 GB<br>
Almacenamiento nodo worker: 54GB<br>
Memoria nodo master: 3,4GB<br>
Memoria nodo worker: >10GB<br>

CPUs virtuales master: 2<br>
CPUs virtuales worker: 8<br>

Adaptador 1:<br>
	&nbsp;Conectado a: Adaptador puente<br>
	&nbsp;Modo promiscuo: Permitir todo<br>

### Habilitar virtualización anidada (en carpeta de instalacion de Vbox para windows) 
 
.\VBoxManage modifyvm <<nombre vm>> --nested-hw-virt on<br>

### Montar carpeta compartida
sudo mount –t vboxsf nombre carpeta compartida creada ruta de montaje<br>
## Instalación del SO
Base de instalación: Estándar<br>
Configuración IP inicial: DHCP<br>
Configuraciones adicionales: Instalado OpenSSH server package<br>

## Instalación nodo k8master
### Instalación paquetes básicos:
sudo apt update<br>
sudo apt install -y nano net-tools git make gcc apt-transport-https ca-certificates curl<br>

### Nombres de dominio (/etc/hosts) 
192.168.1.100 k8master<br>
192.168.1.111 k8worker01<br>
192.168.1.222 k8worker02<br>

### Configuración manual IP y ruta por defecto

sudo nano /etc/netplan/00-installer-config-yaml<br>

network:<br>
 &nbsp;ethernets:<br>
  &nbsp;&nbsp;enp0s3:<br>
   &nbsp;&nbsp;&nbsp;addresses: [192.168.1.100/24]<br>
    &nbsp;&nbsp;&nbsp;&nbsp;nameservers:<br>
     &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;addresses: [8.8.8.8]<br>
     &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;routes:<br>
      &nbsp;&nbsp;&nbsp;&nbsp;to: default<br>
      &nbsp;&nbsp;&nbsp;&nbsp;via: 192.168.1.1<br>
version: 2<br>

sudo netplan apply<br>

### Configuración básica
sudo su<br>

sudo ufw disable<br>
echo '1' > /proc/sys/net/bridge/bridge-nf-call-iptables<br>
echo '1' > /proc/sys/net/ipv4/ip-forward<br>
swapoff –a      (SESIÓN)<br>
sudo sed –i ‘/ swap / s/^\(.*\)$/#\1/g’ /etc/fstab<br>
sudo tee /etc/modules-load.d/containerd.conf <<EOF <br>
overlay<br>
br_netfilter<br>
EOF<br>
modprobe br_netfilter<br>
modprobe overlay<br>
modprobe kvm<br>

<br>

sudo tee /etc/sysctl.d/kubernetes.conf <<EOF<br>
Net.bridge.bridge-nf-call-ip6tables =1<br>
Net.bridge.bridge-nf-call-iptables = 1<br>
Net.ipv4.ip_forward = 1<br>
EOF<br>

sudo sysctl --system<br>

### Instalación Kubectl, Kubelet, Kubeadm (root)

curl -fsSL https://pkgs.k8s.io/core:/stable:/v1.29/deb/Release.key | sudo gpg --dearmor -o /etc/apt/keyrings/kubernetes-apt-keyring.gpg<br>

echo 'deb [signed-by=/etc/apt/keyrings/kubernetes-apt-keyring.gpg] https://pkgs.k8s.io/core:/stable:/v1.29/deb/ /' | sudo tee /etc/apt/sources.list.d/kubernetes.list<br>



### Instalación CRI cri-dockerd

apt-get update<br>
apt-get install -y kubelet kubeadm kubectl<br>
apt-mark hold kubelet kubeadm kubectl<br>

install -o root -g root -m 0755 cri-dockerd /usr/local/bin/cri-dockerd <br>
install packaging/systemd/* /etc/systemd/system <br>
sed -i -e 's,/usr/bin/cri-dockerd,/usr/local/bin/cri-dockerd,' /etc/systemd/system/cri-docker.service <br>
systemctl daemon-reload <br>
systemctl enable --now cri-docker.socket<br>


### Docker (se puede emplear la clave y repositorio anteriores))

(Add Docker's official GPG key)<br>
sudo apt-get update<br>
sudo apt-get install ca-certificates curl<br>
sudo install -m 0755 -d /etc/apt/keyrings<br>
sudo curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc<br>
sudo chmod a+r /etc/apt/keyrings/docker.asc<br>
 
(Add the repository to Apt sources)<br>
echo \<br>
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/ubuntu \<br>
  $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | \<br>
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null<br>
sudo apt-get update<br>
sudo apt-get install docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin<br>

sudo groupadd docker<br>
sudo usermod -aG docker $USER<br>

## Instalación nodo k8worker01

### Instalación paquetes básicos
sudo apt update<br>
sudo apt install -y nano net-tools git make gcc apt-transport-https ca-certificates curl<br>

### Nombres de dominio (/etc/hosts) 

192.168.1.100  k8master<br>
192.168.1.111 k8worker01<br>
192.168.1.222 k8worker02<br>

### Configuración manual IP y vía a internet por defecto

/etc/netplan/00-installer-config-yaml<br>
network:<br>
	&nbsp;ethernets:<br>
		&nbsp;&nbsp;enp0s3:<br>
			&nbsp;&nbsp;&nbsp;addresses: [192.168.1.111/24]<br>
			&nbsp;&nbsp;&nbsp;nameservers:<br>
				&nbsp;&nbsp;&nbsp;&nbsp;addresses: [8.8.8.8]<br>
			&nbsp;&nbsp;&nbsp;routes:<br>
-	to: default<br>
	&nbsp;&nbsp;via: 192.168.1.1<br>
	&nbsp;&nbsp;version: 2<br>

sudo netplan apply<br>


### Configuración básica:
sudo su<br>

sudo ufw disable<br>
modprobe br_netfilter<br>
echo '1' > /proc/sys/net/bridge/bridge-nf-call-iptables<br>
echo '1' > /proc/sys/net/ipv4/ip-forward<br>

swapoff –a     	(SESIÓN)<br>
nano /etc/fstab<br>

### Instalación Kubectl, Kubelet, Kubeadm (root/v1.29)

curl -fsSL https://pkgs.k8s.io/core:/stable:/v1.29/deb/Release.key | sudo gpg --dearmor -o /etc/apt/keyrings/kubernetes-apt-keyring.gpg<br>

echo 'deb [signed-by=/etc/apt/keyrings/kubernetes-apt-keyring.gpg] https://pkgs.k8s.io/core:/stable:/v1.29/deb/ /' | sudo tee /etc/apt/sources.list.d/kubernetes.list<br>



apt-get update<br>
apt-get install -y kubelet kubeadm kubectl<br>
apt-mark hold kubelet kubeadm kubectl<br>

### Instalación CRI cri-dockerd

install -o root -g root -m 0755 cri-dockerd /usr/local/bin/cri-dockerd <br>
install packaging/systemd/* /etc/systemd/system <br>
sed -i -e 's,/usr/bin/cri-dockerd,/usr/local/bin/cri-dockerd,' /etc/systemd/system/cri-docker.service <br>
systemctl daemon-reload <br>
systemctl enable --now cri-docker.socket<br>


### Docker (se puede emplear la clave y repositorio anteriores))

(Add Docker's official GPG key:)<br>
sudo apt-get update<br>
sudo apt-get install ca-certificates curl<br>
sudo install -m 0755 -d /etc/apt/keyrings<br>
sudo curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc<br>
sudo chmod a+r /etc/apt/keyrings/docker.asc<br>
 
( Add the repository to Apt sources)<br>
echo \<br>
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/ubuntu \<br>
  $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | \<br>
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null<br>
sudo apt-get update<br>
sudo apt-get install docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin<br>

sudo groupadd docker<br>
sudo usermod -aG docker $USER<br>
### Agregación de nodos al cluster
kubeadm join 192.168.1.100:6443 --token <<TOKEN>> --discovery-token-ca-cert-hash sha256:<<HASH>> --cri-socket unix:///var/run/cri-dockerd.sock<br>


### Crear carpeta para el volumen persistente
mkdir /home/k8worker01/kubedata<br>


## Instalación nodo k8worker02

### Instalación paquetes básicos
sudo apt update<br>
sudo apt install -y nano net-tools git make gcc apt-transport-https ca-certificates curl<br>


### Nombres de dominio (/etc/hosts) 

192.168.1.100  k8master<br>
192.168.1.111 k8worker01<br>
192.168.1.222 k8worker02<br>

### Configuración manual IP y vía a internet por defecto

/etc/netplan/00-installer-config-yaml<br>
network:<br>
	&nbsp;ethernets:<br>
		&nbsp;&nbsp;enp0s3:<br>
			&nbsp;&nbsp;&nbsp;addresses: [192.168.1.222/24]<br>
			&nbsp;&nbsp;&nbsp;nameservers:<br>
				&nbsp;&nbsp;&nbsp;&nbsp;addresses: [8.8.8.8]<br>
			&nbsp;&nbsp;&nbsp;routes:<br>
-&nbsp;to: default<br>
	&nbsp;&nbsp;via: 192.168.1.1<br>
	&nbsp;&nbsp;version: 2<br>

sudo netplan apply<br>



### Configuración básica
sudo su<br>

sudo ufw disable<br>
modprobe br_netfilter<br>
echo '1' > /proc/sys/net/bridge/bridge-nf-call-iptables<br>
echo '1' > /proc/sys/net/ipv4/ip-forward<br>

swapoff -a	(SESIÓN)<br>
nano /etc/fstab<br>

### Instalación Kubectl, Kubelet, Kubeadm (root/v1.29)

curl -fsSL https://pkgs.k8s.io/core:/stable:/v1.29/deb/Release.key | sudo gpg --dearmor -o /etc/apt/keyrings/kubernetes-apt-keyring.gpg<br>

echo 'deb [signed-by=/etc/apt/keyrings/kubernetes-apt-keyring.gpg] https://pkgs.k8s.io/core:/stable:/v1.29/deb/ /' | sudo tee /etc/apt/sources.list.d/kubernetes.list<br>



apt-get update<br>
apt-get install -y kubelet kubeadm kubectl<br>
apt-mark hold kubelet kubeadm kubectl<br>

### Instalación CRI cri-dockerd

install -o root -g root -m 0755 cri-dockerd /usr/local/bin/cri-dockerd <br>
install packaging/systemd/* /etc/systemd/system <br>
sed -i -e 's,/usr/bin/cri-dockerd,/usr/local/bin/cri-dockerd,' /etc/systemd/system/cri-docker.service <br>
systemctl daemon-reload <br>
systemctl enable --now cri-docker.socket<br>


### Docker (se puede emplear la clave y repositorio anteriores))

(Add Docker's official GPG key)<br>
sudo apt-get update<br>
sudo apt-get install ca-certificates curl<br>
sudo install -m 0755 -d /etc/apt/keyrings<br>
sudo curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc<br>
sudo chmod a+r /etc/apt/keyrings/docker.asc<br>
 
(Add the repository to Apt sources)<br>
echo \<br>
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/ubuntu \<br>
  $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | \<br>
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null<br>
sudo apt-get update<br>
sudo apt-get install docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin<br>

sudo groupadd docker<br>
sudo usermod -aG docker $USER<br>
### Crear carpeta para el volumen persistente
mkdir /home/k8worker02/kubedata<br>

# Despliegue del cluster con KNE (nodo master)



### KNE en nodo controller
git clone https://github.com/openconfig/kne.git<br>
cd kne<br>
make install<br>

## Despliegue de cluster
### Instalación Golang
Version : 1.21.3<br>
curl -O https://dl.google.com/go/go1.21.3.linux-amd64.tar.gz<br>
sudo rm -rf /usr/local/go && sudo tar -C /usr/local -xzf go1.21.3.linux-amd64.tar.gz<br>
rm go1.21.3.linux-amd64.tar.gz<br>
export PATH=$PATH:/usr/local/go/bin<br>
export PATH=$PATH:$(go env GOPATH)/bin<br>

### Despliegue de cluster
kne deploy kne/deploy/kne/kubeadm.yaml (emplear el del repositorio)<br>
Anotar token y hash del log generado al finalizar el comando para añadir nodos al cluster
### Uso de cluster:
mkdir -p $HOME/.kube<br>
sudo cp -i /etc/kubernetes/admin.conf $HOME/.kube/config<br>
sudo chown $(id -u):$(id -g) $HOME/.kube/config<br>

### Limpiar datos de CNI
kubeadm reset
systemctl stop kubelet
systemctl stop docker
rm -rf /var/lib/cni/
rm -rf /var/lib/kubelet/*
rm -rf /etc/cni/
ifconfig cni0 down
ifconfig flannel.1 down
ifconfig docker0 down
ip link delete cni0
ip link delete flannel.1
systemctl start kubelet
systemctl start docker

### Instalación de Flannel (CLI):
kubectl apply -f https://github.com/flannel-io/flannel/releases/latest/download/kube-flannel.yml<br>
### Instalación de Multus-cni:
git clone https://github.com/k8snetworkplumbingwg/multus-cni.git && cd multus-cni<br>
cat ./deployments/multus-daemonset.yml |kubectl apply -f -<br>

## Agregación de nodos al cluster (desde nodos worker)
kubeadm join 192.168.1.100:6443 --token (TOKEN) --discovery-token-ca-cert-hash sha256:(HASH) --cri-socket unix:///var/run/cri-dockerd.sock<br>

# Creación y uso de topología


## Crear Topología
kne create examples/arista/ceos/2ceos/2ceos.yaml (copiar carpeta 2ceos del repositorio a la ruta kne/arista/ceos)<br>

## Acecesos remotos
Router: ssh admin@ip del servicio ssh del router (usuario/contraseña: admin/admin)
Host (desde el nodo donde está desplegado): docker exec –it (id del contenedor) sh<br>
## Configuración de hosts
Ver archivo “configuracion/hostX” y aplicar comandos en cada host<br>
## Comandos testing
traceroute <<IP red interna>><br>
ping <<IP red interna>> -i <<intervalo>> -s <<tamaño bytes>><br>

## Comandos router ceos
tcmp dump –i <<nombre interfaz>><br>
# Despliegue Prometheus (nodo maestro)
kubectl create namespace monitoring<br>
## Prometheus
git clone https://github.com/techiescamp/kubernetes-prometheus<br>
Kubectl create –f <<archivo>><br>

Desplegar:<br>
•	clusterRole.yaml<br>
•	config-map.yaml<br>
•	prometheus-deployment.yaml<br>
•	prometheus-service.yaml<br>
## Kube-metrics

git clone https://github.com/devopscube/kube-state-metrics-configs.git<br>

kubectl apply -f kube-state-metrics-configs/<br>

## Node exporter

git clone https://github.com/bibinwilson/kubernetes-node-exporter<br>

kubectl create -f daemonset.yaml<br>

# Despliegue administrador SNMP (nodo maestro)
sudo apt update<br>
sudo apt install snmp snmp-mibs-downloader<br>
sudo nano /etc/snmp/snmp.conf (aplicar los cambios del archivo del repositorio)<br>

# Uso de scripts
## Instalación de Python3
sudo apt-get install python3<br>
## Instalación de paquetes
pip install kubernetes<br>
pip install prometheus-client
pip install pysnmp
pip install asciichartpy

## Uso del script
python3 <<archivo .py>>
