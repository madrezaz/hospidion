from enum import Enum
import re


class SqlQuery:
    def __init__(self, table, conditions):
        self.table = table
        self.conditions = conditions

    def and_condition(self, condition):
        if self.conditions is not None:
            self.conditions = self.conditions.and_condition(condition)

    def or_condition(self, condition):
        if self.conditions is not None:
            self.conditions = self.conditions.or_condition(condition)

    @staticmethod
    def parse(query: str) -> 'SqlQuery':
        query = " ".join(query.split())
        try:
            operation = query[:7].lower()
            if operation == 'select ':
                return SelectQuery(query)
            elif operation == 'insert ' and query[7:12] == 'into ':
                return InsertQuery(query)
            elif operation == 'update ':
                return UpdateQuery(query)
            elif operation == 'delete ' and query[7:12] == 'from ':
                return DeleteQuery(query)
        except IndexError:
            pass
        raise Exception("Invalid query")


class SelectQuery(SqlQuery):
    def __init__(self, query):
        from_match = re.search(" from ", query, flags=re.IGNORECASE)
        if not from_match:
            raise Exception("Invalid query")
        from_span = from_match.span()
        target = query[7:from_span[0]]
        query = query[from_span[1]:]

        where_match = re.search(" where ", query, flags=re.IGNORECASE)
        if not where_match:
            raise Exception("Invalid query")
        where_span = where_match.span()
        table = query[:where_span[0]]
        conditions = query[where_span[1]:]

        super().__init__(table, Condition.parse(conditions))
        self.target = target

    def __str__(self):
        return "select %s from %s where %s" % (self.target, self.table, self.conditions)


class InsertQuery(SqlQuery):
    def __init__(self, query):
        values_match = re.search(" values ", query, flags=re.IGNORECASE)
        if not values_match:
            raise Exception("Invalid query")
        values_span = values_match.span()
        table = query[12:values_span[0]]
        values = query[values_span[1]:]
        super().__init__(table, None)
        self.values = values

    def __str__(self):
        return "insert into %s values %s" % (self.table, self.values)


class UpdateQuery(SqlQuery):
    def __init__(self, query):
        set_match = re.search(" set ", query, flags=re.IGNORECASE)
        if not set_match:
            raise Exception("Invalid query")
        set_span = set_match.span()
        table = query[7:set_span[0]]
        query = query[set_span[1]:]

        where_match = re.search(" where ", query, flags=re.IGNORECASE)
        if not where_match:
            raise Exception("Invalid query")
        where_span = where_match.span()
        conditions = query[where_span[1]:]
        query = query[:where_span[0]]

        equal_match = re.search(" = ", query, flags=re.IGNORECASE)
        if not equal_match:
            raise Exception("Invalid query")
        where_span = equal_match.span()
        column = query[:where_span[0]]
        value = query[where_span[1]:]

        super().__init__(table, Condition.parse(conditions))
        self.column = column
        self.value = value

    def __str__(self):
        return "update %s set %s = %s where %s" % (self.table, self.column, self.value, self.conditions)


class DeleteQuery(SqlQuery):
    def __init__(self, query):
        where_match = re.search(" where ", query, flags=re.IGNORECASE)
        if not where_match:
            raise Exception("Invalid query")
        where_span = where_match.span()
        table = query[12:where_span[0]]
        conditions = query[where_span[1]:]
        super().__init__(table, Condition.parse(conditions))

    def __str__(self):
        return "delete from %s where %s" % (self.table, self.conditions)


class Condition:
    def and_condition(self, cond: 'Condition') -> 'Condition':
        return BinaryCondition(self, BinaryCondition.Operator.AND, cond)

    def or_condition(self, cond: 'Condition') -> 'Condition':
        return BinaryCondition(self, BinaryCondition.Operator.OR, cond)

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
            return UnaryCondition(UnaryCondition.Operator.NOT, Condition.parse(string[span[1]:]))

        pieces = string.split()
        if len(pieces) != 3:
            raise Exception("Invalid Query")
        return SimpleCondition(pieces[0], SimpleCondition.Operator(pieces[1]), pieces[2])


class SimpleCondition(Condition):
    def __init__(self, lvalue: str, operator: 'Operator', rvalue: str):
        self.lvalue = lvalue
        self.operator = operator
        self.rvalue = rvalue

    def __str__(self) -> str:
        return "%s %s %s" % (self.lvalue, self.operator.value, self.rvalue)

    class Operator(Enum):
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

    class Operator(Enum):
        AND = "AND"
        OR = "OR"


class UnaryCondition(Condition):
    def __init__(self, operator, rvalue: Condition):
        self.operator = operator
        self.rvalue = rvalue

    def __str__(self):
        return "%s %s" % (self.operator.value, self.rvalue)

    class Operator(Enum):
        NOT = "NOT"
