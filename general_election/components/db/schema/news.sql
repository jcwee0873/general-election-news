-- DROP TABLE news;

CREATE TABLE news (
    news_id                 VARCHAR(50),
    pvdr_cd                 VARCHAR(50),
    media_cd                INTEGER,
    title                   TEXT,
    summary                 TEXT,
    text                    TEXT,
    published_at            VARCHAR(14),
    origin_url              VARCHAR(500),
    naver_url               VARCHAR(500),
    created_at              VARCHAR(14)      DEFAUlT TO_CHAR(NOW(), 'YYYYMMDDHH24MISS'),
    updated_at              VARCHAR(14),
    deleted_at              VARCHAR(14),
    CONSTRAINT news_pk PRIMARY KEY (news_id)
);

CREATE INDEX news_pub_at_idx ON news (published_at);