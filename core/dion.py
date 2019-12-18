import psycopg2
import config
from core.models import *
from core.sql import *


class QueryExecutor:
    def __init__(self, session: Session):
        self.session = session

        sec_cond = SimpleCondition('section', SimpleCondition.Op.EQUAL, section_dominance[session.get_section()][0])
        for sec in section_dominance[session.get_section()][1:]:
            sec_cond = sec_cond.or_condition(SimpleCondition('section', SimpleCondition.Op.EQUAL, sec))
        self.section_condition = sec_cond

        read_cond = BinaryCondition(SimpleCondition('msl', SimpleCondition.Op.GTE, prepare(self.session.get_asl())),
                                    BinaryCondition.Op.AND,
                                    SimpleCondition('asl', SimpleCondition.Op.LTE, prepare(self.session.get_rsl())))
        self.read_condition = BinaryCondition(read_cond, BinaryCondition.Op.AND, self.section_condition)

        write_cond = BinaryCondition(SimpleCondition('csl', SimpleCondition.Op.LTE, prepare(self.session.get_asl())),
                                     BinaryCondition.Op.AND,
                                     SimpleCondition('asl', SimpleCondition.Op.GTE, prepare(self.session.get_wsl())))
        self.write_condition = BinaryCondition(write_cond, BinaryCondition.Op.AND, self.section_condition)

    def execute(self, query: str):
        query = SqlQuery.parse(query)
        self.__validate_query(query)

        # Special queries
        if type(query) is MyPrivacyQuery:
            return self.privacy()

        # system manager can execute queries directly
        if self.session.get_table() == Table.EMPLOYEE and self.session.entity[4] == EmployeeRole.SYSTEM_MANAGER.value:
            return self.__execute_directly(query)

        # Exceptions in access control policy
        # Exception 1: Nurse should not write Nurse
        exception1 = query.table == Table.NURSE and self.session.get_table() == Table.NURSE
        # Exception 2: Section manager must be able to write Physician
        # Exception 3: Medical VP must be able to write Physician
        phys_on_phys = query.table == Table.PHYSICIAN and self.session.get_table() == Table.PHYSICIAN
        exception2 = phys_on_phys and self.session.entity[5] == PhysicianManagementRole.SECTION_MANAGER.value
        exception3 = phys_on_phys and self.session.entity[5] == PhysicianManagementRole.MEDICAL_VP.value

        model = tables[query.table]

        if type(query) is SelectQuery:
            query.and_condition(self.read_condition)
            return self.__execute_read(query)

        elif type(query) is InsertQuery:
            if exception1:
                raise Exception("Unauthorized")

            user_asl = self.session.get_asl()
            if exception2 or exception3:
                user_asl = Classification.TS

            section = query.values[model.section_index]
            if self.session.get_wsl() > model.asl or user_asl < model.csl \
                    or section not in section_dominance[self.session.get_section()]:
                raise Exception("Unauthorized")

            query.values += (prepare(model.asl), prepare(model.msl), prepare(model.csl))

        elif type(query) is UpdateQuery or type(query) is DeleteQuery:
            if exception1:
                raise Exception("Unauthorized")
            if exception2 or exception3:
                write_cond = BinaryCondition(
                    SimpleCondition('csl', SimpleCondition.Op.LTE, Classification.TS.value),
                    BinaryCondition.Op.AND,
                    SimpleCondition('asl', SimpleCondition.Op.GTE, prepare(self.session.get_wsl())))
                query.and_condition(BinaryCondition(write_cond, BinaryCondition.Op.AND, self.section_condition))
            else:
                query.and_condition(self.write_condition)
            return self.__execute_write(query)

        raise Exception("Could not execute query")

    def privacy(self):
        pass

    def __execute_directly(self, query: SqlQuery):
        if query.table == Table.USER and type(query) is InsertQuery:
            try:
                table = Table(query.values[2])
            except ValueError:
                raise Exception("Invalid type", query.values[2])

            if len(query.values) == len(User.columns) - 3:
                levels = subject_levels[table]
                query.values += (prepare(levels[0]), prepare(levels[1]), prepare(levels[2]))

            return self.__execute_write(query)

        if type(query) is SelectQuery:
            return self.__execute_read(query)
        else:
            if type(query) == InsertQuery:
                model = tables[query.table]
                query.values += (prepare(model.asl), prepare(model.msl), prepare(model.csl))
            return self.__execute_write(query)

    @staticmethod
    def __validate_query(query):
        model = tables[query.table]
        if type(query) is InsertQuery:
            if query.table == Table.USER:
                if len(model.columns) != len(query.values) and len(model.columns) != len(query.values) - 3:
                    raise Exception("Invalid values")
            elif len(model.columns) != len(query.values):
                raise Exception("Invalid values")

            for i in model.enums:
                try:
                    model.enums[i](query.values[i])
                except ValueError:
                    raise Exception("Invalid value", query.values[i])
        elif type(query) is UpdateQuery:
            for col, val in query.setters:
                if col not in model.columns:
                    raise Exception("Invalid column", col)

    @staticmethod
    def __execute_read(query: SqlQuery):
        connection, cursor = QueryExecutor.create_db_connection()

        cursor.execute(str(query))
        result = cursor.fetchall()

        cursor.close()
        connection.close()

        return result

    @staticmethod
    def __execute_write(query: SqlQuery):
        connection, cursor = QueryExecutor.create_db_connection()

        cursor.execute(str(query))
        result = cursor.rowcount

        connection.commit()
        cursor.close()
        connection.close()

        return result

    @staticmethod
    def create_db_connection():
        connection = psycopg2.connect(dbname=config.db_name, user=config.db_user, password=config.db_password,
                                      host=config.db_host, port=config.db_port)
        cursor = connection.cursor()
        return connection, cursor
