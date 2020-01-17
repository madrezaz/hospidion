from functools import wraps

import psycopg2
from flask import Flask, request, session, render_template, redirect, url_for, abort

from core.auth import create_session
from core.dion import DionExecutor
import config
from core.models import *
from core.sql import SqlException, DefaultQueryExecutor
from outsourcing.indexing import IndexingQueryExecutor
from outsourcing.partitioning import PartitioningQueryExecutor

app = Flask(__name__)
app.secret_key = config.secret


def create_db_executor():
    if config.outsourced == 0:
        executor = DefaultQueryExecutor
    elif config.outsourced == 1:
        executor = IndexingQueryExecutor
    else:
        executor = PartitioningQueryExecutor
    return executor(config.db_name, config.db_user, config.db_password, config.db_host, config.db_port)


def create_executor(user_session):
    return DionExecutor(user_session, create_db_executor())


@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'username' in session:
        return redirect(url_for('index'))
    if request.method == 'POST':
        username = request.form['username']
        s = create_session(create_db_executor(), username, request.form['password'])
        if s is not None:
            session['username'] = username
            return redirect(url_for('index'))
        return render_template('login.html', failed=True)
    else:
        return render_template('login.html')


@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('index'))


def login_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if 'username' not in session:
            return redirect(url_for('login'))
        kwargs['user_session'] = create_session(create_db_executor(), session['username'])
        return func(*args, **kwargs)

    return wrapper


@app.route('/')
@login_required
def index(user_session):
    executor = create_executor(user_session)
    privacy = executor.execute("my privacy")
    readers = ", ".join([r[0] for r in privacy.readers])
    writers = ", ".join([r[0] for r in privacy.writers])
    return render_template('index.html', readers=readers, writers=writers, user_session=user_session)


@app.route('/physicians')
@login_required
def physicians(user_session):
    executor = create_executor(user_session)
    res = executor.execute("select * from physicians")
    return render_template('physicians.html', list=res)


@app.route('/physicians/create', methods=['GET', 'POST'])
@login_required
def create_physician(user_session):
    if request.method == 'POST':
        for col in Physician.columns:
            if col not in request.form or request.form[col] == '':
                return render_template('create_physician.html', error="%s must be non-empty" % col)
        executor = create_executor(user_session)
        try:
            res = executor.execute("insert into physicians values " +
                                   "('%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s')" %
                                   (request.form['personnel_id'], request.form['first_name'], request.form['last_name'],
                                    request.form['national_code'], request.form['proficiency'],
                                    request.form['management_role'], request.form['section'],
                                    request.form['employment_date'], request.form['age'], request.form['gender'],
                                    request.form['salary'], request.form['married']))
            if res == 0:
                return render_template('create_physician.html', error="Failed")
        except (DionException, SqlException, psycopg2._psycopg.Error) as ex:
            return render_template('create_physician.html', error=str(ex))
        return redirect(url_for('physicians'))
    else:
        return render_template('create_physician.html')


@app.route('/physicians/edit/<physician_id>', methods=['GET', 'POST'])
@login_required
def edit_physician(physician_id, user_session):
    executor = create_executor(user_session)
    result = executor.execute("select * from physicians where personnel_id = '%s'" % physician_id)
    if len(result) != 1:
        abort(404)
    if request.method == 'POST':
        changed_cols = []
        for i in range(len(Physician.columns)):
            col = Physician.columns[i]
            if col not in request.form or request.form[col] == '':
                return render_template('edit_physician.html', p=result[0], error="%s must be non-empty" % col)
            if col == 'married' and str(result[0][i]).lower() == request.form[col] or \
                    str(result[0][i]) != request.form[col]:
                changed_cols += [col]
        setters = ", ".join(["%s = '%s'" % (col, request.form[col]) for col in changed_cols])
        try:
            executor.execute("update physicians set %s where personnel_id = '%s'" % (setters, physician_id))
        except (DionException, SqlException, psycopg2._psycopg.Error) as ex:
            return render_template('edit_physician.html', p=result[0], error=str(ex))
        return redirect(url_for('physicians'))
    else:
        return render_template('edit_physician.html', p=result[0])


@app.route('/physicians/delete/<physician_id>')
@login_required
def delete_physician(physician_id, user_session):
    executor = create_executor(user_session)
    try:
        executor.execute("delete from physicians where personnel_id = '%s'" % physician_id)
    except (DionException, SqlException, psycopg2._psycopg.Error) as ex:
        pass
    return redirect(url_for('physicians'))


@app.route('/patients')
@login_required
def patients(user_session):
    executor = create_executor(user_session)
    res = executor.execute("select * from patients")
    return render_template('patients.html', list=res)


@app.route('/patients/create', methods=['GET', 'POST'])
@login_required
def create_patient(user_session):
    if request.method == 'POST':
        for col in Patient.columns:
            if col not in request.form or request.form[col] == '':
                return render_template('create_patient.html', error="%s must be non-empty" % col)
        executor = create_executor(user_session)
        try:
            res = executor.execute("insert into patients values " +
                                   "('%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s')" %
                                   (request.form['reception_id'], request.form['first_name'], request.form['last_name'],
                                    request.form['national_code'], request.form['age'], request.form['gender'],
                                    request.form['sickness_type'], request.form['section'],
                                    request.form['physician_id'], request.form['nurse_id'], request.form['drugs']))
            if res == 0:
                return render_template('create_patient.html', error="Failed")
        except (DionException, SqlException, psycopg2._psycopg.Error) as ex:
            return render_template('create_patient.html', error=str(ex))
        return redirect(url_for('patients'))
    else:
        return render_template('create_patient.html')


@app.route('/patients/edit/<patient_id>', methods=['GET', 'POST'])
@login_required
def edit_patient(patient_id, user_session):
    executor = create_executor(user_session)
    result = executor.execute("select * from patients where reception_id = '%s'" % patient_id)
    if len(result) != 1:
        abort(404)
    if request.method == 'POST':
        changed_cols = []
        for i in range(len(Patient.columns)):
            col = Patient.columns[i]
            if col not in request.form or request.form[col] == '':
                return render_template('edit_patient.html', p=result[0], error="%s must be non-empty" % col)
            if col == 'married' and str(result[0][i]).lower() == request.form[col] or \
                    str(result[0][i]) != request.form[col]:
                changed_cols += [col]
        setters = ", ".join(["%s = '%s'" % (col, request.form[col]) for col in changed_cols])
        try:
            executor.execute("update patients set %s where reception_id = '%s'" % (setters, patient_id))
        except (DionException, SqlException, psycopg2._psycopg.Error) as ex:
            return render_template('edit_patient.html', p=result[0], error=str(ex))
        return redirect(url_for('patients'))
    else:
        return render_template('edit_patient.html', p=result[0])


@app.route('/patients/delete/<patient_id>')
@login_required
def delete_patient(patient_id, user_session):
    executor = create_executor(user_session)
    try:
        executor.execute("delete from patients where reception_id = '%s'" % patient_id)
    except (DionException, SqlException, psycopg2._psycopg.Error) as ex:
        pass
    return redirect(url_for('patients'))


@app.route('/nurses')
@login_required
def nurses(user_session):
    executor = create_executor(user_session)
    res = executor.execute("select * from nurses")
    return render_template('nurses.html', list=res)


@app.route('/nurses/create', methods=['GET', 'POST'])
@login_required
def create_nurse(user_session):
    if request.method == 'POST':
        for col in Nurse.columns:
            if col not in request.form or request.form[col] == '':
                return render_template('create_nurse.html', error="%s must be non-empty" % col)
        executor = create_executor(user_session)
        try:
            res = executor.execute("insert into nurses values " +
                                   "('%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s')" %
                                   (request.form['personnel_id'], request.form['first_name'], request.form['last_name'],
                                    request.form['national_code'], request.form['section'],
                                    request.form['employment_date'], request.form['age'], request.form['gender'],
                                    request.form['salary'], request.form['married']))
            if res == 0:
                return render_template('create_nurse.html', error="Failed")
        except (DionException, SqlException, psycopg2._psycopg.Error) as ex:
            return render_template('create_nurse.html', error=str(ex))
        return redirect(url_for('nurses'))
    else:
        return render_template('create_nurse.html')


@app.route('/nurses/edit/<nurse_id>', methods=['GET', 'POST'])
@login_required
def edit_nurse(nurse_id, user_session):
    executor = create_executor(user_session)
    result = executor.execute("select * from nurses where personnel_id = '%s'" % nurse_id)
    if len(result) != 1:
        abort(404)
    if request.method == 'POST':
        changed_cols = []
        for i in range(len(Nurse.columns)):
            col = Nurse.columns[i]
            if col not in request.form or request.form[col] == '':
                return render_template('edit_nurse.html', p=result[0], error="%s must be non-empty" % col)
            if col == 'married' and str(result[0][i]).lower() == request.form[col] or \
                    str(result[0][i]) != request.form[col]:
                changed_cols += [col]
        setters = ", ".join(["%s = '%s'" % (col, request.form[col]) for col in changed_cols])
        try:
            executor.execute("update nurses set %s where personnel_id = '%s'" % (setters, nurse_id))
        except (DionException, SqlException, psycopg2._psycopg.Error) as ex:
            return render_template('edit_nurse.html', p=result[0], error=str(ex))
        return redirect(url_for('nurses'))
    else:
        return render_template('edit_nurse.html', p=result[0])


@app.route('/nurses/delete/<nurse_id>')
@login_required
def delete_nurse(nurse_id, user_session):
    executor = create_executor(user_session)
    try:
        executor.execute("delete from nurses where personnel_id = '%s'" % nurse_id)
    except (DionException, SqlException, psycopg2._psycopg.Error) as ex:
        pass
    return redirect(url_for('nurses'))


@app.route('/employees')
@login_required
def employees(user_session):
    executor = create_executor(user_session)
    res = executor.execute("select * from employees")
    return render_template('employees.html', list=res)


@app.route('/employees/create', methods=['GET', 'POST'])
@login_required
def create_employee(user_session):
    if request.method == 'POST':
        for col in Employee.columns:
            if col not in request.form or request.form[col] == '':
                return render_template('create_employee.html', error="%s must be non-empty" % col)
        executor = create_executor(user_session)
        try:
            res = executor.execute("insert into employees values " +
                                   "('%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s')" %
                                   (request.form['personnel_id'], request.form['first_name'], request.form['last_name'],
                                    request.form['national_code'], request.form['role'],
                                    request.form['section'], request.form['employment_date'], request.form['age'],
                                    request.form['gender'], request.form['salary'], request.form['married']))
            if res == 0:
                return render_template('create_employee.html', error="Failed")
        except (DionException, SqlException, psycopg2._psycopg.Error) as ex:
            return render_template('create_employee.html', error=str(ex))
        return redirect(url_for('employees'))
    else:
        return render_template('create_employee.html')


@app.route('/employees/edit/<employee_id>', methods=['GET', 'POST'])
@login_required
def edit_employee(employee_id, user_session):
    executor = create_executor(user_session)
    result = executor.execute("select * from employees where personnel_id = '%s'" % employee_id)
    if len(result) != 1:
        abort(404)
    if request.method == 'POST':
        changed_cols = []
        for i in range(len(Employee.columns)):
            col = Employee.columns[i]
            if col not in request.form or request.form[col] == '':
                return render_template('edit_employee.html', p=result[0], error="%s must be non-empty" % col)
            if col == 'married' and str(result[0][i]).lower() == request.form[col] or \
                    str(result[0][i]) != request.form[col]:
                changed_cols += [col]
        setters = ", ".join(["%s = '%s'" % (col, request.form[col]) for col in changed_cols])
        try:
            executor.execute("update employees set %s where personnel_id = '%s'" % (setters, employee_id))
        except (DionException, SqlException, psycopg2._psycopg.Error) as ex:
            return render_template('edit_employee.html', p=result[0], error=str(ex))
        return redirect(url_for('employees'))
    else:
        return render_template('edit_employee.html', p=result[0])


@app.route('/employees/delete/<employee_id>')
@login_required
def delete_employee(employee_id, user_session):
    executor = create_executor(user_session)
    try:
        executor.execute("delete from employees where personnel_id = '%s'" % employee_id)
    except (DionException, SqlException, psycopg2._psycopg.Error) as ex:
        pass
    return redirect(url_for('employees'))


@app.route('/reports')
@login_required
def reports(user_session):
    executor = create_executor(user_session)
    try:
        res = executor.execute("select * from reports")
        return render_template('reports.html', list=res)
    except (DionException, SqlException, psycopg2._psycopg.Error) as ex:
        return str(ex)


def __edit_report(executor, table, report_id):
    result = executor.execute("select * from %s where id = %s" % (table, report_id))
    if len(result) != 1:
        abort(404)
    if request.method == 'POST':
        changed_cols = []
        for i in range(len(Report.columns)):
            col = Report.columns[i]
            if col not in request.form or request.form[col] == '':
                return render_template('edit_report.html', p=result[0], error="%s must be non-empty" % col)
            if str(result[0][i]) != request.form[col]:
                changed_cols += [col]
        setters = ", ".join(["%s = '%s'" % (col, request.form[col]) for col in changed_cols])
        try:
            executor.execute("update %s set %s where id = '%s'" % (table, setters, report_id))
        except (DionException, SqlException, psycopg2._psycopg.Error) as ex:
            return render_template('edit_report.html', p=result[0], error=str(ex))
        return redirect(url_for('reports'))
    else:
        return render_template('edit_report.html', p=result[0])


@app.route('/reports/edit/<report_id>', methods=['GET', 'POST'])
@login_required
def edit_reports(report_id, user_session):
    return __edit_report(create_executor(user_session), "reports", report_id)


@app.route('/reports/delete/<report_id>')
@login_required
def delete_reports(report_id, user_session):
    executor = create_executor(user_session)
    try:
        executor.execute("delete from reports where id = %s" % report_id)
    except (DionException, SqlException, psycopg2._psycopg.Error) as ex:
        pass
    return redirect(url_for('reports'))


@app.route('/reports/inspector')
@login_required
def inspector_reports(user_session):
    executor = create_executor(user_session)
    try:
        res = executor.execute("select * from inspector_reports")
        return render_template('reports.html', list=res, inspector=True)
    except (DionException, SqlException, psycopg2._psycopg.Error) as ex:
        return str(ex)


@app.route('/reports/inspector/edit/<report_id>', methods=['GET', 'POST'])
@login_required
def edit_inspector_reports(report_id, user_session):
    return __edit_report(create_executor(user_session), "inspector_reports", report_id)


@app.route('/reports/inspector/delete/<report_id>')
@login_required
def delete_inspector_reports(report_id, user_session):
    executor = create_executor(user_session)
    try:
        executor.execute("delete from inspector_reports where id = %s" % report_id)
    except (DionException, SqlException, psycopg2._psycopg.Error) as ex:
        pass
    return redirect(url_for('inspector_reports'))


@app.route('/reports/manager')
@login_required
def manager_reports(user_session):
    executor = create_executor(user_session)
    try:
        res = executor.execute("select * from manager_reports")
        return render_template('reports.html', list=res, manager=True)
    except (DionException, SqlException, psycopg2._psycopg.Error) as ex:
        return str(ex)


@app.route('/reports/inspector/edit/<report_id>', methods=['GET', 'POST'])
@login_required
def edit_manager_reports(report_id, user_session):
    return __edit_report(create_executor(user_session), "manager_reports", report_id)


@app.route('/reports/inspector/delete/<report_id>')
@login_required
def delete_manager_reports(report_id, user_session):
    executor = create_executor(user_session)
    try:
        executor.execute("delete from manager_reports where id = %s" % report_id)
    except (DionException, SqlException, psycopg2._psycopg.Error) as ex:
        pass
    return redirect(url_for('manager_reports'))


@app.route('/reports/send', methods=['GET', 'POST'])
@login_required
def send_report(user_session):
    if request.method == 'POST':
        if 'report' not in request.form or request.form['report'] == '':
            return render_template('send_report.html', error="report must be non-empty")
        executor = create_executor(user_session)
        res = executor.execute("send report '%s'" % request.form['report'])
        if res == 0:
            return render_template('send_report.html', error="Failed")
        return redirect(url_for('index'))
    else:
        return render_template('send_report.html')


@app.route('/reports/migrate/<report_id>')
@login_required
def migrate_report(report_id, user_session):
    executor = create_executor(user_session)
    try:
        res = executor.execute("migrate reports where id = %s" % report_id)
        if res == 0:
            return redirect(url_for('reports'))
        executor.execute("delete from reports where id = %s" % report_id)
        return redirect(url_for('reports'))
    except (DionException, SqlException, psycopg2._psycopg.Error) as ex:
        return str(ex)


@app.route('/reports/inspector/migrate/<report_id>')
@login_required
def migrate_inspector_report(report_id, user_session):
    executor = create_executor(user_session)
    try:
        res = executor.execute("migrate reports where id = %s" % report_id)
        if res == 0:
            return redirect(url_for('inspector_reports'))
        executor.execute("delete from inspector_reports where id = %s" % report_id)
        return redirect(url_for('inspector_reports'))
    except (DionException, SqlException, psycopg2._psycopg.Error) as ex:
        return str(ex)
