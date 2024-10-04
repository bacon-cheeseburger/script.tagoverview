import threading
from CDialogTagOverview import CDialogTagOverview
from strings import *

class CThreadTagOverview(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
    def run(self):
        debug("CThreadTagOverview run start")
        wnd = CDialogTagOverview()
        wnd.doModal()
        debug("CThreadTagOverview run stop")
