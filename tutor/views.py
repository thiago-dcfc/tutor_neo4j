from .models import Person, CourseClass, ClassSubject, Question, Answer
from flask import Flask, request, session, redirect, url_for, render_template, flash, abort
from bcrypt import hashpw, gensalt
from os import urandom

app = Flask(__name__)
app.secret_key = urandom(24)


# TODO #0 validar email no registro e alteração do perfil
# TODO #1 terminar parte do aluno
# TODO #2 o que vai ter no Ver Perfil?
# TODO #3 criar cursos. só admin pode criar cursos. disciplinas ligadas a um curso. professor pode estar ligado a vários cursos.
# TODO #4 limpar código. retirar funções legadas do exemplo
# TODO #5 colocar algo na tela principal do professor. últimas respostas? algum gráfico?
# TODO #6 colocar algo na tela principal do estudante. últimas respostas? perguntas/assuntos que outras pessoas da mesma turma estão respondendo?
# TODO #7 revisar todas as rotas. não deixar entrar nas rotas que não pode.
# TODO #8 papel e funções de administrador. adicionar professores? manipular dados de outras pessoas?
# TODO #9 dockerizar


@app.route('/')
def index():
    # session['username'] = 'sirlon'
    # session['person_name'] = 'Sirlon'
    # session['email'] = 'sirlon@sirlon.com'
    # session['type'] = 'teacher'
    return render_template('index.html')


################################
#   REGISTER, LOGIN E LOGOUT   #
################################
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        p_type = "student"
        hashed = hashpw(password.encode('utf-8'), gensalt())

        if not confirm_passwords(password, confirm_password):
            flash('As senhas não são iguais', 'error')
        elif Person(username).find():
            flash('Nome de usuário já existente', 'error')
        elif Person(username).register(name, hashed.decode('utf-8'), email, p_type):
            session['username'] = username
            session['person_name'] = name
            session['email'] = email
            session['type'] = p_type
            flash('Cadastro efetuado com sucesso.', 'success')
            return redirect(url_for('index'))

        return render_template('register.html',
                               name=name,
                               username=username)

    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if not username or not password:
            flash('Nome de usuário e senha devem ser preenchidos', 'error')
        else:
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

    return render_template('login.html')


@app.route('/logout', methods=['GET'])
def logout():
    if session:
        session.pop('username', None)
        session.clear()
        flash('Você saiu do sistema.', 'success')
    return redirect(url_for('index'))


#
# User's Profile
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

            return render_template('profile.html', user=user, classes=classes)
    else:
        return render_template('profile.html', user=user)

    return render_template('profile.html', user=user)


@app.route('/edit_profile', methods=['GET', 'POST'])
def edit_profile():
    logged_in()

    user = Person(session.get('username')).find()
    if request.method == 'GET':
        return render_template('edit_profile.html',
                               name=user['name'],
                               username=user['username'],
                               email=user['email'])
    elif request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        if password:
            if confirm_passwords(password, confirm_password):
                hashed = hashpw(password.encode('utf-8'), gensalt())
                if not Person(session.get('username')).change_password(hashed.decode('utf-8')):
                    flash('Erro ao alterar a senha', 'error')
                    return render_template('edit_profile.html',
                                           name=name,
                                           username=user['username'],
                                           email=email)
            else:
                flash('As senhas não são iguais', 'error')
                return render_template('edit_profile.html',
                                       name=name,
                                       username=user['username'],
                                       email=email)

        if Person(session.get('username')).edit_personal_data(name, email):
            session['person_name'] = name
            session['email'] = email
            flash('Dados alterados com sucesso', 'success')
        else:
            flash('Erro ao alterar os dados', 'error')
            return render_template('edit_profile.html',
                                   name=name,
                                   username=user['username'],
                                   email=email)

        return redirect(url_for('edit_profile'))


####################
#   COURSE CLASS   #
####################

#
# List and Create Course Classes for Teachers
#
@app.route('/course_classes', methods=['GET', 'POST'])
def course_classes():
    is_teacher()

    if request.method == 'GET':
        users_course_classes = list(CourseClass().get_course_classes(session.get('username')))
        return render_template(
            'course_class.html',
            course_classes=users_course_classes
        )
    elif request.method == 'POST':
        title = request.form['title']
        username = session.get('username')

        if len(title) < 1:
            flash('A Disciplina deve possuir pelo menos 1 caractere', 'error')
        elif CourseClass().create(title, username):
            flash('Disciplina criada com sucesso.', 'success')
        else:
            flash('Disciplina já existente', 'error')

        return redirect(request.referrer)


#
# Edit Course Classes
#
@app.route('/edit_course_class/<cc_identity>', methods=['GET', 'POST'])
def edit_course_class(cc_identity):
    is_teacher()

    course_class = CourseClass().find_by_identity_and_user(cc_identity, session.get('username'))
    if course_class:
        if request.method == 'GET':
            return render_template('edit_course_class.html', course_class=course_class)
        elif request.method == 'POST':
            new_title = request.form['new_title']

            if course_class['title'] == new_title or CourseClass().edit(cc_identity, new_title,
                                                                        session.get('username')):
                flash('Disciplina alterada com sucesso.', 'success')
                return redirect(url_for('course_classes'))
            else:
                flash('Disciplina já existente', 'error')
                return render_template('edit_course_class.html', course_class=course_class)
    abort(404)


#
# Delete Course Classes
#
@app.route('/delete_course_class/<cc_identity>', methods=['POST'])
def delete_course_class(cc_identity):
    is_teacher()

    if not CourseClass().find_no_relationship_course_class_and_subject(cc_identity):
        flash('A Disciplina não pode ser excluída, pois contém assuntos.', 'error')
    else:
        if CourseClass().delete(cc_identity):
            flash('Disciplina excluída com sucesso.', 'success')
        else:
            flash('Ocorreu algum erro ao tentar excluir a disciplina.', 'success')

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

    return redirect(url_for('open_course_class_student', user=user))


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
        if request.method == 'GET':
            course_class_subjects = list(ClassSubject().get_class_subjects_with_previous_and_forward(cc_identity))

            return render_template('class_subject.html',
                                   course_class=course_class,
                                   class_subjects=course_class_subjects)
        elif request.method == 'POST':
            subject_title = request.form['subject_title']
            support_material = request.form['support_material']
            previous_subject = request.form.get('previous_subject')
            next_subject = request.form.get('next_subject')

            if len(subject_title) < 1:
                flash('O assunto deve possuir pelo menos 1 caractere', 'error')
            elif ClassSubject().create(cc_identity, subject_title, previous_subject, next_subject, support_material):
                flash('Assunto criado com sucesso.', 'success')
            else:
                flash('Assunto já existente', 'error')

            return redirect(request.referrer)
    abort(404)


#
# Edit Class Subjects
#
@app.route('/edit_class_subject/<cc_identity>/<cs_identity>', methods=['GET', 'POST'])
def edit_class_subject(cc_identity, cs_identity):
    is_teacher()

    course_class = CourseClass().find_by_identity_and_user(cc_identity, session.get('username'))
    class_subject = ClassSubject().find_in_course(cc_identity, cs_identity)
    if course_class and class_subject:
        if request.method == 'GET':
            list_subjects = list(ClassSubject().get_class_subjects_and_course_class_except_current_subject(cc_identity,
                                                                                                           cs_identity))
            previous_subject = ClassSubject().find_previous(cc_identity, cs_identity)
            next_subject = ClassSubject().find_next(cc_identity, cs_identity)

            return render_template('edit_class_subject.html',
                                   course_class=course_class,
                                   class_subject=class_subject,
                                   previous_subject=previous_subject,
                                   next_subject=next_subject,
                                   class_subjects=list_subjects)
        elif request.method == 'POST':
            subject_title = request.form['subject_title']
            previous_subject = request.form['previous_subject']
            next_subject = request.form['next_subject']
            support_material = request.form['support_material']
            initial = request.form['checkbox_initial']

            if ClassSubject().edit(cc_identity, cs_identity, subject_title, previous_subject,
                                   next_subject, support_material, initial):
                flash('Assunto alterado com sucesso.', 'success')
            else:
                flash('Erro ao alterar assunto', 'error')

            return redirect(url_for('class_subjects', cc_identity=cc_identity))
    abort(404)


#
# Delete Class Subjects
#
@app.route('/delete_class_subject/<cc_identity>/<cs_identity>', methods=['POST'])
def delete_class_subject(cc_identity, cs_identity):
    is_teacher()

    if not ClassSubject().find_single_class_subject(cc_identity, cs_identity):
        flash('Assunto não pode ser excluído, pois possui questões.', 'error')
    elif not ClassSubject().get_initial_value(cc_identity, cs_identity):
        flash('Assunto não pode ser excluído, pois é o assunto inicial.', 'error')
    else:
        ClassSubject().delete(cc_identity, cs_identity)
        flash('Assunto excluído com sucesso.', 'success')

    return redirect(url_for('class_subjects', cc_identity=cc_identity))


#################
#   QUESTIONS   #
#################

#
# List Questions
#
@app.route('/questions/<cc_identity>/<cs_identity>', methods=['GET', 'POST'])
def questions(cc_identity, cs_identity):
    is_teacher()

    course_class = CourseClass().find_by_identity_and_user(cc_identity, session.get('username'))
    class_subject = ClassSubject().find_in_course(cc_identity, cs_identity)
    if course_class and class_subject:
        if request.method == 'GET':
            all_questions = list(Question().get_questions(cc_identity, cs_identity))

            return render_template('question.html',
                                   course_class=course_class,
                                   class_subject=class_subject,
                                   questions=all_questions)
        elif request.method == 'POST':
            title = request.form['question_title']
            body = request.form['question_body']
            choice_a = request.form['choice_a']

            if len(title) < 1:
                flash('O título deve possuir pelo menos 1 caractere', 'error')
            elif len(body) < 1:
                flash('O enuciado deve possuir pelo menos 1 caractere', 'error')
            elif len(choice_a) < 1:
                flash('A alternativa A deve possuir pelo menos 1 caractere', 'error')
            elif Question().create(cc_identity, cs_identity, title, body,
                                   request.form['support_material'], request.form['difficulty'],
                                   choice_a, request.form['choice_b'],
                                   request.form['choice_c'], request.form['choice_d'],
                                   request.form['right_answer'], session["username"]):
                flash('Questão criada com sucesso.', 'success')
            else:
                flash('Erro ao cadastrar questão', 'error')

            return redirect(request.referrer)
    abort(404)


#
# Edit Questions
#
@app.route('/edit_question/<cc_identity>/<cs_identity>/<question_identity>', methods=['GET', 'POST'])
def edit_question(cc_identity, cs_identity, question_identity):
    is_teacher()

    course_class = CourseClass().find_by_identity_and_user(cc_identity, session.get('username'))
    class_subject = ClassSubject().find_in_course(cc_identity, cs_identity)
    question = Question().get_question(question_identity).evaluate()
    if course_class and class_subject and question:
        if request.method == 'GET':
            return render_template('edit_question.html',
                                   course_class=course_class,
                                   class_subject=class_subject,
                                   question=question)
        elif request.method == 'POST':
            title = request.form['question_title']
            if len(title) < 1:
                flash('O título da questão deve possuir pelo menos 1 caractere', 'error')
                return redirect(url_for('edit_questions', cc_identity=cc_identity,
                                        cs_identity=cs_identity,
                                        question_identity=question_identity))
            else:
                if Question().edit(question_identity, title, request.form['question_body'],
                                   request.form['support_material'], request.form['difficulty'],
                                   request.form['choice_a'], request.form['choice_b'],
                                   request.form['choice_c'], request.form['choice_d'],
                                   request.form['right_answer']):
                    flash('Questão alterada com sucesso.', 'success')
                else:
                    flash('Erro ao alterar questão.', 'error')
                return redirect(url_for('questions', cc_identity=cc_identity,
                                        cs_identity=cs_identity,
                                        question_identity=question_identity))
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

    return redirect(url_for('questions', cc_identity=cc_identity, cs_identity=cs_identity))


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