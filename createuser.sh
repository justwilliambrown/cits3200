echo "create user '$2'@'%' identified by password('$3');"| mysql --user=root --password=$1

cat > sqluser <<- END
{
	'user' : '$2',
	'password' : '$3'
}
END