-- DROP TABLE common_code;

CREATE TABLE common_code (
    category_cd           VARCHAR(10),
    category_nm           VARCHAR(50),
    code                  VARCHAR(50),
    code_name             VARCHAR(50),
    created_at            VARCHAR(14)   DEFAUlT TO_CHAR(NOW(), 'YYYYMMDDHH24MISS'),
    CONSTRAINT common_code_pk PRIMARY KEY (category_cd, code)
);