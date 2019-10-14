#!/bin/bash 
#download the mysql server
wget https://dev.mysql.com/get/mysql-apt-config_0.8.13-1_all.deb 
#install python3 and utilities
echo installing python 3 and libraries
sudo apt-get -y update 
sudo apt-get -y install python3 python3-venv python3-pip 
#create a virtual environment for all our dependencies
python3 -m venv venv 
#installing all the dependencies for the web front end
python3 -m pip install -r dependencies.txt 
