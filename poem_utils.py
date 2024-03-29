# -*- coding: utf-8 -*-

import json
from poetrydata import poem, read
import re
import openai

CREDENTIALS = 'openai.json'

with open(CREDENTIALS, 'r') as f:
    openai.api_key = json.load(f)["OPENAI_API_KEY"]

TEST_POEMS = [
    {'title' : "no poem", 'lines' : [], 'author' : "me"},
    {'title' : "no_author", 'lines' : ["this", "is", "a", "poem"], 'author' : ""},
    {'title' : "", 'lines' : ["this", "has", "no title", ""], 'author' : "me"},
    {'title' : "long author", 'lines' : ["too", "long?"], 'author' : "this is the nameofavery longauthorIwonderifitwillwrapproperly?"},
    {'title' : "this is the titleofavery longpoemIwonderifitwillwrapproperly?", 'lines' : ["too", "long?"], 'author' : "me"},
    {'title' : "this is the titleofavery longpoemIwonderifitwillwrapproperly?", 'lines' : ["too", "long?"], 'author' : "me"},
    {'title' : "poem with long words", 'lines' : ["asdfiqowiefnioqrvoqwejwhjefiojas fqwefjowihfowhfonqiosdoajsdfassfjaoiwmececmqw9jfoiwejrqiwenfcnqoengdjrg-e wefqjwef9j3fqefqf"], 'author' : ""},
    {'title' : "nums", 'lines' : ['012345678901234567890123456789012345678901234567890123456789012345678901234567890', 'abcdefghijklmnopqrstuvwxyzabcdefghijklmnopqrstuvwxyzabcdefghijklmnopqrstuvwxyz'], 'author' : ""},
    {'title' : "poem with long lines", 'lines' : ["asdfiqowie fnioqrvoqwe jwhjefiojas fqwefjowihfowh fonqiosdoaj sdfassfjao iwmececmqw9jfoiwej rqiwen fcnqoengdjrg-e  wefqjwef9j3fq", "a boy crossed the road and then went to the other side but before he did that he stopped and picked up somethign. It was: a little gem. You think this is dull? No, it was shiny."], 'author' : ""}
]
REAL_TESTS = [
    {'title' : "Piute Creek", 'author' : "Gary Snyder", 'lines' : ["One granite ridge", "A tree, would be enough", "Or even a rock, a small creek,", "A bark shred in a pool.", "Hill beyond hill, folded and twisted", "Tough trees crammed", "In thin stone fractures", "A huge moon on it all, is too much.", "The mind wanders. A million", "Summers, night air still and the rocks", "Warm.   Sky over endless mountains.", "All the junk that goes with being human", "Drops away, hard rock wavers", "Even the heavy present seems to fail", "This bubble of a heart.", "Words and books", "Like a small creek off a high ledge", "Gone in the dry air.", "", "A clear, attentive mind", "Has no meaning but that", "Which sees is truly seen.", "No one loves rock, yet we are here.", "Night chills. A flick", "In the moonlight", "Slips into Juniper shadow:", "Back there unseen", "Cold proud eyes", "Of Cougar or Coyote", "Watch me rise and go."], 'date' : "2009"},
    {'title' : "Stopping by Woods on a Snowy Evening", 'author' : "Robert Frost", 'lines' : ["Whose woods these are I think I know.", "His house is in the village though;", "He will not see me stopping here", "To watch his woods fill up with snow.", "", "My little horse must think it queer", "To stop without a farmhouse near", "Between the woods and frozen lake", "The darkest evening of the year.", "", "He gives his harness bells a shake", "To ask if there is some mistake.", "The only other sound's the sweep", "Of easy wind and downy flake.", "", "The woods are lovely, dark and deep,", "But I have promises to keep,", "And miles to go before I sleep,", "And miles to go before I sleep."], 'date' : '1923'},
    {'title' : "Digging", 'author' : "Seamus Heaney", 'date' : '1966', 'lines' : ["Between my finger and my thumb", "The squat pen rests; snug as a gun.", "", "Under my window, a clean rasping sound", "When the spade sinks into gravelly ground:", "My father, digging. I look down", "", "Till his straining rump among the flowerbeds", "Bends low, comes up twenty years away", "Stooping in rhythm through potato drills", "Where he was digging.", "", "The coarse boot nestled on the lug, the shaft", "Against the inside knee was levered firmly.", "He rooted out tall tops, buried the bright edge deep", "To scatter new potatoes that we picked,", "Loving their cool hardness in our hands.", "", "By God, the old man could handle a spade.", "Just like his old man.", "", "My grandfather cut more turf in a day", "Than any other man on Toner’s bog.", "Once I carried him milk in a bottle", "Corked sloppily with paper. He straightened up", "To drink it, then fell to right away", "Nicking and slicing neatly, heaving sods", "Over his shoulder, going down and down", "For the good turf. Digging.", "", "The cold smell of potato mould, the squelch and slap", "Of soggy peat, the curt cuts of an edge", "Through living roots awaken in my head.", "But I’ve no spade to follow men like them.", "", "Between my finger and my thumb", "The squat pen rests.", "I’ll dig with it."]},
    {'title' : "When You are Old", 'author' : "William B. Yeats", 'lines' : ["When you are old and grey and full of sleep,", "And nodding by the fire, take down this book,", "And slowly read, and dream of the soft look", "Your eyes had once, and of their shadows deep;", "How many loved your moments of glad grace,", "And loved your beauty with love false or true,", "But one man loved the pilgrim Soul in you,", "And loved the sorrows of your changing face;", "And bending down beside the glowing bars,", "Murmur, a little sadly, how Love fled", "And paced upon the mountains overhead", "And hid his face amid a crowd of stars"]}
]


FAILED_GENERATION_POEM_TITLES = []


def serial_to_poem(serial):
    title = ''
    if 'title' in serial and isinstance(serial['title'], str):
        title = serial['title']
        author = ''
    if 'author' in serial and isinstance(serial['author'], str):
        author = serial['author']
        lines = []
    if 'lines' in serial and isinstance(serial['lines'], list):
        lines = serial['lines']
    return poem.Poem(title=title, lines=lines, author=author)

def get_real_poem():
    return read.get_random_poem()

def get_context():
    base_poem = None
    while base_poem is None or base_poem.title in FAILED_GENERATION_POEM_TITLES:
        base_poem = get_real_poem()

    firstStanza = ""
    for line in base_poem.lines:
        if len(line) == 0:
            break
        firstStanza += line + "\n"

    if len(firstStanza) > 0:
        return (base_poem, firstStanza)
    else:
        FAILED_GENERATION_POEM_TITLES.append(base_poem.title)
        return None

def generate_stanza(initialContext):
    generatedPoem = ""
    responses = 0
    context = initialContext
    blankResponses = 0
    while generatedPoem.count('\n') < initialContext.count('\n') and blankResponses < 3:
        response = openai.Completion.create(engine="curie",
                                            prompt=context,
                                            max_tokens=10,
                                            frequency_penalty=.1,
                                            presence_penalty=.2,
                                            temperature=.8,
                                            stop=["\n"])

        if response is None or 'choices' not in response or len(response['choices']) < 1:
            continue

        thisLine = ""

        responses += 1
        if responses > 2 and len(generatedPoem) < 2:
            return None

        responseText = response['choices'][0]['text']
        thisLine += responseText
        
        if len(responseText) < 1:
            blankResponses += 1
        else:
            blankResponses = 0

        if response['choices'][0]['finish_reason'] == "stop":
            thisLine += '\n'

        generatedPoem += thisLine
        if responses < 2:
            context = initialContext.strip() + "\n\n" + thisLine
        else:
            context += thisLine

    return generatedPoem
        
def get_generated_poem():
    base_poem, firstStanza = None, None
    while base_poem is None:
        base_poem, firstStanza = get_context()

    print(base_poem)

    generatedPoem = generate_stanza(str(base_poem))

    generatedPoem = generatedPoem.strip()
    generatedPoem = re.sub(r"\n{3,}", "\n\n", generatedPoem)
    context = generatedPoem + "\nThe title of this poem is \""
    response = openai.Completion.create(engine="curie",
                                        prompt=context,
                                        max_tokens=20,
                                        temperature=.8,
                                        stop=['"'])
        
    lines = generatedPoem.split('\n')

    if 'choices' in response and 'text' in response['choices'][0]:
        title = response['choices'][0]['text']
    else:
        title = lines[0]
        
    return poem.Poem(title=title, lines=lines, author="computer")
