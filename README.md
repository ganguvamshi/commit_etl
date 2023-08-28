# commit_etl

## Assessment

For a particular repository, example Airflow (https://github.com/apache/airflow)
- pull in the commits  over the last 6 months. (plus points if this window of time can be varied) 

With the data ingested, address the follow queries: 
- For the ingested commits, determine the top 5 committers ranked by count of commits and  their number of commits. 
- For the ingested commits, determine the committer with the longest commit streak. 
- For the ingested commits, generate a heatmap of number of commits count by all users by day  of the week and by 3 hour blocks. 



## Solution

Here we are using Python to authenticate and extract the commits from Github REST API. Transform or filter the required fields and load them to the local postgres database which is running inside a docker containter.


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

### Build and Run Postgres Database in Docker

#### Building the postgres docker image

Postgres docker image is built using [commitsdb.Dockerfile](./DB/commitsdb.Dockerfile) which initialise the table and view creation that are stored in [setup.sql](./DB/setup.sql). The sql creates two views within the database called `commits_view` and `commits_extended`. This `commits_extended` view contains the `Day`, `Hour` and `hour_block` calculated automatically when the data is populated into the main `commits` table.

 _make sure to set/export the environmental variables declared in [.env](./.env) file_

```
cd DB
export ../.env
docker build -t githubdb -f commitsdb.Dockerfile . 
```

### Create Github personal token 

The GitHub REST API uses rate limiting to control API traffic. This is not mandatory but the requests with authenticated connection have higher rate limits compared to the general requests. check this [token-github](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/managing-your-personal-access-tokens#creating-a-fine-grained-personal-access-token) link for more information. once the token is created, save it as a environmental variable name `GITHUB_TOKEN`

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
docker run -d -n gitpostgres -p 5432:5432 githubdb 

```

### 2. Extract the Commits from Github API using python

```
mamba activate gitapienv
python ETL/etl.py -u 'https://github.com/apache/airflow' -d 180 
```

`-d` can be changed according to the desired time window. This will extract the commits from Github repo, select the required feilds and load them into the githubdb database. 

### 3. Analysis

_make sure you are in the same conda environment_

main script: [analysis.py](./queries/analysis.py)
```
python queries/analysis.py

```
This will connect to the database, extract the records and prints the output to the console for 
- top 5 committers 
- commiter with the longest commit streak
- heatmap count grouped by `day` and `hour_block`
  - will also save the plot as [heatmap_plot.png](./queries/heatmap_plot.png)


