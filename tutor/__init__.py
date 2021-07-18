from flask import Flask, render_template, redirect, url_for, session
from .views import app


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
