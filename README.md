# DBMS_final_project

[Dataset link](https://www.kaggle.com/datasets/pa13lito/27m-movie-ratings/)

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

### start

Just get in the directory and 

```
python3 main.py
```

The webpage will be at localhost:5000/
