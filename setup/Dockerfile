FROM ubuntu:20.04
ENV DEBIAN_FRONTEND noninteractive
ENV LANG C.UTF-8

WORKDIR /home

RUN apt-get -y update

RUN apt-get install -y python3-pip openssh-server zip vim git nodejs npm pkg-config mysql-server screen
RUN ln -snf /usr/bin/python3 /usr/bin/python
RUN ln -snf /usr/bin/pip3 /usr/bin/pip
RUN pip install sqlalchemy mysqlclient PyExecJS jsbeautifier xeger tqdm lithium-reducer termcolor

RUN mkdir /var/run/sshd
RUN echo "root:fuzzli123456**" | chpasswd
RUN echo "PasswordAuthentication yes" >> /etc/ssh/sshd_config
RUN echo "PermitRootLogin yes" >> /etc/ssh/sshd_config
RUN echo "service ssh restart" >> ~/.bashrc

RUN git clone https://github.com/NWU-NISL-Fuzzing/fuzzli_tool.git

WORKDIR /home/fuzzli_tool/EmbeddedFuzzer
RUN npm install esprima estraverse escodegen

RUN echo "cd /home/fuzzli_tool" >> ~/.bashrc