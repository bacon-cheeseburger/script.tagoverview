import threading
from CDialogTagMovies import CDialogTagMovies
from strings import *

class CThreadTagMovies(threading.Thread):
    def __init__(self, movieId=0, type=''):
        threading.Thread.__init__(self)
        self.movieId = movieId
        self.type = type
    def run(self):
        debug("CThreadTagMovies run start")
        wnd = CDialogTagMovies()
        if self.movieId != 0 and self.type != '':
            wnd.doModal(self.movieId, self.type)
        else:
            wnd.doModal()
        debug("CThreadTagMovies run stop")
