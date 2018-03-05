#!/usr/bin/env bash

sudo systemctl stop systemd-resolved
sudo systemctl disable systemd-resolved

sudo minikube start --vm-driver=none

kubectl create -f https://raw.githubusercontent.com/kubernetes/dashboard/master/src/deploy/recommended/kubernetes-dashboard.yaml

kubectl proxy &

DOCKERHUB_USR=$(cat ~/secrets/GITHUB_USR.txt)
DOCKERHUB_PWD=$(cat ~/secrets/GITHUB_PWD.txt)

docker login -p "$DOCKERHUB_PWD" -u "$DOCKERHUB_USR"

# might not be needed
kubectl create -f ./aioverlord-frontend/webPersistentVolume.yaml

bash terminals.sh


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




