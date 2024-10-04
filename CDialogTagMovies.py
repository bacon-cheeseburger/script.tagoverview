import xbmc, xbmcgui, xbmcaddon
from CVideoDatabase import CVideoDatabase
from CThreadTagOverview import CThreadTagOverview
from strings import *

t=None
assetID = xbmc.getInfoLabel('ListItem.DBID')
assetTYPE = xbmc.getInfoLabel('ListItem.DBtype')
assetTITLE = xbmc.getInfoLabel('ListItem.label')
taggableAssets = ["movie", "tvshow", "musicvideo"]

class CDialogTagMovies(xbmcgui.WindowXMLDialog):
    #subclassing new to integrate the dialog definition into the dialog control class
    def __new__(cls):
        debug("CDialogTagMovies new")
        return super(CDialogTagMovies, cls).__new__(cls, "TagMovies.xml", ADDON.getAddonInfo('path'))

    #init window
    def __init__(self, *args, **kwargs):
        debug("CDialogTagMovies init")
        self.getFileInfos()
        super(CDialogTagMovies, self).__init__()

    #if the dialog is called from tagfiles with parameter the domodal function is extended to get the parameters
    def doModal(self,id=0, type=''):
        debug("CDialogTagMovies modal")
        if id!=0:
            self.entry = "modal"
            if type == PROPERTY_MOVIE:
                result = self.vdb.getMovieById(id)
            elif type == PROPERTY_MUSICVIDEO:
                result = self.vdb.getMusicvideosById(id)
            elif type == PROPERTY_TVSHOW:
                result = self.vdb.getTVShowsById(id)
            self.name = result[0][2]
            self.id     = assetID
            self.type   = assetTITLE
        xbmcgui.WindowXMLDialog.doModal(self)

        #init eventhandler
    def onInit( self ):
        debug("CDialogTagMovies onInit")
        #if nothing selected or plays then open tag overview and close this window
        #this cause this script to stop. the program continues in the new thread
        if assetTYPE not in taggableAssets:
            self.openTagOverview()
            self.close()
            return
        #set film title
        pl=self.getControl(PATHLABEL)
        pl.setLabel(assetTITLE)
        self.buildList()
        self.setFocusId(TAGLIST)

    #to workaround a memmory issue in my personal workflow with circular opening the windows
    #tagmovie,tagoverview,select movies with no tags, and open the tagmovie dialog again
    # i open the dialog in a seperate thread. the memory of the earlier opened dialogs are released
    def openTagOverview(self):
        global t
        debug("CDialogTagMovies call to open CDialogTagOverview window")
        t = CThreadTagOverview()
        t.start()

    #determine if a movie is selected or is playing and collect some informations
    #if a movie playing in background and another movie is selected, the player wins
    def getFileInfos(self):
        debug("CDialogTagMovies getFileInfos")
        self.player = xbmc.Player()
        self.vdb = CVideoDatabase()
        #self.filepath = decode(xbmc.getInfoLabel('ListItem.FileNameAndPath'))
        self.filepath = xbmc.getInfoLabel('ListItem.FileNameAndPath')
        self.path = xbmc.getInfoLabel('ListItem.Path')
        self.name = xbmc.getInfoLabel('ListItem.Label')
        self.dbid = xbmc.getInfoLabel('ListItem.DBID')
        self.entry = "selection"
        #self.dump()
        if self.player.isPlayingVideo():
            self.filepath = self.player.getPlayingFile()
            self.name = self.player.getVideoInfoTag().getTitle()
            self.entry = "player"
        if self.getData(self.vdb):
            debug(u"CDialogTagMovies Load Movietagging for '{0}' with path '{1}' by {2}, type: {3}, id: {4}".format(self.name, self.path, self.entry, self.type, self.id))
            return True
        else:
            debug(u"",self.name)
            debug(u"",self.path)
            debug(u"",self.entry)
            debug(u"",self.type)
            debug(u"",self.id)
            debug("CDialogTagMovies No valid item selected")
            return False

    #create the listview
    def buildList(self):
        debug("CDialogTagMovies buildList")
        alltags = self.vdb.GetAllTags()
        vidtags = self.vdb.GetVideoTags(assetID, assetTYPE)
        control=self.getControl(TAGLIST)
        control.addItem(self.createListItem(language(LABEL_NEWTAG),PROPSTATE_OFF,0)) #50000
        for tag in alltags:
            if self.TagInList(tag[1],vidtags):
                control.addItem(self.createListItem(tag[1],PROPSTATE_TRUE,tag[0]))
        for tag in alltags:
            if not self.TagInList(tag[1],vidtags):
                control.addItem(self.createListItem(tag[1],PROPSTATE_FALSE,tag[0]))

    #help function to test if a movie has already the tag
    def TagInList(self, tag, tags):
        for t in tags:
            if t[1] == tag:
                return True
        return False

    #collect id and type of the movie (movie, tvshow, musicvideo)

    def getData(self, vdb):
        debug("CDialogTagMovies getData")
        fileid = vdb.GetFileId(self.filepath)
        data = vdb.GetTypeAndId(fileid, self.path)
        debug("filepath",self.filepath)
        debug("self.path",self.path)
        debug("fileid",fileid)
        debug("data",data)
        if data != 0:
            self.id     = data[1]
            self.type   = data[0]
            self.name   = data[2]
            return True
        else:
            self.id     = 0
            self.type   = ''
            self.name   = ""
            return False

    #control windowactions
    def onAction(self, action):
        if not (action.getId() == ACTION_SELECT_ITEM) or not (action.getId() == ACTION_SELECT_ITEM2):
            self.onAction1(action)
        if (action == ACTION_SELECT_ITEM) or (action == ACTION_SELECT_ITEM2):
            controlId = self.getFocusId()
            if controlId == TAGLIST:
                self.switchState(self.getControl(controlId))
            if controlId == TAGMGMTBTN:
                self.openTagOverview()
                self.close()

    def onAction1(self, action):
        if (action == ACTION_PREVIOUS_MENU) or (action == ACTION_PARENT_DIR) or (action == ACTION_PREVIOUS_MENU2):
            self.state = -1 #success
            self.close() #exit

    #switch the tag-radios on/off or not visible and create or delete the db-entry
    def switchState(self, cntrl):
        debug("CDialogTagMovies switchState")
        li = cntrl.getSelectedItem()
        if li.getProperty(PROPERTY_ENABLED) == PROPSTATE_OFF:
            self.GetNewTag(cntrl)
            return
        if li.getProperty(PROPERTY_ENABLED) == PROPSTATE_TRUE:
            li.setProperty(PROPERTY_ENABLED,PROPSTATE_FALSE)
            tag_id = li.getProperty(PROPERTY_TAGID)
            self.RemoveTagToItem(tag_id,assetID, assetTYPE)
            debug('self.AddTag(li.getLabel()=', self.AddTag(li.getLabel()))
            li.setProperty(PROPERTY_TAGID, str(self.AddTag(li.getLabel())))
        else:
            li.setProperty(PROPERTY_ENABLED,PROPSTATE_TRUE)
            tag_id = li.getProperty(PROPERTY_TAGID)
            self.AddTagToItem(tag_id,assetID, assetTYPE)

    #helpfuntion to seperate the call to vdb-layer
    #create a new tag
    def AddTag(self, value):
        debug("CDialogTagMovies addtag")
        return self.vdb.AddToTable("tag", "tag_id", "name", value)

    #show keyboard, create tag and rebuild the listview
    def GetNewTag(self, cntrl):
        debug("CDialogTagMovies getnewtag")
        keyboard = xbmc.Keyboard('', language(LABEL_NEWTAG)) #50000
        keyboard.doModal()
        if keyboard.isConfirmed() and keyboard.getText():
            self.AddTag(decode(keyboard.getText().strip()))
            cntrl.reset()
            self.buildList()

    #helpfuntion to seperate the call to vdb-layer
    #connect tag and movie
    def AddTagToItem(self, tag_id, idMovie, type):
        self.vdb.AddTagToItem(idMovie, tag_id, type)

    #helpfuntion to seperate the call to vdb-layer
    #remove the connection between tag and movie
    def RemoveTagToItem(self, tag_id, idMovie, type):
        debug("CDialogTagMovies removetagtoitem")
        self.vdb.RemoveTagFromItem(idMovie, tag_id, type)

    #create a listitem for the listview and set properties
    def createListItem(self, label, enabled, tagid):
        li = xbmcgui.ListItem(label)
        li.setProperty(PROPERTY_ENABLED,str(enabled))
        li.setProperty(PROPERTY_TAGID, str(tagid))
        return li

    def dump(self):
        debug('Container.FolderPath',xbmc.getInfoLabel('Container.FolderPath'))
        debug('Container.FolderName',xbmc.getInfoLabel('Container.FolderName'))
        debug('Container.Viewmode',xbmc.getInfoLabel('Container.Viewmode'))
        debug('Container.SortMethod',xbmc.getInfoLabel('Container.SortMethod'))
        debug('Container.PluginName',xbmc.getInfoLabel('Container.PluginName'))
        debug('Container.PluginCategory',xbmc.getInfoLabel('Container.PluginCategory'))
        debug('Container.ShowPlot',xbmc.getInfoLabel('Container.ShowPlot'))
        debug('Fanart.Color1',xbmc.getInfoLabel('Fanart.Color1'))
        debug('Fanart.Color2',xbmc.getInfoLabel('Fanart.Color2'))
        debug('Fanart.Color3',xbmc.getInfoLabel('Fanart.Color3'))
        debug('Listitem.Label',xbmc.getInfoLabel('Listitem.Label'))
        debug('ListItem.Label2',xbmc.getInfoLabel('ListItem.Label2'))
        debug('ListItem.Title',xbmc.getInfoLabel('ListItem.Title'))
        debug('ListItem.OriginalTitle',xbmc.getInfoLabel('ListItem.OriginalTitle'))
        debug('ListItem.SortLetter',xbmc.getInfoLabel('ListItem.SortLetter'))
        debug('ListItem.TrackNumber',xbmc.getInfoLabel('ListItem.TrackNumber'))
        debug('ListItem.Artist',xbmc.getInfoLabel('ListItem.Artist'))
        debug('ListItem.Album',xbmc.getInfoLabel('ListItem.Album'))
        debug('ListItem.DiscNumber',xbmc.getInfoLabel('ListItem.DiscNumber'))
        debug('ListItem.Year',xbmc.getInfoLabel('ListItem.Year'))
        debug('ListItem.Premiered',xbmc.getInfoLabel('ListItem.Premiered'))
        debug('ListItem.Genre',xbmc.getInfoLabel('ListItem.Genre'))
        debug('ListItem.Director',xbmc.getInfoLabel('ListItem.Director'))
        debug('ListItem.Country',xbmc.getInfoLabel('ListItem.Country'))
        debug('ListItem.Episode',xbmc.getInfoLabel('ListItem.Episode'))
        debug('ListItem.Season',xbmc.getInfoLabel('ListItem.Season'))
        debug('ListItem.TVShowTitle',xbmc.getInfoLabel('ListItem.TVShowTitle'))
        debug('ListItem.FileName',xbmc.getInfoLabel('ListItem.FileName'))
        debug('ListItem.Path',xbmc.getInfoLabel('ListItem.Path'))
        debug('ListItem.FolderName',xbmc.getInfoLabel('ListItem.FolderName'))
        debug('ListItem.FileNameAndPath',xbmc.getInfoLabel('ListItem.FileNameAndPath'))
        debug('ListItem.FileExtension',xbmc.getInfoLabel('ListItem.FileExtension'))
        debug('ListItem.Date',xbmc.getInfoLabel('ListItem.Date'))
        debug('ListItem.DateAdded',xbmc.getInfoLabel('ListItem.DateAdded'))
        debug('ListItem.Size',xbmc.getInfoLabel('ListItem.Size'))
        debug('ListItem.Rating',xbmc.getInfoLabel('ListItem.Rating'))
        debug('ListItem.Votes',xbmc.getInfoLabel('ListItem.Votes'))
        debug('ListItem.RatingAndVotes',xbmc.getInfoLabel('ListItem.RatingAndVotes'))
        debug('ListItem.Mpaa',xbmc.getInfoLabel('ListItem.Mpaa'))
        debug('ListItem.ProgramCount',xbmc.getInfoLabel('ListItem.ProgramCount'))
        debug('ListItem.Duration',xbmc.getInfoLabel('ListItem.Duration'))
        debug('ListItem.DBID',xbmc.getInfoLabel('ListItem.DBID'))
        debug('ListItem.Cast',xbmc.getInfoLabel('ListItem.Cast'))
        debug('ListItem.CastAndRole',xbmc.getInfoLabel('ListItem.CastAndRole'))
        debug('ListItem.Studio',xbmc.getInfoLabel('ListItem.Studio'))
        debug('ListItem.Trailer',xbmc.getInfoLabel('ListItem.Trailer'))
        debug('ListItem.Writer',xbmc.getInfoLabel('ListItem.Writer'))
        debug('ListItem.Tagline',xbmc.getInfoLabel('ListItem.Tagline'))
        debug('ListItem.PlotOutline',xbmc.getInfoLabel('ListItem.PlotOutline'))
        debug('ListItem.Plot',xbmc.getInfoLabel('ListItem.Plot'))
        debug('ListItem.PercentPlayed',xbmc.getInfoLabel('ListItem.PercentPlayed'))
        debug('ListItem.LastPlayed',xbmc.getInfoLabel('ListItem.LastPlayed'))
        debug('ListItem.PlayCount',xbmc.getInfoLabel('ListItem.PlayCount'))
        debug('ListItem.StartTime',xbmc.getInfoLabel('ListItem.StartTime'))
        debug('ListItem.EndTime',xbmc.getInfoLabel('ListItem.EndTime'))
        debug('ListItem.StartDate',xbmc.getInfoLabel('ListItem.StartDate'))
        debug('ListItem.Date',xbmc.getInfoLabel('ListItem.Date'))
        debug('ListItem.ChannelNumber',xbmc.getInfoLabel('ListItem.ChannelNumber'))
        debug('ListItem.ChannelName',xbmc.getInfoLabel('ListItem.ChannelName'))
        debug('ListItem.VideoCodec',xbmc.getInfoLabel('ListItem.VideoCodec'))
        debug('ListItem.VideoResolution',xbmc.getInfoLabel('ListItem.VideoResolution'))
        debug('ListItem.VideoAspect',xbmc.getInfoLabel('ListItem.VideoAspect'))
        debug('ListItem.SubtitleLanguage',xbmc.getInfoLabel('ListItem.SubtitleLanguage'))
        debug('ListItem.StartTime',xbmc.getInfoLabel('ListItem.StartTime'))
        debug('ListItem.EndTime',xbmc.getInfoLabel('ListItem.EndTime'))
        debug('ListItem.StartDate',xbmc.getInfoLabel('ListItem.StartDate'))
        debug('ListItem.EndDate',xbmc.getInfoLabel('ListItem.EndDate'))
        debug('ListItem.NextTitle',xbmc.getInfoLabel('ListItem.NextTitle'))
        debug('ListItem.NextGenre',xbmc.getInfoLabel('ListItem.NextGenre'))
        debug('ListItem.NextPlot',xbmc.getInfoLabel('ListItem.NextPlot'))
        debug('ListItem.NextPlotOutline',xbmc.getInfoLabel('ListItem.NextPlotOutline'))
        debug('ListItem.NextStartTime',xbmc.getInfoLabel('ListItem.NextStartTime'))
        debug('ListItem.NextEndTime',xbmc.getInfoLabel('ListItem.NextEndTime'))
        debug('ListItem.NextStartDate',xbmc.getInfoLabel('ListItem.NextStartDate'))
        debug('ListItem.NextEndDate',xbmc.getInfoLabel('ListItem.NextEndDate'))
        debug('ListItem.ChannelName',xbmc.getInfoLabel('ListItem.ChannelName'))
        debug('ListItem.ChannelNumber',xbmc.getInfoLabel('ListItem.ChannelNumber'))
        debug('ListItem.ChannelGroup',xbmc.getInfoLabel('ListItem.ChannelGroup'))
        debug('ListItem.Progress',xbmc.getInfoLabel('ListItem.Progress'))
        debug('Network.IPAddress',xbmc.getInfoLabel('Network.IPAddress'))
        debug('Network.MacAddress',xbmc.getInfoLabel('Network.MacAddress'))
        debug('Network.IsDHCP',xbmc.getInfoLabel('Network.IsDHCP'))
        debug('Network.LinkState',xbmc.getInfoLabel('Network.LinkState'))
        debug('Network.SubnetAddress',xbmc.getInfoLabel('Network.SubnetAddress'))
        debug('Network.GatewayAddress',xbmc.getInfoLabel('Network.GatewayAddress'))
        debug('Network.DHCPAddress',xbmc.getInfoLabel('Network.DHCPAddress'))
        debug('Network.DNS1Address',xbmc.getInfoLabel('Network.DNS1Address'))
        debug('Network.DNS2Address',xbmc.getInfoLabel('Network.DNS2Address'))
        debug('Player.FinishTime',xbmc.getInfoLabel('Player.FinishTime'))
        debug('Player.Chapter',xbmc.getInfoLabel('Player.Chapter'))
        debug('Player.ChapterCount',xbmc.getInfoLabel('Player.ChapterCount'))
        debug('Player.Time',xbmc.getInfoLabel('Player.Time'))
        debug('Player.TimeRemaining',xbmc.getInfoLabel('Player.TimeRemaining'))
        debug('Player.Duration',xbmc.getInfoLabel('Player.Duration'))
        debug('Player.SeekTime',xbmc.getInfoLabel('Player.SeekTime'))
        debug('Player.SeekOffset',xbmc.getInfoLabel('Player.SeekOffset'))
        debug('Player.Volume',xbmc.getInfoLabel('Player.Volume'))
        debug('Player.CacheLevel',xbmc.getInfoLabel('Player.CacheLevel'))
        debug('Player.ProgressCache',xbmc.getInfoLabel('Player.ProgressCache'))
        debug('Player.Folderpath',xbmc.getInfoLabel('Player.Folderpath'))
        debug('Player.Filenameandpath',xbmc.getInfoLabel('Player.Filenameandpath'))
        debug('Player.StartTime',xbmc.getInfoLabel('Player.StartTime'))
        debug('Player.Title',xbmc.getInfoLabel('Player.Title'))
        debug('Playlist.Position',xbmc.getInfoLabel('Playlist.Position'))
        debug('Playlist.Length',xbmc.getInfoLabel('Playlist.Length'))
        debug('Playlist.Random',xbmc.getInfoLabel('Playlist.Random'))
        debug('Playlist.Repeat',xbmc.getInfoLabel('Playlist.Repeat'))
        debug('Skin.CurrentTheme',xbmc.getInfoLabel('Skin.CurrentTheme'))
        debug('Skin.CurrentColourTheme',xbmc.getInfoLabel('Skin.CurrentColourTheme'))
        debug('Skin.AspectRatio',xbmc.getInfoLabel('Skin.AspectRatio'))
        debug('System.Time',xbmc.getInfoLabel('System.Time'))
        debug('System.Date',xbmc.getInfoLabel('System.Date'))
        debug('System.AlarmPos',xbmc.getInfoLabel('System.AlarmPos'))
        debug('System.BatteryLevel',xbmc.getInfoLabel('System.BatteryLevel'))
        debug('System.FreeSpace',xbmc.getInfoLabel('System.FreeSpace'))
        debug('System.UsedSpace',xbmc.getInfoLabel('System.UsedSpace'))
        debug('System.TotalSpace',xbmc.getInfoLabel('System.TotalSpace'))
        debug('System.UsedSpacePercent',xbmc.getInfoLabel('System.UsedSpacePercent'))
        debug('System.FreeSpacePercent',xbmc.getInfoLabel('System.FreeSpacePercent'))
        debug('System.CPUTemperature',xbmc.getInfoLabel('System.CPUTemperature'))
        debug('System.GPUTemperature',xbmc.getInfoLabel('System.GPUTemperature'))
        debug('System.FanSpeed',xbmc.getInfoLabel('System.FanSpeed'))
        debug('System.BuildVersion',xbmc.getInfoLabel('System.BuildVersion'))
        debug('System.BuildDate',xbmc.getInfoLabel('System.BuildDate'))
        debug('System.FriendlyName',xbmc.getInfoLabel('System.FriendlyName'))
        debug('System.FPS',xbmc.getInfoLabel('System.FPS'))
        debug('System.FreeMemory',xbmc.getInfoLabel('System.FreeMemory'))
        debug('System.ScreenMode',xbmc.getInfoLabel('System.ScreenMode'))
        debug('System.ScreenWidth',xbmc.getInfoLabel('System.ScreenWidth'))
        debug('System.ScreenHeight',xbmc.getInfoLabel('System.ScreenHeight'))
        debug('System.StartupWindow',xbmc.getInfoLabel('System.StartupWindow'))
        debug('System.CurrentWindow',xbmc.getInfoLabel('System.CurrentWindow'))
        debug('System.CurrentControl',xbmc.getInfoLabel('System.CurrentControl'))
        debug('System.DVDLabel',xbmc.getInfoLabel('System.DVDLabel'))
        debug('System.HddTemperature',xbmc.getInfoLabel('System.HddTemperature'))
        debug('System.KernelVersion',xbmc.getInfoLabel('System.KernelVersion'))
        debug('System.Uptime',xbmc.getInfoLabel('System.Uptime'))
        debug('System.TotalUptime',xbmc.getInfoLabel('System.TotalUptime'))
        debug('System.CpuFrequency',xbmc.getInfoLabel('System.CpuFrequency'))
        debug('System.ScreenResolution',xbmc.getInfoLabel('System.ScreenResolution'))
        debug('System.VideoEncoderInfo',xbmc.getInfoLabel('System.VideoEncoderInfo'))
        debug('System.InternetState',xbmc.getInfoLabel('System.InternetState'))
        debug('System.Language',xbmc.getInfoLabel('System.Language'))
        debug('System.ProfileName',xbmc.getInfoLabel('System.ProfileName'))
        debug('System.ProfileCount',xbmc.getInfoLabel('System.ProfileCount'))
        debug('System.ProfileAutoLogin',xbmc.getInfoLabel('System.ProfileAutoLogin'))
        debug('System.TemperatureUnits',xbmc.getInfoLabel('System.TemperatureUnits'))
        debug('Visualisation.Preset',xbmc.getInfoLabel('Visualisation.Preset'))
        debug('Visualisation.Name',xbmc.getInfoLabel('Visualisation.Name'))
        debug('VideoPlayer.Time',xbmc.getInfoLabel('VideoPlayer.Time'))
        debug('VideoPlayer.TimeRemaining',xbmc.getInfoLabel('VideoPlayer.TimeRemaining'))
        debug('VideoPlayer.TimeSpeed',xbmc.getInfoLabel('VideoPlayer.TimeSpeed'))
        debug('VideoPlayer.Duration',xbmc.getInfoLabel('VideoPlayer.Duration'))
        debug('VideoPlayer.Title',xbmc.getInfoLabel('VideoPlayer.Title'))
        debug('VideoPlayer.TVShowTitle',xbmc.getInfoLabel('VideoPlayer.TVShowTitle'))
        debug('VideoPlayer.Season',xbmc.getInfoLabel('VideoPlayer.Season'))
        debug('VideoPlayer.Episode',xbmc.getInfoLabel('VideoPlayer.Episode'))
        debug('VideoPlayer.Genre',xbmc.getInfoLabel('VideoPlayer.Genre'))
        debug('VideoPlayer.Director',xbmc.getInfoLabel('VideoPlayer.Director'))
        debug('VideoPlayer.Country',xbmc.getInfoLabel('VideoPlayer.Country'))
        debug('VideoPlayer.Year',xbmc.getInfoLabel('VideoPlayer.Year'))
        debug('VideoPlayer.Rating',xbmc.getInfoLabel('VideoPlayer.Rating'))
        debug('VideoPlayer.Votes',xbmc.getInfoLabel('VideoPlayer.Votes'))
        debug('VideoPlayer.RatingAndVotes',xbmc.getInfoLabel('VideoPlayer.RatingAndVotes'))
        debug('VideoPlayer.mpaa',xbmc.getInfoLabel('VideoPlayer.mpaa'))
        debug('VideoPlayer.PlaylistPosition',xbmc.getInfoLabel('VideoPlayer.PlaylistPosition'))
        debug('VideoPlayer.PlaylistLength',xbmc.getInfoLabel('VideoPlayer.PlaylistLength'))
        debug('VideoPlayer.Cast',xbmc.getInfoLabel('VideoPlayer.Cast'))
        debug('VideoPlayer.CastAndRole',xbmc.getInfoLabel('VideoPlayer.CastAndRole'))
        debug('VideoPlayer.Album',xbmc.getInfoLabel('VideoPlayer.Album'))
        debug('VideoPlayer.Artist',xbmc.getInfoLabel('VideoPlayer.Artist'))
        debug('VideoPlayer.Studio',xbmc.getInfoLabel('VideoPlayer.Studio'))
        debug('VideoPlayer.Writer',xbmc.getInfoLabel('VideoPlayer.Writer'))
        debug('VideoPlayer.Tagline',xbmc.getInfoLabel('VideoPlayer.Tagline'))
        debug('VideoPlayer.PlotOutline',xbmc.getInfoLabel('VideoPlayer.PlotOutline'))
        debug('VideoPlayer.Plot',xbmc.getInfoLabel('VideoPlayer.Plot'))
        debug('VideoPlayer.LastPlayed',xbmc.getInfoLabel('VideoPlayer.LastPlayed'))
        debug('VideoPlayer.PlayCount',xbmc.getInfoLabel('VideoPlayer.PlayCount'))
        debug('VideoPlayer.VideoCodec',xbmc.getInfoLabel('VideoPlayer.VideoCodec'))
        debug('VideoPlayer.VideoResolution',xbmc.getInfoLabel('VideoPlayer.VideoResolution'))
        debug('VideoPlayer.VideoAspect',xbmc.getInfoLabel('VideoPlayer.VideoAspect'))
        debug('VideoPlayer.EndTime',xbmc.getInfoLabel('VideoPlayer.EndTime'))
        debug('VideoPlayer.NextTitle',xbmc.getInfoLabel('VideoPlayer.NextTitle'))
        debug('VideoPlayer.NextGenre',xbmc.getInfoLabel('VideoPlayer.NextGenre'))
        debug('VideoPlayer.NextPlot',xbmc.getInfoLabel('VideoPlayer.NextPlot'))
        debug('VideoPlayer.NextPlotOutline',xbmc.getInfoLabel('VideoPlayer.NextPlotOutline'))
        debug('VideoPlayer.NextStartTime',xbmc.getInfoLabel('VideoPlayer.NextStartTime'))
        debug('VideoPlayer.NextEndTime',xbmc.getInfoLabel('VideoPlayer.NextEndTime'))
        debug('VideoPlayer.NextDuration',xbmc.getInfoLabel('VideoPlayer.NextDuration'))
        debug('VideoPlayer.ChannelName',xbmc.getInfoLabel('VideoPlayer.ChannelName'))
        debug('VideoPlayer.ChannelNumber',xbmc.getInfoLabel('VideoPlayer.ChannelNumber'))
        debug('VideoPlayer.ChannelGroup',xbmc.getInfoLabel('VideoPlayer.ChannelGroup'))
        debug('VideoPlayer.ParentalRating',xbmc.getInfoLabel('VideoPlayer.ParentalRating'))
        debug('Weather.Conditions',xbmc.getInfoLabel('Weather.Conditions'))
        debug('Weather.Temperature',xbmc.getInfoLabel('Weather.Temperature'))
        debug('Weather.Location',xbmc.getInfoLabel('Weather.Location'))
