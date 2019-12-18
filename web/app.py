from functools import wraps
from flask import Flask, request, session, render_template, redirect, url_for
from web.auth import do_the_login
import config

app = Flask(__name__)
app.secret_key = config.secret


def login_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if 'username' not in session:
            return redirect(url_for('login'))
        kwargs['user'] = session['username']
        return func(*args, **kwargs)

    return wrapper


@app.route('/')
@login_required
def index(user):
    return render_template('index.html')


@app.route('/physicians')
@login_required
def physicians(user):
    return render_template('physicians.html', list=[('1', 'Mohammadreza', 'Ziraki', '2282400860', 'Nothing', 'Manager',
                                                     'General', '2020/01/01', '22', 'M', '4000000', 'S')])


@app.route('/physicians/create', methods=['GET', 'POST'])
@login_required
def create_physician(user):
    if request.method == 'POST':
        print(request.form)
        return redirect(url_for('physicians'))
    else:
        return render_template('create_physician.html')


@app.route('/physicians/edit/<id>', methods=['GET', 'POST'])
@login_required
def edit_physician(id, user):
    if request.method == 'POST':
        print(request.form)
        return redirect(url_for('physicians'))
    else:
        return render_template('edit_physician.html', p=('1', 'Mohammadreza', 'Ziraki', '2282400860', 'Nothing',
                                                         'Manager', 'General', '2020-01-01', '22', 'M', '4000000', 'S'))


@app.route('/physicians/delete/<id>')
@login_required
def delete_physician(id, user):
    return redirect(url_for('physicians'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'username' in session:
        return redirect(url_for('index'))
    if request.method == 'POST':
        username = request.form['username']
        if do_the_login(username, request.form['password']) is not None:
            session['username'] = username
            return redirect(url_for('index'))
        return render_template('login.html', failed=True)
    else:
        return render_template('login.html')


@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('index'))
