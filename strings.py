import xbmcaddon, xbmc

ADDON = xbmcaddon.Addon(id='script.tagoverview')
language = ADDON.getLocalizedString
ACTION_MOVE_LEFT       =  1 #Dpad Left
ACTION_MOVE_RIGHT      =  2 #Dpad Right
ACTION_MOVE_UP         =  3 #Dpad Up
ACTION_MOVE_DOWN       =  4 #Dpad Down
ACTION_PAGE_UP         =  5 #Left trigger
ACTION_PAGE_DOWN       =  6 #Right trigger
ACTION_SELECT_ITEM     =  7 #'A'
ACTION_SELECT_ITEM2    =  100 #Mouse Left Click'
ACTION_HIGHLIGHT_ITEM  =  8
ACTION_PARENT_DIR      =  9 #'B'
ACTION_PREVIOUS_MENU   = 10 #'Back'
ACTION_SHOW_INFO       = 11
ACTION_PAUSE           = 12
ACTION_STOP            = 13 #'Start'
ACTION_NEXT_ITEM       = 14
ACTION_PREV_ITEM       = 15
ACTION_XBUTTON	       = 18 #'X'
ACTION_YBUTTON 	       = 34	#'Y'
ACTION_MOUSEMOVE       = 90 # Mouse has moved
ACTION_PREVIOUS_MENU2  = 92 #'Back'
ACTION_CONTEXT_MENU    = 117 # pops up the context menu
ACTION_CONTEXT_MENU2   = 229 # pops up the context menu (remote control "title" button)

TAGLIST = 4
TAGMGMTBTN = 30
NEWTAGBTN = 30
PATHLABEL = 3

PROPERTY_TAGID                  = "tagid"
PROPERTY_MOVIEID                = "movieid"
PROPERTY_TYPE                   = "type"

PROPERTY_ENABLED = "enabled"

PROPSTATE_TRUE = "1"
PROPSTATE_FALSE = "0"
PROPSTATE_OFF = "2"

LABEL_CONFIRM                   = 40025     #Are you sure?"
LABEL_NEWTAG                    = 50000     #New Tag
LABEL_FILENAME                  = 50001     #Filename
LABEL_ADDTAGSTOMOVIE            = 50002     #Add Tags to Movie
LABEL_ADDMOVIE                  = 50003     #Add MOVIE

LABEL_SHOWMOVIES                = 50010     #Show tagged Movies
LABEL_SHOWTVSHOWS               = 50011     #*Show tagged TVShows
LABEL_SHOWMVIDEOS               = 50012     #*Show tagged musicvideos
LABEL_DELTAG                    = 50013     #*Delete this tag


LABEL_MAKESELECTION             = 50014     #Make a selection
LABEL_TAGSMGMT                  = 50015     #Tag overview
LABEL_NOTIMPLEMENTED            = 50016     #Not implemented
LABEL_WITHOUTTAG                = 50017     #Without Tag

LABEL_ADDMUSICVIDEO             = 50018     #Add Musicvideo
LABEL_ADDTVSHOW                 = 50019     #Add TVShow


PROPERTY_MOVIE          = 'movie'
PROPERTY_TVSHOW        =  'tvshow'
PROPERTY_MUSICVIDEO     = 'musicvideo'


def debug(msg, *args):
    try:
        txt=u''
        msg=unicode(msg)
        for arg in args:
            if type(arg) == int:
                arg = unicode(arg)
            if type(arg) == list:
                arg = unicode(arg)
            txt = txt + u"/" + arg
        if txt == u'':
            xbmc.log(u"Tag: {0}".format(msg).encode('ascii','xmlcharrefreplace'), xbmc.LOGDEBUG)
        else:
            xbmc.log(u"Tag: {0}#{1}#".format(msg, txt).encode('ascii','xmlcharrefreplace'), xbmc.LOGDEBUG)
    except:
        print("Error in Debugoutput")
        print(msg)
        print(args)

def error(msg, *args):
    txt=''
    for arg in args:
        if type(arg) == int:
            arg = str(arg)
        txt = txt + "/" + str(arg)
    if txt == '':
        xbmc.log("Tag: "+str(msg), xbmc.LOGERROR)
    else:
        xbmc.log("Tag: "+str(msg)+"#"+txt+"#", xbmc.LOGERROR)

def encode(s):
    return s.encode('utf-8','replace')

def decode(string):
    return string.decode('utf-8','replace')

def uc(s):
    return unicode(s, 'utf-8','replace')
