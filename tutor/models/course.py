import uuid
from py2neo import Node, CONTAINS
from tutor.models.db import matcher, graph


class Course:
    def __init__(self, node_course=None):
        if node_course:
            self.id = node_course['id']
            self.name = node_course['name']
            self.initials = node_course['initials']

    def find(self, identity):
        return matcher.match("Course", id=identity).first()

    def find_by_name_and_initials(self, name, initials):
        return matcher.match("Course", name=name, initials=initials).first()

    def find_by_name_and_initials_not_current(self, identity, name, initials):
        query = '''
                MATCH (c:Course)
                WHERE c.name = $name AND c.initials = $initials AND c.id <> $identity
                RETURN c
                ORDER BY c.order
                '''
        return graph.evaluate(query, identity=identity, name=name, initials=initials)

    def get_courses(self, search=''):
        query = '''
                MATCH (c:Course)
                WHERE toLower(c.name) CONTAINS toLower($search)
                RETURN c
                ORDER BY c.name 
                '''
        return graph.run(query, search=search)
        # return matcher.match("Course", name=CONTAINS(search)).order_by('_.name')

    def get_courses_with_pagination(self, skip, limit, search=''):
        query = '''
                        MATCH (c:Course)
                        WHERE toLower(c.name) CONTAINS toLower($search)
                        RETURN c
                        ORDER BY c.name
                        SKIP $skip
                        LIMIT $limit 
                        '''
        return graph.run(query, skip=skip, limit=limit, search=search)
        # return matcher.match("Course", name=CONTAINS(search)).order_by('_.name').skip(skip).limit(limit)

    def find_no_relationship_course_and_course_classes(self, identity):
        query = '''
                 MATCH (c:Course {id: $identity})
                 WHERE NOT (c:Course)<-->(:CourseClass)
                 RETURN c
                 '''
        return graph.run(query, identity=identity).evaluate()

    def create(self, name, initials):
        if not self.find_by_name_and_initials(name, initials):
            cc = Node("Course", name=name, initials=initials, id=str(uuid.uuid1()))
            graph.create(cc)
            return True
        return False

    def edit(self, identity, name, initials):
        if not self.find_by_name_and_initials_not_current(identity, name, initials):
            query = '''
                    MATCH (c:Course {id: $identity})
                    SET c.name = $name, c.initials = $initials
                    RETURN c
                    '''
            graph.run(query, identity=identity, name=name, initials=initials)
            return True
        return False

    def delete(self, identity):
        if self.find(identity):
            course = matcher.match("Course", id=identity).first()
            graph.delete(course)
            return True
        return False
