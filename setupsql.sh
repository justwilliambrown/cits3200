#!/bin/bash
mysql --login-path=local -e "create user '$1'@'%' identified by '$2';"
mysql --login-path=local -e "create database app; select app;"
mysql --login-path=local -e "grant all privileges on app.* to $1;"
cat > sqluser.txt <<- END
{
	"user" : "$1",
	"password" : "$2"
}
END
#echo "SQL_USER=$1:$2@%" | sudo cat >> /etc/environment
python3 replacedetails.py $1 $2 
