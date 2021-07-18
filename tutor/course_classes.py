from tutor.models.course_class import CourseClass
from flask import request, session, redirect, url_for, render_template, flash, abort, Blueprint
from tutor.forms import CourseClassForm
from tutor.auth import teacher_only

bp = Blueprint('course_classes', __name__, url_prefix='/course_classes')


#
# List or Create Course Classes for Teachers
#
@bp.route('/view', methods=['GET', 'POST'])
@teacher_only
def view():
    form = CourseClassForm(request.form)
    users_course_classes = list(CourseClass().get_course_classes(session.get('username')))
    error = False
    if request.method == 'POST':
        title = form.title.data
        if form.validate():
            if CourseClass().create(title, session.get('username')):
                flash('Disciplina criada com sucesso.', 'success')
                return redirect(url_for('course_classes.view'))
            flash('Disciplina já existente', 'error')
        error = True
    return render_template('course_class/view.html',
                           course_classes=users_course_classes,
                           form=form,
                           error=error)


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

        if request.method == 'POST':
            if form.validate():
                new_title = form.title.data
                if course_class.title == new_title or CourseClass().edit(cc_identity, new_title,
                                                                         session.get('username')):
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
def student():
    # is_student()

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
def enrollment(course_class):
    # is_student()

    user = session.get('username')
    if not CourseClass().enrollment(course_class, user):
        flash('Erro ao matricular-se Disciplina', 'error')
    else:
        flash('Matrícula realizada com sucesso.', 'success')

    return redirect(url_for('course_classes.student',
                            user=user))
