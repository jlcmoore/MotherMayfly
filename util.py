TOPICS = "topics.txt"
TIME_FORMAT = "%x %X"

DEFAULT_TOPICS = [
    'corn',
    'apple butter',
    'red velvet',
    'block island',
    'charges',
    'ukulele',
    'moss',
    'fedora',
    'go away',
    'so fabulous',
    'curtain rod',
    'lawn care',
    'volunteer',
    'monarch',
    'the washington post',
    'stubbed my toe',
    'violet',
    'concerto',
    'yellow',
    'nails',
    'honeycrisp'
    'rain',
    'laugh',
    'Calgary',
    'Park Hill',
    'golfcart races',
    'Reston',
    'deluge',
    'ginger syrup',
    'tormented',
    'pee',
    'pillow',
    'climbing',
    'walk the line',
    'throw',
    'a rolling stone gathers no moss',
    'spun around',
    'brown eyes',
    'drew merrily',
    'forgot quickly',
    'died slowly',
    'capris',
    'fridge magnet',
    'curly hair',
    'sleep',
    'work',
    'play',
    'run',
    'swim',
    'dance',
    'eat',
    'hide',
    'run away',
    'cook',
    'reward',
    'regret ',
    'reply',
    'replay',
    'refine',
    'redistribute',
    'renegotiate',
    'mother',
    'father ',
    'baby',
    'sister',
    'brother',
    'uncle'
]

class GracefulKiller(object):
    """
    A class to signal when the SIGINT or SIGTERM signals are received
    Originally from
    https://stackoverflow.com/questions/18499497/how-to-process-sigterm-signal-gracefully
    """
    def __init__(self, event):
        self.dead = event
        signal.signal(signal.SIGINT, self.exit_gracefully)
        signal.signal(signal.SIGTERM, self.exit_gracefully)

    def exit_gracefully(self, *_):
        """
        Signal received, flag death
        """
        self.dead.set()