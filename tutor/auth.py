import functools

from tutor.models.person import Person
from flask import request, session, redirect, url_for, render_template, flash, Blueprint, abort, g
from bcrypt import hashpw, gensalt
from tutor.forms import RegistrationForm, LoginForm


bp = Blueprint('auth', __name__)


@bp.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm(request.form)

    if request.method == 'POST':
        name = form.name.data
        username = form.username.data
        email = form.email.data
        password = form.password.data
        if form.validate():
            hashed = hashpw(password.encode('utf-8'), gensalt())
            if Person(username).find():
                flash('Nome de usuário já existente', 'error')
            else:
                user = Person(username).register(name, hashed.decode('utf-8'), email)
                if user:
                    session['username'] = username
                    session['name'] = user['name']
                    session['email'] = user['email']
                    session['type'] = list(user.labels)
                    flash('Cadastro efetuado com sucesso.', 'success')
                    return redirect(url_for('index'))
    return render_template('auth/register.html',
                           form=form)


@bp.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm(request.form)

    if request.method == 'POST':
        username = form.username.data
        password = form.password.data
        user = Person(username).verify_password(password)
        if not user:
            flash('Nome de usuário ou senha incorretos', 'error')
        else:
            session['username'] = username
            session['name'] = user['name']
            session['email'] = user['email']
            session['type'] = list(user.labels)
            flash('Login efetuado com sucesso.', 'success')
            return redirect(url_for('index'))
    return render_template('auth/login.html',
                           form=form)


@bp.route('/logout', methods=['GET'])
def logout():
    if session:
        session.pop('username', None)
        session.clear()
        flash('Você saiu do sistema.', 'success')
    return redirect(url_for('index'))


############################
#   UTIL AND VALIDATIONS   #
############################
def is_teacher():
    logged_in()
    if 'Teacher' not in session.get('type'):
        abort(403)


def teacher_only(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        logged_in()
        if 'Teacher' not in session.get('type'):
            abort(403)
        return view(**kwargs)
    return wrapped_view


def is_student():
    logged_in()
    if 'Student' not in session.get('type'):
        abort(403)


def student_only(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        logged_in()
        if 'Student' not in session.get('type'):
            abort(403)
        return view(**kwargs)
    return wrapped_view


def logged_in():
    if not session.get('username'):
        flash('Você não está logado. Realize login!', 'error')
        abort(401)


def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if not session.get('username'):
            abort(401)
        return view(**kwargs)
    return wrapped_view


def confirm_passwords(password, confirm_password):
    if password == confirm_password:
        return True
    else:
        return False
