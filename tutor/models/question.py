import uuid

from py2neo import Node, Relationship
from tutor.models.db import matcher, graph
from tutor.models.class_subject import ClassSubject


class Question:
    def __init__(self, node_question=None):
        if node_question:
            self.id = node_question['id']
            self.title = node_question['title']
            self.body = node_question['body']
            self.support_material = node_question['support_material']
            self.difficulty = node_question['difficulty']
            self.choice_a = node_question['choice_a']
            self.choice_b = node_question['choice_b']
            self.choice_c = node_question['choice_c']
            self.choice_d = node_question['choice_d']
            self.right_answer = node_question['right_answer']

    # Retorna uma questão através do id (NÃO ESTA SENDO USADO)
    def find(self, identity):
        return matcher.match("Question", id=identity).first()

    # Cria uma questão
    def create(self, cc_identity, cs_identity, title, body, support_material, difficulty, choice_a, choice_b, choice_c,
               choice_d, right_answer):
        cs = ClassSubject().find_in_course(cc_identity, cs_identity)

        question = Node(
            "Question",
            id=str(uuid.uuid1()),
            title=title,
            body=body,
            support_material=support_material,
            difficulty=difficulty,
            choice_a=choice_a,
            choice_b=choice_b,
            choice_c=choice_c,
            choice_d=choice_d,
            right_answer=right_answer
        )
        graph.create(question)
        graph.merge(Relationship(question, 'ASKED', cs))
        return True

    # Edita uma questão através do id
    def edit(self, question_id, title, body, support_material, difficulty, choice_a, choice_b, choice_c,
             choice_d, right_answer):
        query = '''
                MATCH (q:Question {id: $question_id})
                SET q.title = $title, q.body = $body, q.support_material = $support_material, q.difficulty = 
                $difficulty, q.choice_a = $choice_a, q.choice_b = $choice_b, q.choice_c = $choice_c, q.choice_d =
                $choice_d, q.right_answer = $right_answer
                '''
        graph.run(query, question_id=question_id, title=title, body=body, support_material=support_material,
                  difficulty=difficulty, choice_a=choice_a, choice_b=choice_b, choice_c=choice_c, choice_d=choice_d,
                  right_answer=right_answer)
        return True

    # Retorna uma questão atráves do título da Disciplina e do título do Assunto
    def get_questions(self, cc_identity, cs_identity, search=''):
        query = '''
                MATCH (q:Question)-[:ASKED]->(cs:ClassSubject)-[:TAUGHT]->(cc:CourseClass)
                WHERE cs.id = $cs_identity AND cc.id = $cc_identity
                AND toLower(q.title) CONTAINS toLower($search)
                RETURN q
                ORDER BY q.title
                '''
        return graph.run(query, cc_identity=cc_identity, cs_identity=cs_identity, search=search)

    def get_questions_with_pagination(self, cc_identity, cs_identity, skip, limit, search=''):
        query = '''
                MATCH (q:Question)-[:ASKED]->(cs:ClassSubject)-[:TAUGHT]->(cc:CourseClass)
                WHERE cs.id = $cs_identity AND cc.id = $cc_identity
                AND toLower(q.title) CONTAINS toLower($search)
                RETURN q
                ORDER BY q.title
                SKIP $skip
                LIMIT $limit
                '''
        return graph.run(query, cc_identity=cc_identity, cs_identity=cs_identity, skip=skip, limit=limit, search=search)

    def get_question(self, question_id):
        query = '''
                MATCH (q:Question {id: $question_id})
                RETURN q
                '''
        return graph.run(query, question_id=question_id)

    # Retorna uma questão aleatória de um Assunto específico
    def get_random_question(self, cc_title):
        cs_id_initial = ClassSubject().get_initial_id(cc_title)
        query = '''
                MATCH (cs:ClassSubject)<-[:ASKED]-(q:Question)
                WHERE id(cs) = $cs_id
                WITH q, rand() as rand
                ORDER BY rand LIMIT 1
                RETURN id(q)
                '''
        id = graph.run(query, cs_id=cs_id_initial).evaluate()
        return matcher.get(id)

    def get_second_random_question(self, cs_title):
        query = '''
                MATCH (cs:ClassSubject)<-[:ASKED]-(q:Question)
                WHERE id(cs) = $cs_id
                WITH q, rand() as rand
                ORDER BY rand LIMIT 1
                RETURN id(q)
                '''
        id = graph.run(query, cs_title=cs_title).evaluate()
        return matcher.get(id)

    # Retorna a questão atual, não respondida, de uma Disciplina
    def get_current_question(self, cc_title, user):
        query = '''
                MATCH (p:Person)-->(a:Answer)-->(q:Question)-->()-->(cc:CourseClass {title: $cc_title})
                WHERE a.question_answered = "" AND p.username = $user
                RETURN q
                '''
        return graph.run(query, cc_title=cc_title, user=user)

    def delete(self, identity):
        if self.find(identity):
            question = matcher.match("Question", id=identity).first()
            graph.delete(question)
            return True
        return False
