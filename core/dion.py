from core.models import *
from core.sql import *


class DionExecutor:
    def __init__(self, session: Session, executor: QueryExecutor):
        self.session = session
        self.executor = executor

        sec0 = section_dominance[session.get_section()][0]
        sec_cond = SimpleCondition('section', SimpleCondition.Op.EQUAL, prepare(sec0))
        for sec in section_dominance[session.get_section()][1:]:
            sec_cond = sec_cond.or_condition(SimpleCondition('section', SimpleCondition.Op.EQUAL, prepare(sec)))
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

        # Special queries
        if type(query) is MyPrivacyQuery:
            return self.privacy()

        if type(query) is SendReportQuery:
            return self.send_report(query)

        if type(query) is MigrateReportQuery:
            return self.migrate_report(query)

        self.__validate_query(query)

        # system manager can execute queries directly
        if self.session.get_table() == Table.EMPLOYEE and self.session.entity[4] == EmployeeRole.SYSTEM_MANAGER.value:
            return self.__execute_directly(query)

        if query.table in ["reports", "inspector_reports", "manager_reports"]:
            return self.__manage_reports(query)

        if query.table == Table.USER.value:
            raise DionException("Unauthorized")

        # Exceptions in access control policy
        # Exception 1: Nurse should not write Nurse
        exception1 = query.table == Table.NURSE.value and self.session.get_table() == Table.NURSE
        # Exception 2: Section manager must be able to write Physician
        # Exception 3: Medical VP must be able to write Physician
        phys_on_phys = query.table == Table.PHYSICIAN.value and self.session.get_table() == Table.PHYSICIAN
        exception2 = phys_on_phys and self.session.entity[5] == PhysicianManagementRole.SECTION_MANAGER.value
        exception3 = phys_on_phys and self.session.entity[5] == PhysicianManagementRole.MEDICAL_VP.value

        model = tables[Table(query.table)]
        # Exception 4: Two step check for physician access on his own patient
        exception4 = model == Patient and self.session.get_table() == Table.PHYSICIAN
        # Exception 5: Two step check for nurse access on his own patient
        exception5 = model == Patient and self.session.get_table() == Table.NURSE
        # Exception 6: Inspector should not write nurse
        exception6 = model == Employee and self.session.entity[4] == EmployeeRole.INSPECTOR.value and \
                     self.session.get_table() == Table.NURSE

        self_query = query.table == self.session.get_table().value
        self_cond = SimpleCondition(model.columns[0], SimpleCondition.Op.EQUAL, prepare(self.session.entity[0]))

        if type(query) is SelectQuery:
            rc = self.read_condition
            if self_query:
                rc = rc.or_condition(self_cond)
            query.and_condition(rc)

            if exception5:
                query.and_condition(SimpleCondition('nurse', SimpleCondition.Op.EQUAL, prepare(self.session.entity[0])))

            return self.__execute_read(query)

        elif type(query) is InsertQuery:
            if exception1 or exception6:
                return 0

            if exception4 and query.values[8][1:-1] != self.session.entity[0]:
                return 0

            user_asl = self.session.get_asl()
            if exception2 or exception3:
                user_asl = Classification.TS

            section = Section(query.values[model.section_index][1:-1])
            if self.session.get_wsl() > model.asl or user_asl < model.csl \
                    or section not in section_dominance[self.session.get_section()]:
                return 0

            query.values += (prepare(model.msl), prepare(model.asl), prepare(model.csl))
            return self.__execute_write(query)

        elif type(query) is UpdateQuery or type(query) is DeleteQuery:
            if exception6:
                return 0

            if exception1:
                query.conditions = self_cond
                return self.__execute_write(query)

            if exception2 or exception3:
                write_cond = BinaryCondition(
                    SimpleCondition('csl', SimpleCondition.Op.LTE, Classification.TS.value),
                    BinaryCondition.Op.AND,
                    SimpleCondition('asl', SimpleCondition.Op.GTE, prepare(self.session.get_wsl())))
                query.and_condition(BinaryCondition(write_cond, BinaryCondition.Op.AND, self.section_condition))
            elif exception4:
                cond = SimpleCondition('physician', SimpleCondition.Op.EQUAL, prepare(self.session.entity[0]))
                query.and_condition(BinaryCondition(self.write_condition, BinaryCondition.Op.AND, cond))
            else:
                query.and_condition(self.write_condition)

            if self_query:
                query.or_condition(self_cond)
            return self.__execute_write(query)

        raise DionException("Could not execute query")

    def privacy(self):
        readers = []
        writers = []

        o_msl = self.session.entity[-3]
        o_asl = self.session.entity[-2]
        o_csl = self.session.entity[-1]

        sections = section_dominance_reverse[self.session.get_section()]
        cond = " or ".join(["t.section = %s" % prepare(sec) for sec in sections])

        for table in ["physicians", "nurses", "employees"]:
            q = JoinSelectQuery('username', 'users',
                                Condition.parse("u.rsl >= %s and u.asl <= %s and (%s)" % (o_asl, o_msl, cond)),
                                "as u inner join %s as t on u.id = t.personnel_id" % table)
            readers += self.executor.execute_read(q)

            q.conditions = Condition.parse("u.wsl <= %s and u.asl >= %s and (%s)" % (o_asl, o_csl, cond))
            writers += self.executor.execute_read(q)

        q = JoinSelectQuery('username', 'users',
                            Condition.parse("u.rsl >= %s and u.asl <= %s and (%s)" % (o_asl, o_msl, cond)),
                            "as u inner join patients as t on u.id = t.reception_id")
        readers += self.executor.execute_read(q)

        q.conditions = Condition.parse("u.wsl <= %s and u.asl >= %s and (%s)" % (o_asl, o_csl, cond))
        writers += self.executor.execute_read(q)

        return Privacy(readers, writers)

    def send_report(self, query: SqlQuery):
        o_msl = self.session.entity[-3]
        o_asl = self.session.entity[-2]
        o_csl = self.session.entity[-1]

        q = SqlQuery.parse("insert into reports (username, report, msl, asl, csl) VALUES ('%s', '%s',%s, %s, %s)"
                           % (self.session.user[0], query.text, o_msl, o_asl, o_csl))
        return self.executor.execute_write(q)

    def migrate_report(self, query: SqlQuery):
        if self.session.get_table() == Table.EMPLOYEE and self.session.entity[5] == Section.ADMINISTRATIVE.value:
            condition = SimpleCondition('asl', SimpleCondition.Op.LTE, prepare(self.session.get_rsl()))
            if query.conditions is not None:
                condition = condition.and_condition(query.conditions)
            result = self.executor.execute_read(SqlQuery.parse("select * from reports where %s" % condition))
            res = 0
            for record in result:
                msl = Classification(record[3])
                csl = Classification(record[5])
                if msl >= Classification.S.value and csl >= Classification.C.value:
                    self.executor.execute_write(SqlQuery.parse(
                        "insert into inspector_reports (username, report, msl, asl, csl) VALUES ('%s', '%s',"
                        "%s, %s, %s)" % (record[1], record[2], record[3], record[4], record[5])))
                    res += 1
            return res
        elif self.session.get_table() == Table.EMPLOYEE and self.session.entity[4] == EmployeeRole.INSPECTOR.value:
            condition = query.conditions.and_condition(
                SimpleCondition('asl', SimpleCondition.Op.LTE, prepare(self.session.get_rsl()))
            )
            result = self.executor.execute_read("select * from inspector_reports where %s" % condition)
            res = 0
            for record in result:
                msl = Classification(record[3])
                csl = Classification(record[5])
                if msl >= Classification.TS.value and csl >= Classification.S.value:
                    self.executor.execute_write(SqlQuery.parse(
                        "insert into manager_reports (username, report, msl, asl, csl) VALUES ('%s', '%s', %s, %s, %s)"
                        % (record[1], record[2], record[3], record[4], record[5])))
                    res += 1
            return res
        raise Exception("Unauthorized")

    def __manage_reports(self, query):
        if type(query) is InsertQuery:
            raise DionException("Unauthorized")

        if query.table == "manager_reports" and \
                (self.session.get_table() != Table.PHYSICIAN or
                 self.session.entity[5] != PhysicianManagementRole.HOSPITAL_MANAGER.value):
            raise DionException("Unauthorized")

        if query.table == "inspector_reports" and \
                (self.session.get_table() != Table.EMPLOYEE or
                 self.session.entity[4] != EmployeeRole.INSPECTOR.value):
            raise DionException("Unauthorized")

        if query.table == "reports" and \
                (self.session.get_table() != Table.EMPLOYEE or
                 self.session.entity[5] != Section.ADMINISTRATIVE.value):
            raise DionException("Unauthorized")

        if type(query) is SelectQuery:
            query.and_condition(SimpleCondition('asl', SimpleCondition.Op.LTE, prepare(self.session.get_rsl())))
            return self.__execute_read(query)

        elif type(query) is UpdateQuery or type(query) is DeleteQuery:
            query.and_condition(SimpleCondition('asl', SimpleCondition.Op.GTE, prepare(self.session.get_wsl())))
            if type(query) is UpdateQuery:
                if query.table == "inspector_reports":
                    query.setters += [('msl', 3), ('asl', 3), ('csl', 2)]
                elif query.table == "manger_reports":
                    query.setters += [('msl', 4), ('asl', 4), ('csl', 3)]
            return self.__execute_write(query)

        raise DionException("Could not execute query")

    def __execute_directly(self, query: SqlQuery):
        if query.table == Table.USER.value and type(query) is InsertQuery:
            try:
                table = Table(query.values[2][1:-1])
            except ValueError:
                raise DionException("Invalid type %s" % query.values[2])

            q = SqlQuery.parse("select * from %s where %s = '%s'" %
                               (table.value, tables[table].columns[0], query.values[3][1:-1]))
            entity = self.executor.execute_single_read(q)

            if entity is None:
                raise DionException("Invalid id %s" % query.values[3])

            if len(query.values) == len(User.columns) - 3:
                if table == Table.PHYSICIAN and (entity[5] == PhysicianManagementRole.SECTION_MANAGER.value or
                                                 entity[5] == PhysicianManagementRole.MEDICAL_VP.value):
                    levels = (Classification.TS, Classification.S, Classification.C)
                elif table == Table.PHYSICIAN and (entity[5] == PhysicianManagementRole.FINANCIAL_VP.value or
                                                   entity[5] == PhysicianManagementRole.ADMINISTRATIVE_VP.value):
                    levels = (Classification.TS, Classification.TS, Classification.TS)
                elif table == Table.PHYSICIAN and entity[5] == PhysicianManagementRole.HOSPITAL_MANAGER.value:
                    levels = (Classification.TS, Classification.TS, Classification.S)
                elif table == Table.EMPLOYEE and entity[4] == EmployeeRole.INSPECTOR.value:
                    levels = (Classification.TS, Classification.S, Classification.S)
                else:
                    levels = subject_levels[table]
                query.values += (prepare(levels[0]), prepare(levels[1]), prepare(levels[2]))

            return self.__execute_write(query)

        if type(query) is SelectQuery:
            return self.__execute_read(query)
        else:
            if type(query) == InsertQuery:
                model = tables[Table(query.table)]
                if model in [Report, InspectorReport, ManagerReport]:
                    raise DionException("Unauthorized")
                query.values += (prepare(model.msl), prepare(model.asl), prepare(model.csl))
            return self.__execute_write(query)

    @staticmethod
    def __validate_query(query):
        try:
            model = tables[Table(query.table)]
        except ValueError:
            raise DionException("Invalid table")
        if type(query) is InsertQuery:
            if model == User:
                if len(model.columns) != len(query.values) and len(model.columns) - 3 != len(query.values):
                    raise DionException("Invalid values")
            elif len(model.columns) != len(query.values):
                raise DionException("Invalid values")

            for i in model.enums:
                try:
                    model.enums[i](query.values[i][1:-1])
                except ValueError:
                    raise DionException("Invalid value %s" % query.values[i])
        elif type(query) is UpdateQuery:
            for col, val in query.setters:
                if col not in model.columns:
                    raise DionException("Invalid column %s" % col)
                ind = model.columns.index(col)
                if ind in model.enums:
                    try:
                        model.enums[ind](val[1:-1])
                    except ValueError:
                        raise DionException("Invalid value %s" % val)

    def __execute_read(self, query: SqlQuery):
        return self.executor.execute_read(query)

    def __execute_write(self, query: SqlQuery):
        return self.executor.execute_write(query)
