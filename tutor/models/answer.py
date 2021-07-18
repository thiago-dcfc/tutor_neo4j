from tutor.models.db import matcher, graph


class Answer:
    def set_answer_question(self, alternative_answered, user):
        query = '''
                MATCH (p:Person {username:$user})-->(a:Answer)
                WHERE a.question_answered = ''
                SET a.question_answered = $alternative_answered
                '''
        graph.run(query, user=user, alternative_answered=alternative_answered)
        return True
