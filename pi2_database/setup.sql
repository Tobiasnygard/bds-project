CREATE DATABASE IF NOT EXISTS sportsdb;

USE sportsdb;

CREATE TABLE images (
    id INT AUTO_INCREMENT PRIMARY KEY,
    url TEXT,
    source VARCHAR(50),
    classification VARCHAR(100),
    image_blob LONGBLOB NOT NULL
);

CREATE OR REPLACE VIEW classification_counts AS
  SELECT
    classification,
    COUNT(*) AS num_images
  FROM images
  GROUP BY classification;


GRANT ALL PRIVILEGES ON sportsdb.* TO 'piuser'@'%' IDENTIFIED BY 'password';
FLUSH PRIVILEGES;