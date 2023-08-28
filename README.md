# commit_etl

## Assessment

For a particular repository, example Airflow (https://github.com/apache/airflow)
- pull in the commits  over the last 6 months. (plus points if this window of time can be varied) 

With the data ingested, address the follow queries: 
- For the ingested commits, determine the top 5 committers ranked by count of commits and  their number of commits. 
- For the ingested commits, determine the committer with the longest commit streak. 
- For the ingested commits, generate a heatmap of number of commits count by all users by day  of the week and by 3 hour blocks. 



## Solution

Here I am using Python for ETL process. This will authenticate and extract the commits from Github REST API, Transform or filter the required fields and load them to the local postgres database which is running inside a docker containter.


## Prerequisites

- [Mamba](https://mamba.readthedocs.io/en/latest/mamba-installation.html#mamba-install) A faster conda like environment manager used to create the python environment. 
- [Docker](https://docs.docker.com/engine/install/) for building the postgres database. 


## Installation

### Create the conda environment

you can create the conda environment using [env.yml](./env.yml) file

```
mamba env create -f env.yml -n gitapienv
mamba activate gitapienv
```

### Build Postgres docker image

Postgres docker image is built using [commitsdb.Dockerfile](./DB/commitsdb.Dockerfile) which initialise the table and view creation that are stored in [setup.sql](./DB/setup.sql). The sql creates two views within the database called `commits_view` and `commits_extended`. This `commits_extended` view contains the `Day`, `Hour` and `hour_block` columns which are calculated automatically when the data is populated into the main `commits` table and the view is invoked.

 _make sure to set/export the environmental variables declared in [.env](./.env) file_

```
cd DB
export ../.env
docker build -t githubdb -f commitsdb.Dockerfile . 
```

### Create Github personal token 

The GitHub REST API uses rate limiting to control API traffic. This is not mandatory but the requests with authenticated connection have higher rate limits compared to the general requests. Check this [token-github](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/managing-your-personal-access-tokens#creating-a-fine-grained-personal-access-token) link for more information. Once the token is created, save it as a environmental variable name `GITHUB_TOKEN`

```
export GITHUB_TOKEN='adceafaxxxxxx......'
# can save it to ~/.bashrc for more consistent usage
```

## Scripts

ETL:
 - [Github.py](./ETL/Github.py) used to create a GithubCommitExtractor class for connecting to Github via REST API and pull the commits 
 - [etl.py](./ETL/etl.py) The main script for Extracting the Commits, Transforming the records and Loading them to the PostgresDB

Database:
 - [setup.sql](./DB/setup.sql) used for creating the tables and required views. 
 - [commitsdb.Dockerfile](./DB/commitsdb.Dockerfile) Dockerfile used for building postgresDB. 

Environment:
 - [.env](./.env) dot file containing the environmental variables used for DB connection.

Queries:
 - [sql.py](./queries/sql.py) used for creating database class to connect and read from the postgres.
 - [analysis.py](./queries/analysis.py) contains the solutions for the three anlysis questions


## Implementation

### 1. Start the Postgres DB

```
# run the built docker image in detached mode
docker run -d --name gitpostgres --env-file ../.env -p 5432:5432 githubdb 

```

Check whether the container is running. If it is running, we can ssh into the running container to see the tables and records

```
docker ps 

```
should list the running container as below
```
CONTAINER ID   IMAGE      COMMAND                  CREATED         STATUS         PORTS                    NAMES
ad814f168826   githubdb   "docker-entrypoint.s…"   4 seconds ago   Up 4 seconds   0.0.0.0:5432->5432/tcp   gitpostgres
```

the tables and records can be listed as well. we should not see any records as we just created the table alone.
```
docker exec -it gitpostgres bash 

#once login inside, connect to psql 
psql -d github -U vamshi

#show the table records
select * from commits;

```
desired output:
```
root@ad814f168826:/# psql -d github -U vamshi
psql (15.4 (Debian 15.4-1.pgdg120+1))
Type "help" for help.

github=# \dt
         List of relations
 Schema |  Name   | Type  | Owner
--------+---------+-------+--------
 public | commits | table | vamshi
(1 row)

github=# select * from commits;
 commit_id | committer_name | committer_email | committer_date | created_at 
-----------+----------------+-----------------+----------------+------------
(0 rows)

github=#
```
### 2. Extract the Commits from Github API using python

```
mamba activate gitapienv
python ETL/etl.py -u 'https://github.com/apache/airflow' -d 180 2>&1 |tee ETL/log_etl.txt
```

`-d` can be changed according to the desired time window. This will extract the commits from Github repo, select the required feilds and load them into the githubdb database. 

output log file: [log_etl.txt](./ETL/log_etl.txt)

### 3. Analysis

I am using Python for the analysis. This will read data stored in the postgres database via `sqlalchemy` and `psycopg2`. I used pandas to analyse the data and return the required answers. 

main script: [analysis.py](./queries/analysis.py)
```
cd queries
python analysis.py 2>&1 |tee log_analysis.txt

```

output:
```
postgres_sql-INFO-2023-08-28 17:14:34,552-Conncection successful to github.commits
Top 5 Commiters 
     committer_name  num_counts
0     Jarek Potiuk         405
1    Hussein Awala         142
2          eladkal          93
3   Tzu-ping Chung          69
4  Miroslav Šedivý          69

Commiter with longest streak:
     committer_name   streak_duration
126   Jarek Potiuk 178 days 07:06:48

count heatmap by Day and Hour Block:
 hour_block  00-03  03-06  06-09  09-12  12-15  15-18  18-21  21-00
day
MON             8     28     61     34     35     54     68     17
TUE             9     26     32     47     39     46     75     34
WED            21     33     60     51     40     55     55     33
THU            20     26     54     43     58     66     63     43
FRI             9     33     51     45     39     96     65     26
SAT             3     14     51     29     30     40     46     21
SUN             4     21     13     23     26     37     40     28

heatmap plot is saved to heatmap_plot.png
```

output file: [log_analysis.txt](./queries/log_analysis.txt)
This will connect to the database, extract the records and prints the output to the console for 
- top 5 committers 
- commiter with the longest commit streak
- heatmap count grouped by `day` and `hour_block`
  - will also save the plot as [heatmap_plot.png](./queries/heatmap_plot.png)


