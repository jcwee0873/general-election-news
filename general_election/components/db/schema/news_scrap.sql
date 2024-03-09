-- DROP TABLE news_scrap;

CREATE TABLE news_scrap (
    collect_no              INTEGER,
    scrap_no                INTEGER,
    media_cd                INTEGER,
    title                   TEXT,
    summary                 TEXT,
    text                    TEXT,
    publish_date            VARCHAR(8),
    publish_time            VARCHAR(6),
    origin_url              VARCHAR(500),
    naver_url               VARCHAR(500),
    created_at              VARCHAR(14)      DEFAUlT TO_CHAR(NOW(), 'YYYYMMDDHH24MISS'),
    updated_at              VARCHAR(14),
    deleted_at              VARCHAR(14),
    CONSTRAINT news_scrap_pk PRIMARY KEY (collect_no, scrap_no)
);