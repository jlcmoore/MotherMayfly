import random
import test_poems
import query_hafez

class Poem(object):
    # todo: add a date should not be required
    # and add a typ
    def __init__(self, title, lines, author):
        self.title = title
        self.lines = lines
        self.author = author

def serial_to_poem(serial):
    title = ''
    if 'title' in serial and isinstance(serial['title'], basestring):
        title = serial['title']
        author = ''
    if 'author' in serial and isinstance(serial['author'], basestring):
        author = serial['author']
        lines = []
    if 'lines' in serial and isinstance(serial['lines'], list):
        lines = serial['lines']
    return Poem(title, lines, author)

def get_poem():
    return serial_to_poem(random.choice(test_poems.REAL_TESTS))

def generate(topic):
    # this is very blocking
    return Poem(topic, query_hafez.query(topic), "computer")
