from core.sql import *


class IndexingQueryExecutor(DefaultQueryExecutor):
    def __init__(self, db_name, db_user, db_password, db_host, db_port):
        super().__init__(db_name, db_user, db_password, db_host, db_port)

    def execute_read(self, query: SelectQuery):
        return super().execute_read(self.__prepare_query(query))

    def execute_single_read(self, query: SelectQuery):
        return super().execute_single_read(self.__prepare_query(query))

    def execute_write(self, query: SqlQuery):
        raise SqlException("Not supported")

    def __prepare_query(self, query):
        if isinstance(query, SelectQuery):
            query.conditions = self.__convert_condition(query.conditions, query.table)
        return query

    def __convert_condition(self, condition, table):
        if type(condition) is SimpleCondition:
            return SimpleCondition(condition.lvalue + "_i", condition.operator, condition.rvalue)
        elif type(condition) is BinaryCondition:
            return BinaryCondition(self.__convert_condition(condition.lvalue, table),
                                   condition.operator,
                                   self.__convert_condition(condition.rvalue, table))
        elif type(condition) is UnaryCondition:
            return UnaryCondition(condition.operator, self.__convert_condition(condition.rvalue, table))
        raise SqlException("Something went wrong")
