FROM centos:7

RUN yum install -y https://dl.fedoraproject.org/pub/epel/epel-release-latest-7.noarch.rpm 
RUN curl -o /etc/yum.repos.d/pbench.repo https://copr.fedorainfracloud.org/coprs/ndokos/pbench/repo/epel-7/ndokos-pbench-epel-7.repo 

RUN yum install -y openssh-clients pbench-fio pbench-agent pbench-report pbench-sysstat wget automake libtool pbench-sysstat-debuginfo mariadb mariadb-bench mariadb-server firewalld \
	mariadb-test gcc gcc-c++ python2-pandas autoconf automake make libtool zlib zlib-devel openssl-devel gettext mariadb-devel \
	uperf netperf iozone fio smallfile stress openssh-server libaio-devel && yum clean all

# setup ssh keys
RUN ssh-keygen -A && \
    systemctl enable sshd && \ 
    echo "root:redhat" | chpasswd
# create this key prior running docker build - use : ssh-keygen 
COPY id_rsa_fio.pub  /root/.ssh/authorized_keys

# some more stuff 
RUN rm -f /lib/systemd/system/systemd*udev* && rm -f /lib/systemd/system/getty.target
RUN sed -i 's/PermitRootLogin without-password/PermitRootLogin yes/' /etc/ssh/sshd_config
RUN sed 's@session\s*required\s*pam_loginuid.so@session optional pam_loginuid.so@g' -i /etc/pam.d/sshd
RUN echo "export TERM=dumb" >> /root/.bashrc
WORKDIR /root
EXPOSE 22
USER root
CMD ["/usr/sbin/sshd", "-D"]
