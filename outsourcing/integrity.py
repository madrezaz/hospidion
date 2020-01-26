import datetime

from core.sql import *
from outsourcing import crypto


class IntegrityCheckQueryExecutor(DefaultQueryExecutor):
    def __init__(self, db_name, db_user, db_password, db_host, db_port):
        super().__init__(db_name, db_user, db_password, db_host, db_port)

    def execute_read(self, query: 'SelectQuery'):
        result = super().execute_read(query)
        res = []
        for row in result:
            self.__check_row(row)
            res += [row[:-1]]
        return res

    def execute_single_read(self, query: 'SelectQuery'):
        row = super().execute_single_read(query)
        self.__check_row(row)
        return row[:-1]

    def execute_write(self, query: 'SqlQuery'):
        if type(query) is InsertQuery:
            query.values += ("'%s'" % crypto.str_hmac("(%s)" % (", ".join(query.values))),)
            return super().execute_write(query)
        raise Exception("Not supported")

    @staticmethod
    def __check_row(row):
        lst = list(row)
        for i in range(len(lst)):
            item = lst[i]
            if type(item) is datetime.date:
                lst[i] = "%d-%d-%d" % (item.year, item.month, item.day)
            elif type(item) is bool:
                lst[i] = str(item).lower()
        row = tuple(lst)
        if not crypto.verify_hmac(str(row[:-1]), row[-1]):
            raise SqlException("Integrity check failed")
