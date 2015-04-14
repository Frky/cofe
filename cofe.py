
import ssl
import sys
import argparse
import itertools
import time
import sched
from random import randint, choice, seed
from threading import Thread, Timer

import irc
import irc.client, irc.bot
import jaraco.logging

TESTING = False

if TESTING:
    WAIT_BEFORE_QUIT = 30
    WAIT_BEFORE_JOIN = 60
    WAIT_BEFORE_POST = 30
    NB_MSG_BEFORE_QUIT = 7
else:
    WAIT_BEFORE_QUIT = 3600
    WAIT_BEFORE_JOIN = 3*86400
    WAIT_BEFORE_POST = 18000
    NB_MSG_BEFORE_QUIT = 7

original_nicks = ["Oxdeca", "_0xdec", "Oxcafe", "oxdeca", "oxcafe", "_0xcaf"]
nicknames = ["Oxdeca", "_0xdeca", "Oxcafe", "oxdeca", "oxcafe"]
s_nouns = ["A dude", "My mom", "The king", "Some guy", "A cat with rabies", "A sloth", "Your homie", "This cool guy my gardener met yesterday", "Superman"]
p_nouns = ["These dudes", "Both of my moms", "All the kings of the world", "Some guys", "All of a cattery's cats", "The multitude of sloths living under your bed", "Your homies", "Like, these, like, all these people", "Supermen"]
s_verbs = ["eats", "kicks", "gives", "treats", "meets with", "creates", "hacks", "configures", "spies on", "retards", "meows on", "flees from", "tries to automate", "explodes"]
p_verbs = ["eat", "kick", "give", "treat", "meet with", "create", "hack", "configure", "spy on", "retard", "meow on", "flee from", "try to automate", "explode"]
infinitives = ["to make a pie.", "for no apparent reason.", "because the sky is green.", "for a disease.", "to be able to make toast explode.", "to know more about archeology."]

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

    def on_privmsg(self, c, e):
        global original_nicks
        auth = e.source
        msg = e.arguments[0].split(":", 1)[0]
	print "[{0}] {1}".format(auth, msg)
        if auth[:min(6, len(auth))] in original_nicks:
            if msg.count("!to_") > 0:
                dest = ""
                idx = msg.index("!to_") + 4
                while len(msg) > idx and msg[idx] != " ":
                    dest += msg[idx]
                    idx += 1
                c.privmsg(dest, msg[idx + 1:])
            else:
                c.privmsg(self.target, msg)
        else:
            c.privmsg("Oxcafe_", "[" + auth + "] " + msg)

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
        return
        c.privmsg(self.target, self.sing_sen_maker()) 

    def quit(self, c):
        c.quit("What else ?")

    def main_loop(self, connection):
        ttl = randint(1, NB_MSG_BEFORE_QUIT)
        print "[{0}] TTL: {1}".format(self.nick, ttl)
        next_msg = 0
        for i in xrange(ttl):
            rdm = randint(1, WAIT_BEFORE_POST)
            next_msg += rdm 
	    print "[{0}] Next message in {1} sec".format(self.nick, rdm)
            Timer(next_msg, self.spam, args=[connection]).start()
        Timer(next_msg + WAIT_BEFORE_QUIT, self.quit, args=[connection]).start()

    def on_disconnect(self, connection, event):
        global nicknames
        time.sleep(randint(1, WAIT_BEFORE_QUIT))
        nicknames.append(self.nick)

    def sing_sen_maker(self):
        global s_nouns, s_verbs, infinitives, p_nouns
        return choice(s_nouns) + " " + choice(s_verbs) + " " + (choice(s_nouns).lower() or choice(p_nouns).lower()) + " " + choice(infinitives)

    
def main():
    global nicknames
    seed()
    server = "securimag.org"
    port = 6697
    if TESTING:
        target = "#troll"
    else:
        target = "#securimag"
    while True:
        if len(nicknames) > 0:
            bot = Bot(nicknames.pop(), server, port, target)
            rdm = randint(1, WAIT_BEFORE_JOIN)
            Timer(rdm, bot.start).start()
            print "[{0}] created".format(bot.nick)
            print "[{0}] will join in {1} sec".format(bot.nick, rdm)
        time.sleep(1)

if __name__ == '__main__':
    main()

