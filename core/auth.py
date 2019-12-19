from core.dion import QueryExecutor
from core.models import *


def create_session(username, password=None):
    con, cur = QueryExecutor.create_db_connection()
    if password is not None:
        cur.execute("select * from users where username = %s and password = %s", (username, password))
    else:
        cur.execute("select * from users where username = %s", (username,))
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
