import os
import sys
import logging
import psycopg2
import sqlalchemy
import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.sql import text
from urllib.parse import quote_plus


load_dotenv(dotenv_path="../.env")

logging.basicConfig(level=logging.INFO, format="%(name)s-%(levelname)s-%(asctime)s-%(message)s")
logger = logging.getLogger("postgres_sql")

class CommitsDB():
    "PostgresSQL calss for commits db"

    def __init__(self):
        self.port = 5432
        self.dbuser = os.getenv('DB_USER')
        self.dbpasswd = os.getenv('DB_PASSWD')
        self.hostname = 'localhost'
        self.dbname = os.getenv('DB_NAME')
        self.table = 'commits'
    
    def create_engine(self):
        try:
            uri =  f"postgresql+psycopg2://{quote_plus(self.dbuser)}:{quote_plus(self.dbpasswd)}@{self.hostname}:{self.port}/{self.dbname}"
            engine = create_engine(uri)
        except Exception as err:
            logger.error(err)
            return False
        else:
            return engine
    
    def test_conn(self):
        query = f"select * from {self.table} limit 20;"
        try:
            db_engine = self.create_engine()
            with db_engine.connect() as conn:
                query = conn.execute(text(query))
            df = pd.DataFrame(query.fetchall())
            
        except Exception as error:
            logger.error(f"Connection failed {error}")
            return False
        else:
            logger.info(f"Conncection successful to {self.dbname}.{self.table}")
            return df
        
    
    def read_query(self, query):
        """ get data by sql query """
        try:
            db_engine = self.create_engine()
            with db_engine.connect() as conn:
                query = conn.execute(text(query))
            df = pd.DataFrame(query.fetchall())
        except Exception as err:
            logger.error(err)
            return False
        else:
            return df
        
