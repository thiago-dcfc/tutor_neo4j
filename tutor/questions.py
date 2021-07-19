from tutor.models.course_class import CourseClass
from tutor.models.class_subject import ClassSubject
from tutor.models.question import Question
from tutor.models.answer import Answer
from flask import request, session, redirect, url_for, render_template, flash, abort, Blueprint
from tutor.forms import QuestionForm
from tutor.auth import teacher_only, student_only
from flask_paginate import get_page_parameter
from .pagination import get_skip, get_per_page, default_pagination

bp = Blueprint('questions', __name__, url_prefix='/questions')


#
# List or Create Questions
#
@bp.route('/view/<cc_identity>/<cs_identity>', methods=['GET', 'POST'])
@teacher_only
def view(cc_identity, cs_identity):
    q = request.args.get('q') if request.args.get('q') else ''
    page = request.args.get(get_page_parameter(), type=int, default=1)

    course_class = CourseClass().find_by_identity_and_user(cc_identity, session.get('username'))
    class_subject = ClassSubject().find_in_course(cc_identity, cs_identity)
    if course_class and class_subject:
        total = len(list(Question().get_questions(cc_identity, cs_identity, q)))
        all_questions = list(Question().get_questions_with_pagination(cc_identity, cs_identity,
                                                                      get_skip(page), get_per_page(), q))
        pagination = default_pagination(page, total, q)

        form = QuestionForm(request.form)
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
                    return redirect(url_for('questions.view',
                                            cc_identity=cc_identity,
                                            cs_identity=cs_identity))
                flash('Erro ao cadastrar questão', 'error')
            error = True
        return render_template('question/view.html',
                               course_class=course_class,
                               class_subject=class_subject,
                               questions=all_questions,
                               form=form,
                               error=error,
                               pagination=pagination)
    abort(404)


#
# Edit Questions
#
@bp.route('/edit/<cc_identity>/<cs_identity>/<question_identity>', methods=['GET', 'POST'])
@teacher_only
def edit(cc_identity, cs_identity, question_identity):
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
                    return redirect(url_for('questions.view',
                                            cc_identity=cc_identity,
                                            cs_identity=cs_identity,
                                            question_identity=question_identity))
                flash('Erro ao alterar questão.', 'error')
        return render_template('question/edit.html',
                               course_class=course_class,
                               class_subject=class_subject,
                               question=question,
                               form=form)
    abort(404)


#
# Delete Questions
#
@bp.route('/delete/<cc_identity>/<cs_identity>/<question_identity>', methods=['POST'])
@teacher_only
def delete(cc_identity, cs_identity, question_identity):
    course_class = CourseClass().find_by_identity_and_user(cc_identity, session.get('username'))
    class_subject = ClassSubject().find_in_course(cc_identity, cs_identity)
    if course_class and class_subject and Question().delete(question_identity):
        flash('Questão excluida com sucesso.', 'success')
    else:
        flash('Erro ao excluir questão.', 'error')

    return redirect(url_for('questions.view',
                            cc_identity=cc_identity,
                            cs_identity=cs_identity))


@bp.route('/answer/<cc_identity>')
@student_only
def answer(cc_identity):
    user = session.get('username')
    question = Question().get_current_question(cc_identity, user).evaluate()
    cs_title = ClassSubject().get_class_subject_current_question(cc_identity, user).evaluate()

    return render_template('question/answer_question.html',
                           cc_identity=cc_identity,
                           cs_title=cs_title,
                           question=question,
                           user=user)


@bp.route('/answer_question', methods=['GET', 'POST'])
@student_only
def answer_question():
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

        return render_template('question/alert_question_answered.html',
                               cs_title=cs_title,
                               title=title,
                               body=body,
                               support_material=support_material,
                               username=user)


def get_difficulty_choices():
    return [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]


def get_right_answer_choices():
    return [('a', 'Alternativa A'), ('b', 'Alternativa B'), ('c', 'Alternativa C'), ('d', 'Alternativa D')]
