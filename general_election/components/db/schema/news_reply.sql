-- DROP TABLE news_reply;

CREATE TABLE news_reply (
    news_id         VARCHAR(50),
    pvdr_cd         INTEGER,
    rply_no         INTEGER,
    rply            TEXT,
    writer          VARCHAR(200),
    agree_cnt       INTEGER,
    disagree_cnt    INTEGER,
    write_datetime  VARCHAR(14),
    created_at      VARCHAR(14),
    updated_at      VARCHAR(14),
    deleted_at      VARCHAR(14),
    CONSTRAINT news_reply_pk PRIMARY KEY (news_id, pvdr_cd, rply_no)
);