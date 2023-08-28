#!/usr/bin/env python

import os
import sys
from datetime import datetime
import logging 
from Github import GithubCommitExtractor
import argparse 
import pandas as pd
from sqlalchemy import create_engine
import psycopg2
import psycopg2.extras
import os
from dotenv import load_dotenv



def filter_json_records(json_commits):
    fil_records = []
    for rec in json_commits:
        commit_sha = rec['sha']
        committer_name = rec['commit']['author']['name']
        committer_email =  rec['commit']['author']['email']
        committer_date = rec['commit']['author']['date']
        res = { 'commit_id' : commit_sha,
                'committer_name': committer_name, 
                'committer_email': committer_email,
                'committer_date': committer_date,
                }
        fil_records.append(res)
    return fil_records


def loadDB(records, envfile):
    load_dotenv(dotenv_path=envfile)
    # set up the db connection
    connection = psycopg2.connect(
        host="localhost",
        port = 5432,
        database=os.getenv('DB_NAME'),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASSWD'),
    )
    connection.autocommit = True
    with connection.cursor() as cursor:
        psycopg2.extras.execute_batch(cursor, """
            INSERT INTO commits VALUES (
                %(commit_id)s,
                %(committer_name)s,
                %(committer_email)s,
                %(committer_date)s
            );
        """, filtered_records)
    connection.close()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(name)s-%(levelname)s-%(asctime)s-%(message)s")
    logger = logging.getLogger("github_etl")
    envfile = os.path.join(os.path.dirname(os.path.dirname(__file__)),".env")
    argp = argparse.ArgumentParser()
    argp.add_argument('-u', dest="github_url", required=True, action='store', type=str, help="github repo url")
    argp.add_argument('-d', dest='interval_days', default=180, action='store', type=int, help="time interval in days (def: 180)")
    argp.add_argument('-e', dest='env_file', default=envfile, help="path to the .env file (def:../.env)")
    args = argp.parse_args()
    logger.info(f"env file used: {args.env_file}")
    # Create the api class object
    #example: git_extractor = GithubCommitExtractor("https://github.com/apache/airflow")
    git_extractor = GithubCommitExtractor(args.github_url)
    logger.info("extractor class is ready")
    # extract the commits
    # commits = git_extractor.fetch_commits(120)
    commits = git_extractor.fetch_commits(args.interval_days)
    if isinstance(commits, dict):
        logger.error(f"error while extracting commits {commits}")
        sys.exit(1)
    logger.info(f"finished pulling commits for {args.github_url} for the past {args.interval_days}, Total Commits: {len(commits)}")
    
    # extact the required records from the json responses
    filtered_records = filter_json_records(commits)
    logger.info(f"filtered the required records from the api response")
    # Load them into the backend DB
    loadDB(filtered_records, args.env_file)
    logger.info(f"finished loading the records to DB ({os.getenv('DB_NAME')})")