mysql_config_editor set --login-path=local --host=localhost --user=root --password=$1
mysql --login-path=local -e "create user '$2'@'%' identified by password '$3';"
mysql --login-path-local -e "create database app; select app;"
mkdir upload_files
mkdir gamelogs
flask db init
flask db migrate -m "users table"
flask db upgrade
cat > sqluser <<- END
{
	"user" : "$2",
	"password" : "$3"
}
END
