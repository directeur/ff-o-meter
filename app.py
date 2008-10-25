#!/usr/bin/env python
#-*- encoding: utf-8 -*-

import wx
from threading import *
import sets
from utils import Fieldset, FFUser

# Define notification event for HeavyCall thread completion
EVT_READY_ID = wx.NewId()


def EVT_READY(win, func):
    """Define Result Event."""
    win.Connect(-1, -1, EVT_READY_ID, func)


class ReadyEvent(wx.PyEvent):
    """Simple event to carry arbitrary result data."""
    def __init__(self, data=None):
        """Init Result Event."""
        wx.PyEvent.__init__(self)
        self.SetEventType(EVT_READY_ID)
        self.data = data


# Thread class that executes processing
class HeavyCall(Thread):
    """Calls func and then renders."""
    def __init__(self, caller, func, *args, **kwargs):
        """Init Worker Thread Class."""
        Thread.__init__(self)
        self.caller = caller
        self.func = func
        self.args = args
        self.kwargs = kwargs
        self.start()

    def run(self):
        """Run the HeavyCall Thread."""  
        try:
            self.caller._message_on = True
            method = getattr(self.caller, self.func)
            entries = method(*self.args, **self.kwargs)
            wx.PostEvent(self.caller, ReadyEvent(entries))
        except Exception, e:
            print (e)
            #pass

    def abort(self):
        """abort HeavyCall thread."""
        self._want_abort = 1


class MainFrame(wx.Frame):
    """The main app's window"""
    def __init__(self, title='Friendfeed-O-meter'):
        wx.Frame.__init__(self, parent=None, id=-1, title=title, size=(500, 300))
        self.sizer = wx.BoxSizer(wx.VERTICAL)

        #authentication data
        self.login = ''
        self.key = ''

        self.Center()

        UsersFildset = Fieldset(self, 'Two users to check')
        u1label = wx.StaticText(self, -1, label=u'User A')
        self.u1 = wx.TextCtrl(self, -1)
        vs = wx.StaticText(self, -1, label=u'<=======>')
        u2label = wx.StaticText(self, -1, label=u'User B')
        self.u2 = wx.TextCtrl(self, -1)

        self.check = wx.Button(self, -1, u"O'meter 'em!")
        UsersFildset.AddControls(
                [u1label, self.u1, vs, u2label, self.u2], 
                )


        ResultsFildset = Fieldset(self, u"O'metering Results")
        self.result = wx.StaticText(self, -1, 'Click on the button above :)')
        ResultsFildset.AddControls(
                [self.result], 
                )
        

        self.sizer.Add(UsersFildset, border=10, flag=wx.EXPAND|wx.ALL)
        self.sizer.Add(self.check, border=10, flag=wx.ALL|wx.ALIGN_RIGHT)
        self.sizer.Add(ResultsFildset, border=10, flag=wx.EXPAND|wx.ALL)
        self.SetSizer(self.sizer)
        self.sizer.Fit(self)

        self.check.Bind(wx.EVT_BUTTON, self.OnCheck)

    def OnCheck(self, event):
        self.result.SetLabel(u'Computing... please hold on')
        self.worker = HeavyCall(self, '_compute')
        EVT_READY(self, self.OnDataReady)


    def _compute(self):
        self.user1 = FFUser(self.u1.GetValue())
        self.user2 = FFUser(self.u2.GetValue())
        self.user1.getActivity()
        self.user2.getActivity()
        wx.PostEvent(self, ReadyEvent())

    def OnDataReady(self, event):
        f1 = set(self.user1.friends)
        f2 = set(self.user2.friends)
        commonfriends = list(f1 & f2)
        friendsproximity = len(commonfriends) 

        
        k1 = set(self.user1.keywords)
        k2 = set(self.user2.keywords)
        commonkeywords = list(k1 & k2)
        keywordproximity = len(commonkeywords) 

        c1 = set(self.user1.comments_ids)
        c2 = set(self.user2.comments_ids)
        commoncomments = list(c1 & c2)
        commentproximity = len(commoncomments) 

        l1 = set(self.user1.likes_ids)
        l2 = set(self.user2.likes_ids)
        commonlikes = list(l1 & l2)
        likeproximity = len(commonlikes) 

        self.result.SetLabel( ' %d common friends\n %d common keywords\n %d common Likes\n %d common entries commented on' % \
                (friendsproximity, keywordproximity, commentproximity, likeproximity))




if __name__ == '__main__':
    app = wx.App(False)
    mainframe = MainFrame()
    mainframe.Show()
    app.MainLoop()
