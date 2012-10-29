import cookielib
import irclib
import re
from ssl import SSLError
from urllib2 import urlopen, URLError, Request, HTTPCookieProcessor, build_opener
from urllib import urlencode
from httplib import BadStatusLine

#irclib.DEBUG = True
network = 'uk.ircnet.org'
port = 6667
channel = '#qmul-its'
channels = ['#freefrom', '#qmul-its', '#qmul']
nick = 'whdbot'
name  = 'whdbot'

class WhdBot():
    def __init__(self):
        self.whdDead = False
        self.irc = irclib.IRC()
        self.irc.add_global_handler('pubmsg', self.handlePubMsg) 

        server = self.irc.server()
        server.connect(network, port, nick, ircname = name)
        for channel in channels:
            server.join(channel)
        self.connection = self.irc.connections[0]

        self.irc.execute_delayed(30, self.checkWhd)
        self.irc.process_forever()

    def handlePubMsg(self, connection, event):
        p = re.compile('.*?(\d{5}\d?).*?')
        m = p.match(event.arguments()[0])
        #print event.arguments()
        if event.arguments()[0] == '!iswhddead':
            if self.whdDead:
                print ">#whddead 'yes'"
                connection.privmsg(event.target(), 'Yes')
            else:
                print ">#whddead 'no'"
                connection.privmsg(event.target(), 'No')
        elif m:
            connection.privmsg(event.target(), "https://helpdesk.its.qmul.ac.uk/helpdesk/WebObjects/Helpdesk.woa/wa/ticket?ticketId={0}".format(m.group(1)))

    def checkWhd(self):
        try:
            print 'checking whd'
            cj = cookielib.CookieJar()
            opener = build_opener(HTTPCookieProcessor(cj))
            response = opener.open('https://helpdesk.its.qmul.ac.uk/helpdesk/WebObjects/Helpdesk.woa', timeout=20)
            html = response.read()
            q = re.compile('.*?(https://helpdesk.its.qmul.ac.uk/helpdesk/WebObjects/Helpdesk.woa/wo/\w+/0.11.1.5.11).*?', re.DOTALL)
            n = q.match(html)
            formData = urlencode({'userName':'username','password':'password'})
            post = opener.open(n.group(1), data=formData, timeout=20)
            #print post.read()

            if self.whdDead:
                self.whdDead = False
                for channel in channels:
                    self.connection.privmsg(channel, 'It\'s back!')
            print 'it\'s alive'
        except Exception as e:
            print 'whd is dead', e
            if not self.whdDead:
                for channel in channels:
                    self.connection.privmsg(channel, 'I think whd is dead')
                self.whdDead = True
        finally:
            self.connection.execute_delayed(30, self.checkWhd)


    def autoOp(self, connection, event):
        pass

whdbot = WhdBot()
