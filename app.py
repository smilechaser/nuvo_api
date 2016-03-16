'''

https://justcheckingonall.wordpress.com/2009/06/09/howto-vsp-socat/

socat -d -d pty,raw,echo=0 pty,raw,echo=0

http://pyserial.sourceforge.net/shortintro.html
'''

import re
import serial

# TODO need to handle error responses i.e. #\n

COM_PORT = '/dev/tty.usbserial-AI025295'

RESPONSE_RE = re.compile(b'#([^\r]+)')


def intbool(value):

    return bool(int(value))


class Response:
    pass


class ZoneConnectStatusResponse(Response):
    '''
    #Z0xPWRppp,SRCs,GRPt,VOL-yy<CR>
    '''

    FILTER_RE = re.compile(b'Z0(?P<zone>\d)'
                           b'PWR(?P<power>ON|OFF),'
                           b'SRC(?P<source>\d),'
                           b'GRP(?P<group>0|1),'
                           b'VOL(?P<volume>-\d\d|MT|XM)')

    TYPE_MAP = {
        'zone': int,
        # 'power': enum?
        'source': int,
        'group': intbool,
        # 'volume': ???
    }

    def __init__(self):

        self.zone = None
        self.power = None
        self.source = None
        self.group = None
        self.volume = None

    @classmethod
    def parse(clz, msg):

        match = clz.FILTER_RE.match(msg)

        if not match:
            return None

        obj = clz()

        for k, v in match.groupdict().items():

            if hasattr(obj, k):
                setattr(obj, k, clz.TYPE_MAP.get(k, lambda x: x)(v))

        return obj

    def to_dict(self):

        return {
            'zone': self.zone,
            'power': self.power,
            'source': self.source,
            'group': self.group,
            'volume': self.volume
        }


class ZoneSettingsStatusResponse(Response):
    '''
    #Z0xPWRppp,SRCs,GRPt,VOL-yy<CR>
    '''

    FILTER_RE = re.compile(b'Z0(?P<zone>\d),'
                           b'BASS(?P<bass>[+-]\d\d),'
                           b'TREB(?P<treble>[+-]\d\d),'
                           b'GRP(?P<group>0|1)')

    TYPE_MAP = {
        'zone': int,
        'bass': int,
        'treble': int,
        'group': intbool,
    }

    def __init__(self):

        self.zone = None
        self.bass = None
        self.treble = None
        self.group = None

    @classmethod
    def parse(clz, msg):

        match = clz.FILTER_RE.match(msg)

        if not match:
            return None

        obj = clz()

        for k, v in match.groupdict().items():

            if hasattr(obj, k):
                setattr(obj, k, clz.TYPE_MAP.get(k, lambda x: x)(v))

        return obj

    def to_dict(self):

        return {
            'zone': self.zone,
            'bass': self.power,
            'treble': self.source,
            'group': self.group,
        }


class PowerResponse(Response):
    '''
    #Z0xPWRppp
    '''

    FILTER_RE = re.compile(b'Z0(?P<zone>\d)'
                           b'PWR(?P<power>ON|OFF)')

    TYPE_MAP = {
        'zone': int,
        # 'power': enum?
    }

    def __init__(self):

        self.zone = None
        self.power = None

    @classmethod
    def parse(clz, msg):

        match = clz.FILTER_RE.match(msg)

        if not match:
            return None

        obj = clz()

        for k, v in match.groupdict().items():

            if hasattr(obj, k):
                setattr(obj, k, clz.TYPE_MAP.get(k, lambda x: x)(v))

        return obj

    def to_dict(self):

        return {
            'zone': self.zone,
            'power': self.power
        }


class ResponseFactory:
    '''
    Returns a Response object if there is a Response class that can
    parse a given message.
    '''

    RESPONSES = (
        ZoneConnectStatusResponse,
        ZoneSettingsStatusResponse,
        PowerResponse
    )

    def __init__(self):

        self.responses = self.RESPONSES[:]

    def parse(self, msg):

        for parser in self.responses:

            resp = parser.parse(msg)

            if resp:
                return resp


def unpack_message(msg):
    '''
    Return a filtered message or None if there is no match.
    '''

    match = RESPONSE_RE.match(msg)

    if match:

        return match.groups()[0]


class Controller:
    '''
    This allows us to send commands to the Nuvo unit.
    '''

    # TODO
    pass


class MyApplication:
    '''
    This is our application. It listens for messages and responds accordingly.
    '''

    ZONE_OUTDOOR = 4

    def __init__(self):
        pass

    def update(self, msg, controller):

        if isinstance(msg, StatusResponse):

            # we don't allow the outdoor zone to be
            # turned on - since we don't want to bother the neighbors
            if msg.group == self.ZONE_OUTDOOR and msg.power == b'ON':

                # TODO agent.say('Sorry, the outdoor zone '
                # 'cannot be enabled.')
                # TODO agent.say(KITCHEN, '...')

                controller.zone_off(self.ZONE_OUTDOOR)


def main():

    app = MyApplication()
    controller = Controller()

    conn = serial.Serial(COM_PORT,
                         9600,
                         bytesize=serial.EIGHTBITS,
                         timeout=5,
                         parity=serial.PARITY_NONE,
                         stopbits=serial.STOPBITS_ONE)

    resp_factory = ResponseFactory()

    print('Processing...')

    outgoing_messages = [
        b'*Z01SETSR\r',
        b'*Z02SETSR\r',
        b'*Z03SETSR\r',
        b'*Z04SETSR\r'
    ]

    receive_buffer = b''

    message = b''

    while True:

        # fill accumulator until we get a message

        data = conn.read(1)

        if data:

            receive_buffer += data

            if b'\r' in receive_buffer:

                message, sep, receive_buffer = receive_buffer.partition(b'\r')

        else:

            print('.', end='', flush=True)

            if outgoing_messages:
                conn.write(outgoing_messages.pop())

            continue

        if message:

                unpacked = unpack_message(message)

                if unpacked:

                    response = resp_factory.parse(unpacked)

                    if response:
                        print('\n', response.to_dict())
                    else:
                        print('\n', '???')

                    app.update(response, controller)

                message = b''

#    nuvo = model.System()

#    driver = SerialDriver(conn, nuvo)

#    while True:

#        driver.pump()
#
if __name__ == '__main__':

    main()
