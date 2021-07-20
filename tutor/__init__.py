from flask import Flask, redirect, url_for, render_template, session
from os import urandom
from commands import seeds_blueprint
from tutor import auth, profile, course_classes, class_subjects, questions, routes, courses


def create_app():
    app = Flask(__name__)
    app.secret_key = urandom(24)

    # session['username'] = 'sirlon'
    # session['person_name'] = 'Sirlon'
    # session['email'] = 'sirlon@sirlon.com'
    # session['type'] = 'teacher'

    app.register_blueprint(seeds_blueprint)
    app.register_blueprint(routes.bp)
    app.register_blueprint(auth.bp)
    app.register_blueprint(profile.bp)
    app.register_blueprint(course_classes.bp)
    app.register_blueprint(class_subjects.bp)
    app.register_blueprint(questions.bp)
    app.register_blueprint(courses.bp)

    @app.errorhandler(404)
    def not_found(error):
        if not session.get('username'):
            return redirect(url_for('index'))
        return render_template('error/404.html'), 404

    @app.errorhandler(401)
    def unauthorized(error):
        return redirect(url_for('auth.login'))

    @app.errorhandler(403)
    def forbidden(error):
        return redirect(url_for('index'))

    @app.errorhandler(405)
    def method_not_allowed(error):
        return redirect(url_for('index'))

    return app
