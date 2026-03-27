FROM ubuntu:20.04
ENV DEBIAN_FRONTEND noninteractive
ENV LANG C.UTF-8

WORKDIR /home

RUN apt-get -y update

RUN apt-get install -y python3-pip openssh-server zip vim git nodejs npm pkg-config mysql-server screen
RUN ln -snf /usr/bin/python3 /usr/bin/python
RUN ln -snf /usr/bin/pip3 /usr/bin/pip
COPY requirements.txt .
RUN pip install -r requirements.txt

RUN mkdir /var/run/sshd
RUN echo "root:fuzzli123456**" | chpasswd
RUN echo "PasswordAuthentication yes" >> /etc/ssh/sshd_config
RUN echo "PermitRootLogin yes" >> /etc/ssh/sshd_config
RUN echo "service ssh restart" >> ~/.bashrc

RUN git clone [anonymous]

WORKDIR /home/fuzzli_tool/EmbeddedFuzzer
RUN npm install esprima estraverse escodegen

RUN echo "cd /home/fuzzli_tool" >> ~/.bashrc