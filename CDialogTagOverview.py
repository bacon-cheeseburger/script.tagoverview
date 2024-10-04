import xbmc, xbmcgui, xbmcaddon
from CVideoDatabase import CVideoDatabase
from CDialogTagFiles import CDialogTagFiles
from strings import *

class CDialogTagOverview(xbmcgui.WindowXMLDialog):
    #subclassing new to integrate the dialog definition into the dialog control class
    def __new__(cls):
        debug("CDialogTagOverview open")
        return super(CDialogTagOverview, cls).__new__(cls, "TagOverview.xml", ADDON.getAddonInfo('path'))

        #init window
    def __init__(self):
        debug("CDialogTagOverview init")
        super(CDialogTagOverview, self).__init__()

    #init eventhandler
    def onInit( self ):
        debug("CDialogTagOverview onInit")
        self.buildList()
        self.setFocusId(TAGLIST)

    #create the listview
    #count the movies/tvshows/musicvideos with a special tag
    #additional it shows the same for all without a tag
    def buildList(self):
        debug("CDialogTagOverview buildList")
        self.vdb = CVideoDatabase()
        control=self.getControl(TAGLIST)
        mo = len(self.vdb.getAllMoviesWithoutTag(PROPERTY_MOVIE))
        ep = len(self.vdb.getAllMoviesWithoutTag(PROPERTY_TVSHOW))
        mv = len(self.vdb.getAllMoviesWithoutTag(PROPERTY_MUSICVIDEO))
        control.addItem(self.createListItem(encode(language(LABEL_WITHOUTTAG)),mo, ep, mv,-1))
        #control.addItem(self.createListItem(encode(language(LABEL_WITHOUTTAG)),16, 3, 6,-1))
        cnttags = self.vdb.GetCountedTags()
        name = ''
        ep = 0
        mv = 0
        mo = 0
        prevId=''
        for tag in cnttags:
            if tag[3] != prevId and prevId != '':
                control.addItem(self.createListItem(name,mo, ep, mv,tagId))
                name = ''
                ep = 0
                mv = 0
                mo = 0
                tagId = 0
            name = tag[0]
            tagId = tag[3]
            if tag[1] == PROPERTY_MOVIE:
                mo = tag[2]
            if tag[1] == PROPERTY_TVSHOW:
                ep = tag[2]
            if tag[1] == PROPERTY_MUSICVIDEO:
                mv = tag[2]
            prevId = tagId
        if name != '':
            control.addItem(self.createListItem(name,mo, ep, mv, tagId))

    #create a listitem for the listview and set properties
    def createListItem(self, tag, movie, tvshow, musicvideo,tagId):
        li = xbmcgui.ListItem(tag)
        li.setProperty(PROPERTY_MOVIE, str(movie))
        li.setProperty(PROPERTY_TVSHOW, str(tvshow))
        li.setProperty(PROPERTY_MUSICVIDEO, str(musicvideo))
        li.setProperty(PROPERTY_TAGID, str(tagId))
        return li

    #control windowactions
    def onAction(self, action):
        if not (action.getId() == ACTION_SELECT_ITEM) or not (action.getId() == ACTION_SELECT_ITEM2):
            self.onAction1(action)
        if (action == ACTION_SELECT_ITEM) or (action == ACTION_SELECT_ITEM2):
            controlId = self.getFocusId()
            if controlId == TAGLIST:
                self.tagSelected(self.getControl(controlId))
            if controlId == NEWTAGBTN:
                self.GetNewTag(self.getControl(TAGLIST))

    #show keyboard, create tag and rebuild the listview
    def GetNewTag(self, cntrl):
        debug("CDialogTagOverview getnewtag")
        keyboard = xbmc.Keyboard('', language(LABEL_NEWTAG)) #50000
        keyboard.doModal()
        if keyboard.isConfirmed() and keyboard.getText():
            self.AddTag(keyboard.getText().strip())
            cntrl.reset()
            self.buildList()

    #show a little select dialog to see the detailed movies/tvshows/musicvideos for a single tag
    #additional you can get a list of all without a tag
    #or delete a complete tag
    #atm only the movie part is implemented
    def tagSelected(self, control):
        wnd = None
        okdialog = None
        seldialog = xbmcgui.Dialog()

        #assetMsg = "'%s'" % control.getSelectedItem().getProperty(PROPERTY_TAGID)
        #xbmc.executebuiltin("Notification(\"Tag Quick Edit\", \"%s\")" % assetMsg)

        if control.getSelectedItem().getProperty(PROPERTY_TAGID) == '-1':
            TagName = encode(language(LABEL_WITHOUTTAG))
        else:
            TagName = self.vdb.GetTagById(control.getSelectedItem().getProperty(PROPERTY_TAGID))[0][1]

        ret = seldialog.select(encode(language(LABEL_MAKESELECTION)), [encode(language(LABEL_SHOWMOVIES)),encode(language(LABEL_SHOWTVSHOWS)),encode(language(LABEL_SHOWMVIDEOS)), encode(language(LABEL_DELTAG))])
        if ret == 0: #show movies
            debug("CDialogTagOverview tagSelected movies before")
            wnd = CDialogTagFiles()
            wnd.doModal(control.getSelectedItem().getProperty(PROPERTY_TAGID),PROPERTY_MOVIE, self, windowtitle=TagName)
            debug("CDialogTagOverview tagSelected movies after")
        elif ret == 1: #show tvshows
            debug("CDialogTagOverview tagSelected tvshow before")
            wnd = CDialogTagFiles()
            wnd.doModal(control.getSelectedItem().getProperty(PROPERTY_TAGID),PROPERTY_TVSHOW, self, windowtitle=TagName)
            debug("CDialogTagOverview tagSelected tvshow after")
        elif ret == 2: #show music videos
            debug("CDialogTagOverview tagSelected music before")
            wnd = CDialogTagFiles()
            wnd.doModal(control.getSelectedItem().getProperty(PROPERTY_TAGID),PROPERTY_MUSICVIDEO, self, windowtitle=TagName)
            debug("CDialogTagOverview tagSelected music after")
        elif ret == 3: #delete tag
            debug("CDialogTagOverview tagSelected delete tag")
            debug("Trying OK dialogue")
            dialog = xbmcgui.Dialog()
            confirm = dialog.yesno(language(LABEL_DELTAG)+": "+TagName, language(LABEL_CONFIRM))
            if confirm:
                self.deleteTag(control, control.getSelectedItem().getProperty(PROPERTY_TAGID))
        control.reset()
        self.buildList()

    def onAction1(self, action):
        if (action == ACTION_PREVIOUS_MENU) or (action == ACTION_PARENT_DIR) or (action == ACTION_PREVIOUS_MENU2):
            self.state = -1 #success
            self.close() #exit

    def deleteTag(self, cntrl, tag_id):
        debug("CDialogTagOverview deletetag tag_id:",tag_id)
        self.vdb.Removetag_link(tag_id)
        #this line is normaly not needed because of the standard delete-trigger of tag_link. but if no record in tag_link is deleted we have to delete the tag seperately
        self.vdb.RemoveTag(tag_id)

    #helpfuntion to seperate the call to vdb-layer
    #create a new tag
    def AddTag(self, value):
        debug("CDialogTagOverview addtag")
        self.vdb.AddToTable("tag", "tag_id", "name", value)

    #show keyboard, create tag and rebuild the listview
    def GetNewTag(self, cntrl):
        debug("CDialogTagOverview getnewtag")
        keyboard = xbmc.Keyboard('', language(LABEL_NEWTAG)) #50000
        keyboard.doModal()
        if keyboard.isConfirmed() and keyboard.getText():
            self.AddTag(keyboard.getText().strip())
            cntrl.reset()
            self.buildList()
