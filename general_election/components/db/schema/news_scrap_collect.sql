-- DROP TABLE news_scrap_collect;

CREATE TABLE news_scrap_collect (
    collect_no           SERIAL,
    pvdr_cd              INTEGER,
    keyword              VARCHAR(50),
    created_at           VARCHAR(14)      DEFAUlT TO_CHAR(NOW(), 'YYYYMMDDHH24MISS'),
    CONSTRAINT news_scrap_collect_pk PRIMARY KEY (collect_no)
);