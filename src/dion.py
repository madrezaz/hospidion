import psycopg2
import config
from src.session import Session
from src.sql import *


def execute_query(session: Session, cur, con, query: str):
    query = SqlQuery.parse(query)
    if type(query) is SelectQuery:
        if session.role == "owner":
            cur.execute(str(query))
            return str(cur.fetchall())
        if session.manage_role == 'assistant_hospital' and query.table == 'employees':
            return 'There are not any records'
        if (session.manage_role == "official_financial_assistant") and query.table == 'employees':
            query.and_condition(SimpleCondition('role', SimpleCondition.Operator.EQUAL, "financial"))
            query.or_condition(SimpleCondition('role', SimpleCondition.Operator.EQUAL, "official"))
            cur.execute(str(query))
            return str(cur.fetchall())
        if (session.manage_role == "official_financial_assistant"):
            return 'There are not any records'
        if session.type == 'employees' and ((session.role != 'official' and session.role != 'financial') or query.table == "patients"):
            return 'There are not any records'
        elif session.role == 'official' or session.role == 'financial' and (query.table == 'physicians' or query.table == 'nurses' or query.table == 'employees'):
            query.and_condition(SimpleCondition('o_msl', SimpleCondition.Operator.GTE, session.asl.value))
            cur.execute(str(query))
            return str(cur.fetchall())
        if (session.type == 'physicians' and query.table == 'nurses' and (session.manage_role != 'manager_section' and session.manage_role != 'assistant_hospital')) or (session.type == query.table and (session.manage_role != 'manager_section' and session.manage_role != 'assistant_hospital')) or session.type == 'patients' or (session.type == 'nurses' and query.table == 'physicians'):
            return 'There are not any records'
        if session.type == 'nurses' and query.table == 'patients':
            query.and_condition(SimpleCondition('nurse', SimpleCondition.Operator.EQUAL, session.pid))
        if (session.type == 'physicians' or session.type == 'nurses') and (query.table == 'patients' or query.table == 'nurses' or query.table == 'physicians') and session.manage_role != 'assistant_hospital' :
            query.and_condition(SimpleCondition('section', SimpleCondition.Operator.EQUAL, session.section))
        query.and_condition(SimpleCondition('o_msl', SimpleCondition.Operator.GTE, session.asl.value))
        cur.execute(str(query))
        return str(cur.fetchall())
    if  type(query) is DeleteQuery or type(query) is UpdateQuery:
        if session.role == "owner":
            cur.execute(str(query))
            con.commit()
            return "Opertion is done"
        if (session.manage_role == "official_financial_assistant") and query.table == 'employees':
            query.and_condition(SimpleCondition('role', SimpleCondition.Operator.EQUAL, "financial"))
            query.or_condition(SimpleCondition('role', SimpleCondition.Operator.EQUAL, "official"))
            cur.execute(str(query))
            con.commit()
            return "Opertion is done"
        if (session.manage_role == "official_financial_assistant"):
            return "You can not do this"
        if session.type == 'employees' and (session.role != 'official' and session.role != 'financial'):
            return "You can not do this"
        if (session.role == 'financial' or session.role == 'official') and (query.table == 'physicians' or query.table == 'nurses' or query.table == 'employees'):
            cur.execute(str(query))
            con.commit()
            return "Opertion is done"
        if session.type == query.table and session.manage_role != 'manager_section' and session.manage_role != 'assistant_hospital':
            return "You can not do this"
        if session.type == 'physicians' and query.table == 'patients' and session.manage_role != 'assistant_hospital':
            query.and_condition(SimpleCondition('physician', SimpleCondition.Operator.EQUAL, session.pid))
        if (session.type == 'physicians' and (query.table == 'patients' or query.table == 'nurses') or (session.manage_role == 'manager_section' and query.table == 'physicians')) and session.manage_role != 'assistant_hospital':
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
        if session.type == query.table and (session.manage_role == 'manager_section' and session.manage_role != 'assistant_hospital'):
            return "You can not do this"
        if (session.type == 'physicians' and (query.table == 'nurses' or query.table == 'patients')):
            can = True
        if (session.manage_role == 'manager_section' and session.manage_role != 'assistant_hospital') and (query.table == 'nurses' or query.table == 'patients' or query.table == 'physicians'):
            can = True
        if can:
            cur.execute(str(query))
            con.commit()
            return "Insertion is successful!"
        else:
            return "You can not insert data!"
    '''if type(query) is MyInformation:
        query = "select * from %s where username = '%s'" % (session.type,session.username)
        cur.execute(query)
        return str(cur.fetchone())
    '''