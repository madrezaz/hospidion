from core.models import *
from core.sql import QueryExecutor, SqlQuery


def create_session(executor: QueryExecutor, username, password=None):
    if password is not None:
        q = SqlQuery.parse("select * from users where username = '%s' and password = '%s'" % (username, password))
        user = executor.execute_single_read(q)
    else:
        q = SqlQuery.parse("select * from users where username = '%s'" % username)
        user = executor.execute_single_read(q)
    session = None
    if user is not None:
        table = Table(user[2])
        pk = tables[table].columns[0]
        q = SqlQuery.parse("select * from %s where %s = '%s'" % (table.value, pk, user[3]))
        entity = executor.execute_single_read(q)
        session = Session(user, entity)
    return session
