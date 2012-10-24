import irclib
from urllib2 import urlopen, URLError

irclib.DEBUG = True
network = 'uk.ircnet.org'
port = 6667
channel = '#qmul-its'
nick = 'whdbot'
name  = 'whdbot'

class WhdBot():
    def __init__(self):
        self.whdDead = False
        self.irc = irclib.IRC()
        self.irc.add_global_handler('pubmsg', self.handlePubMsg) 

        server = self.irc.server()
        server.connect(network, port, nick, ircname = name)
        server.join(channel)
        self.connection = self.irc.connections[0]

        self.irc.execute_delayed(30, self.checkWhd)
        self.irc.process_forever()

    def handlePubMsg(self, connection, event):
        print event.arguments()[0], 'err'
        if event.arguments()[0] == '!iswhddead':
            if self.whdDead:
                print ">#whddead 'yes'"
                connection.privmsg(channel, 'Yes')
            else:
                print ">#whddead 'no'"
                connection.privmsg(channel, 'No')

    def checkWhd(self):
        try:
            print 'checking whd'
            response = urlopen('https://helpdesk.its.qmul.ac.uk', timeout=10)
            if self.whdDead:
                self.whdDead = False
                self.connection.privmsg(channel, 'It\'s back!')
            print 'it\'s alive'
        except URLError:
            print 'whd is dead'
            if not self.whdDead:
                self.connection.privmsg(channel, 'I think whd is dead')
                self.whdDead = True
            self.connection.execute_delayed(10, self.checkWhd)
        self.connection.execute_delayed(30, self.checkWhd)

whdbot = WhdBot()

