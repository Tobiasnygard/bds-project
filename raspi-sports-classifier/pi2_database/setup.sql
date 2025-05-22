CREATE DATABASE sportsdb;
USE sportsdb;

CREATE TABLE images (
    id INT AUTO_INCREMENT PRIMARY KEY,
    url TEXT,
    source VARCHAR(50),
    classification VARCHAR(100),
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

GRANT ALL PRIVILEGES ON sportsdb.* TO 'piuser'@'%' IDENTIFIED BY 'password';
FLUSH PRIVILEGES;
