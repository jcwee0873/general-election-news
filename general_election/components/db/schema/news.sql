-- DROP TABLE news;

CREATE TABLE news (
    news_id                 VARCHAR(50),
    pvdr_cd                 INTEGER,
    media_cd                INTEGER,
    title                   TEXT,
    summary                 TEXT,
    text                    TEXT,
    publish_dt            VARCHAR(8),
    publish_tm            VARCHAR(6),
    origin_url              VARCHAR(500),
    naver_url               VARCHAR(500),
    created_at              VARCHAR(14)      DEFAUlT TO_CHAR(NOW(), 'YYYYMMDDHH24MISS'),
    updated_at              VARCHAR(14),
    deleted_at              VARCHAR(14),
    CONSTRAINT news_pk PRIMARY KEY (news_id)
);

