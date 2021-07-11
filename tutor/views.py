from .models import Person, CourseClass, ClassSubject, Question, Answer
from flask import Flask, request, session, redirect, url_for, render_template, flash
from bcrypt import hashpw, gensalt
from os import urandom

app = Flask(__name__)
app.secret_key = urandom(24)

# TODO #1 editar informações do próprio perfil
# TODO #2 terminar parte da resposta do aluno
# TODO #3 criar cursos. só admin pode criar cursos. disciplinas ligadas a um curso. professor pode estar ligado a vários cursos.
# TODO #4 colocar algo na tela principal do professor. últimas respostas? algum gráfico?
# TODO #5 colocar algo na tela principal do estudante. últimas respostas? perguntas/assuntos que outras pessoas da mesma turma estão respondendo?
# TODO #6 revisar todas as rotas. não deixar entrar nas rotas que não pode.
# TODO #7 papel e funções de administrador. adicionar professores? manipular dados de outras pessoas?

@app.route('/')
def index():
    # session['username'] = 'sirlon'
    # session['type'] = 'teacher'
    return render_template('index.html')


# REGISTRO, LOGIN E LOGOUT #
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        username = request.form['username']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        p_type = "student"
        hashed = hashpw(password.encode('utf-8'), gensalt())

        if not Person(username).confirm_passwords(password, confirm_password):
            flash('As senhas não são iguais', 'error')
        elif Person(username).find():
            flash('Nome de usuário já existente', 'error')
        elif Person(username).register(name, hashed.decode('utf-8'), p_type):
            session['username'] = username
            session['person_name'] = name
            session['type'] = p_type
            flash('Cadastro efetuado com sucesso.', 'success')
            return redirect(url_for('index'))
        
        return render_template('register.html',
                                   name=name,
                                   username=username
                                   )

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
                flash('Login efetuado com sucesso.', 'success')

                # if user['type'] == 'student':
                # chamar funções das duas listas
                # return render_template('index.html, param=param)

                return redirect(url_for('index'))

    return render_template('login.html')


@app.route('/logout')
def logout():
    session.pop('username', None)
    flash('Você saiu do sistema.', 'success')
    return redirect(url_for('index'))


# COURSE CLASS #
@app.route('/enrollment_course_class/<cc>')
def enrollment_course_class(cc):
    if not is_student():
        return redirect(url_for('login'))

    user = session.get('username')
    if not CourseClass().enrollment(cc, user):
        flash('Erro ao matricular-se Disciplina', 'error')
    else:
        flash('Matrícula realizada com sucesso.', 'success')

    return redirect(url_for('open_course_class_student',
                            user=user))


@app.route('/edit_course_class', methods=['GET', 'POST'])
def edit_course_class():
    if not is_teacher():
        return redirect(url_for('login'))

    if request.method == 'POST':
        cc = request.form['cc']
        title = request.form['new_title']

        if cc == title:
            flash('Disciplina alterada com sucesso.', 'success')
        elif not CourseClass().edit(title, cc, session.get('username')):
            flash('Disciplina já existente', 'error')
            return render_template(
                'edit_course_class.html',
                cc=cc
            )
        else:
            flash('Disciplina alterada com sucesso.', 'success')

    course_classes = list(CourseClass().get_course_classes(session.get('username')))
    return render_template(
        'course_class.html',
        cc=course_classes
    )


@app.route('/open_edit_course_class/<title>')
def open_edit_course_class(title):
    if not is_teacher():
        return redirect(url_for('login'))

    return render_template(
        'edit_course_class.html',
        cc=title
    )


@app.route('/open_course_class')
def open_course_class():
    if not is_teacher():
        return redirect(url_for('login'))

    course_classes = list(CourseClass().get_course_classes(session.get('username')))
    return render_template(
        'course_class.html',
        cc=course_classes
    )


@app.route('/open_course_class_student')
def open_course_class_student():
    if not is_student():
        return redirect(url_for('login'))

    user = session.get('username')
    student_course_classes = CourseClass().get_student_course_classes(user)
    no_student_course_classes = CourseClass().get_no_student_course_classes(user)

    return render_template(
        'course_class_student.html',
        scc=student_course_classes,
        nscc=no_student_course_classes
    )


@app.route('/create_course_class', methods=['GET', 'POST'])
def create_course_class():
    if not is_teacher():
        return redirect(url_for('login'))

    if request.method == 'POST':
        title = request.form['title']
        username = session.get('username')

        if len(title) < 1:
            flash('A Disciplina deve possuir pelo menos 1 caractere', 'error')
        elif not CourseClass().create(title, username):
            flash('Disciplina já existente', 'error')
        else:
            flash('Disciplina criada com sucesso.', 'success')

    return redirect(request.referrer)


@app.route('/confirm_delete_course_class/<title>')
def confirm_delete_course_class(title):
    if not is_teacher():
        return redirect(url_for('login'))

    return render_template(
        'confirm_delete_course_class.html',
        cc=title
    )


@app.route('/delete_course_class/<title>', methods=['GET', 'POST'])
def delete_course_class(title):
    if not is_teacher():
        return redirect(url_for('login'))

    if not CourseClass().find_single_course_class(title):
        flash('A Disciplina contém assunto, não pode ser excluida.', 'error')
    else:
        CourseClass().delete(title)
        flash('Disciplina excluida com sucesso.', 'success')

    course_classes = list(CourseClass().get_course_classes(session.get('username')))
    return render_template(
        'course_class.html',
        cc=course_classes
    )

# CLASS SUBJECT #
@app.route('/edit_class_subject/', methods=['GET', 'POST'])
def edit_class_subject():
    if not is_teacher():
        return redirect(url_for('login'))

    if request.method == 'POST':
        cc = request.form['cc']
        title = request.form['title']
        st = request.form['subject_title']
        ps = request.form['previous_subject']
        ns = request.form['next_subject']
        sm = request.form['support_material']
        cb = request.form['checkbox_initial']

        if not ClassSubject().edit(st, title, cc, ps, ns, sm, cb):
            flash('Erro ao alterar assunto', 'error')
        else:
            flash('Assunto alterado com sucesso.', 'success')

    return redirect(url_for('open_class_subject', title=cc))


@app.route('/open_edit_class_subject/<cc>/<title>')
def open_edit_class_subject(cc, title):
    if not is_teacher():
        return redirect(url_for('login'))

    class_subjects = list(ClassSubject().get_class_subjects_and_course_class_except_current_subject(cc, title))

    cs = ClassSubject().find_in_course(cc, title)
    ini = ClassSubject().get_initial_value(title, cc)

    ps = ClassSubject().find_previous(title, cc)
    ns = ClassSubject().find_next(title, cc)

    return render_template(
        'edit_class_subject.html',
        cc=cc,
        title=title,
        ps=ps,
        ns=ns,
        cs=class_subjects,
        support_material=cs.evaluate()["support_material"],
        initial=ini
    )


@app.route('/open_class_subject/<title>', methods=['GET', 'POST'])
def open_class_subject(title):
    if not is_teacher():
        return redirect(url_for('login'))

    class_subjects = list(ClassSubject().get_class_subjects_with_previous_and_forward(title))

    return render_template(
        'class_subject.html',
        cc=title,
        cs=class_subjects
    )


@app.route('/confirm_delete_class_subject/<cc_title>/<cs_title>')
def confirm_delete_class_subject(cc_title, cs_title):
    if not is_teacher():
        return redirect(url_for('login'))

    flash('Tem certeza de deseja excluir esse assunto?', 'warning')

    return render_template(
        'confirm_delete_class_subject.html',
        cc=cc_title,
        cs=cs_title
    )


@app.route('/delete_class_subject/<cc_title>/<cs_title>', methods=['GET', 'POST'])
def delete_class_subject(cc_title, cs_title):
    if not is_teacher():
        return redirect(url_for('login'))

    if not ClassSubject().find_single_class_subject(cs_title, cc_title):
        flash('Assunto possui questões, não pode ser excluído.', 'error')
    elif not ClassSubject().get_initial_value(cs_title, cc_title):
        flash('Assunto inicial, não pode ser excluído.', 'error')
    else:
        ClassSubject().delete(cs_title, cc_title)
        flash('Assunto excluído com sucesso.', 'success')

    return redirect(url_for('open_class_subject', title=cc_title))


@app.route('/create_class_subject', methods=['GET', 'POST'])
def create_class_subject():
    if not is_teacher():
        return redirect(url_for('login'))

    if request.method == 'POST':
        title = request.form['subject_title']
        cc = request.form['cc']
        support_material = request.form['support_material']
        ps = request.form.get('previous_subject')
        ns = request.form.get('next_subject')

        if len(title) < 1:
            flash('O assunto deve possuir pelo menos 1 caractere', 'error')
        elif not ClassSubject().create(cc, title, ps, ns, support_material):
            flash('Assunto já existente', 'error')
        else:
            flash('Assunto criado com sucesso.', 'success')

    return redirect(request.referrer)


# QUESTIONS #
@app.route('/edit_question/<cc>/<cs>/<question_id>', methods=['GET', 'POST'])
def edit_question(cc, cs, question_id):
    if not is_teacher():
        return redirect(url_for('login'))

    if request.method == 'POST':
        title = request.form['question_title']
        body = request.form['question_body']
        support_material = request.form['support_material']
        difficulty = request.form['difficulty']
        choice_a = request.form['choice_a']
        choice_b = request.form['choice_b']
        choice_c = request.form['choice_c']
        choice_d = request.form['choice_d']
        right_answer = request.form['right_answer']

        if len(title) < 1:
            flash('O título da questão deve possuir pelo menos 1 caractere', 'error')
            return redirect(url_for('open_edit_questions', question_id=question_id, cs_title=cs, cc_title=cc))

        else:
            Question().edit(question_id, title, body, support_material, difficulty, choice_a, choice_b, choice_c,
                            choice_d, right_answer)
            flash('Questão alterado com sucesso.', 'success')
            return redirect(url_for('open_questions', cs_title=cs, cc_title=cc))



@app.route('/open_edit_questions/<cc_title>/<cs_title>/<question_id>')
def open_edit_questions(cc_title, cs_title, question_id):
    if not is_teacher():
        return redirect(url_for('login'))

    question = Question().get_question(question_id).evaluate()

    return render_template(
        'edit_question.html',
        cc=cc_title,
        cs=cs_title,
        q=question
    )


@app.route('/open_answer_questions/<cc_title>')
def open_answer_questions(cc_title):
    if not is_student():
        return redirect(url_for('login'))

    user = session.get('username')
    question = Question().get_current_question(cc_title, user).evaluate()
    cs_title = ClassSubject().get_class_subject_current_question(cc_title, user).evaluate()

    return render_template(
        'answer_question.html',
        cc=cc_title,
        cs=cs_title,
        q=question,
        username=user
    )


@app.route('/answer_question', methods=['GET', 'POST'])
def answer_question():
    if not is_student():
        return redirect(url_for('login'))

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

    return render_template(
        'alert_question_answered.html',
        cs_title=cs_title,
        title=title,
        body=body,
        support_material=support_material,
        username=user
    )


@app.route('/open_questions/<cc_title>/<cs_title>', methods=['GET', 'POST'])
def open_questions(cc_title, cs_title):
    if not is_teacher():
        return redirect(url_for('login'))

    questions = list(Question().get_questions(cs_title, cc_title))

    return render_template(
        'question.html',
        cs=cs_title,
        cc=cc_title,
        q=questions
    )


@app.route('/create_question', methods=['GET', 'POST'])
def create_question():
    if not is_teacher():
        return redirect(url_for('login'))

    if request.method == 'POST':
        cs = request.form['cs']
        cc = request.form['cc']
        title = request.form['question_title']
        body = request.form['question_body']
        support_material = request.form['support_material']
        difficulty = request.form['difficulty']
        choice_a = request.form['choice_a']
        choice_b = request.form['choice_b']
        choice_c = request.form['choice_c']
        choice_d = request.form['choice_d']
        right_answer = request.form['right_answer']

        if len(title) < 1:
            flash('O título deve possuir pelo menos 1 caractere', 'error')
        elif len(body) < 1:
            flash('O enuciado deve possuir pelo menos 1 caractere', 'error')
        elif len(choice_a) < 1:
            flash('A alternativa A deve possuir pelo menos 1 caractere', 'error')
        elif not Question().create(cc, cs, title, body, support_material, difficulty, choice_a, choice_b, choice_c,
                                   choice_d, right_answer,
                                   session["username"]):
            flash('Erro ao cadastrar questão', 'error')
        else:
            flash('Questão criada com sucesso.', 'success')

    return redirect(request.referrer)


@app.route('/confirm_delete_question/<cc>/<cs>/<id>')
def confirm_delete_question(cc, cs, id):
    if not is_teacher():
        return redirect(url_for('login'))

    flash('Tem certeza que deseja excluir essa questão?', 'warning')

    return render_template(
        'confirm_delete_question.html',
        id=id,
        cc=cc,
        cs=cs
    )


@app.route('/delete_question/<cc>/<cs>/<id>')
def delete_question(cc, cs, id):
    if not is_teacher():
        return redirect(url_for('login'))

    Question().delete(id)
    flash('Questão excluida com sucesso.', 'success')

    return redirect(url_for('open_questions', cs_title=cs, cc_title=cc))


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


@app.route('/profile/<username>')
def profile(username):
    logged_in_username = session.get('username')
    user_being_viewed_username = username

    user_being_viewed = Person(user_being_viewed_username)
    posts = user_being_viewed.get_recent_posts()

    similar = []
    common = []

    if logged_in_username:
        logged_in_user = Person(logged_in_username)

        if logged_in_user.username == user_being_viewed.username:
            similar = logged_in_user.get_similar_users()
        else:
            common = logged_in_user.get_commonality_of_user(user_being_viewed)

    return render_template(
        'profile.html',
        username=username,
        posts=posts,
        similar=similar,
        common=common
    )

# VERIFICA USUARIO #
def is_teacher():
    if not logged_in():
        return False

    if session.get('type') != 'teacher':
        flash('Você não está logado como professor.', 'error')
        return False
    
    return True
        

def is_student():
    if not logged_in():
        return False
    
    if session.get('type') != 'student':
        flash('Você não está logado como aluno.', 'error')
        return False

    return True

def logged_in():
    if not session.get('username'):
        flash('Você não está logado. Realize login!', 'error')
        return False
    return True