from .models import Person, CourseClass, ClassSubject, Question, Answer
from flask import Flask, request, session, redirect, url_for, render_template, flash, abort
from bcrypt import hashpw, gensalt
from os import urandom
from .forms import RegistrationForm, LoginForm, EditProfileForm, CourseClassForm, ClassSubjectForm, QuestionForm

app = Flask(__name__)
app.secret_key = urandom(24)


# TODO #1 terminar parte do aluno
# TODO #2 campos extrar dos relacionamentos (questão criada em/alterada em, questão respondida em/alterada em etc.)
# TODO #3 aceitar múltiplos assuntos anteriores/posteriores
# TODO #4 o que vai ter no Ver Perfil?
# TODO #5 criar cursos. só admin pode criar cursos. disciplinas ligadas a um curso. professor pode estar ligado a vários cursos.
# TODO #6 limpar código. retirar funções legadas do exemplo
# TODO #7 colocar algo na tela principal do professor. últimas respostas? algum gráfico?
# TODO #8 colocar algo na tela principal do estudante. últimas respostas? perguntas/assuntos que outras pessoas da mesma turma estão respondendo?
# TODO #9 revisar todas as rotas. não deixar entrar nas rotas que não pode.
# TODO #10 papel e funções de administrador. mudar papeis dos usuários, cadastrar cursos.
# TODO #11 dockerizar


@app.route('/')
def index():
    # session['username'] = 'sirlon'
    # session['person_name'] = 'Sirlon'
    # session['email'] = 'sirlon@sirlon.com'
    # session['type'] = 'teacher'
    return render_template('index.html')


###########################################
#   REGISTER, PROFILE, LOGIN AND LOGOUT   #
###########################################
@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm(request.form)

    if request.method == 'POST':
        name = form.name.data
        username = form.username.data
        email = form.email.data
        password = form.password.data
        p_type = "student"
        if form.validate():
            hashed = hashpw(password.encode('utf-8'), gensalt())
            if Person(username).find():
                flash('Nome de usuário já existente', 'error')
            elif Person(username).register(name, hashed.decode('utf-8'), email, p_type):
                session['username'] = username
                session['person_name'] = name
                session['email'] = email
                session['type'] = p_type
                flash('Cadastro efetuado com sucesso.', 'success')
                return redirect(url_for('index'))
    return render_template('register.html',
                           form=form)


@app.route('/login', methods=['GET', 'POST'])
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
            session['type'] = user['type']
            session['person_name'] = user['name']
            session['email'] = user['email']
            flash('Login efetuado com sucesso.', 'success')
            return redirect(url_for('index'))
    return render_template('login.html',
                           form=form)


@app.route('/logout', methods=['GET'])
def logout():
    if session:
        session.pop('username', None)
        session.clear()
        flash('Você saiu do sistema.', 'success')
    return redirect(url_for('index'))


#
# View user's Profile
#
@app.route('/profile/')
@app.route('/profile/<username>')
def profile(username=None):
    logged_in()

    if not username:
        username = session.get('username')
    user = Person(username).find()

    # vendo o próprio perfil
    if username == session.get('username'):
        if user['type'] == 'teacher':
            classes = CourseClass().get_course_classes(user['username'])

            return render_template('profile.html',
                                   user=user,
                                   classes=classes)
    return render_template('profile.html',
                           user=user)


#
# Edit profile information
# Users can edit only their name, email and password (if a new one is provided)
#
@app.route('/edit_profile', methods=['GET', 'POST'])
def edit_profile():
    logged_in()

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
                    return render_template('edit_profile.html',
                                           form=form)

            if Person(session.get('username')).edit_personal_data(name, email):
                session['person_name'] = name
                session['email'] = email
                flash('Dados alterados com sucesso', 'success')
    return render_template('edit_profile.html',
                           form=form)


####################
#   COURSE CLASS   #
####################

#
# List or Create Course Classes for Teachers
#
@app.route('/course_classes', methods=['GET', 'POST'])
def course_classes():
    is_teacher()

    form = CourseClassForm(request.form)
    users_course_classes = list(CourseClass().get_course_classes(session.get('username')))
    error = False
    if request.method == 'POST':
        title = form.title.data
        if form.validate():
            if CourseClass().create(title, session.get('username')):
                flash('Disciplina criada com sucesso.', 'success')
                return redirect(url_for('course_classes'))
            flash('Disciplina já existente', 'error')
        error = True
    return render_template('course_class.html',
                           course_classes=users_course_classes,
                           form=form,
                           error=error)


#
# Edit Course Classes
#
@app.route('/edit_course_class/<cc_identity>', methods=['GET', 'POST'])
def edit_course_class(cc_identity):
    is_teacher()

    node_course_class = CourseClass().find_by_identity_and_user(cc_identity, session.get('username'))
    if node_course_class:
        course_class = CourseClass(node_course_class)
        form = CourseClassForm(request.form, course_class)

        if request.method == 'POST':
            if form.validate():
                new_title = form.title.data
                if course_class.title == new_title or CourseClass().edit(cc_identity, new_title,
                                                                         session.get('username')):
                    flash('Disciplina alterada com sucesso.', 'success')
                    return redirect(url_for('course_classes'))
                flash('Disciplina já existente', 'error')

        return render_template('edit_course_class.html',
                               course_class=course_class,
                               form=form)
    abort(404)


#
# Delete Course Classes
#
@app.route('/delete_course_class/<cc_identity>', methods=['POST'])
def delete_course_class(cc_identity):
    is_teacher()

    if not CourseClass().find_no_relationship_course_class_and_subject(cc_identity):
        flash('A Disciplina não pode ser excluída, pois contém assuntos.', 'error')
    elif CourseClass().delete(cc_identity):
        flash('Disciplina excluída com sucesso.', 'success')
    else:
        flash('Ocorreu algum erro ao tentar excluir a disciplina.', 'error')
    return redirect(url_for('course_classes'))


#
# List Course Classes for Students
#
@app.route('/open_course_class_student')
def open_course_class_student():
    is_student()

    user = session.get('username')
    student_course_classes = CourseClass().get_student_course_classes(user)
    no_student_course_classes = CourseClass().get_no_student_course_classes(user)

    return render_template('course_class_student.html',
                           scc=student_course_classes,
                           nscc=no_student_course_classes)


#
# Enrollment on Course Classes
#
@app.route('/enrollment_course_class/<course_class>')
def enrollment_course_class(course_class):
    is_student()

    user = session.get('username')
    if not CourseClass().enrollment(course_class, user):
        flash('Erro ao matricular-se Disciplina', 'error')
    else:
        flash('Matrícula realizada com sucesso.', 'success')

    return redirect(url_for('open_course_class_student',
                            user=user))


#####################
#   CLASS SUBJECT   #
#####################

#
# List or Create Class Subjects
#
@app.route('/class_subjects/<cc_identity>', methods=['GET', 'POST'])
def class_subjects(cc_identity):
    is_teacher()

    course_class = CourseClass().find_by_identity_and_user(cc_identity, session.get('username'))
    if course_class:
        form = ClassSubjectForm(request.form)
        course_class_subjects = list(ClassSubject().get_class_subjects_with_previous_and_forward(cc_identity))

        # populates all select fields with their respective choices
        form.previous_subject.choices = get_choices_with_empty_placeholder(course_class_subjects)
        form.next_subject.choices = get_choices_with_empty_placeholder(course_class_subjects)

        # this variable prevents the form from being collapsed in case there's an error
        error = False
        if request.method == 'POST':
            del form.initial
            if form.validate():
                if ClassSubject().create(cc_identity, form.title.data, form.previous_subject.data,
                                         form.next_subject.data, form.support_material.data):
                    flash('Assunto criado com sucesso.', 'success')
                    return redirect(url_for('class_subjects',
                                            cc_identity=cc_identity))
                flash('Assunto já existente', 'error')
            error = True
        return render_template('class_subject.html',
                               course_class=course_class,
                               class_subjects=course_class_subjects,
                               form=form,
                               error=error)
    abort(404)


#
# Edit Class Subjects
#
@app.route('/edit_class_subject/<cc_identity>/<cs_identity>', methods=['GET', 'POST'])
def edit_class_subject(cc_identity, cs_identity):
    is_teacher()

    course_class = CourseClass().find_by_identity_and_user(cc_identity, session.get('username'))
    node_class_subject = ClassSubject().find_in_course(cc_identity, cs_identity)
    if course_class and node_class_subject:
        class_subject = ClassSubject(node_class_subject)

        # Preparing the form
        form = ClassSubjectForm(request.form, class_subject)
        list_subjects = list(ClassSubject().get_class_subjects_and_course_class_except_current_subject(cc_identity,
                                                                                                       cs_identity))
        # populates all select fields with their respective choices
        form.previous_subject.choices = get_choices_with_empty_placeholder(list_subjects)
        form.next_subject.choices = get_choices_with_empty_placeholder(list_subjects)
        form.initial.choices = get_yes_or_no_choices()

        if request.method == 'GET':
            form.previous_subject.data = ClassSubject().find_previous(cc_identity, cs_identity)
            form.next_subject.data = ClassSubject().find_next(cc_identity, cs_identity)
        elif request.method == 'POST':
            if form.validate():
                if ClassSubject().edit(cc_identity, cs_identity,
                                       form.title.data, form.previous_subject.data,
                                       form.next_subject.data, form.support_material.data,
                                       form.initial.data):
                    flash('Assunto alterado com sucesso.', 'success')
                    return redirect(url_for('class_subjects',
                                            cc_identity=cc_identity))
                flash('Erro ao alterar assunto', 'error')
        return render_template('edit_class_subject.html',
                               course_class=course_class,
                               class_subject=class_subject,
                               form=form)
    abort(404)


#
# Delete Class Subjects
#
@app.route('/delete_class_subject/<cc_identity>/<cs_identity>', methods=['POST'])
def delete_class_subject(cc_identity, cs_identity):
    is_teacher()

    if ClassSubject().get_initial_value(cc_identity, cs_identity) == 'True' \
            and int(ClassSubject().find_node_count(cc_identity)) > 1:
        flash('Assunto não pode ser excluído, pois é o assunto inicial.', 'error')
    elif ClassSubject().find_class_subject_has_questions(cc_identity, cs_identity):
        flash('Assunto não pode ser excluído, pois possui questões.', 'error')
    elif ClassSubject().delete(cc_identity, cs_identity):
        flash('Assunto excluído com sucesso.', 'success')
    else:
        flash('Ocorreu algum erro ao tentar excluir o assunto.', 'error')
    return redirect(url_for('class_subjects',
                            cc_identity=cc_identity))


#################
#   QUESTIONS   #
#################

#
# List or Create Questions
#
@app.route('/questions/<cc_identity>/<cs_identity>', methods=['GET', 'POST'])
def questions(cc_identity, cs_identity):
    is_teacher()

    course_class = CourseClass().find_by_identity_and_user(cc_identity, session.get('username'))
    class_subject = ClassSubject().find_in_course(cc_identity, cs_identity)
    if course_class and class_subject:
        form = QuestionForm(request.form)
        all_questions = list(Question().get_questions(cc_identity, cs_identity))
        form.difficulty.choices = get_difficulty_choices()
        form.right_answer.choices = get_right_answer_choices()

        error = False
        if request.method == 'POST':
            if form.validate():
                if Question().create(cc_identity, cs_identity,
                                     form.title.data, form.body.data,
                                     form.support_material.data, form.difficulty.data,
                                     form.choice_a.data, form.choice_b.data,
                                     form.choice_c.data, form.choice_d.data,
                                     form.right_answer.data):
                    flash('Questão criada com sucesso.', 'success')
                    return redirect(url_for('questions',
                                            cc_identity=cc_identity,
                                            cs_identity=cs_identity))
                flash('Erro ao cadastrar questão', 'error')
            error = True
        return render_template('question.html',
                               course_class=course_class,
                               class_subject=class_subject,
                               questions=all_questions,
                               form=form,
                               error=error)
    abort(404)


#
# Edit Questions
#
@app.route('/edit_question/<cc_identity>/<cs_identity>/<question_identity>', methods=['GET', 'POST'])
def edit_question(cc_identity, cs_identity, question_identity):
    is_teacher()

    course_class = CourseClass().find_by_identity_and_user(cc_identity, session.get('username'))
    class_subject = ClassSubject().find_in_course(cc_identity, cs_identity)
    node_question = Question().get_question(question_identity).evaluate()
    if course_class and class_subject and node_question:
        question = Question(node_question)

        # Preparing the form
        form = QuestionForm(request.form, question)
        form.difficulty.choices = get_difficulty_choices()
        form.right_answer.choices = get_right_answer_choices()

        if request.method == 'POST':
            if form.validate():
                if Question().edit(question_identity, form.title.data,
                                   form.body.data, form.support_material.data,
                                   form.difficulty.data, form.choice_a.data,
                                   form.choice_b.data, form.choice_c.data,
                                   form.choice_d.data, form.right_answer.data):
                    flash('Questão alterada com sucesso.', 'success')
                    return redirect(url_for('questions',
                                            cc_identity=cc_identity,
                                            cs_identity=cs_identity,
                                            question_identity=question_identity))
                flash('Erro ao alterar questão.', 'error')
        return render_template('edit_question.html',
                               course_class=course_class,
                               class_subject=class_subject,
                               question=question,
                               form=form)
    abort(404)


#
# Delete Questions
#
@app.route('/delete_question/<cc_identity>/<cs_identity>/<question_identity>', methods=['POST'])
def delete_question(cc_identity, cs_identity, question_identity):
    is_teacher()

    course_class = CourseClass().find_by_identity_and_user(cc_identity, session.get('username'))
    class_subject = ClassSubject().find_in_course(cc_identity, cs_identity)
    if course_class and class_subject and Question().delete(question_identity):
        flash('Questão excluida com sucesso.', 'success')
    else:
        flash('Erro ao excluir questão.', 'error')

    return redirect(url_for('questions',
                            cc_identity=cc_identity,
                            cs_identity=cs_identity))


@app.route('/open_answer_questions/<cc_identity>')
def open_answer_questions(cc_identity):
    is_student()

    user = session.get('username')
    question = Question().get_current_question(cc_identity, user).evaluate()
    cs_title = ClassSubject().get_class_subject_current_question(cc_identity, user).evaluate()

    return render_template('answer_question.html',
                           cc_identity=cc_identity,
                           cs_title=cs_title,
                           question=question,
                           user=user)


@app.route('/answer_question', methods=['GET', 'POST'])
def answer_question():
    is_student()

    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        support_material = request.form['support_material']
        right_answer = request.form['right_answer']
        cs_title = request.form['cs_title']
        alternative_answered = request.form['alternative_answered']
        user = request.form['username']
        Answer().set_answer_question(alternative_answered, user)

        if alternative_answered == right_answer:
            flash('Acertou', 'success')
        else:
            flash('Errou', 'error')

        return render_template('alert_question_answered.html',
                               cs_title=cs_title,
                               title=title,
                               body=body,
                               support_material=support_material,
                               username=user)


# MÉTODOS LEGADOS DO EXEMPLO #
# @app.route('/add_post', methods=['POST'])
# def add_post():
#     title = request.form['title']
#     tags = request.form['tags']
#     text = request.form['text']

#     if not title:
#         flash('You must give your post a title.')
#     elif not tags:
#         flash('You must give your post at least one tag.')
#     elif not text:
#         flash('You must give your post a text body.')
#     else:
#         Person(session['username']).add_post(title, tags, text)

#     return redirect(url_for('index'))


# @app.route('/like_post/<post_id>')
# def like_post(post_id):
#     username = session.get('username')

#     if not username:
#         flash('You must be logged in to like a post.')
#         return redirect(url_for('login'))

#     Person(username).like_post(post_id)

#     flash('Liked post.')
#     return redirect(request.referrer)


############################
#   UTIL AND VALIDATIONS   #
############################
def is_teacher():
    logged_in()
    if session.get('type') != 'teacher':
        abort(403)


def is_student():
    logged_in()
    if session.get('type') != 'student':
        abort(403)


def logged_in():
    if not session.get('username'):
        flash('Você não está logado. Realize login!', 'error')
        abort(401)


def confirm_passwords(password, confirm_password):
    if password == confirm_password:
        return True
    else:
        return False


def get_choices_with_empty_placeholder(list_of_choices):
    choices = [('', '-- Nenhum --')]
    for g in list_of_choices:
        choices.append([g['cs']['id'], g['cs']['title']])
    return choices


def get_difficulty_choices():
    return [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]


def get_right_answer_choices():
    return [('a', 'Alternativa A'), ('b', 'Alternativa B'), ('c', 'Alternativa C'), ('d', 'Alternativa D')]


def get_yes_or_no_choices():
    return [(True, 'Sim'), (False, 'Não')]
