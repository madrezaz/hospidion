from enum import Enum
import re


class SqlQuery:
    def __init__(self, table, conditions):
        self.table = table
        self.conditions = conditions

    @staticmethod
    def parse(query: str) -> 'SqlQuery':
        pieces = query.split()
        operation = pieces[0].lower()
        if operation == 'select':
            return SelectQuery(pieces[3], pieces[1], Condition.parse(pieces[5]))
        elif operation == 'insert':
            return InsertQuery(pieces[2], pieces[4])
        elif operation == 'update':
            return UpdateQuery(pieces[1], pieces[3], pieces[5], Condition.parse(pieces[7]))
        elif operation == 'delete':
            return DeleteQuery(pieces[2], Condition.parse(pieces[5]))
        raise Exception("Invalid query")


class SelectQuery(SqlQuery):
    def __init__(self, table: str, target, conditions: 'Condition'):
        super().__init__(table, conditions)
        self.target = target


class InsertQuery(SqlQuery):
    def __init__(self, table: str, values):
        super().__init__(table, None)


class UpdateQuery(SqlQuery):
    def __init__(self, table: str, column, value, conditions: 'Condition'):
        super().__init__(table, conditions)


class DeleteQuery(SqlQuery):
    def __init__(self, table: str, conditions: 'Condition'):
        super().__init__(table, conditions)


class Condition:
    def and_condition(self, cond: 'Condition') -> 'Condition':
        return ComplexBinaryCondition(self, ComplexBinaryCondition.Operator.AND, cond)

    def or_condition(self, cond: 'Condition') -> 'Condition':
        return ComplexBinaryCondition(self, ComplexBinaryCondition.Operator.OR, cond)

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
            return ComplexUnaryCondition(ComplexUnaryCondition.Operator.NOT, Condition.parse(string[span[1]:]))

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


class ComplexBinaryCondition(Condition):
    def __init__(self, lvalue: Condition, operator, rvalue: Condition):
        self.lvalue = lvalue
        self.operator = operator
        self.rvalue = rvalue

    def __str__(self):
        return "(%s) %s (%s)" % (self.lvalue, self.operator.value, self.rvalue)

    class Operator(Enum):
        AND = "AND"
        OR = "OR"


class ComplexUnaryCondition(Condition):
    def __init__(self, operator, rvalue: Condition):
        self.operator = operator
        self.rvalue = rvalue

    def __str__(self):
        return "%s %s" % (self.operator.value, self.rvalue)

    class Operator(Enum):
        NOT = "NOT"
