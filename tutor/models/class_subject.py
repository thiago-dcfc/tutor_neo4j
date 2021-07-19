import uuid

from py2neo import Node, Relationship
from tutor.models.db import graph
from tutor.models.course_class import CourseClass


class ClassSubject:
    def __init__(self, node_class_subject=None):
        if node_class_subject:
            self.id = node_class_subject['id']
            self.title = node_class_subject['title']
            self.support_material = node_class_subject['support_material']
            self.initial = node_class_subject['initial']

    # método que retorna a quantidade de nós ClassSubject
    def find_node_count(self, cc_identity, cs_identity=''):
        query = '''
                MATCH (cc:CourseClass {id: $cc_identity})<-->(cs:ClassSubject)
                OPTIONAL MATCH (cs)<-->(cs {id: $cs_identity})
                RETURN count(cs)
                '''
        return graph.evaluate(query, cc_identity=cc_identity, cs_identity=cs_identity)

    def find_in_course(self, cc_identity, cs_identity):
        query = '''
                MATCH (cs:ClassSubject)-[:TAUGHT]->(cc:CourseClass)
                WHERE cc.id = $cc_identity AND cs.id = $cs_identity
                RETURN cs
                '''
        return graph.run(query, cc_identity=cc_identity, cs_identity=cs_identity).evaluate()

    def find_in_course_by_title(self, cc_identity, title):
        query = '''
                MATCH (cs:ClassSubject)-[:TAUGHT]->(cc:CourseClass)
                WHERE cc.id = $cc_identity AND cs.title = $title
                RETURN cs
                ORDER BY cs.order
                '''
        return graph.run(query, cc_identity=cc_identity, title=title)

    def find_in_course_by_title_not_current(self, cc_identity, title, cs_identity):
        query = '''
                MATCH (cs:ClassSubject)-[:TAUGHT]->(cc:CourseClass)
                WHERE cc.id = $cc_identity AND cs.title = $title AND cs.id <> $cs_identity
                RETURN cs
                ORDER BY cs.order
                '''
        return graph.evaluate(query, cc_identity=cc_identity, title=title, cs_identity=cs_identity)

    # Retorna o valor do campo 'initial' de um Assunto específco
    def get_initial_value(self, cc_identity, cs_identity):
        query = '''
                MATCH (cs:ClassSubject)-[:TAUGHT]->(cc:CourseClass)
                WHERE cc.id = $cc_identity AND cs.id = $cs_identity
                RETURN cs.initial
                '''
        return graph.evaluate(query, cc_identity=cc_identity, cs_identity=cs_identity)

    def get_initial_id(self, cc_title):
        query = '''
                MATCH (cc:CourseClass {title: $cc})<-[:TAUGHT]-(cs:ClassSubject)
                WHERE cs.initial = "True"
                RETURN id(cs)
                '''
        return graph.evaluate(query, cc=cc_title)

    def get_initial(self, title, cc):
        query = '''
                MATCH (cc:CourseClass {title: $cc})<-->(cs:ClassSubject {title: $title})
                WHERE NOT cs.initial = "True"
                RETURN cs
                '''
        return graph.evaluate(query, title=title, cc=cc)

    def find_previous(self, cc_identity, cs_identity):
        query = '''
                MATCH (cc:CourseClass {id:$cc_identity})<-[:TAUGHT]-(cs:ClassSubject {id:$cs_identity})-[:PREVIOUS]->(c:ClassSubject)
                RETURN c.id
                '''
        return graph.evaluate(query, cc_identity=cc_identity, cs_identity=cs_identity)

    def find_next(self, cc_identity, cs_identity):
        query = '''
                MATCH (cc:CourseClass {id:$cc_identity})<-[:TAUGHT]-(cs:ClassSubject {id:$cs_identity})-[:FORWARD]->(c:ClassSubject)
                RETURN c.id
                '''
        return graph.evaluate(query, cc_identity=cc_identity, cs_identity=cs_identity)

    # Retorna o nó de um Assunto através do título do Assunto e do título da Disciplina
    def find_class_subject_has_questions(self, cc_identity, cs_identity):
        query = '''
                MATCH (cc:CourseClass {id: $cc_identity})<-->(cs:ClassSubject {id: $cs_identity})
                WHERE (cs)<-->(:Question)
                RETURN cs
                '''
        return graph.evaluate(query, cc_identity=cc_identity, cs_identity=cs_identity)

    def create(self, cc_identity, title, ps, ns, support_material):
        if not self.find_in_course_by_title(cc_identity, title).evaluate():
            cc = CourseClass().find_by_identity(cc_identity)

            initial = "False"
            if CourseClass().find_no_relationship_course_class_and_subject(cc_identity):
                initial = "True"

            cs = Node("ClassSubject", title=title, initial=initial,
                      support_material=support_material, id=str(uuid.uuid1()))
            graph.create(cs)
            graph.merge(Relationship(cs, 'TAUGHT', cc))

            if ps:
                previous_subject = self.find_in_course(cc_identity, ps)
                graph.merge(Relationship(cs, 'PREVIOUS', previous_subject))

            if ns:
                next_subject = self.find_in_course(cc_identity, ns)
                graph.merge(Relationship(cs, 'FORWARD', next_subject))
            return True
        return False

    def edit(self, cc_identity, cs_identity, subject_title, previous_subject, next_subject, support_material, initial):
        if not self.find_in_course_by_title_not_current(cc_identity, subject_title, cs_identity):
            query = '''
                    MATCH (cc:CourseClass {id: $cc_identity})
                    OPTIONAL MATCH (cs:ClassSubject {id: $cs_identity})
                    WHERE (cc)<-->(cs)
                    SET cs.title = $subject_title, cs.support_material = $support_material, cs.initial = $initial
                    '''

            class_subject = self.find_in_course(cc_identity, cs_identity)
            if initial == "False" and initial != class_subject['initial'] and \
                    self.find_node_count(cc_identity, cs_identity) > 1:
                initial = "True"
            elif initial == "True" and initial != class_subject['initial']:
                self.set_class_subject_initial_false(cc_identity)

            graph.run(query, cc_identity=cc_identity, cs_identity=cs_identity,
                      subject_title=subject_title, support_material=support_material,
                      initial=initial)

            self.delete_previous_subject(cc_identity, cs_identity)
            if previous_subject:
                self.create_relationship_with_previous_subject(cc_identity, cs_identity, previous_subject)

            self.delete_next_subject(cc_identity, cs_identity)
            if next_subject:
                self.create_relationship_with_next_subject(cc_identity, cs_identity, next_subject)
            return True
        return False

    def delete_previous_subject(self, cc_identity, cs_identity):
        query = '''
                MATCH (cs:ClassSubject {id: $cs_identity})-[:TAUGHT]->(cc:CourseClass {id: $cc_identity})
                OPTIONAL MATCH (cs)-[r:PREVIOUS]->(ps:ClassSubject)
                DELETE r
                '''
        graph.run(query, cc_identity=cc_identity, cs_identity=cs_identity)

    def delete_next_subject(self, cc_identity, cs_identity):
        query = '''
                MATCH (cs:ClassSubject {id: $cs_identity})-[:TAUGHT]->(cc:CourseClass {id: $cc_identity})
                OPTIONAL MATCH (cs)-[r:FORWARD]->(ps:ClassSubject)
                DELETE r
                '''
        graph.run(query, cc_identity=cc_identity, cs_identity=cs_identity)

    def create_relationship_with_previous_subject(self, cc_identity, cs_identity, ps_identity):
        query = '''
                MATCH (cc:CourseClass)<-->(cs:ClassSubject), (cc:CourseClass)<-->(cs1:ClassSubject)
                WHERE (cc.id = $cc_identity) AND (cs.id = $cs_identity) AND (cs1.id = $ps_identity)
                CREATE (cs)-[r:PREVIOUS]->(cs1)
                '''
        graph.run(query, cc_identity=cc_identity, cs_identity=cs_identity, ps_identity=ps_identity)

    def create_relationship_with_next_subject(self, cc_identity, cs_identity, ns_identity):
        query = '''
                MATCH (cc:CourseClass)<-->(cs:ClassSubject), (cc:CourseClass)<-->(cs1:ClassSubject)
                WHERE (cc.id = $cc_identity) AND (cs.id = $cs_identity) AND (cs1.id = $ns_identity)
                CREATE (cs)-[r:FORWARD]->(cs1)
                '''
        graph.run(query, cc_identity=cc_identity, cs_identity=cs_identity, ns_identity=ns_identity)

    def set_class_subject_initial_false(self, cc_identity):
        query = '''
                MATCH (cs:ClassSubject)-[:TAUGHT]->(cc:CourseClass)
                WHERE cc.id = $cc_identity AND cs.initial = "True"
                SET cs.initial = "False"
                '''
        graph.run(query, cc_identity=cc_identity)

    def get_class_subjects(self, title):
        query = '''
                MATCH (cs:ClassSubject)-[:TAUGHT]->(cc:CourseClass)
                WHERE cc.title = $title
                RETURN cs
                '''
        return graph.run(query, title=title)

    def get_class_subjects_and_course_class(self, title):
        query = '''
                MATCH (cs:ClassSubject)-[:TAUGHT]->(cc:CourseClass)
                WHERE cc.title = $title
                RETURN cs, cc
                '''
        return graph.run(query, title=title)

    def get_class_subjects_and_course_class_except_current_subject(self, cc_identity, cs_identity):
        query = '''
                MATCH (cs:ClassSubject)-[:TAUGHT]->(cc:CourseClass)
                WHERE cc.id = $cc_identity AND cs.id <> $cs_identity
                RETURN cs, cc
                '''
        return graph.run(query, cc_identity=cc_identity, cs_identity=cs_identity)

    # Retorna o id do Assunto initial da Disciplina
    def get_id_class_subjects(self, cc_title):
        query = '''
                MATCH (cc:CourseClass)<--(cs:ClassSubject {title: $title})
                RETURN id(cs)
                '''
        return graph.run(query, title=cc_title)

    def get_class_subjects_with_previous_and_forward(self, cc_identity, search=''):
        query = '''
                MATCH (cs:ClassSubject)-[:TAUGHT]->(cc:CourseClass {id: $cc_identity})
                WHERE toLower(cs.title) CONTAINS toLower($search)
                OPTIONAL MATCH (cs)-[:FORWARD]->(ns:ClassSubject)
                OPTIONAL MATCH (cs)-[:PREVIOUS]->(ps:ClassSubject)
                RETURN cs, ns.title as ns_title, ps.title as ps_title
                ORDER BY cs.title
                '''
        return graph.run(query, cc_identity=cc_identity, search=search)

    def get_class_subjects_with_previous_and_forward_with_pagination(self, cc_identity, skip, limit, search=''):
        query = '''
                MATCH (cs:ClassSubject)-[:TAUGHT]->(cc:CourseClass {id: $cc_identity})
                WHERE toLower(cs.title) CONTAINS toLower($search)
                OPTIONAL MATCH (cs)-[:FORWARD]->(ns:ClassSubject)
                OPTIONAL MATCH (cs)-[:PREVIOUS]->(ps:ClassSubject)
                RETURN cs, ns.title as ns_title, ps.title as ps_title
                ORDER BY cs.order
                SKIP $skip
                LIMIT $limit
                '''
        return graph.run(query, cc_identity=cc_identity, skip=skip, limit=limit, search=search)

    def delete(self, cc_identity, cs_identity):
        if self.find_in_course(cc_identity, cs_identity):
            query = '''
                    MATCH (cs:ClassSubject)-[:TAUGHT]->(cc:CourseClass)
                    WHERE cc.id = $cc_identity AND cs.id = $cs_identity
                    RETURN cs
                    '''
            cs = graph.evaluate(query, cc_identity=cc_identity, cs_identity=cs_identity)
            graph.delete(cs)
            return True
        return False

    def get_class_subject_current_question(self, cc_title, user):
        query = '''
                MATCH (p:Person)-->(a:Answer)-->()-->(cs:ClassSubject)-->(cc:CourseClass {title: $cc_title})
                WHERE a.question_answered = "" AND p.username = $user
                RETURN cs
                '''
        return graph.run(query, cc_title=cc_title, user=user)
