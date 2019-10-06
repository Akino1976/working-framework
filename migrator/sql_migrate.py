import logging
import sys
import os
import time
import logging

from glob import glob
from typing import (
    List,
    Dict,
    Any
)

import pytds
import sqlalchemy_pytds


from sqlalchemy.orm import scoped_session, sessionmaker

from sqlalchemy import (
    MetaData,
    Table,
    create_engine,
    text,
    func,
    update,
    and_,
    select
)
from sqlalchemy.engine import Engine

logger = logging.getLogger(__name__)


DB_ENDPOINT = os.getenv('storage')
DB_USERNAME = os.getenv('DB_USERNAME', 'SA')
ENVIRONMENT = os.getenv('ENVIRONMENT', 'docker')
DB_PASSWORD_KEY = os.getenv('DB_PASSWORD_KEY')


def list_all_files(path: str, pattern: str=None)->List[str]:
    sorted_list = []

    if os.path.isdir(path):
        glob_pattern = '*.*' if pattern is None else pattern
        all_files = [
            base_path for filepath in os.walk(path)
            for base_path in glob(os.path.join(filepath[0], glob_pattern))
        ]

        sorting_criteria = [
            'Tables',
            'Functions',
            'Procedures'
        ]

        for criteria in sorting_criteria:
            for file in all_files:
                if criteria in file:
                    sorted_list.append(file)

        return sorted_list

    else:
        raise ValueError(f'Not a valid path[{path}]')


class ConnectSpecfication(object):
    def __init__(self,
                 database=None):

        self.database = 'master' if database is None else database

    def connect_spec(self):
        return pytds.connect(
                dsn='storage',
                database=self.database,
                autocommit=True,
                user=DB_USERNAME,
                password=DB_PASSWORD_KEY
            )


def _get_engine(destination: str) -> Engine:
    con = ConnectSpecfication(database=destination)
    connection_setup = con.connect_spec

    engine = create_engine(
        f'mssql+pytds://[{destination}]',
        creator=connection_setup
    )

    try:
        assert engine.connect()
    except AssertionError as exception:
        logger.error(f'Failed to get connection: {exception}')

    return engine


def _get_table(engine: Engine, tablename: str) -> Table:
    meta = MetaData()

    return Table(
        tablename,
        meta,
        autoload=True,
        autoload_with=engine
    )


def create_databases(databases: List[str], drop: bool=False):
    engine = _get_engine(destination='master')
    connect = engine.connect()

    for database in databases:
        logger.info(f'Checking if database {database} exists')

        query_db_exists = """
            SELECT name
            FROM [master].[sys].[databases]
            WHERE NAME = '{database}'
        """.format(
            database=database
        )

        res_db_exists = connect.execute(query_db_exists)
        db_exists = len(res_db_exists.fetchall()) > 0

        if not db_exists:
            connect.execute(f'CREATE DATABASE [{database}]')

        res_db_exists.close()

        logger.info(f'Provisioned database {database}')

    connect.close()
    engine.dispose()


def provision_sql(database: str, path: str=None):
    sql_path = os.path.join(
        path,
        database
    )

    if os.path.exists(sql_path):
        engine = _get_engine(destination=database)
        connection = engine.connect()

        sql_files = list_all_files(path=sql_path)

        if sql_files:

            for sqlpath in sql_files:
                logger.info(f'Executing query from file [{sqlpath}')

                with open(os.path.join(sqlpath), 'r') as sqlpath:
                    statement = text(sqlpath.read())
                    connection.execute(statement)

                    logger.info(f'Done [{sqlpath}]')

            logger.info(f'Succesfully executed {len(sql_files)} files')

        connection.close()
        engine.dispose()


def migrate(path: str):
    databases = os.listdir(path)

    create_databases(
        databases
    )

    for database in databases:
        provision_sql(
            database=database,
            path=path
        )

    logger.info('Completed migrations')
