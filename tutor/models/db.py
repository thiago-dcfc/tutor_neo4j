from py2neo import Graph, NodeMatcher
from os import environ

graph = Graph(environ['DB_URL'], auth=(environ['DB_USERNAME'], environ['DB_PASSWORD']))
matcher = NodeMatcher(graph)


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
