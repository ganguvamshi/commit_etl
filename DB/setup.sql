CREATE TABLE IF NOT EXISTS commits (
    commit_id  VARCHAR(100),
    committer_name VARCHAR(100),
    committer_email VARCHAR(100) NOT NULL,
    committer_date TIMESTAMPTZ  NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (commit_id)
);

-- create a view with DAY and Hour columns
CREATE OR REPLACE VIEW commits_view AS 
SELECT *,
    LEFT(TO_CHAR(committer_date, 'DAY'),3) as day,
    EXTRACT(HOUR from committer_date) as hour 
FROM commits;


-- create extended view with hour block
CREATE OR REPLACE VIEW  commits_extended AS 
SELECT *,
CASE WHEN hour <=3 THEN '00-03'
            WHEN (hour >3) AND (hour <=6) THEN '03-06'
            WHEN (hour >6) AND (hour <=9) THEN '06-09'
            WHEN (hour >9) AND (hour <=12) THEN '09-12'
            WHEN (hour >12) AND (hour <=15) THEN '12-15'
            WHEN (hour >15) AND (hour <=18) THEN '15-18'
            WHEN (hour >18) AND (hour <=21) THEN '18-21'
            ELSE '21-00' END
            AS hour_block
 FROM commits_view;