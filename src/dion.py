import psycopg2
import config
from src.session import Session
from src.sql import *


def execute_query(session: Session, cur, con, query: str):
    query = SqlQuery.parse(query)
    if type(query) is SelectQuery:
        if session.role == "owner":
            cur.execute(str(query))
            return str(cur.fetchone())
        if (session.manage_role == "official_financial_assistant") and query.table == 'employees':
            query.and_condition(SimpleCondition('role', SimpleCondition.Operator.EQUAL, "financial"))
            query.or_condition(SimpleCondition('role', SimpleCondition.Operator.EQUAL, "official"))
            print(query)
            cur.execute(str(query))
            return str(cur.fetchone())
        if session.type == 'employees' and (session.role != 'official' or session.role != 'financial'):
            return 'There are not any records'
        elif session.role == 'official' or session.role == 'financial' and (query.table == 'physicians' or query.table == 'nurses' or query.table == 'employees'):
            query.and_condition(SimpleCondition('o_msl', SimpleCondition.Operator.GTE, session.asl.value))
            print(query)
            cur.execute(str(query))
            return str(cur.fetchone())
        if (session.type == 'physicians' and query.table == 'nurses' and (session.manage_role != 'manager_section' or session.manage_role != 'assistant_hospital')) or (session.type == query.table and (session.manage_role != 'manager_section' or session.manage_role != 'assistant_hospital')) or session.type == 'patients' or (session.type == 'nurses' and query.table == 'physicians'):
            print("dgsgsdgsdgjsdgjdsh")
            return 'There are not any records'
        if session.type == 'nurses' and query.table == 'patients':
            query.and_condition(SimpleCondition('nurse', SimpleCondition.Operator.EQUAL, session.pid))
        if (session.type == 'physicians' or session.type == 'nurses') and (query.table == 'patients' or query.table == 'nurses' or query.table == 'physicians') and session.manage_role != 'assistant_hospital' :
            query.and_condition(SimpleCondition('section', SimpleCondition.Operator.EQUAL, session.section))
        query.and_condition(SimpleCondition('o_msl', SimpleCondition.Operator.GTE, session.asl.value))
        print(query)
        cur.execute(str(query))
        return str(cur.fetchone())
    if  type(query) is DeleteQuery or type(query) is UpdateQuery:
        if session.role == "owner":
            cur.execute(str(query))
            con.commit()
            return "Opertion is done"
        if (session.manage_role == "official_financila_assistant") and query.table == 'employees':
            query.and_condition(SimpleCondition('role', SimpleCondition.Operator.EQUAL, "financial"))
            query.or_condition(SimpleCondition('role', SimpleCondition.Operator.EQUAL, "official"))
            cur.execute(str(query))
            con.commit()
            return "Opertion is done"
        if session.type == 'employees' and (session.role != 'official' or session.role != 'financial'):
            return "You can not do this"
        if (session.role == 'financial' or session.role == 'official') and (query.table == 'physicians' or query.table == 'nurses' or query.table == 'employees'):
            cur.execute(str(query))
            con.commit()
            return "Opertion is done"
        if session.type == query.table and session.manage_role != 'manager_section' and session.manage_role != 'assistant_hospital':
            return "You can not do this"
        if session.type == 'physicians' and query.table == 'patients':
            query.and_condition(SimpleCondition('physician', SimpleCondition.Operator.EQUAL, session.pid))
        if (session.type == 'physicians' and (query.table == 'patients' or query.type == 'nurses') or (session.manage_role == 'manager_section' and query.table == 'physicians')) and session.manage_role != 'assistant_hospital':
            query.and_condition(SimpleCondition('section', SimpleCondition.Operator.EQUAL, session.section))
        query.and_condition(SimpleCondition('o_csl', SimpleCondition.Operator.LTE, session.asl.value))
        cur.execute(str(query))
        con.commit()
        return "Opertion is done"
    if  type(query) is InsertQuery:
        can = False
        if session.role == "owner":
            can = True
        if (session.manage_role == "official_financial_assistant") and query.table == 'employees':
            can = True
        if (session.role == 'financial' or session.role == 'official') and (query.table == 'physicians' or query.table == 'nurses' or query.table == 'employees') :
            can = True
        if session.type == query.table and (session.manage_role == 'manager_section' or session.manage_role != 'assistant_hospital'):
            return "You can not do this"
        if (session.type == 'physicians' and (query.table == 'nurses' or query.table == 'patients')):
            can = True
        if (session.manage_role == 'manager_section' or session.manage_role != 'assistant_hospital') and (query.table == 'nurses' or query.table == 'patients' or query.table == 'physicians'):
            can = True
        if can:
            cur.execute(str(query))
            con.commit()
            return "Insertion is successful!"
        else:
            return "You can not insert data!"

