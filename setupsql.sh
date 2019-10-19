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
c=`cat <<EOF
import os
filepath = os.getcwd() + "/config.py"
file = open(filepath, "r")
f = file.read()
file.close()
f = f.replace("REPLACEME", "$1:$2@localhost")
file = open(filepath, "w+")
file.write(f)
file.close()
EOF`
python -c "$c"