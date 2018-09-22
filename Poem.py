from poems import test_poems
import random

class Poem:
    # todo: add a date should not be required
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
#    return serial_to_poem(random.choice(test_poems))
    return serial_to_poem(test_poems[7])
    
def generate():
    return get_poem()
