from enum import IntEnum, Enum


class Session:
    def __init__(self, user, entity):
        self.user = user
        self.entity = entity

    def get_asl(self) -> 'Classification':
        return self.user[5]

    def get_rsl(self) -> 'Classification':
        return self.user[4]

    def get_wsl(self) -> 'Classification':
        return self.user[6]

    def get_table(self):
        return Table(self.user[2])

    def get_section(self) -> 'Section':
        return Section(self.entity[tables[self.get_table()].section_index])


class Classification(IntEnum):
    TS = 4
    S = 3
    C = 2
    U = 1


class PhysicianManagementRole(Enum):
    SECTION_MANAGER = 'section_manager'
    HOSPITAL_MANAGER = 'hospital_manager'
    MEDICAL_VP = 'medical_vp'
    FINANCIAL_VP = 'financial_vp'
    ADMINISTRATIVE_VP = 'administrative_vp'
    NOTHING = 'nothing'


class EmployeeRole(Enum):
    INSPECTOR = 'inspector'
    SYSTEM_MANAGER = 'system_manager'
    ORDINARY = 'ordinary'


class Gender(Enum):
    MALE = 'M'
    FEMALE = 'F'


class Section(Enum):
    GENERAL = 'general'
    SPECIALITY = 'speciality'
    SUPER_SPECIALITY = 'super_speciality'
    EMERGENCY = 'emergency'
    FINANCIAL = 'financial'
    ADMINISTRATIVE = 'administrative'
    MEDICAL = 'medical'
    HOSPITAL = 'hospital'


class Table(Enum):
    USER = "users"
    PATIENTS = "patients"
    PHYSICIAN = "physicians"
    NURSE = "nurses"
    EMPLOYEE = "employees"


class User:
    columns = ['username', 'password', 'type', 'id', 'asl', 'rsl', 'wsl']
    enums = {2: Table}


class Physician:
    columns = ['personnel_id', 'first_name', 'last_name', 'national_code', 'proficiency', 'management_role',
               'section', 'employment_date', 'age', 'gender', 'salary', 'married']
    enums = {5: PhysicianManagementRole, 6: Section, 9: Gender}
    section_index = 6
    msl = Classification.TS
    asl = Classification.TS
    csl = Classification.TS


class Patient:
    columns = ['reception_id', 'first_name', 'last_name', 'national_code', 'age', 'gender', 'sickness_type',
               'section', 'physician_id', 'nurse_id', 'drugs']
    enums = {5: Gender, 7: Section}
    section_index = 7
    msl = Classification.S
    asl = Classification.C
    csl = Classification.C


class Nurse:
    columns = ['personnel_id', 'first_name', 'last_name', 'national_code', 'section', 'employment_date', 'age',
               'gender', 'salary', 'married']
    enums = {4: Section, 7: Gender}
    section_index = 4
    msl = Classification.TS
    asl = Classification.TS
    csl = Classification.S


class Employee:
    columns = ['personnel_id', 'first_name', 'last_name', 'national_code', 'role', 'section', 'employment_date',
               'age', 'gender', 'salary', 'married']
    enums = {4: EmployeeRole, 5: Section, 8: Gender}
    section_index = 5
    msl = Classification.TS
    asl = Classification.TS
    csl = Classification.TS


class Privacy:
    def __init__(self, readers, writers):
        self.readers = readers
        self.writers = writers


class DionException(Exception):
    def __init__(self, message) -> None:
        super().__init__(message)
        self.message = message


section_dominance = {Section.GENERAL: [Section.GENERAL],
                     Section.SPECIALITY: [Section.SPECIALITY],
                     Section.SUPER_SPECIALITY: [Section.SUPER_SPECIALITY],
                     Section.EMERGENCY: [Section.EMERGENCY],
                     Section.FINANCIAL: [Section.FINANCIAL, Section.GENERAL, Section.SPECIALITY,
                                         Section.SUPER_SPECIALITY, Section.EMERGENCY],
                     Section.ADMINISTRATIVE: [Section.ADMINISTRATIVE, Section.GENERAL, Section.SPECIALITY,
                                              Section.SUPER_SPECIALITY, Section.EMERGENCY],
                     Section.MEDICAL: [Section.MEDICAL, Section.GENERAL, Section.SPECIALITY,
                                       Section.SUPER_SPECIALITY, Section.EMERGENCY],
                     Section.HOSPITAL: [Section.HOSPITAL, Section.FINANCIAL, Section.ADMINISTRATIVE, Section.GENERAL,
                                        Section.SPECIALITY, Section.SUPER_SPECIALITY, Section.EMERGENCY]}


subject_levels = {Table.PHYSICIAN: (Classification.S, Classification.S, Classification.C),
                  Table.NURSE: (Classification.S, Classification.S, Classification.S),
                  Table.PATIENTS: (Classification.U, Classification.U, Classification.U),
                  Table.EMPLOYEE: (Classification.TS, Classification.TS, Classification.S)}


tables = {Table.USER: User, Table.PHYSICIAN: Physician, Table.PATIENTS: Patient,
          Table.NURSE: Nurse, Table.EMPLOYEE: Employee}
