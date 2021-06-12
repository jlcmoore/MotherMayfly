import json
import urllib2
import urllib
import re
from poetrydata import poem

BASE_URL = "http://vivaldi.isi.edu:8080/api/poem_check?"
BREAK_DEL = r'\s*<br\/\/>'

def query(topic):
    """
    Queries the Hafez system at BASE_URL with certain parameters
    and returns the lines of the poem generated on the topic given.
    """
    # most integer parameters can range from -5 to 5 integers?
    parameters = {'topic' : topic,
                  'k' : 1,
                  'model' : 0,
                  'nline' : 4,
                  'encourage_words' : '',
                  'disencourage_words' : '',
                  'enc_weight' : 0,
                  'cword' : -5,
                  'reps' : 0,
                  'allit' : 0,
                  'topical' : 1,
                  'wordlen' : 0,
                  'mono' : -5,
                  'sentiment' : 0,
                  'concrete' : 0,
                  'is_default' : 1,
                  'source' : "auto"}

    web_params = urllib.urlencode(parameters)
    full_url = BASE_URL + web_params
    webpage = urllib2.urlopen(full_url)
    results = webpage.read()
    poem_info = json.loads(results)
    poem_lines = re.split(BREAK_DEL, poem_info["poem"])
    return [line for line in poem_lines if line]

def hafez_poem(topic):
    """
    Returns a poem as generated by the Hafez system
    """
    # this is very blocking
    return poem.Poem(title=topic, lines=query(topic), author="computer")