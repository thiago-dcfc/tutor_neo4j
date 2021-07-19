from tutor.models.course_class import CourseClass
from tutor.models.course import Course
from flask import request, session, redirect, url_for, render_template, flash, abort, Blueprint
from tutor.forms import CourseClassForm
from tutor.auth import teacher_only, student_only
from flask_paginate import get_page_parameter
from .pagination import get_skip, get_per_page, default_pagination

bp = Blueprint('course_classes', __name__, url_prefix='/course_classes')


#
# List or Create Course Classes for Teachers
#
@bp.route('/view', methods=['GET', 'POST'])
@teacher_only
def view():
    q = request.args.get('q') if request.args.get('q') else ''
    page = request.args.get(get_page_parameter(), type=int, default=1)

    total = len(list(CourseClass().get_course_classes(session.get('username'), q)))
    users_course_classes = list(CourseClass().get_course_classes_with_pagination(session.get('username'),
                                                                                 get_skip(page), get_per_page(),
                                                                                 q))
    pagination = default_pagination(page, total, q)

    form = CourseClassForm(request.form)
    form.course.choices = get_course_choices(list(Course().get_courses()))
    error = False
    if request.method == 'POST':
        if form.validate():
            if CourseClass().create(form.title.data, session.get('username'), form.course.data):
                flash('Disciplina criada com sucesso.', 'success')
                return redirect(url_for('course_classes.view'))
            flash('Disciplina já existente', 'error')
        error = True
    return render_template('course_class/view.html',
                           course_classes=users_course_classes,
                           form=form,
                           error=error,
                           pagination=pagination)


#
# Edit Course Classes
#
@bp.route('/edit/<cc_identity>', methods=['GET', 'POST'])
@teacher_only
def edit(cc_identity):
    node_course_class = CourseClass().find_by_identity_and_user(cc_identity, session.get('username'))
    if node_course_class:
        course_class = CourseClass(node_course_class)
        form = CourseClassForm(request.form, course_class)
        form.course.choices = get_course_choices(list(Course().get_courses()))

        if request.method == 'GET':
            form.course.data = CourseClass().get_course_of_course_class(cc_identity)
        elif request.method == 'POST':
            if form.validate():
                new_title = form.title.data
                if course_class.title == new_title or CourseClass().edit(cc_identity, new_title,
                                                                         session.get('username'),
                                                                         form.course.data):
                    flash('Disciplina alterada com sucesso.', 'success')
                    return redirect(url_for('course_classes.view'))
                flash('Disciplina já existente', 'error')

        return render_template('course_class/edit.html',
                               course_class=course_class,
                               form=form)
    abort(404)


#
# Delete Course Classes
#
@bp.route('/delete/<cc_identity>', methods=['POST'])
@teacher_only
def delete(cc_identity):
    if not CourseClass().find_no_relationship_course_class_and_subject(cc_identity):
        flash('A Disciplina não pode ser excluída, pois contém assuntos.', 'error')
    elif CourseClass().delete(cc_identity):
        flash('Disciplina excluída com sucesso.', 'success')
    else:
        flash('Ocorreu algum erro ao tentar excluir a disciplina.', 'error')
    return redirect(url_for('course_classes.view'))


#
# List Course Classes for Students
#
@bp.route('/student')
@student_only
def student():
    user = session.get('username')
    student_course_classes = CourseClass().get_student_course_classes(user)
    no_student_course_classes = CourseClass().get_no_student_course_classes(user)

    return render_template('course_class/course_class_student.html',
                           scc=student_course_classes,
                           nscc=no_student_course_classes)


#
# Enrollment on Course Classes
#
@bp.route('/enrollment/<course_class>')
@student_only
def enrollment(course_class):
    user = session.get('username')
    if not CourseClass().enrollment(course_class, user):
        flash('Erro ao matricular-se Disciplina', 'error')
    else:
        flash('Matrícula realizada com sucesso.', 'success')

    return redirect(url_for('course_classes.student',
                            user=user))


def get_course_choices(list_of_choices):
    choices = []
    for g in list_of_choices:
        choices.append([g['c']['id'], g['c']['name']])
    return choices
