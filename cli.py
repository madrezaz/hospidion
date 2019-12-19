import psycopg2
import getpass
from core.dion import QueryExecutor, SqlException
from core.models import *


def authenticate(username, password):
    con, cur = QueryExecutor.create_db_connection()
    cur.execute("select * from users where username = %s and password = %s", (username, password))
    user = cur.fetchone()
    session = None
    if user is not None:
        table = Table(user[2])
        pk = tables[table].columns[0]
        q = "select * from %s where %s = " % (table.value, pk)
        cur.execute(q + "%s", (user[3],))
        entity = cur.fetchone()
        session = Session(user, entity)
    cur.close()
    con.close()
    return session


def main():
    print("***Welcome to Sharif [Mental]Hospital***")
    session = None
    while session is None:
        username = input("Username: ")
        password = getpass.getpass(prompt="Password: ")
        session = authenticate(username, password)
        if session is None:
            print("Invalid username or password")

    executor = QueryExecutor(session)
    print("+++ Hello %s +++" % session.user[0])
    query = input("$ ")
    while query.lower() != 'q':
        try:
            result = executor.execute(query)
            if type(result) is list:
                print("\n".join(str(r) for r in result))
            elif type(result) is Privacy:
                print("Readers:")
                print(result.readers)
                print("Writers:")
                print(result.readers)
            else:
                print("%d rows affected" % result)
        except DionException as ex:
            print("Error:", ex.message)
        except SqlException as ex:
            print("Error:", ex.message)
        except psycopg2._psycopg.Error as ex:
            print("Error: ", ex)
        query = input("$ ")


if __name__ == '__main__':
    main()
