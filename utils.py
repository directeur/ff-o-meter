#-*- encoding: utf-8 -*-
import wx
import friendfeed
from threading import *


stopwords = [u"aboard", u"about", u"above", u"absent", u"according to", u"across", u"after", u"against", u"aheadof", 
u"along", u"along with", u"alongside", u"another", u"amid", u"amidst", u"among", u"amongst", u"anent", u"anti", u"are", u"around", u"asidefrom", 
u"aslant", u"astride", u"athwart", u"atop", u"barring", u"because", u"before", u"behind", u"behither", u"below", u"beneath", 
u"beside", u"besides", u"between", u"betwixt", u"beyond", u"but", u"bymeansof", u"circa", u"closeto", u"com", u"cum", u"de", 
u"despite", u"down", u"dueto", u"during", u"en", u"except", u"exceptfor", u"failing", u"farfrom", u"following", u"for", u"from", 
u"fromoutof", u"how", u"in accordance with", u"in addition to", u"in case of", u"in front of", u"inlieuof", u"inplace of", 
u"inspite of", u"into", u"inside", u"inside of", u"instead of", u"into", u"like", u"mid", u"minus", u"near", u"nearto", u"next", 
u"nextto", u"not with standing", u"onaccount of", u"on behalf of", u"onto", u"on top of", u"onto", u"opposite", u"out", u"outof", 
u"outside", u"outside of", u"over", u"owingto", u"past", u"per", u"plus", u"priorto", u"pro", u"pursuantto", u"qua", u"re", u"regarding", 
u"regardlessof", u"round", u"sans", u"save", u"since", u"subsequent to", u"than", u"that", u"the", u"this", u"through", u"throughout", 
u"till", u"times", u"to", u"toward", u"towards", u"und", u"under", u"underneath", u"unlike", u"until", u"unto", u"up", u"upon", u"versus", 
u"via", u"vis-à-vis", u"was", u"what", u"when", u"where", u"who", u"will", u"with", u"within", u"without", u"worth", u"www", u"a", u"about", 
u"above", u"accordingly", u"after", u"again", u"against", u"ah", u"all", u"also", u"although", u"always", u"am", u"an", u"and", u"any", 
u"anymore", u"anyone", u"are", u"as", u"at", u"away", u"be", u"been", u"begin", u"beginning", u"goes", u"beginnings", u"begins", u"begone", 
u"begun", u"being", u"below", u"between", u"but", u"by", u"ca", u"can", u"cannot", u"come", u"could", u"did", u"do", u"doing", u"during", 
u"each", u"either", u"else", u"end", u"et", u"etc", u"even", u"ever", u"far", u"ff", u"following", u"for", u"from", u"further", u"get", u"go", 
u"goes", u"going", u"got", u"had", u"has", u"have", u"he", u"her", u"hers", u"herself", u"him", u"himself", u"his", u"how", u"i", u"if", u"in", 
u"into", u"is", u"it", u"its", u"itself", u"last", u"lastly", u"less", u"many", u"may", u"me", u"might", u"more", u"must", u"my", u"myself", 
u"near", u"nearly", u"never", u"new", u"next", u"no", u"not", u"now", u"of", u"off", u"often", u"oh", u"on", u"only", u"or", u"other", u"otherwise", 
u"our", u"ourselves", u"out", u"over", u"perhaps", u"put", u"puts", u"quite", u"said", u"saw", u"say", u"see", u"seen", u"shall", u"she", u"should", 
u"since", u"so", u"some", u"such", u"than", u"that", u"the", u"their", u"them", u"themselves", u"then", u"there", u"therefore", u"these", u"they", 
u"this", u"those", u"thou", u"though", u"throughout", u"thus", u"to", u"too", u"toward", u"unless", u"until", u"up", u"upon", u"us", u"ve", 
u"very", u"was", u"we", u"were", u"what", u"whatever", u"when", u"where", u"which", u"while", u"who", u"whom", u"whomever", u"whose", u"why", 
u"with", u"within", u"without", u"would", u"yes", u"i", u"you", u"your", u"yours", u"yourself", u"yourselves", u"what", u"ex", u"into", u"-"
  ];


def get_keywords(text):
    """get keywords from a text"""
    words = text.lower().split(' ')
    keywords = [w for w in words if w not in stopwords]
    return keywords

# Define notification event for thread completion
EVT_RESULT_ID = wx.NewId()


def EVT_RESULT(win, func):
    """Define Result Event."""
    win.Connect(-1, -1, EVT_RESULT_ID, func)

class ResultEvent(wx.PyEvent):
    """Simple event to carry arbitrary result data."""
    def __init__(self, data):
        """Init Result Event."""
        wx.PyEvent.__init__(self)
        self.SetEventType(EVT_RESULT_ID)
        self.data = data


# Thread class that executes urls fetching
class WorkerThread(Thread):
    """Worker Thread Class."""
    def __init__(self, url):
        """Init Worker Thread Class."""
        Thread.__init__(self)
        self._url = url
        self.start()

    def run(self):
        """Run Worker Thread."""  
        try:
            data =  urllib.urlopen(self._url).read()
            wx.PostEvent(self._notify_window, ResultEvent(self._url, data))
        except:
            pass

    def abort(self):
        """abort worker thread."""
        self._want_abort = 1


class Fieldset(wx.StaticBoxSizer):
    """Controls Wrapper that acts like a HTML Fieldset"""
    def __init__(self, parent, label="", cols=0, gap=10):
        self.cols = cols
        self.currentcol = 0
        self.currentrow = 0
        boite = wx.StaticBox(parent, label=label)
        wx.StaticBoxSizer.__init__(self, boite, wx.VERTICAL)
        self.sizer = wx.GridBagSizer(hgap=gap, vgap=gap)
        self.Add(self.sizer, flag=wx.EXPAND)

    def AddControls(self, *rows):
        #set cols if not specified
        if self.cols == 0:
            self.cols = max([len(row) for row in rows])
        for row in rows:
            self.currentcol = 0
            for control in row:
                x = self.currentrow
                y = self.currentcol
                if y == len(row)-1 and len(row)<self.cols:
                    spancols = self.cols-y
                    self.sizer.Add(control, pos=(x,y), span=(1, spancols), flag=wx.EXPAND)
                    self.sizer.AddGrowableCol(self.currentcol)
                else:
                    self.sizer.Add(control, pos=(x,y))

                self.currentcol += 1
            self.currentrow += 1





class FFUser(object):
    """A friendfeed's user"""
    def __init__(self, login):
        self.login = login

    def getFriends(self):
        f = friendfeed.FriendFeed()
        profile = f.fetch_user_profile(self.login)
        friends = profile['subscriptions']
        return [friend['nickname'] for friend in friends]

    def getActivity(self):
        f = friendfeed.FriendFeed()
        ethread = Thread(None,self._ffcall, None, ('fetch_user_feed', self.login, 'entries'))
        cthread = Thread(None,self._ffcall, None, ('fetch_user_comments_feed', self.login, 'comments'))
        lthread = Thread(None,self._ffcall, None, ('fetch_user_likes_feed', self.login, 'likes'))
        fthread = Thread(None,self._ffcall, None, ('fetch_user_profile', self.login, 'profile'))
        
        ethread.start()
        cthread.start()
        lthread.start()
        fthread.start()

        ethread.join()
        cthread.join()
        lthread.join()
        fthread.join()

        entries_titles = [e['title'] for e in self.entries["entries"]]

        hisblabla = ' '.join(entries_titles) 
        self.keywords = get_keywords(hisblabla)

        self.entries_ids = [e['id'] for e in self.entries["entries"]]
        self.comments_ids = [c['id'] for c in self.comments["entries"]]
        self.likes_ids = [l['id'] for l in self.likes["entries"]]
        self.friends = [friend['nickname'] for friend in self.profile['subscriptions']]

    def _ffcall(self, ffmethod, nick, attr):
        f = friendfeed.FriendFeed()
        setattr(self, attr, getattr(f, ffmethod)(nick))
        #wx.PostEvent(self._notify_window, ResultEvent(self._url, data))



