'''
'''


class System:

    def __init__(self):

        self.status = None
        self.mute = None
        self.external_mute = None

        self.zones = []

    def mute(self):
        pass

    def unmute(self):
        pass


class Zone:

    def __init__(self):

        self.status = None  # TODO make this an enum: Unknown, On, Off
        self.mute = None

        # prop
        self.source = None

        # prop
        self.group = None

        # prop
        self.volume = None

        # prop
        self.bass = None

        # prop
        self.treble = None

    def on(self):
        pass

    def off(self):
        pass

    def mute(self):
        pass

    def unmute(self):
        pass
