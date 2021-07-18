from flask import Blueprint
import os
from bcrypt import hashpw, gensalt
from tutor.models import Person

seeds_blueprint = Blueprint('seed', __name__)


@seeds_blueprint.cli.command('seed_db')
def seed_db():
    """
    Seeds the Neo4j database with important data
    """
    if os.environ['FLASK_ENV'] == 'development':
        password = hashpw('123456'.encode('utf-8'), gensalt()).decode('utf-8')
        Person('admin').register('Administrator', password, 'admin@admin.com', 'admin', 'Administrator')
        Person('teacher').register('Teacher', password, 'teacher@teacher.com', 'teacher', 'Teacher')
        Person('student').register('Student', password, 'student@student.com', 'admin')
