import signal

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
