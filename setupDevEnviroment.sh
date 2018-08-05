#!/usr/bin/env bash
# script to initialize dev environment

# to solve a dns related to ubuntu issue with had to do this:
# https://kubernetes.io/docs/tasks/administer-cluster/dns-debugging-resolution/
# https://github.com/kubernetes/minikube/issues/2027 --- see down
sudo sysctl net.ipv4.tcp_fin_timeout=30
sudo sysctl net.ipv4.ip_local_port_range="15000 61000"
sudo sed -i -e 's/^#*.*DNSStubListener=.*$/DNSStubListener=no/' /etc/systemd/resolved.conf
sudo sed -i -e 's/nameserver 127.0.1.1/nameserver 8.8.8.8/' /etc/resolv.conf
systemctl is-active systemd-resolved >& /dev/null && sudo systemctl stop systemd-resolved
systemctl is-enabled systemd-resolved >& /dev/null && sudo systemctl disable systemd-resolved

sudo systemctl stop systemd-resolved
sudo systemctl disable systemd-resolved

sudo minikube stop
sudo minikube delete



sudo minikube start --vm-driver=none

kubectl create -f https://raw.githubusercontent.com/kubernetes/dashboard/master/src/deploy/recommended/kubernetes-dashboard.yaml

kubectl proxy &

# no credentials in code
DOCKERHUB_USR=$(cat ~/secrets/GITHUB_USR.txt)
DOCKERHUB_PWD=$(cat ~/secrets/GITHUB_PWD.txt)

docker login -p "$DOCKERHUB_PWD" -u "$DOCKERHUB_USR"
#restarting registry if needed
docker run -d -p 5000:5000 --restart=always --name registry registry:2


#opening a lot of terminals
cd /home/hugo/PycharmProjects/AppProject
#bash terminals.sh


#example build code... should be jenkins/grunt
#  docker build  ./aioverlord-frontend/  --tag nathor/frontend:latest
#  docker tag 45cdb98cc93d nathor/backend:latest
#  docker push nathor/frontend:latest
#  docker push nathor/backend:latest
# kubectl get ep/web -o jsonpath="{.subsets[0].addresses[0].ip}"
# kubectl get ep/web -o jsonpath="{.subsets[0].ports[0].port}"

#echo web address
# echo  "$(kubectl get ep/web -o jsonpath='{.subsets[0].addresses[0].ip}'):$(kubectl get ep/web -o jsonpath='{.subsets[0].ports[0].port}')"
#echo  "$(kubectl get ep/flask -o jsonpath='{.subsets[0].addresses[0].ip}'):$(kubectl get ep/flask -o jsonpath='{.subsets[0].ports[0].port}')"




