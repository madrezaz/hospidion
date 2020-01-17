import psycopg2
import getpass

import config
from core.auth import create_session
from core.dion import DionExecutor, SqlException
from core.models import *
from core.sql import DefaultQueryExecutor, SqlQuery
from outsourcing.indexing import IndexingQueryExecutor
from outsourcing.partitioning import PartitioningQueryExecutor


def create_db_executor():
    if config.outsourced == 0:
        executor = DefaultQueryExecutor
    elif config.outsourced == 1:
        executor = IndexingQueryExecutor
    else:
        executor = PartitioningQueryExecutor
    return executor(config.db_name, config.db_user, config.db_password, config.db_host, config.db_port)


def main():
    db_executor = create_db_executor()
    print("***Welcome to Sharif [Mental]Hospital***")
    session = None
    while session is None:
        username = input("Username: ")
        password = getpass.getpass(prompt="Password: ")
        session = create_session(db_executor, username, password)
        if session is None:
            print("Invalid username or password")

    executor = DionExecutor(session, db_executor)
    print("+++ Hello %s +++" % session.user[0])
    query = input("$ ")
    while query.lower() != 'q':
        try:
            result = executor.execute(query)
            if type(result) is list:
                print("\n".join(str(r) for r in result))
            elif type(result) is Privacy:
                print("Readers:")
                print(", ".join([r[0] for r in result.readers]))
                print("Writers:")
                print(", ".join([r[0] for r in result.writers]))
            else:
                print("%d rows affected" % result)
        except DionException as ex:
            print("Error:", ex.message)
        except SqlException as ex:
            print("Error:", ex.message)
        except psycopg2._psycopg.Error as ex:
            print("Error: ", ex)
        query = input("$ ")


def main2():
    db = create_db_executor()
    while True:
        print(db.execute_read(SqlQuery.parse(input())))


if __name__ == '__main__':
    main()
