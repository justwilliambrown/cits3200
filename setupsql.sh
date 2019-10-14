#! /bin/bash
mysql_config_editor set --login-path=local --host=localhost --user=root --password 
mysql --login-path=local -e "create user '$1'@'%' identified by '$2';" 
mysql --login-path=local -e "create database app; select app;" 
mkdir upload_files 
mkdir gamelogs 
flask db init 
flask db migrate -m "users table" 
flask db upgrade 
cat > sqluser <<- END 
{
	"user" : "$1",
	"password" : "$2"
}
END
