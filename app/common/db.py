import logging
import sys
import time

from typing import (
    List,
    Dict,
    Any
)

import pytds
import sqlalchemy_pytds
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.automap import automap_base

from pytds import login
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

import common.utils as utils
import settings

logger = logging.getLogger(__name__)


class ConnectSpecfication(object):
    def __init__(self,
                 database=None):

        self.database = database

    def connect_spec(self):

        return pytds.connect(
                dsn=dsn,
                database=self.database,
                autocommit=False,
                user='SA',
                password='Test-password'
            )


def _get_table(engine: Engine, tablename: str) -> Table:
    meta = MetaData()

    return Table(
        tablename,
        meta,
        autoload=True,
        autoload_with=engine
    )


def get_engine(destination: str) -> Engine:
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


def insert_data(dataset: List[Dict[str, Any]],
                database: str=None,
                tablename: str=None):
    try:
        Base = automap_base()

        engine = get_engine(destination=database)
        Base.prepare(engine, reflect=True)

        meta_table = Base.classes[tablename]

        session = scoped_session(sessionmaker())
        session.configure(
            bind=engine,
            autoflush=False,
            expire_on_commit=False
        )

        start_time = time.time()

        for chunk in utils.get_chunk(dataset, chunk_size=100):

            session.bulk_insert_mappings(
                meta_table,
                chunk
            )

            session.commit()

        total_time = time.time() - start_time
        session.remove()
        logger.info(
            f'Inserted {len(dataset)} records into the'
            f' table {tablename} in {round(total_time, 2)} seconds'
        )

    except Exception as error:
        logger.exception(f'Error in insert_data() for {tablename} {error}')

        raise error

    finally:
        engine.dispose()


def insert_data_wrapper(chunked_kwarg: Dict[str, Any]):

    insert_data(**chunked_kwarg)


def execute_stored_procedure(database: str=None,
                             procedurename: str=None):

    engine = get_engine(database)
    connection = engine.connect().connection

    try:
        cursor = connection.cursor()
        cursor.callproc(procedurename)
        cursor._commit(engine)
        cursor.close()

    except Exception as error:
        logger.exception(f'Error in calling {procedurename} {error}')

        raise error

    finally:
        engine.dispose()
        connection.close()


def truncate_table(database: str,
                   tablename: str):
    try:
        engine = get_engine(destination=database)
        connection = engine.connect()

        table = _get_table(engine, tablename)
        delete_query = table.delete()
        connection.execute(delete_query)

    except Exception as error:
        logger.exception(f'Error in truncating {error}')

        raise error

    finally:
        connection.close()
        engine.dispose()


def get_count(database: str, tablename: str) -> int:
    try:
        engine = get_engine(database)
        table = _get_table(engine, tablename)

        results = engine.execute(
            select([func.count()]).select_from(table)
        )

        row_count = results.first()[0]

        results.close()

    except Exception as error:
        logger.exception(f'Error in count {tablename} {error}')

        raise error

    return row_count


def get_column_names(database: str, tablename: str) -> List[str]:
    engine = get_engine(destination=database)
    table_data = _get_table(engine=engine, tablename=tablename)

    return [
        table_info.name
        for table_info in table_data.columns
    ]
