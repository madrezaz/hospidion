import numbers
from ast import literal_eval
from enum import Enum, IntEnum
import re


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
            return SelectQuery(query)
        elif operation == 'insert ' and query[7:12] == 'into ':
            return InsertQuery(query)
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
    def __init__(self, query):
        from_match = re.search(" from ", query, flags=re.IGNORECASE)
        if not from_match:
            raise SqlException("Invalid query")
        from_span = from_match.span()
        target = query[7:from_span[0]]
        query = query[from_span[1]:]

        where_match = re.search(" where ", query, flags=re.IGNORECASE)
        if not where_match:
            table = query
            conditions = None
        else:
            where_span = where_match.span()
            table = query[:where_span[0]]
            conditions = Condition.parse(query[where_span[1]:])

        super().__init__(table, conditions)
        self.target = target

    def __str__(self):
        s = "select %s from %s" % (self.target, self.table)
        if self.conditions is not None:
            s += " where %s" % self.conditions
        return s


class InsertQuery(SqlQuery):
    def __init__(self, query):
        values_match = re.search(" values ", query, flags=re.IGNORECASE)
        if not values_match:
            raise SqlException("Invalid query")
        values_span = values_match.span()
        table = query[12:values_span[0]]
        values = query[values_span[1]:]
        if values[0] != '(' or values[-1] != ')':
            raise SqlException("Invalid query")
        values = ("".join(values[1:-1].split())).split(",")
        super().__init__(table, None)
        self.values = tuple(values)

    def __str__(self):
        return "insert into %s values %s" % (self.table, "(%s)" % (", ".join(self.values)))


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

        equal_match = re.search(" = ", query, flags=re.IGNORECASE)
        if not equal_match:
            raise SqlException("Invalid query")
        equal_span = equal_match.span()
        column = query[:equal_span[0]]
        value = query[equal_span[1]:]

        super().__init__(table, conditions)
        self.setters = [(column, value)]

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

    def __str__(self) -> str:
        return "%s %s %s" % (self.lvalue, self.operator.value, self.rvalue)

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

    def __str__(self):
        return "(%s) %s (%s)" % (self.lvalue, self.operator.value, self.rvalue)

    class Op(Enum):
        AND = "AND"
        OR = "OR"


class UnaryCondition(Condition):
    def __init__(self, operator, rvalue: Condition):
        self.operator = operator
        self.rvalue = rvalue

    def __str__(self):
        return "%s %s" % (self.operator.value, self.rvalue)

    class Op(Enum):
        NOT = "NOT"
