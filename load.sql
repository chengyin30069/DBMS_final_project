CREATE TABLE tags (
    userid INT PRIMARY KEY,
    movieid INT PRIMARY KEY,
    tag INT PRIMARY KEY,
    timestamp BIGINT
);

-- 匯入 tags.csv 的數據
LOAD DATA INFILE '/path/to/tags.csv'
INTO TABLE tags
FIELDS TERMINATED BY ','  -- 欄位分隔符
LINES TERMINATED BY '\n'  -- 每行結束符
IGNORE 1 ROWS;            -- 忽略表頭

CREATE TABLE ratings (
    userid INT PRIMARY KEY,
    movieid INT PRIMARY KEY,
    rating FLOAT,
    timestamp BIGINT
);

LOAD DATA INFILE '/path/to/ratings.csv'
INTO TABLE ratings
FIELDS TERMINATED BY ','  
LINES TERMINATED BY '\n'  
IGNORE 1 ROWS;            

CREATE TABLE movies (
    movieid INT PRIMARY KEY,
    title varchar(50),
    genres varchar(100)
);

LOAD DATA INFILE '/path/to/movies.csv'
INTO TABLE movies
FIELDS TERMINATED BY ','  
LINES TERMINATED BY '\n'  
IGNORE 1 ROWS;            

CREATE TABLE links (
    movieid INT PRIMARY KEY,
    imdbid varchar(10),
    tmdbid INT,
);

LOAD DATA INFILE '/path/to/links.csv'
INTO TABLE links
FIELDS TERMINATED BY ','  
LINES TERMINATED BY '\n'  
IGNORE 1 ROWS;            

CREATE TABLE users (
    userid INT PRIMARY KEY,
    username varchar(50) DEFAULT NULL,
    password varchar(50) DEFAULT NULL
);
