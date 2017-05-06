#!/usr/bin/env bash
#
#
# Copyright (c) 2015 Elvir Kurić 
#
# This software is licensed to you under the GNU General Public License,
# version 3 (GPLv3). There is NO WARRANTY for this software, express or
# implied, including the implied warranties of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. You should have received a copy of GPLv3
# along with this software; if not, see http://www.gnu.org/licenses/gpl.txt
#


printf "%s\n" "Script to download kubernets source and build binary files"
printf "%s\n" "Supposed to run on RHEL based distributions"

# check user

if [ "$UID" -ne 0 ]; then
    printf "%s\n" "You have to be root in order to run this script"
    exit 0
fi

log_file=/root/build_kubernetes.$(date +%d.%m.%Y).log

# install software

start_docker(){

    systemctl start docker | tee -a $log_file
    systemctl enable docker | tee -a $log_file
}

install_software() {

    if grep -q "^Fedora" /etc/redhat-release; then
        echo "Installing on Fedora, we need docker-io"
        yum install -y golang glibc-static device-mapper-devel btrfs-progs btrfs-progs-devel sqlite-devel docker-io git | tee -a $log_file
        start_docker

    elif egrep -q "release 6|release 7" /etc/redhat-release; then
        echo "Installing on RHEL 6/CentoOS 6, or RHEL 7/CentOS 7 , docker package is named docker"
        yum install -y golang glibc-static device-mapper-devel btrfs-progs btrfs-progs-devel sqlite-devel docker git | tee -a $log_file
        start_docker

    else
        echo "Cannot determine rpm based platform here, ... check it again"
        exit 1
    fi
}

install_software

printf "%s\n" "Clonning kubernetes code and starting build"

cd /root/

git clone https://github.com/GoogleCloudPlatform/kubernetes | tee -a $log_file
cd kubernetes/build
sed -i 's/KUBE_SKIP_CONFIRMATIONS\:\-n/KUBE_SKIP_CONFIRMATIONS\:\-y/' common.sh
./release.sh | tee -a $log_file

cd ~/kubernetes/_output/dockerized/bin/linux/amd64

printf "%s\n" "Binaries are build and can be found in ~/kubernetes/_output/dockerized/bin/linux/amd64"

for m in $(ls -l | awk '{print $NF}');do
    sha256sum $m >> sha256sums.txt
done

ls -l | tee -a $log_file

exit 0



