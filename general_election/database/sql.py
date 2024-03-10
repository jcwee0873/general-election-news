SELECT_CANDIDATE_SCRAP_TARGET = """
WITH last_scrap AS (
    SELECT
        pvdr_cd,
        keyword,
        MAX(created_at) last_dttm
    FROM
        news_scrap_collect
    GROUP BY
        pvdr_cd, keyword 
)
SELECT
    political_party,
    candidate_nm,
    candidate_title,
    s.last_dttm
FROM
    candidate_scrap_target c
    LEFT JOIN last_scrap s
    ON c.candidate_nm = s.keyword
WHERE
    TO_CHAR(NOW(), 'YYYYMMDD') <= election_day
"""



INSERT_NEWS_SCRAP_COLLECT = """
INSERT INTO news_scrap_collect (
    pvdr_cd,
    keyword
) VALUES (
    '001',
    '{keyword}'
) RETURNING collect_no
;
"""


INSERT_NEWS_SCRAP = """
WITH new_no AS (
    SELECT 
        '001' pvdr_cd,
        COALESCE(MAX(media_cd), 0) + 1 media_cd
    FROM news_media
), ins AS (
    INSERT INTO news_media (pvdr_cd, media_cd, domain_name) 
    SELECT pvdr_cd, media_cd, {domain_name}
    FROM new_no
    WHERE NOT EXISTS (
      SELECT 1 FROM news_media WHERE domain_name = {domain_name}
    )
    RETURNING media_cd
), select_insert AS (
    SELECT media_cd FROM ins
    UNION ALL
    SELECT media_cd FROM news_media WHERE domain_name = {domain_name} LIMIT 1
)

INSERT INTO news_scrap (
    collect_no,
    scrap_no,
    media_cd,
    title,
    summary,
    text,
    published_at,
    origin_url,
    naver_url
) VALUES 
(
    {collect_no},
    (SELECT COALESCE(MAX(scrap_no), 0) + 1 FROM news_scrap WHERE collect_no = {collect_no}),
    (SELECT * FROM select_insert),
    {title},
    {summary},
    {text},
    {published_at},
    {origin_url},
    {naver_url}
) ON CONFLICT DO NOTHING;
"""


SELECT_NEWS_MIGRATE_TARGET = """
SELECT
    s.collect_no,
    s.scrap_no,
    c.pvdr_cd,
    s.media_cd,
    s.origin_url,
    s.naver_url,
    s.published_at
FROM
    news_scrap s
    INNER JOIN news_scrap_collect c
    ON s.collect_no = c.collect_no
WHERE
    s.published_at >= '{sql_last_run}'
ORDER BY
    s.published_at
ASC
;
"""


INSERT_NEWS = """
INSERT INTO news (news_id, pvdr_cd, media_cd, title, summary, text, published_at, origin_url, naver_url)
SELECT '{news_id}' news_id, c.pvdr_cd, s.media_cd, s.title, s.summary, s.text, s.published_at, s.origin_url, s.naver_url
FROM news_scrap s
INNER JOIN news_scrap_collect c ON s.collect_no = c.collect_no
WHERE s.collect_no = {collect_no} AND s.scrap_no = {scrap_no}
ON CONFLICT DO NOTHING;
"""


SELECT_NEWS_REPLY_TARGET = """
SELECT
    news_id, naver_url
FROM
    news n
WHERE
    naver_url LIKE 'https://n.news.naver.com%'
    AND NOT EXISTS (SELECT 1 FROM news_reply r WHERE r.news_id = n.news_id)
    AND published_at >= '20240101000000'
    AND published_at < TO_CHAR(NOW() - interval '4 hours' , 'YYYYMMDDHH24MISS')
"""


INSERT_NEWS_REPLY_COL = """
INSERT INTO news_reply(
    news_id,
    rply_no,
    rply,
    writer,
    agree_cnt,
    disagree_cnt,
    written_at
) VALUES 
"""

INSERT_NEWS_REPLY_VAL = """
(
    '{news_id}',
    {rply_no},
    {rply},
    {writer},
    {agree_cnt},
    {disagree_cnt},
    '{written_at}'
)
"""