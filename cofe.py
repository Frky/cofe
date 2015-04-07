
import ssl
import sys
import argparse
import itertools
import time
import sched
from random import randint
from threading import Thread, Timer

import irc
import irc.client, irc.bot
import jaraco.logging

WAIT_BEFORE_QUIT = 18000
WAIT_BEFORE_JOIN = 18000
WAIT_BEFORE_POST = 3600
NB_MSG_BEFORE_QUIT = 10

nicknames = ["Oxdeca", "_0xdeca", "Oxcafe", "oxdeca", "oxcafe"]

class Bot(irc.bot.SingleServerIRCBot):

    def __init__(self, nick, server, port, target):
        ssl_factory = irc.connection.Factory(wrapper=ssl.wrap_socket)
        irc.bot.SingleServerIRCBot.__init__(self, [(server, port)], nick, nick, connect_factory=ssl_factory)
        self.target = target
        self.nick = nick
        self.ttl = 1

    def on_nicknameinuse(self, c, e):
        c.nick(c.get_nickname() + "_")

    def on_welcome(self, c, e):
        c.join(self.target)

    def on_join(self, c, e):
        self.main_loop(c)

    def on_dccchat(self, c, e):
        if len(e.arguments) != 2:
            return
        args = e.arguments[1].split()
        if len(args) == 4:
            try:
                address = ip_numstr_to_quad(args[2])
                port = int(args[3])
            except ValueError:
                return
            self.dcc_connect(address, port)

    def spam(self, c):
        c.privmsg(self.target, "(nespresso)") 

    def quit(self, c):
        c.quit("What else ?")

    def main_loop(self, connection):
        ttl = randint(1, NB_MSG_BEFORE_QUIT)
        next_msg = 0
        for i in xrange(ttl):
            next_msg += randint(1, WAIT_BEFORE_POST)
            Timer(next_msg, self.spam, args=[connection]).start()
        Timer(next_msg + WAIT_BEFORE_QUIT, self.quit, args=[connection]).start()

    def on_disconnect(self, connection, event):
        global nicknames
        time.sleep(randint(1, WAIT_BEFORE_QUIT))
        nicknames.append(self.nick)

    
def main():
    global nicknames
    server = "securimag.org"
    port = 6697
    target = "#securimag"
    while True:
        if len(nicknames) > 0:
            bot = Bot(nicknames.pop(), server, port, target)
            Timer(randint(1, WAIT_BEFORE_JOIN), bot.start).start()
            print "Bot created"
        time.sleep(1)

if __name__ == '__main__':
    main()

