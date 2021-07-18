from tutor.models.person import Person
from tutor.models.course_class import CourseClass
from flask import request, session, render_template, flash, abort, Blueprint
from bcrypt import hashpw, gensalt
from tutor.forms import EditProfileForm
from tutor.auth import login_required

bp = Blueprint('profile', __name__, url_prefix='/profile')


#
# View user's Profile
#
@bp.route('/')
@bp.route('/<username>')
@login_required
def view(username=None):
    if not username:
        username = session.get('username')
    user = Person(username).find()

    if user:
        # vendo o próprio perfil
        if username == session.get('username'):
            if 'Teacher' in user.labels:
                classes = CourseClass().get_course_classes(user['username'])

                return render_template('profile/view.html',
                                       user=user,
                                       course_classes=classes)
        return render_template('profile/view.html',
                               user=user)
    abort(404)


#
# Edit profile information
# Users can edit only their name, email and password (if a new one is provided)
#
@bp.route('/edit', methods=['GET', 'POST'])
@login_required
def edit():
    user = Person(node_user=Person(session.get('username')).find())
    form = EditProfileForm(request.form, user)
    if request.method == 'POST':
        name = form.name.data
        email = form.email.data
        password = form.password.data
        if form.validate():
            if password:
                hashed = hashpw(password.encode('utf-8'), gensalt())
                if not Person(session.get('username')).change_password(hashed.decode('utf-8')):
                    flash('Erro ao alterar a senha', 'error')
                    return render_template('profile/edit.html',
                                           form=form)

            if Person(session.get('username')).edit_personal_data(name, email):
                session['name'] = name
                session['email'] = email
                flash('Dados alterados com sucesso', 'success')
    return render_template('profile/edit.html',
                           form=form)
