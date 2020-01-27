from core.sql import *
from outsourcing.crypto import decrypt_tuple, encrypt_tuple
from outsourcing.filter import purify
from outsourcing.integrity import IntegrityCheckQueryExecutor


tables_index = {
    'users': {
        'username_i': [['a', 'f', 'k', 'p', 'u', 'z'], [150, 33, 121, 174, 94, 114, 2]],
        'password_i': [['a', 'f', 'k', 'p', 'u', 'z'], [91, 5, 233, 68, 226, 155, 64]],
        'type_i': [['a', 'f', 'k', 'p', 'u', 'z'], [234, 197, 4, 220, 200, 151, 69]],
        'id_i': [['0', '2', '4', '6', '8', ':'], [97, 189, 51, 96, 131, 36, 182]],
        'rsl_i': [[1, 2, 3, 4], [118, 118, 119, 223, 65]],
        'asl_i': [[1, 2, 3, 4], [138, 138, 126, 220, 227]],
        'wsl_i': [[1, 2, 3, 4], [47, 47, 142, 217, 80]],
    },
    'physicians': {
        'personnel_id_i': [['0', '2', '4', '6', '8', ':'], [35, 45, 85, 161, 31, 66, 91]],
        'national_code_i': [['0', '2', '4', '6', '8', ':'], [227, 159, 240, 223, 235, 58, 97]],
        'management_role_i': [['a', 'f', 'k', 'p', 'u', 'z'], [27, 18, 42, 37, 150, 158, 5]],
        'section_i': [['a', 'f', 'k', 'p', 'u', 'z'], [17, 216, 172, 20, 122, 102, 83]],
        'age_i': [[20, 30, 40, 50, 60, 70], [230, 46, 198, 206, 244, 104, 9]],
        'gender_i': [['f', 'm'], [1, 1, 0]],
        'salary_i': [[20000, 40000, 60000, 80000, 100000, 120000], [194, 65, 102, 105, 178, 23, 196]],
        'married_i': [['f', 't'], [85, 85, 186]],
        'msl_i': [[1, 2, 3, 4], [120, 120, 88, 103, 224]],
        'asl_i': [[1, 2, 3, 4], [230, 230, 115, 238, 27]],
        'csl_i': [[1, 2, 3, 4], [126, 126, 249, 95, 5]],
    },
    'nurses': {
        'personnel_id_i': [['0', '2', '4', '6', '8', ':'], [94, 203, 107, 62, 235, 83, 247]],
        'national_code_i': [['0', '2', '4', '6', '8', ':'], [15, 186, 181, 87, 23, 146, 171]],
        'section_i': [['a', 'f', 'k', 'p', 'u', 'z'], [49, 120, 180, 38, 144, 14, 37]],
        'age_i': [[20, 30, 40, 50, 60, 70], [221, 27, 51, 66, 108, 30, 182]],
        'gender_i': [['f', 'm'], [1, 1, 0]],
        'salary_i': [[20000, 40000, 60000, 80000, 100000, 120000], [214, 8, 25, 180, 122, 60, 139]],
        'married_i': [['f', 't'], [27, 27, 144]],
        'msl_i': [[1, 2, 3, 4], [144, 144, 27, 216, 168]],
        'asl_i': [[1, 2, 3, 4], [57, 57, 197, 146, 81]],
        'csl_i': [[1, 2, 3, 4], [137, 137, 36, 104, 108]],
    },
    'employees': {
        'personnel_id_i': [['0', '2', '4', '6', '8', ':'], [227, 14, 50, 120, 194, 162, 145]],
        'national_code_i': [['0', '2', '4', '6', '8', ':'], [196, 77, 98, 168, 159, 212, 52]],
        'role_i': [['a', 'f', 'k', 'p', 'u', 'z'], [113, 206, 212, 238, 77, 100, 107]],
        'section_i': [['a', 'f', 'k', 'p', 'u', 'z'], [17, 98, 44, 1, 143, 179, 33]],
        'age_i': [[20, 30, 40, 50, 60, 70], [62, 189, 98, 56, 34, 78, 13]],
        'gender_i': [['f', 'm'], [1, 1, 0]],
        'salary_i': [[20000, 40000, 60000, 80000, 100000, 120000], [145, 72, 95, 218, 247, 231, 29]],
        'married_i': [['f', 't'], [7, 7, 167]],
        'msl_i': [[1, 2, 3, 4], [167, 167, 7, 63, 170]],
        'asl_i': [[1, 2, 3, 4], [130, 30, 9, 139, 68]],
        'csl_i': [[1, 2, 3, 4], [75, 75, 218, 41, 188]],
    },
    'patients': {
        'reception_id_i': [['0', '2', '4', '6', '8', ':'], [27, 162, 78, 1, 33, 143, 238]],
        'national_code_i': [['0', '2', '4', '6', '8', ':'], [186, 107, 91, 224, 185, 217, 140]],
        'age_i': [[20, 30, 40, 50, 60, 70], [199, 106, 109, 174, 230, 83, 193]],
        'gender_i': [['f', 'm'], [1, 1, 0]],
        'section_i': [['a', 'f', 'k', 'p', 'u', 'z'], [24, 54, 29, 42, 224, 217, 55]],
        'physician_i': [['0', '2', '4', '6', '8', ':'], [192, 58, 215, 156, 61, 21, 199]],
        'nurse_i': [['0', '2', '4', '6', '8', ':'], [109, 200, 154, 115, 73, 15, 196]],
        'msl_i': [[1, 2, 3, 4], [48, 48, 75, 226, 121]],
        'asl_i': [[1, 2, 3, 4], [249, 249, 247, 104, 58]],
        'csl_i': [[1, 2, 3, 4], [141, 141, 102, 179, 68]],
    }
}

table_i_header = {
    'users': ['tuple', 'username_i', 'password_i', 'type_i', 'id_i', 'rsl_i', 'asl_i', 'wsl_i'],
    'physicians': ['tuple', 'personnel_id_i', 'national_code_i', 'management_role_i',
                   'section_i', 'age_i', 'gender_i', 'salary_i', 'married_i', 'msl_i', 'asl_i', 'csl_i'],
    'nurses': ['tuple', 'personnel_id_i', 'national_code_i',
               'section_i', 'age_i', 'gender_i', 'salary_i', 'married_i', 'msl_i', 'asl_i', 'csl_i'],
    'patients': ['tuple', 'reception_id_i', 'national_code_i', 'age_i', 'gender_i', 'section_i',
                 'physician_i', 'nurse_i', 'msl_i', 'asl_i', 'csl_i'],
    'employees': ['tuple', 'personnel_id_i', 'national_code_i', 'role_i', 'section_i',
                  'age_i', 'gender_i', 'salary_i', 'married_i', 'msl_i', 'asl_i', 'csl_i']
}

table_header = {
    'users': ['username', 'password', 'type', 'id', 'rsl', 'asl', 'wsl'],
    'physicians': ['personnel_id', 'first_name', 'last_name', 'national_code', 'proficiency', 'management_role',
                   'section', 'employment_date', 'age', 'gender', 'salary', 'married', 'msl', 'asl', 'csl'],
    'nurses': ['personnel_id', 'first_name', 'last_name', 'national_code',
               'section', 'employment_date', 'age', 'gender', 'salary', 'married', 'msl', 'asl', 'csl'],
    'patients': ['reception_id', 'first_name', 'last_name', 'national_code', 'age', 'gender', 'sickness_type',
                 'section', 'physician', 'nurse', 'drugs', 'msl', 'asl', 'csl'],
    'employees': ['personnel_id', 'first_name', 'last_name', 'national_code', 'role', 'section', 'employment_date',
                  'age', 'gender', 'salary', 'married', 'msl', 'asl', 'csl'],
    'reports': ['id', 'username', 'report', 'msl', 'asl', 'csl'],
    'inspector_reports': ['id', 'username', 'report', 'msl', 'asl', 'csl'],
    'manager_reports': ['id', 'username', 'report', 'msl', 'asl', 'csl']
}

table_i_header_s = {
    'users': '(tuple, username_i, password_i, type_i, id_i, rsl_i, asl_i, wsl_i, hmac)',
    'physicians': '(tuple, personnel_id_i, national_code_i, management_role_i, section_i, age_i, gender_i, salary_i, married_i, msl_i, asl_i, csl_i, hmac)',
    'nurses': '(tuple, personnel_id_i, national_code_i, section_i, age_i, gender_i, salary_i, married_i, msl_i, asl_i, csl_i, hmac)',
    'patients': '(tuple, reception_id_i, national_code_i, age_i, gender_i, section_i, physician_i, nurse_i, msl_i, asl_i, csl_i, hmac)',
    'employees': '(tuple, personnel_id_i, national_code_i, role_i, section_i, age_i, gender_i, salary_i, married_i, msl_i, asl_i, csl_i, hmac)'
}


class IndexingQueryExecutor(IntegrityCheckQueryExecutor):
    def __init__(self, db_name, db_user, db_password, db_host, db_port):
        super().__init__(db_name, db_user, db_password, db_host, db_port, True)

    def execute_read(self, query: SelectQuery):
        rows = super().execute_read(self.__prepare_query(query))
        res = [decrypt_tuple(row[1]) for row in rows]
        return purify(res, tuple(table_header[query.table]), query)

    def execute_single_read(self, query: SelectQuery):
        rows = self.execute_read(query)
        if len(rows) > 0:
            return rows[0]
        return None

    def execute_write(self, query: SqlQuery):
        if type(query) is InsertQuery:
            nvalues = [''] * len(table_i_header[query.table])
            tup = []
            for i in range(len(query.values)):
                if query.values[i] == "'false'" or query.values[i] == 'false':
                    val = False
                    ind = 'f'
                elif query.values[i] == "'true" or query.values[i] == 'true':
                    val = True
                    ind = 't'
                elif query.values[i][0] == "'":
                    val = query.values[i][1:-1]
                    ind = val[0].lower()
                else:
                    val = int(query.values[i])
                    ind = val
                tup += [val]
                col = table_header[query.table][i] + "_i"
                if col in tables_index[query.table]:
                    metadata = tables_index[query.table][col]
                    i = self.value_index(ind, metadata)
                    nvalues[table_i_header[query.table].index(col)] = str(metadata[1][i])
            nvalues[0] = "'%s'" % encrypt_tuple(tuple(tup))
            q = CInsertQuery(query.table, table_i_header_s[query.table], tuple(nvalues))
            return super().execute_write(q)
        raise SqlException("Not supported")

    def __prepare_query(self, query):
        conditions = self.__convert_condition(query.conditions, query.table)
        return SelectQuery('*', query.table, conditions)

    def __convert_condition(self, condition, table):
        if condition is None:
            return None
        if type(condition) is SimpleCondition:
            col = condition.lvalue.split(".")[-1] + "_i"
            col_metadata = tables_index[table][col]
            if type(condition.rvalue) is str:
                if condition.rvalue[0] == "'":
                    v = condition.rvalue[1].lower()
                else:
                    try:
                        v = int(condition.rvalue)
                    except ValueError:
                        v = condition.rvalue
            else:
                v = condition.rvalue
            i = self.value_index(v, col_metadata)
            if condition.operator == SimpleCondition.Op.EQUAL:
                return SimpleCondition(col, condition.operator, col_metadata[1][i])
            else:
                if condition.operator == SimpleCondition.Op.LTE or condition.operator == SimpleCondition.Op.LT:
                    vals = col_metadata[1][:i + 1]
                else:
                    vals = col_metadata[1][i:]
                cond = SimpleCondition(col, SimpleCondition.Op.EQUAL, vals[0])
                for i in range(1, len(vals)):
                    cond = cond.or_condition(SimpleCondition(col, SimpleCondition.Op.EQUAL, vals[i]))
                return cond
        elif type(condition) is BinaryCondition:
            return BinaryCondition(self.__convert_condition(condition.lvalue, table),
                                   condition.operator,
                                   self.__convert_condition(condition.rvalue, table))
        elif type(condition) is UnaryCondition:
            return UnaryCondition(condition.operator, self.__convert_condition(condition.rvalue, table))
        raise SqlException("Something went wrong")

    @staticmethod
    def value_index(value, lst):
        for i in range(len(lst[0])):
            if value >= lst[0][i]:
                continue
            return i
        return len(lst[0])
