# DBMS_final_project

## Set up

### Download dependencies

Debian-base
```
sudo apt install mysql python3-flask python3-mysql.connector
```
or
Arch-base
```
sudo pacman -S mariadb python-flask python-mysql-connector
```
then start or enable the DB
```
sudo systemctl start mysql
```

### DB:

User and privileges
```sql
CREATE DATABASE DB_final;
CREATE USER 'final_backend'@'localhost' IDENTIFIED BY 'passwd';
GRANT ALL PRIVILEGES ON `DB_final` . * TO 'final_backend'@'localhost';
```

Load dataset: Just use load.sql in the repo

