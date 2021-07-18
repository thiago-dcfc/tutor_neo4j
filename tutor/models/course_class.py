import uuid

from py2neo import Node, Relationship
from datetime import datetime
from tutor.models.db import matcher, graph
from tutor.models.person import Person


class CourseClass:
    def __init__(self, node_course_class=None):
        if node_course_class:
            self.id = node_course_class['id']
            self.title = node_course_class['title']

    def find(self, title):
        return matcher.match("CourseClass", title=title).first()

    def find_by_identity(self, identity):
        return matcher.match("CourseClass", id=identity).first()

    def find_by_identity_and_user(self, identity, user):
        query = '''
                MATCH (p:Person {username: $user})-[r:CREATED]->(cc:CourseClass {id: $identity})
                RETURN cc
                '''
        return graph.run(query, user=user, identity=identity).evaluate()

    def find_by_user(self, title, user):
        query = '''
                MATCH (p:Person {username: $user})-[r:CREATED]->(cc:CourseClass {title: $title})
                RETURN cc
                '''
        return graph.run(query, user=user, title=title).evaluate()

    def create(self, title, username):
        if not self.find_by_user(title, username):
            user = Person(username).find()
            cc = Node("CourseClass", title=title, id=str(uuid.uuid1()))
            graph.create(cc)
            graph.merge(Relationship(user, 'CREATED', cc))
            return True
        return False

    def edit(self, identity, title, user):
        if not self.find_by_user(title, user):
            query = '''
                    MATCH (cc:CourseClass {id: $identity})<--(p:Person {username: $user})
                    SET cc.title = $title
                    RETURN cc
                    '''
            graph.run(query, identity=identity, title=title, user=user)
            return True
        return False

    def delete(self, identity):
        if self.find_by_identity(identity):
            cc = matcher.match("CourseClass", id=identity).first()
            graph.delete(cc)
            return True
        return False

    # Matricula o aluno em uma disciplina
    def enrollment(self, title, user):
        username = Person(user).find()

        if self.find(title):
            return True
        return False

    def get_student_course_classes(self, user):
        query = '''
                MATCH (p:Person {username: $user})-->()-->()-->()-->(cc:CourseClass)
                RETURN cc
                ORDER BY cc.title
                '''
        return list(graph.run(query, user=user))

    def get_no_student_course_classes(self, user):
        query = '''
                MATCH (p:Person {username: $user})
                OPTIONAL MATCH (cc:CourseClass)
                WHERE NOT (p)-->()-->()-->()-->(cc)
                RETURN cc
                ORDER BY cc.title
                '''
        return list(graph.run(query, user=user))

    def get_course_classes(self, user):
        query = '''
                MATCH (cc:CourseClass)<-[r:CREATED]-(p:Person)
                WHERE p.username = $user
                RETURN cc
                ORDER BY cc.title
                '''
        return graph.run(query, user=user)

    # método que verifica se a disciplina não tem nenhum relacionamento com outro assunto
    def find_no_relationship_course_class_and_subject(self, identity):
        query = '''
                 MATCH (cc:CourseClass {id: $identity})
                 WHERE NOT (cc:CourseClass)<-->(:ClassSubject)
                 RETURN cc
                 '''
        return graph.run(query, identity=identity).evaluate()


def date():
    return datetime.now().strftime('%Y-%m-%d')
