echo "create user '$2'@'%' identified by password('$3');"| mysql --user=root --password=$1
echo "create database app; select app"| mysql -user=root --password=$1
mkdir upload_files
mkdir gamelogs
flask db init
flask db migrate -m "users table"
flask db upgrade
cat > sqluser <<- END
{
	'user' : '$2',
	'password' : '$3'
}
END