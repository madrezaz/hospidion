from enum import IntEnum

users = ['username', 'password', 'type']
physicians = ['personnel_id', 'first_name', 'last_name', 'national_code', 'proficiency', 'management_role',
              'section', 'employment_date', 'age', 'gender', 'salary', 'marital_status']
nurses = ['personnel_id', 'first_name', 'last_name', 'national_code', 'section', 'employment_date', 'age',
          'gender', 'salary', 'marital_status']
patients = ['reception_id', 'first_name', 'last_name', 'national_code', 'age', 'gender', 'sickness_type',
            'section', 'physician_id', 'nurse_id', 'drugs']
employees = ['personnel_id', 'first_name', 'last_name', 'national_code', 'role', 'employment_date', 'age', 'gender',
             'salary', 'marital_status']

user_types = ['physician', 'patient', 'nurse', 'employee']
genders = ['M', 'F']
marital_statuses = ['S', 'M']
medical_sections = ['general', 'speciality', 'super_speciality', 'emergency']
management_roles = ['section_manager', 'hospital_manager', 'medical_vp', 'financial_vp', 'administrative_vp']
non_medical_sections = ['financial', 'administrative']
employee_roles = ['inspector', 'system_manager', 'financial', 'administrative']


class Classification(IntEnum):
    TS = 4
    S = 3
    C = 2
    U = 1
