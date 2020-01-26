import numbers
from enum import Enum, IntEnum
import re

import psycopg2


def prepare(value):
    if issubclass(type(value), IntEnum):
        return str(value.value)
    if isinstance(value, numbers.Number):
        return str(value)
    if issubclass(type(value), Enum):
        return "'%s'" % value.value
    return "'%s'" % value


class SqlException(Exception):
    def __init__(self, message):
        super().__init__(message)
        self.message = message


class QueryExecutor:
    def execute_read(self, query: 'SqlQuery'):
        raise NotImplementedError()

    def execute_single_read(self, query: 'SqlQuery'):
        raise NotImplementedError()

    def execute_write(self, query: 'SqlQuery'):
        raise NotImplementedError()


class DefaultQueryExecutor:
    def __init__(self, db_name, db_user, db_password, db_host, db_port):
        self.db_name = db_name
        self.db_user = db_user
        self.db_password = db_password
        self.db_host = db_host
        self.db_port = db_port

    def execute_read(self, query: 'SelectQuery'):
        print("Default:", str(query))
        con, cur = self.__get_db_connection()
        cur.execute(str(query))
        result = cur.fetchall()
        cur.close()
        con.close()
        return result

    def execute_single_read(self, query: 'SelectQuery'):
        print("Default:", str(query))
        con, cur = self.__get_db_connection()
        cur.execute(str(query))
        result = cur.fetchone()
        cur.close()
        con.close()
        return result

    def execute_write(self, query: 'SqlQuery'):
        print("Default:", str(query))
        con, cur = self.__get_db_connection()
        cur.execute(str(query))
        result = cur.rowcount
        con.commit()
        cur.close()
        con.close()
        return result

    def __get_db_connection(self):
        con = psycopg2.connect(dbname=self.db_name, user=self.db_user, password=self.db_password,
                               host=self.db_host, port=self.db_port)
        cur = con.cursor()
        return con, cur


class SqlQuery:
    def __init__(self, table, conditions):
        self.table = table
        self.conditions = conditions

    def and_condition(self, condition):
        if self.conditions is not None:
            self.conditions = self.conditions.and_condition(condition)
        elif type(self) is not InsertQuery:
            self.conditions = condition

    def or_condition(self, condition):
        if self.conditions is not None:
            self.conditions = self.conditions.or_condition(condition)
        elif type(self) is not InsertQuery:
            self.conditions = condition

    @staticmethod
    def parse(query: str) -> 'SqlQuery':
        query = " ".join(query.split())
        operation = query[:7].lower()
        if operation == 'select ':
            return SelectQuery.parse(query)
        elif operation == 'insert ' and query[7:12] == 'into ':
            return InsertQuery.parse(query)
        elif operation == 'update ':
            return UpdateQuery(query)
        elif operation == 'delete ' and query[7:12] == 'from ':
            return DeleteQuery(query)
        elif query.lower() == 'my privacy':
            return MyPrivacyQuery()
        elif query.lower()[:12] == 'send report ':
            text = query[12:]
            if text[0] == text[-1] == "'" or text[0] == text[-1] == '"':
                return SendReportQuery(text[1:-1])
        elif query.lower() == 'migrate reports':
            return MigrateReportQuery(None)
        elif query.lower()[:22] == 'migrate reports where ':
            return MigrateReportQuery(Condition.parse(query[22:]))
        raise SqlException("Invalid query")


class SelectQuery(SqlQuery):
    def __init__(self, target: str or None, table: str or None, condition: 'Condition' or None):
        super().__init__(table, condition)
        self.target = target

    def __str__(self):
        s = "select %s from %s" % (self.target, self.table)
        if self.conditions is not None:
            s += " where %s" % self.conditions
        return s

    @staticmethod
    def parse(query: str):
        from_match = re.search(" from ", query, flags=re.IGNORECASE)
        if not from_match:
            raise SqlException("Invalid query")
        from_span = from_match.span()
        target = query[7:from_span[0]]
        query = query[from_span[1]:]

        where_match = re.search(" where ", query, flags=re.IGNORECASE)
        if not where_match:
            table = query
            condition = None
        else:
            where_span = where_match.span()
            table = query[:where_span[0]]
            condition = Condition.parse(query[where_span[1]:])

        return SelectQuery(target, table, condition)


class JoinSelectQuery(SelectQuery):
    def __init__(self, target, table, condition, extra_string):
        super().__init__(target, table, condition)
        self.extra_string = extra_string

    def __str__(self):
        s = "select %s from %s %s" % (self.target, self.table, self.extra_string)
        if self.conditions is not None:
            s += " where %s" % self.conditions
        return s


class DummySelectQuery(SelectQuery):
    def __init__(self, query: str):
        super().__init__(None, None, None)
        self.query = query

    def __str__(self):
        return self.query


class InsertQuery(SqlQuery):
    def __init__(self, table: str, values: tuple):
        super().__init__(table, None)
        self.values = values

    def __str__(self):
        return "insert into %s values %s" % (self.table, "(%s)" % (", ".join(self.values)))

    @staticmethod
    def parse(query):
        values_match = re.search(" values ", query, flags=re.IGNORECASE)
        if not values_match:
            raise SqlException("Invalid query")
        values_span = values_match.span()
        table = query[12:values_span[0]]
        values = query[values_span[1]:]
        if values[0] != '(' or values[-1] != ')':
            raise SqlException("Invalid query")
        values = ("".join(values[1:-1].split())).split(",")
        values = tuple(values)

        return InsertQuery(table, values)


class UpdateQuery(SqlQuery):
    def __init__(self, query):
        set_match = re.search(" set ", query, flags=re.IGNORECASE)
        if not set_match:
            raise SqlException("Invalid query")
        set_span = set_match.span()
        table = query[7:set_span[0]]
        query = query[set_span[1]:]

        where_match = re.search(" where ", query, flags=re.IGNORECASE)
        if not where_match:
            conditions = None
        else:
            where_span = where_match.span()
            conditions = Condition.parse(query[where_span[1]:])
            query = query[:where_span[0]]

        self.setters = []
        values = query.split(",")
        for value in values:
            q = " ".join(value.split())
            equal_match = re.search("=", q, flags=re.IGNORECASE)
            if not equal_match:
                raise SqlException("Invalid query")
            equal_span = equal_match.span()
            column = q[:equal_span[0]].strip()
            value = q[equal_span[1]:].strip()
            self.setters += [(column, value)]

        super().__init__(table, conditions)

    def __str__(self):
        s = "update %s set %s" % (self.table, ", ".join(["%s = %s" % (col, val) for col, val in self.setters]))
        if self.conditions is not None:
            s += " where %s" % self.conditions
        return s


class DeleteQuery(SqlQuery):
    def __init__(self, query):
        where_match = re.search(" where ", query, flags=re.IGNORECASE)
        if not where_match:
            table = query[12:]
            conditions = None
        else:
            where_span = where_match.span()
            table = query[12:where_span[0]]
            conditions = Condition.parse(query[where_span[1]:])
        super().__init__(table, conditions)

    def __str__(self):
        s = "delete from %s" % self.table
        if self.conditions is not None:
            s += " where %s" % self.conditions
        return s


class MyPrivacyQuery(SqlQuery):
    def __init__(self):
        super().__init__(None, None)


class SendReportQuery(SqlQuery):
    def __init__(self, text):
        super().__init__(None, None)
        self.text = text


class MigrateReportQuery(SqlQuery):
    def __init__(self, conditions):
        super().__init__(None, conditions)


class Condition:
    def and_condition(self, cond: 'Condition') -> 'Condition':
        return BinaryCondition(self, BinaryCondition.Op.AND, cond)

    def or_condition(self, cond: 'Condition') -> 'Condition':
        return BinaryCondition(self, BinaryCondition.Op.OR, cond)

    def apply(self, row: tuple, header: tuple):
        raise NotImplementedError()

    @staticmethod
    def parse(string) -> 'Condition':
        string = " " + string
        or_match = re.search(" or ", string, flags=re.IGNORECASE)
        if or_match:
            span = or_match.span()
            return Condition.parse(string[:span[0]]).or_condition(Condition.parse(string[span[1]:]))

        and_match = re.search(" and ", string, flags=re.IGNORECASE)
        if and_match:
            span = and_match.span()
            return Condition.parse(string[:span[0] + 1]).and_condition(Condition.parse(string[span[1] - 1:]))

        not_match = re.search(" not ", string, flags=re.IGNORECASE)
        if not_match:
            span = not_match.span()
            return UnaryCondition(UnaryCondition.Op.NOT, Condition.parse(string[span[1]:]))

        pieces = string.split()
        if len(pieces) != 3:
            raise SqlException("Invalid Query")
        return SimpleCondition(pieces[0], SimpleCondition.Op(pieces[1]), pieces[2])


class SimpleCondition(Condition):
    def __init__(self, lvalue, operator: 'Op', rvalue):
        self.lvalue = lvalue
        self.operator = operator
        self.rvalue = rvalue

    def apply(self, row: tuple, header: tuple):
        a = "%s %s %s" % (prepare(row[header.index(self.lvalue)]),
                          '==' if self.operator == self.Op.EQUAL else self.operator.value,
                          self.rvalue)
        print(a)
        return eval(a)

    def __str__(self) -> str:
        return "%s %s %s" % (self.lvalue, self.operator.value, self.rvalue)

    def __eq__(self, other):
        return type(other) is SimpleCondition and self.lvalue == other.lvalue and self.rvalue == other.rvalue \
               and self.operator == other.operator

    class Op(Enum):
        EQUAL = '='
        GT = '>'
        GTE = '>='
        LT = '<'
        LTE = '<='


class BinaryCondition(Condition):
    def __init__(self, lvalue: Condition, operator, rvalue: Condition):
        self.lvalue = lvalue
        self.operator = operator
        self.rvalue = rvalue

    def apply(self, row: tuple, header: tuple):
        if self.operator == self.Op.AND:
            return self.lvalue.apply(row, header) and self.rvalue.apply(row, header)
        else:
            return self.lvalue.apply(row, header) or self.rvalue.apply(row, header)

    def __str__(self):
        return "(%s) %s (%s)" % (self.lvalue, self.operator.value, self.rvalue)

    def __eq__(self, other):
        return type(other) is BinaryCondition and self.lvalue == other.lvalue and self.rvalue == other.rvalue \
               and self.operator == other.operator

    class Op(Enum):
        AND = "AND"
        OR = "OR"


class UnaryCondition(Condition):
    def __init__(self, operator, rvalue: Condition):
        self.operator = operator
        self.rvalue = rvalue

    def apply(self, row: tuple, header: tuple):
        return not self.rvalue.apply(row, header)

    def __str__(self):
        return "%s %s" % (self.operator.value, self.rvalue)

    def __eq__(self, other):
        return type(other) is UnaryCondition and self.rvalue == other.rvalue and self.operator == other.operator

    class Op(Enum):
        NOT = "NOT"
