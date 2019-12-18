from core.dion import QueryExecutor
from core.models import *


def authenticate(username, password):
    con, cur = QueryExecutor.create_db_connection()
    cur.execute("select * from users where username = %s and password = %s", (username, password))
    user = cur.fetchone()
    session = None
    if user is not None:
        table = Table(user[2])
        pk = tables[table].columns[0]
        cur.execute("select * from %s where %s = %s", (table, pk, user[0]))
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
        password = input("Password: ")
        session = authenticate(username, password)
        if session is None:
            print("Invalid username or password")

    executor = QueryExecutor(session)
    print("+++Hello %s +++" % session.user[0])
    query = input("$ ")
    while query.lower() != 'q':
        result = executor.execute(query)
        if type(result) is list:
            print("\n".join(str(r) for r in result))
        else:
            print("%d rows affected" % result)
        query = input("$ ")


if __name__ == '__main__':
    main()
