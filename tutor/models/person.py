from py2neo import Node
from bcrypt import checkpw
from tutor.models.db import matcher, graph


class Person:
    def __init__(self, username='', node_user=None):
        self.username = username

        if node_user:
            self.username = node_user['username']
            self.name = node_user['name']
            self.email = node_user['email']
            self.password = node_user['password']
            self.type = node_user.labels

    def find(self, label='Person'):
        return matcher.match(label, username=self.username).first()

    def register(self, name, password, email, label='Student'):
        if not self.find():
            user = Node("Person", name=name, username=self.username, password=password, email=email)
            user.add_label(label)
            graph.create(user)
            return user
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
            return False
        return False
