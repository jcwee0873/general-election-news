-- DROP TABLE news_media;

CREATE TABLE news_media (
    pvdr_cd          VARCHAR(50),
    media_cd         INTEGER,
    media_name       VARCHAR(100),
    domain_name      VARCHAR(100),
    created_at       VARCHAR(14)   DEFAUlT TO_CHAR(NOW(), 'YYYYMMDDHH24MISS'),
    CONSTRAINT news_media_pk PRIMARY KEY (media_cd, domain_name)
);