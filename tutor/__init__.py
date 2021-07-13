from flask import Flask, render_template, redirect, url_for, session
from .views import app
# from .models import graph


@app.errorhandler(404)
def not_found(error):
    if not session.get('username'):
        return redirect(url_for('index'))
    return render_template('404.html'), 404


@app.errorhandler(401)
def unauthorized(error):
    return redirect(url_for('login'))


@app.errorhandler(403)
def forbidden(error):
    return redirect(url_for('index'))


@app.errorhandler(405)
def method_not_allowed(error):
    return redirect(url_for('index'))
# graph.schema.create_uniqueness_constraint("Person", "username")
# graph.schema.create_uniqueness_constraint("Subject", "title")
# graph.schema.create_uniqueness_constraint("Post", "id")
