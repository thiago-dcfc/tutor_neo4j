from flask import Flask, render_template
from .views import app
# from .models import graph

# Sample HTTP error handling
@app.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404

# graph.schema.create_uniqueness_constraint("Person", "username")
# graph.schema.create_uniqueness_constraint("Subject", "title")
# graph.schema.create_uniqueness_constraint("Post", "id")
