#!/usr/bin/env bash

printf "%s\n" "Script to download kubernets source and build binary files"
printf "%s\n" "Supposed to run on RHEL based distributions"

# check user
if [ "$UID" -ne 0 ]; then
    printf "%s\n" "You have to be root in order to run this script"
    exit 0
fi

# install software

yum install -y golang glibc-static device-mapper-devel btrfs-progs btrfs-progs-devel sqlite-devel docker git

systemctl start docker
systemctl enable docker

printf "%s\n" "Clonning kubernetes code and starting build"

cd /root/

git clone https://github.com/GoogleCloudPlatform/kubernetes
cd kubernetes/build
sed -i 's/KUBE_SKIP_CONFIRMATIONS\:\-n/KUBE_SKIP_CONFIRMATIONS\:\-y/' common.sh
./release.sh

cd ~/kubernetes/_output/dockerized/bin/linux/amd64

printf "%s\n" "Binaries are build and can be found in ~/kubernetes/_output/dockerized/bin/linux/amd64"

ls -l

exit 0



