import logging
import time
import sys

from typing import (
    Dict,
    Optional,
    Any,
    Union,
    Iterable,
    Tuple,
    List
)

import pytds
import sqlalchemy
import sqlalchemy_pytds

from sqlalchemy import (
    MetaData,
    Table,
    create_engine,
    text,
    insert,
    func,
    desc,
    select,
    delete,
    func
)

from sqlalchemy.engine import Engine, ResultProxy
from sqlalchemy.orm import scoped_session, sessionmaker, Session, load_only


logger = logging.getLogger(__name__)


class ConnectSpecfication(object):
    def __init__(self,
                 database=None):

        self.database = database

    def connect_spec(self):

        return pytds.connect(
                dsn='storage',
                database=self.database,
                autocommit=True,
                user='SA',
                password='Test-password'
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


def get_table(engine: Engine, table_name: str) -> Table:
    meta = MetaData()

    return Table(
        table_name,
        meta,
        autoload=True,
        autoload_with=engine
    )


def get_session(engine: Engine) -> Session:
    return scoped_session(
        sessionmaker(
            bind=engine,
            autocommit=False,
            autoflush=False,
        )
    )


def execute_stored_procedure(database: str=None,
                             procedurename: str=None,
                             arguments: List[str]=None):
    engine = get_engine(destination=database)
    connection = engine.connect().connection

    arguments = [] if arguments[0] == "''" else arguments

    try:
        cursor = connection.cursor()
        cursor.callproc(procedurename, arguments)
        cursor.close()

    except Exception as error:
        logger.exception(f'Error in calling {procedurename} {error}')

        raise error

    finally:
        engine.dispose()
        connection.close()


def execute_stored_procedure_without_arguments(database: str=None,
                                               procedurename: str=None):
    engine = get_engine(destination=database)
    connection = engine.connect().connection

    try:
        cursor = connection.cursor()
        cursor.callproc(procedurename)
        cursor.close()

    except Exception as error:
        logger.exception(f'Error in calling {procedurename} {error}')

        raise error

    finally:
        engine.dispose()
        connection.close()


def get_row_count(tablename: str, database: str) -> int:
    engine = get_engine(destination=database)
    table = get_table(engine, tablename)

    session = scoped_session(sessionmaker())
    session.configure(
        bind=engine,
        autoflush=False,
        expire_on_commit=False
    )
    try:
        result = session.query(table).count()

    except Exception as error:
        logger.exception(f'Error in row_count {error}')

        raise error

    finally:
        session.remove()
        engine.dispose()

    return result


def get_all_data(database: str, tablename: str) -> List[Dict[str, Any]]:
    engine = get_engine(destination=database)
    connection = engine.connect()
    table = get_table(engine, tablename)

    select_query = table.select()
    try:
        result = connection.execute(select_query)
        rows = [dict(row) for row in result]

    except Exception as error:
        logger.exception(f'Error in select table {tablename} {error}')
        raise error

    finally:
        connection.close()
        engine.dispose()

    return rows


def get_subset_data(database: str,
                    tablename: str,
                    orderby: str,
                    columns: List[str]=None) -> List[Dict[str, Any]]:
    engine = get_engine(destination=database)
    table = get_table(engine, tablename)

    session = scoped_session(sessionmaker())
    session.configure(
        bind=engine,
        autoflush=False,
        expire_on_commit=False
    )

    try:
        result = session.query(table).order_by(desc(table.columns[orderby]))
        result_column = [
            _column.get('name')
            for _column in result.column_descriptions
        ]

        rows = [
            dict(zip(result_column, _row))
            for _row in result.all()
        ]

        if columns is not None:
            subset_row = [
                {
                    key: value for key, value in _row.items()
                    if key in columns
                } for _row in rows
            ]

            return subset_row

    except Exception as error:
        logger.exception(f'Error in select table {tablename} {error}')
        raise error

    finally:
        session.remove()
        engine.dispose()

    return rows


def get_data(database: str,
             tablename: str) -> List[Dict[str, Any]]:
    engine = get_engine(destination=database)
    table = get_table(engine, tablename)

    session = scoped_session(sessionmaker())
    session.configure(
        bind=engine,
        autoflush=False,
        expire_on_commit=False
    )

    try:
        result = session.query(table)
        result_column = [
            _column.get('name')
            for _column in result.column_descriptions
        ]

        rows = [
            dict(zip(result_column, _row))
            for _row in result.all()
        ]

    except Exception as error:
        logger.exception(f'Error in select table {tablename} {error}')
        raise error

    finally:
        session.remove()
        engine.dispose()

    return rows


def check_if_table_exist(database: str, tablename: str):
    engine = get_engine(destination=database)
    try:
        table = get_table(engine, tablename)

    except Exception as error:
        return True

    return False


def truncate_table(database: str, tablename: str):
    engine = get_engine(destination=database)
    table = get_table(engine, tablename)
    connection = engine.connect()

    try:
        connection.execute(
            table.delete()
        )
    except Exception as error:
        logger.exception(f'Error in delete table {tablename} {error}')

    finally:
        connection.close()
        engine.dispose()


def insert_data(data_base: str,
                table_name: str,
                dataset: Dict[str, Any]):

    engine = get_engine(destination=data_base)

    try:
        table = get_table(engine, table_name)

        engine.execute(
            table.insert(),
            dataset
        )

    except Exception as error:
        logger.error(f'Error in insert_data {error}')

        raise error

    finally:
        engine.dispose()


def return_stored_procedure(data_base: str=None,
                            procedure_name: str=None) -> List[Dict[str, Any]]:
    engine = get_engine(data_base)
    connection = engine.connect().connection

    try:
        cursor = connection.cursor()
        cursor.callproc(procedure_name)

        column_names = [x[0] for x in cursor.description]
        result = [
            dict(zip(column_names, row))
            for row in cursor.fetchall()
        ]

        cursor.close()

    except Exception as error:
        logger.exception(f'Error in calling {procedure_name} {error}')

        raise error

    finally:
        engine.dispose()
        connection.close()

    return result
