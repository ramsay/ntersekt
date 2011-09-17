''' MIT License 2011 Robert Ramsay <robert.alan.ramsay@gmail.com>

Chat Handler - CRUDite for chats and also passes messages. When creating new chats it uses previous chat metrics to find
a better partner. It will use the google channel-api to send messages.

'''
from datetime import datetime
from google.appengine.ext import db
from google.appengine.api import users
from google.appengine.ext.db import Rollback
try:
    from main import BaseHandler
except ImportError:
    pass

class UserMetrics(db.Model):
    user = db.UserProperty()
    #average word length
    awl = db.IntegerProperty()
    #top words list
    twl = db.StringListProperty()
    #top words count
    twc = db.ListProperty(int)
    #average chat time
    act = db.TimeProperty()
    report = db.FloatProperty()
    def reset(self):
        ''' Sets all of the numerical metrics to their default state (0).
        '''
        self.awl = 0
        self.twl = 0
        self.twc = 0
        self.act = 0
        self.report = 0

class Chat(db.Model):
    host = db.UserProperty()
    guest = db.UserProperty()
    text_list = db.StringListProperty()
    finished = db.BooleanProperty()
    nsfw = db.BooleanProperty()
    created = db.DateTimeProperty()

class ChatHandler(BaseHandler):
    def get(self, id=''):
        '''Gets an archived chat or start the process of creating a new chat.
        '''
        if not id:
            chat = self._new_chat()
        else:
            chat = db.Query(Chat).get(id)
        self.render("templates/chat.html", {'page_title': repr(chat.created) + " Chat", 'chat': chat})

    def _new_chat(self):
        '''Attempts to find a good-matching open chat, if none are found it returns a new open chat with the current
        user as host.
        '''
        user = users.get_current_user()
        metrics = db.Query(UserMetrics).filter('user = ', user).get()
        if metrics is None:
            metrics = UserMetrics()
            metrics.user = user
            metrics.put()
        open_chats = db.Query(Chat).filter('guest = ', None).filter('nsfw = ', False)
        vocab = set(metrics.twl)
        matches = []
        for chat in open_chats:
            host = db.Query(UserMetrics).filter('user =', chat.host).get()
            chat.score = len(vocab.intersection(host.twl))*10 - abs(host.awl-metrics.awl) - abs(host.act-metrics.act)
            if chat.score > -1:
                matches.append(chat)
        if matches:
            matches.sort(key = lambda chat: chat.score, reverse=True)
            for chat in matches:
                result = db.run_in_transaction(join_chat(chat.key(), user))
                if result is not None:
                    return result
        chat = Chat()
        chat.created = datetime.now()
        chat.host = user
        chat.nsfw = False
        chat.finished = False
        chat.guest = None
        db.put(chat)
        return chat

def join_chat(key, user):
    '''Transaction method for joining an open chat.
    '''
    chat = db.get(key)
    if chat.guest is None:
        chat.guest = user
        chat.put()
        return chat
    else:
        raise Rollback()