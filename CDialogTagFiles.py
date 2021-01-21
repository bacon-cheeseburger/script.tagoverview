import xbmc, xbmcgui, xbmcaddon
from CVideoDatabase import CVideoDatabase
from strings import *
t=None
class CDialogTagFiles(xbmcgui.WindowXMLDialog):

    def __new__(cls):
        debug('CDialogTagFiles new')
        return super(CDialogTagFiles, cls).__new__(cls, "TagFiles.xml", ADDON.getAddonInfo('path'))

    #init window
    def __init__(self):
        debug('CDialogTagFiles init')
        self.idTag = -1

        super(CDialogTagFiles, self).__init__()

    #def doModal(self,idTag, type):
    def doModal(self,idTag, type, parent, **kwargs):
        debug('CDialogTagFiles doModal')
        self.idTag = idTag
        self.type = type
        self.parent = parent
        self.windowtitle = kwargs.get("windowtitle")
        xbmcgui.WindowXMLDialog.doModal(self)

    #init eventhandler
    def onInit( self ):
        debug('CDialogTagFiles oninit')
        super(CDialogTagFiles, self).__init__()
        self.buildList()
        self.getControl(1).setLabel(self.windowtitle)
        self.setFocusId(TAGLIST)

    #create the listview
    def buildList(self):
        debug('CDialogTagFiles buildList')
        self.vdb = CVideoDatabase()
        if self.idTag == "-1":
            movietags = self.vdb.getAllMoviesWithoutTag(self.type)
            self.name = ''
        else:
            debug("self.idTag",self.idTag)
            movietags = self.vdb.getAllMoviesWithTag(self.idTag, self.type)
            self.name = self.vdb.GetTagById(self.idTag)[0][1]
        debug('CDialogTagFiles buildList name: {0}, idTag: {1}'.format(self.name, self.idTag))
        control=self.getControl(TAGLIST)
        if self.idTag == "-1":
            for tag in movietags:
                control.addItem(self.createListItem(tag[1],PROPSTATE_OFF,tag[0]))
        else:
            if self.type == PROPERTY_MOVIE:
                control.addItem(self.createListItem(language(LABEL_ADDMOVIE),PROPSTATE_OFF,0))
            elif self.type == PROPERTY_MUSICVIDEO:
                control.addItem(self.createListItem(language(LABEL_ADDMUSICVIDEO),PROPSTATE_OFF,0))
            elif self.type == PROPERTY_TVSHOW:
                control.addItem(self.createListItem(language(LABEL_ADDTVSHOW),PROPSTATE_OFF,0))
            for tag in movietags:
                control.addItem(self.createListItem(tag[1],PROPSTATE_TRUE,tag[0]))

    #create a listitem for the listview and set properties
    def createListItem(self, label, enabled, movieid):
        li = xbmcgui.ListItem(encode(label))
        li.setProperty(PROPERTY_ENABLED,str(enabled))
        li.setProperty(PROPERTY_MOVIEID, str(movieid))
        li.setProperty(PROPERTY_TYPE, str(self.type))
        return li

    #control windowactions
    def onAction(self, action):
        if not (action.getId() == ACTION_SELECT_ITEM) or not (action.getId() == ACTION_SELECT_ITEM2):
            self.onAction1(action)
        if (action == ACTION_SELECT_ITEM) or (action == ACTION_SELECT_ITEM2):
            controlId = self.getFocusId()
            if controlId == TAGLIST:
                if self.idTag == "-1":
                    self.callTagWindow(self.getControl(controlId))
                else:
                    self.switchState(self.getControl(controlId))

    def callTagWindow(self,cntrl):
        global t
        debug('CDialogTagFiles callTagWindow before')
        li = cntrl.getSelectedItem()
        from CThreadTagMovies import CThreadTagMovies
        t = CThreadTagMovies(li.getProperty(PROPERTY_MOVIEID),li.getProperty(PROPERTY_TYPE))
        t.start()
        self.parent.close()
        self.close()
        debug('CDialogTagFiles callTagWindow after')
        return

    #switch the tag-radios on/off and create or delete the db-entry
    def switchState(self, cntrl):
        debug('CDialogTagFiles switchState')
        li = cntrl.getSelectedItem()
        if li.getProperty(PROPERTY_ENABLED) == PROPSTATE_OFF:
            idMovie = self.selectMovie(cntrl)
            if idMovie == -1:
                return
            self.AddTagToItem(self.idTag,idMovie, self.type)
        elif li.getProperty(PROPERTY_ENABLED) == PROPSTATE_TRUE:
            li.setProperty(PROPERTY_ENABLED,PROPSTATE_FALSE)
            idMovie = li.getProperty(PROPERTY_MOVIEID)
            self.RemoveTagFromItem(self.idTag,idMovie, self.type)
            self.idTag = self.AddTag(self.name)
            debug("CDialogTagFiles switchState lastrowid",self.idTag)
        cntrl.reset()
        self.buildList()

    def selectMovie(self,cntrl):
        debug("CDialogTagFiles selectMovie")
        if  self.type == PROPERTY_MOVIE:
            allmovies = self.vdb.GetAllMovies()
        elif  self.type == PROPERTY_MUSICVIDEO:
            allmovies = self.vdb.GetAllMusicvideos()
        elif  self.type == PROPERTY_TVSHOW:
            allmovies = self.vdb.GetAllTVShows()
        allmovies1 = []
        allmovies1[len(allmovies1):] = [x[1] for x in allmovies]
        selmovie = xbmcgui.Dialog()
        ret = selmovie.select(encode(language(LABEL_ADDMOVIE)), allmovies1)
        if ret == -1:
            return ret
        return allmovies[ret][0]

    def onAction1(self, action):
        if (action == ACTION_PREVIOUS_MENU) or (action == ACTION_PARENT_DIR) or (action == ACTION_PREVIOUS_MENU2):
            self.state = -1 #success
            self.close() #exit

    #helpfuntion to seperate the call to vdb-layer
    #connect tag and movie
    def AddTagToItem(self, idTag, idMovie, type):
        debug("CDialogTagFiles AddTagToItem",idMovie,idTag,type)
        return self.vdb.AddTagToItem(idMovie, idTag, type)

    #helpfuntion to seperate the call to vdb-layer
    #remove the connection between tag and movie
    def RemoveTagFromItem(self, idTag, idMovie, type):
        debug("CDialogTagFiles RemoveTagFromItem")
        self.vdb.RemoveTagFromItem(idMovie, idTag, type)

        #helpfuntion to seperate the call to vdb-layer
    #create a new tag
    def AddTag(self, value):
        debug("CDialogTagFiles AddTag")
        return self.vdb.AddToTable("tag", "tag_id", "name", value)

    #show keyboard, create tag and rebuild the listview
    def GetNewTag(self, cntrl):
        debug("CDialogTagFiles getnewtag")
        keyboard = xbmc.Keyboard('', language(LABEL_NEWTAG)) #50000
        keyboard.doModal()
        if keyboard.isConfirmed() and keyboard.getText():
            self.AddTag(keyboard.getText().strip())
            cntrl.reset()
            self.buildList()
