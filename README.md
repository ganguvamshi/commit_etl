# commit_etl

## Assignment

For a particular repository, example Airflow (https://github.com/apache/airflow)
- pull in the commits  over the last 6 months. (plus points if this window of time can be varied) 

With the data ingested, address the follow queries: 
- For the ingested commits, determine the top 5 committers ranked by count of commits and  their number of commits. 
- For the ingested commits, determine the committer with the longest commit streak. 
- For the ingested commits, generate a heatmap of number of commits count by all users by day  of the week and by 3 hour blocks. 



## Solution

Using Python to authenticate and extract the commits from Github REST API. transform or filter the required fields and load them to the local postgres database which is running inside a docker containter.


## Prerequisites

- [Mamba]() A faster conda like environment manager used to create the python environment. 
- [Docker]() for building the postgres database. 


## Installation

### Create the conda environment

### Build and Run Postgres Database in Docker


## Scripts

 - [Github.py](./Github.py) used to create a GithubCommitExtractor class for connecting to Github via REST API and pull the commits 
 - [etl.py](./etl.py) The main script for Extracting the Commits, Transforming the records and Loading them to the PostgresDB
 - [setup.sql](./setup.sql) used for creating the tables and required views. 
 - [commitsdb.Dockerfile](./commitsdb.Dockerfile) Dockerfile used for building postgresDB. 
 - [.env](./.env) dot file containing the environmental variables used for DB connection.


