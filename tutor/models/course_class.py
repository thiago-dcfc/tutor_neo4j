import uuid

from py2neo import Node, Relationship
from datetime import datetime
from tutor.models.db import matcher, graph
from tutor.models.person import Person
from tutor.models.course import Course


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
                MATCH (p:Person {username: $user})-[r:TEACHES]->(cc:CourseClass {id: $identity})
                RETURN cc
                '''
        return graph.run(query, user=user, identity=identity).evaluate()

    def find_by_user(self, title, user, c_identity):
        query = '''
                MATCH (p:Person {username: $user})-[:TEACHES]->(cc:CourseClass {title: $title})-[:BELONGS]->(c:Course {id: $c_identity})
                RETURN cc
                '''
        return graph.run(query, user=user, title=title, c_identity=c_identity).evaluate()

    def create(self, title, username, c_identity):
        if not self.find_by_user(title, username, c_identity):
            user = Person(username).find()
            course = Course().find(c_identity)
            cc = Node("CourseClass", title=title, id=str(uuid.uuid1()))
            graph.create(cc)
            graph.merge(Relationship(user, 'TEACHES', cc))
            graph.merge(Relationship(cc, 'BELONGS', course))
            return True
        return False

    def edit(self, identity, title, user, c_identity):
        if not self.find_by_user(title, user, c_identity):
            query = '''
                    MATCH (cc:CourseClass {id: $identity})<-[r:TEACHES]-(p:Person {username: $user})
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

    def get_course_classes(self, user, search=''):
        query = '''
                MATCH (p:Person)-[:TEACHES]->(cc:CourseClass)-[:BELONGS]->(c:Course)
                WHERE p.username = $user AND toLower(cc.title) CONTAINS toLower($search)
                RETURN cc, c
                ORDER BY c.name, cc.title 
                '''
        return graph.run(query, user=user, search=search)

    def get_course_classes_with_pagination(self, user, skip, limit, search=''):
        query = '''
                MATCH (p:Person)-[:TEACHES]->(cc:CourseClass)-[:BELONGS]->(c:Course)
                WHERE p.username = $user AND toLower(cc.title) CONTAINS toLower($search)
                RETURN cc, c
                ORDER BY c.name, cc.title 
                SKIP $skip
                LIMIT $limit
                '''
        return graph.run(query, user=user, skip=int(skip), limit=int(limit), search=search)

    def get_course_of_course_class(self, cc_identity):
        query = '''
                MATCH (cc:CourseClass)-[r:BELONGS]->(c:Course)
                WHERE cc.id = $cc_identity
                RETURN c.id
                '''
        return graph.evaluate(query, cc_identity=cc_identity)

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
