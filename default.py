# import the kodi python modules we are going to use
# see the kodi api docs to find out what functionality each module provides
import xbmc
import xbmcaddon
import sys
import xbmcgui  #overview

from CDialogTagOverview import CDialogTagOverview  #overview
from strings import *    #overview
from CThreadTagMovies import CThreadTagMovies   #overview

#Everything below is calling the original Tag Overview code
wnd = None
#this script is called when mapped key is pressed

debug("main before")
t = CThreadTagMovies()
t.start()

debug("main after")