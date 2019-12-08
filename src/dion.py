import psycopg2
import config
from src.session import Session
from src.sql import *


def execute_query(session: Session, query: str):
    query = SqlQuery.parse(query)
    if type(query) is SelectQuery:
        query.and_condition(SimpleCondition('o_msl', SimpleCondition.Operator.GTE, session.asl.value))
    # ...
    print(query)

    conn = psycopg2.connect(dbname=config.db_name, user=config.db_user, password=config.db_password,
                            host=config.db_host, port=config.db_port)
    cur = conn.cursor()
    cur.execute(str(query))
    return cur.fetchone()
