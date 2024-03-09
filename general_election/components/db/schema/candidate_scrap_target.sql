-- DROP TABLE candidate_scrap_target;

CREATE TABLE candidate_scrap_target (
    election_day            VARCHAR(8),
    province                VARCHAR(20),
    city                    VARCHAR(20),
    district                VARCHAR(20),
    election_dist           VARCHAR(200),
    political_party         VARCHAR(50),
    candidate_nm            VARCHAR(10),
    candidate_title         VARCHAR(10),
    created_at              VARCHAR(14)      DEFAUlT TO_CHAR(NOW(), 'YYYYMMDDHH24MISS'),
    CONSTRAINT candidate_scrap_target_pk PRIMARY KEY (election_day, province, city, district, political_party, election_dist, candidate_nm)
);