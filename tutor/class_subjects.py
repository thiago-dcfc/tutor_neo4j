from tutor.models.class_subject import ClassSubject
from tutor.models.course_class import CourseClass
from flask import request, session, redirect, url_for, render_template, flash, abort, Blueprint
from tutor.forms import ClassSubjectForm
from tutor.auth import teacher_only
from flask_paginate import get_page_parameter
from .pagination import get_skip, get_per_page, default_pagination

bp = Blueprint('class_subjects', __name__, url_prefix='/class_subjects')


#
# List or Create Class Subjects
#
@bp.route('/view/<cc_identity>', methods=['GET', 'POST'])
@teacher_only
def view(cc_identity):
    q = request.args.get('q') if request.args.get('q') else ''
    page = request.args.get(get_page_parameter(), type=int, default=1)

    course_class = CourseClass().find_by_identity_and_user(cc_identity, session.get('username'))
    if course_class:
        total = len(list(ClassSubject().get_class_subjects_with_previous_and_forward(cc_identity, q)))
        course_class_subjects = list(
            ClassSubject().get_class_subjects_with_previous_and_forward_with_pagination(cc_identity,
                                                                                        get_skip(page),
                                                                                        get_per_page(), q))
        pagination = default_pagination(page, total, q)

        form = ClassSubjectForm(request.form)
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
                    return redirect(url_for('class_subjects.view',
                                            cc_identity=cc_identity))
                flash('Assunto já existente', 'error')
            error = True
        return render_template('class_subject/view.html',
                               course_class=course_class,
                               class_subjects=course_class_subjects,
                               form=form,
                               error=error,
                               pagination=pagination)
    abort(404)


#
# Edit Class Subjects
#
@bp.route('/edit/<cc_identity>/<cs_identity>', methods=['GET', 'POST'])
@teacher_only
def edit(cc_identity, cs_identity):
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
                    return redirect(url_for('class_subjects.view',
                                            cc_identity=cc_identity))
                flash('Erro ao alterar assunto', 'error')
        return render_template('class_subject/edit.html',
                               course_class=course_class,
                               class_subject=class_subject,
                               form=form)
    abort(404)


#
# Delete Class Subjects
#
@bp.route('/delete/<cc_identity>/<cs_identity>', methods=['POST'])
@teacher_only
def delete(cc_identity, cs_identity):
    if ClassSubject().get_initial_value(cc_identity, cs_identity) == 'True' \
            and int(ClassSubject().find_node_count(cc_identity)) > 1:
        flash('Assunto não pode ser excluído, pois é o assunto inicial.', 'error')
    elif ClassSubject().find_class_subject_has_questions(cc_identity, cs_identity):
        flash('Assunto não pode ser excluído, pois possui questões.', 'error')
    elif ClassSubject().delete(cc_identity, cs_identity):
        flash('Assunto excluído com sucesso.', 'success')
    else:
        flash('Ocorreu algum erro ao tentar excluir o assunto.', 'error')
    return redirect(url_for('class_subjects.view',
                            cc_identity=cc_identity))


def get_choices_with_empty_placeholder(list_of_choices):
    choices = [('', '-- Nenhum --')]
    for g in list_of_choices:
        choices.append([g['cs']['id'], g['cs']['title']])
    return choices


def get_yes_or_no_choices():
    return [(True, 'Sim'), (False, 'Não')]
