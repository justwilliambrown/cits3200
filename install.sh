#!/bin/bash 
#download the mysql server
wget -O mysql.deb https://dev.mysql.com/get/mysql-apt-config_0.8.13-1_all.deb 
#installing all the dependencies for the web front end
python3 -m pip install --upgrade pip
mkdir gamelogs cfg upload_files 
