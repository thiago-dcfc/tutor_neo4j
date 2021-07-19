from flask import request, session, redirect, url_for, render_template, flash, abort, Blueprint
from tutor.forms import CourseForm
from tutor.auth import admin_only
from tutor.models.course import Course
from flask_paginate import get_page_parameter
from .pagination import get_skip, get_per_page, default_pagination

bp = Blueprint('courses', __name__, url_prefix='/courses')


#
# List or Create Courses
#
@bp.route('/view', methods=['GET', 'POST'])
@admin_only
def view():
    q = request.args.get('q') if request.args.get('q') else ''
    page = request.args.get(get_page_parameter(), type=int, default=1)

    form = CourseForm(request.form)
    total = len(list(Course().get_courses(q)))
    courses = list(Course().get_courses_with_pagination(get_skip(page), get_per_page(), q))

    pagination = default_pagination(page, total, q)
    error = False
    if request.method == 'POST':
        if form.validate():
            if Course().create(form.name.data, form.initials.data):
                flash('Curso criado com sucesso.', 'success')
                return redirect(url_for('courses.view'))
            flash('Disciplina já existente', 'error')
        error = True
    return render_template('course/view.html',
                           courses=courses,
                           form=form,
                           error=error,
                           pagination=pagination)


#
# Edit Course Classes
#
@bp.route('/edit/<c_identity>', methods=['GET', 'POST'])
@admin_only
def edit(c_identity):
    node_course = Course().find(c_identity)
    if node_course:
        course = Course(node_course)
        form = CourseForm(request.form, course)

        if request.method == 'POST':
            if form.validate():
                if Course().edit(c_identity, form.name.data, form.initials.data):
                    flash('Curso alterado com sucesso.', 'success')
                    return redirect(url_for('courses.view'))
                flash('Curso já existente', 'error')

        return render_template('course/edit.html',
                               course=course,
                               form=form)
    abort(404)


#
# Delete Course Classes
#
@bp.route('/delete/<c_identity>', methods=['POST'])
@admin_only
def delete(c_identity):
    if not Course().find_no_relationship_course_and_course_classes(c_identity):
        flash('O curso não pode ser excluída, pois contém disciplinas.', 'error')
    elif Course().delete(c_identity):
        flash('Curso excluído com sucesso.', 'success')
    else:
        flash('Ocorreu algum erro ao tentar excluir o curso.', 'error')
    return redirect(url_for('courses.view'))
