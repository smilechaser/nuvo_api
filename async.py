'''
Async infrastructure for communicating with the Nuvo device.
'''


class Message:

    def __init__(self):

        self.datetimestamp = None


class MessageQueue:
    '''An ordered collection (FIFO) of message objects.'''

    @property
    def empty(self):
        # TODO
        raise NotImplementedError('TODO')

    def push(self, msg):

        assert isinstance(msg, Message)

        if msg is None:
            return

        raise NotImplementedError('TODO')

    def pop(self):

        raise NotImplementedError('TODO')


class Nuvo:

    def send(self, msg):
        '''Send a message TO the device.'''

        raise NotImplementedError('TODO')

    def receive(self):
        '''Receive a message FROM the device.'''

        raise NotImplementedError('TODO')


class Processor:

    def __init__(self):

        self.to_device_queue = MessageQueue()
        self.from_device_queue = MessageQueue()

        self.device = None

    @property
    def safe_to_send(self):
        '''Has enough time passed since we last sent a message?'''

        # TODO implement this using a "tick queue" so that we don't have a
        # dependency on time (which will make testing easier)

        raise NotImplementedError('TODO')

    def pump(self):

        assert self.device is not None

        self._send()

        self._receive()

    def _send(self):

        if not self.to_device_queue.empty and self.safe_to_send:

            msg = self.to_device_queue.pop()

            self.device.send(msg)

    def _receive(self):

        msg = self.device.receive()

        if msg:
            self.from_device_queue.push(msg)
