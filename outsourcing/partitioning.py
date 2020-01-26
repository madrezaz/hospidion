from typing import List

from core.sql import *
from outsourcing.filter import purify
from outsourcing.integrity import IntegrityCheckQueryExecutor

tables = {'users': [['username', 'password', 'type'], ['username', 'id', 'asl', 'rsl', 'wsl']],
          'physicians': [['personnel_id', 'first_name', 'last_name', 'national_code'],
                         ['personnel_id', 'proficiency', 'management_role', 'section', 'employment_date', 'age',
                          'gender', 'salary', 'married', 'msl', 'asl', 'csl']],
          'nurses': [['personnel_id', 'first_name', 'last_name', 'national_code'],
                     ['personnel_id', 'section', 'employment_date', 'age', 'gender', 'salary', 'married', 'msl', 'asl',
                      'csl']],
          'patients': [['reception_id', 'first_name', 'last_name', 'national_code'],
                       ['reception_id', 'age', 'gender', 'sickness_type', 'section', 'physician', 'nurse',
                        'drugs', 'msl', 'asl', 'csl']],
          'employees': [['personnel_id', 'first_name', 'last_name', 'national_code'],
                        ['personnel_id', 'role', 'section', 'employment_date', 'age', 'gender', 'salary', 'married',
                         'msl', 'asl', 'csl']],
          'reports': [['id', 'username'], ['id', 'report', 'msl', 'asl', 'csl']],
          'inspector_reports': [['id', 'username'], ['id', 'report', 'msl', 'asl', 'csl']],
          'manager_reports': [['id', 'username'], ['id', 'report', 'msl', 'asl', 'csl']]}


class PartitioningQueryExecutor(QueryExecutor):
    def __init__(self, db_name, db_user, db_password, db_host, db_port):
        self.executor1 = IntegrityCheckQueryExecutor(db_name + "_1", db_user, db_password, db_host, db_port)
        self.executor2 = IntegrityCheckQueryExecutor(db_name + "_2", db_user, db_password, db_host, db_port)

    def execute_read(self, query: 'SelectQuery'):
        if query.conditions is not None:
            _, cond1, cond2 = self.__split_condition(query.conditions, query.table)
            l1 = self.executor1.execute_read(SelectQuery('*', query.table, cond1)) if cond1 is not None else []
            l2 = self.executor2.execute_read(SelectQuery('*', query.table, cond2)) if cond2 is not None else []
        else:
            l1 = self.executor1.execute_read(SelectQuery('*', query.table, None))
            l2 = self.executor2.execute_read(SelectQuery('*', query.table, None))
        rows = self.join_results(l1, l2, query.table)
        header = tuple(tables[query.table][0] + tables[query.table][1][1:])
        return purify(rows, header, query)

    def execute_single_read(self, query: 'SelectQuery'):
        res = self.execute_read(query)
        if len(res) != 0:
            return res[0]
        return None

    def execute_write(self, query: 'SqlQuery'):
        if type(query) is InsertQuery:
            x = len(tables[query.table][0])
            v1 = query.values[:x]
            v2 = query.values[:1] + query.values[x:]
            q1 = InsertQuery(query.table, v1)
            q2 = InsertQuery(query.table, v2)

            self.executor1.execute_write(q1)
            return self.executor2.execute_write(q2)

            # check if table is reports

        raise SqlException("Not supported")

    def join_results(self, l1: List, l2: List, table: str):
        l1_pks = {r[0] for r in l1}
        l2_pks = {r[0] for r in l2}

        t1 = tuple(l2_pks - l1_pks)
        t2 = tuple(l1_pks - l2_pks)
        if len(t1) != 0:
            s = str(t1) if len(t1) != 1 else str(t1).replace(',', '')
            l1 += self.executor1.execute_read(DummySelectQuery("select * from %s where %s in %s" %
                                                               (table, tables[table][0][0], s)))
        if len(t2) != 0:
            s = str(t2) if len(t2) != 1 else str(t2).replace(',', '')
            l2 += self.executor2.execute_read(DummySelectQuery("select * from %s where %s in %s" %
                                                               (table, tables[table][0][0], s)))
        l2_dict = {}
        for row in l2:
            l2_dict[row[0]] = row

        res = []
        for row in l1:
            res += [row + l2_dict[row[0]][1:]]

        return res

    def __split_condition(self, condition, table):
        if type(condition) is SimpleCondition:
            if condition.lvalue in tables[table][0] and condition.lvalue in tables[table][1]:
                t = 3
            else:
                t = 1 if condition.lvalue in tables[table][0] else 2
            return t, condition if t != 2 else None, condition if t != 1 else None

        elif type(condition) is BinaryCondition:
            lv = self.__split_condition(condition.lvalue, table)
            rv = self.__split_condition(condition.rvalue, table)

            if lv[0] == rv[0] and lv[0] != 0:
                return lv[0], condition if lv[0] == 1 else None, condition if lv[0] == 2 else None
            else:
                if lv[1] is None or rv[1] is None:
                    v1 = lv[1] if rv[1] is None else rv[1]
                else:
                    v1 = BinaryCondition(lv[1], BinaryCondition.Op.AND
                    if condition.operator == BinaryCondition.Op.AND and (lv[0] in [1, 3] or rv[0] in [1, 3])
                    else BinaryCondition.Op.OR, rv[1])

                if lv[2] is None or rv[2] is None:
                    v2 = lv[2] if rv[2] is None else rv[2]
                else:
                    v2 = BinaryCondition(lv[2], BinaryCondition.Op.AND
                    if condition.operator == BinaryCondition.Op.AND and (lv[0] in [2, 3] or rv[0] in [2, 3])
                    else BinaryCondition.Op.OR, rv[2])

                return 0, v1, v2

        elif type(condition) is UnaryCondition:
            cond = condition.rvalue
            if type(cond) is SimpleCondition:
                t = self.__split_condition(cond, table)[0]
                return t, condition if t == 1 else None, condition if t == 2 else None
            elif type(cond) is UnaryCondition:
                return self.__split_condition(cond.rvalue, table)
            elif type(cond) is BinaryCondition:
                new_cond = BinaryCondition(
                    UnaryCondition(UnaryCondition.Op.NOT, cond.lvalue),
                    BinaryCondition.Op.AND if cond.operator == BinaryCondition.Op.OR else BinaryCondition.Op.OR,
                    UnaryCondition(UnaryCondition.Op.NOT, cond.rvalue))
                return self.__split_condition(new_cond, table)

        raise ValueError()
