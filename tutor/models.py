from py2neo import Graph, Node, Relationship, NodeMatcher
from datetime import datetime
from bcrypt import checkpw
import uuid

graph = Graph("http://localhost:7474", auth=("neo4j", "admin"))
matcher = NodeMatcher(graph)


##############
#   PERSON   #
##############
class Person:
    def __init__(self, username):
        self.username = username

    def find(self):
        return matcher.match("Person", username=self.username).first()

    def register(self, name, password, email, p_type):
        if not self.find():
            user = Node("Person", name=name, username=self.username, password=password, email=email, type=p_type)
            graph.create(user)
            return True
        else:
            return False

    def edit_personal_data(self, name, email):
        query = '''
                MATCH (p:Person {username: $username})
                SET p.name = $name, p.email = $email
                RETURN p
                '''
        if graph.run(query, username=self.username, name=name, email=email):
            return True
        return False

    def change_password(self, password):
        query = '''
                MATCH (p:Person {username: $username})
                SET p.password = $password
                RETURN p
                '''
        if graph.run(query, username=self.username, password=password):
            return True
        return False

    def verify_password(self, password):
        user = self.find()
        if user:
            if checkpw(password.encode('utf-8'), user['password'].encode('utf-8')):
                return user
            else:
                return False
        return False


####################
#   COURSE CLASS   #
####################
class CourseClass:
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
        if not self.find(title):
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

    # Cria o nó "Answer" e faz as ligações necessárias para matricular o aluno a uma Disciplina
    def enrollment(self, title, user):
        username = Person(user).find()

        if self.find(title):
            question_answered = ""
            question = Question().get_random_question(title)
            a = Node("Answer", date=date(), question_answered=question_answered)
            graph.create(a)
            graph.merge(Relationship(username, 'HISTORIC', a))
            graph.merge(Relationship(a, 'BOND', question))
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


#####################
#   CLASS SUBJECT   #
#####################
class ClassSubject:
    # método que retorna a quantidade de nós ClassSubject
    def find_node_count(self, cc_identity, cs_identity):
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
    def find_single_class_subject(self, cc_identity, cs_identity):
        query = '''
                MATCH (cc:CourseClass {id: $cc_identity})<-->(cs:ClassSubject {id: $cs_identity})
                WHERE NOT (cs)<-->(:Question)
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

    def get_class_subjects_with_previous_and_forward(self, cc_identity):
        query = '''
                MATCH (cs:ClassSubject)-[:TAUGHT]->(cc:CourseClass {id: $cc_identity})
                OPTIONAL MATCH (cs)-[:FORWARD]->(ns:ClassSubject)
                OPTIONAL MATCH (cs)-[:PREVIOUS]->(ps:ClassSubject)
                RETURN cs, ns.title as ns_title, ps.title as ps_title
                ORDER BY cs.order
                '''
        return graph.run(query, cc_identity=cc_identity)

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


################
#   QUESTION   #
################
class Question:
    # Retorna uma questão através do id (NÃO ESTA SENDO USADO)
    def find(self, identity):
        return matcher.match("Question", id=identity).first()

    # Cria uma questão
    def create(self, cc_identity, cs_identity, title, body, support_material, difficulty, choice_a, choice_b, choice_c,
               choice_d, right_answer, user):
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
    def get_questions(self, cc_identity, cs_identity):
        query = '''
                MATCH (q:Question)-[:ASKED]->(cs:ClassSubject)-[:TAUGHT]->(cc:CourseClass)
                WHERE cs.id = $cs_identity and cc.id = $cc_identity
                RETURN q
                ORDER BY q.title
                '''
        return graph.run(query, cc_identity=cc_identity, cs_identity=cs_identity)

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


##############
#   ANSWER   #
##############
class Answer:
    def set_answer_question(self, alternative_answered, user):
        query = '''
                MATCH (p:Person {username:$user})-->(a:Answer)
                WHERE a.question_answered = ''
                SET a.question_answered = $alternative_answered
                '''
        graph.run(query, user=user, alternative_answered=alternative_answered)
        return True


############
#   UTIL   #
############
def timestamp():
    epoch = datetime.utcfromtimestamp(0)
    now = datetime.now()
    delta = now - epoch
    return delta.total_seconds()


def date():
    return datetime.now().strftime('%Y-%m-%d')

# def get_recent_posts(self):
#     query = '''
#     MATCH (user:User)-[:PUBLISHED]->(post:Post)<-[:TAGGED]-(tag:Tag)
#     WHERE user.username = $username
#     RETURN post, COLLECT(tag.name) AS tags
#     ORDER BY post.timestamp DESC LIMIT 5
#     '''
#     return graph.run(query, username=self.username)

# def get_similar_users(self):
#     # Find three users who are most similar to the logged-in user
#     # based on tags they've both blogged about.
#     query = '''
#     MATCH (you:User)-[:PUBLISHED]->(:Post)<-[:TAGGED]-(tag:Tag),
#           (they:User)-[:PUBLISHED]->(:Post)<-[:TAGGED]-(tag)
#     WHERE you.username = $username AND you <> they
#     WITH they, COLLECT(DISTINCT tag.name) AS tags
#     ORDER BY SIZE(tags) DESC LIMIT 3
#     RETURN they.username AS similar_user, tags
#     '''

#     return graph.run(query, username=self.username)

# def get_commonality_of_user(self, other):
#     # Find how many of the logged-in user's posts the other user
#     # has liked and which tags they've both blogged about.
#     query = '''
#     MATCH (they:User {username: $they })
#     MATCH (you:User {username: $you })
#     OPTIONAL MATCH (they)-[:PUBLISHED]->(:Post)<-[:TAGGED]-(tag:Tag),
#                    (you)-[:PUBLISHED]->(:Post)<-[:TAGGED]-(tag)
#     RETURN SIZE((they)-[:LIKED]->(:Post)<-[:PUBLISHED]-(you)) AS likes,
#            COLLECT(DISTINCT tag.name) AS tags
#     '''

#     return graph.run(query, they=other.username, you=self.username).next

# def get_todays_recent_posts():
#     query = '''
#         MATCH (user:Person)-[:PUBLISHED]->(post:Post)<-[:TAGGED]-(tag:Tag)
#         WHERE post.date = $today
#         RETURN user.username AS username, post, COLLECT(tag.name) AS tags
#         ORDER BY post.timestamp DESC LIMIT 5
#         '''
#
#     return graph.run(query, today=date())
