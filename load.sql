-- let mysql turn off strict mode
SET sql_mode = '';

CREATE TABLE tags (
    userid INT NOT NULL,
    movieid INT NOT NULL,
    tag varchar(100) NOT NULL,
    timestamp BIGINT,
	PRIMARY KEY(userid, movieid, tag)
) ;

-- 匯入 tags.csv 的數據
LOAD DATA INFILE '/var/lib/mysql-files/tags.csv'
INTO TABLE tags
FIELDS TERMINATED BY ','  -- 欄位分隔符
ENCLOSED BY '"'
LINES TERMINATED BY '\n'  -- 每行結束符
IGNORE 1 ROWS;            -- 忽略表頭


CREATE TABLE ratings (
    userid INT NOT NULL,
    movieid INT NOT NULL,
    rating FLOAT,
    timestamp BIGINT,
	PRIMARY KEY(userid, movieid)
);



LOAD DATA INFILE '/var/lib/mysql-files/ratings.csv'
INTO TABLE ratings
FIELDS TERMINATED BY ','  
LINES TERMINATED BY '\n'  
IGNORE 1 ROWS;            

CREATE TABLE movies (
    movieid INT PRIMARY KEY,
    title varchar(100),
    genres varchar(100)
);

LOAD DATA INFILE '/var/lib/mysql-files/movies.csv'
INTO TABLE movies
FIELDS TERMINATED BY ','  
LINES TERMINATED BY '\n'  
IGNORE 1 ROWS;            

CREATE TABLE links (
    movieid INT PRIMARY KEY,
    imdbid varchar(10),
    tmdbid INT
);

LOAD DATA INFILE '/var/lib/mysql-files/links.csv'
INTO TABLE links
FIELDS TERMINATED BY ','  
LINES TERMINATED BY '\n'  
IGNORE 1 ROWS;            

CREATE TABLE users (
    userid INT PRIMARY KEY,
    username varchar(50) DEFAULT NULL,
    `password` varchar(200) DEFAULT NULL
);

--for approving the speed of query with rating
CREATE TABLE total_ratings (
    movieid INT PRIMARY KEY NOT NULL,
    rating_count INT DEFAULT 0,
    rating_sum FLOAT DEFAULT 0,
    avg_rating FLOAT DEFAULT 0
);

INSERT INTO total_ratings (movieid,rating_count,rating_sum,avg_rating)
SELECT movieid, COUNT(rating) as rating_count, SUM(rating) as rating_sum, (SUM(rating)/COUNT(rating)) as avg_rating
FROM ratings
GROUP BY movieid;
