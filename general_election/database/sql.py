SELECT_CANDIDATE_SCRAP_TARGET = """
WITH last_scrap AS (
    SELECT
        collect_no,
        pvdr_cd,
        keyword,
        MAX(created_at) last_dttm
    FROM
        news_scrap_collect
    GROUP BY
        collect_no, pvdr_cd, keyword 
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
    publish_date,
    publish_time,
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
    {publish_date},
    {publish_time},
    {origin_url},
    {naver_url}
) ON CONFLICT DO NOTHING;
"""
