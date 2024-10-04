from CDatabase import CDatabase
from strings import *

#some functions are inspired from the CVideoDatabase class of the xbmc c++ code
class CVideoDatabase:
    def __init__(self, *args, **kwargs):
        debug("CVideoDatabase init")
        self.db = CDatabase()
        self.cur = self.db.con.cursor()

    #add an item to a table
    def AddToTable(self, table, firstField, secondField, value):
        debug("CVideoDatabase AddToTable")
        sql = "select %s from %s where %s like %s" % (firstField, table, secondField,self.db.pparam)
        print(sql)
        self.cur.execute(sql,((value),))
        row = self.cur.fetchone()
        if row is None:
            sql = "INSERT INTO %s (%s, %s) values(NULL, %s)" % (table, firstField, secondField, self.db.pparam)
            print(sql)
            self.cur.execute(sql,((value),))
            self.db.con.commit()
            debug("CVideoDatabase cursor",self.cur.lastrowid)
            return self.cur.lastrowid
        else:
            return row[0]

    #add a connection between two records
    def AddToLinkTable(self, table, firstField, firstID, secondField, secondID, typeField, type):
        debug("CVideoDatabase AddToLinkTable: table:{0} firstField:{1} firstID:{2} secondField:{3} secondID:{4} typeField:{5} type:{6} ".format(table, firstField, firstID, secondField, secondID, typeField, type))
        sql="select * from %s where %s=%s and %s=%s" % (table, firstField, firstID, secondField, secondID)
        if ((typeField is not None) and (type is not None)):
            sql = sql + " and %s = %s" % (typeField,self.db.pparam)
            debug("CVideoDatabase AddToLinkTable sql select", sql)
            self.cur.execute(sql,((type),))
            row = self.cur.fetchone()
            if row is None:
                if (typeField is None or type is None):
                    sql = "insert into %s (%s,%s) values(%s,%s)" % (table, firstField, secondField, self.db.pparam, self.db.pparam)
                    self.cur.execute(sql,((firstID, secondID)))
                else:
                    sql = "insert into %s (%s,%s,%s) values(%s,%s,%s)" % (table, firstField, secondField, typeField, self.db.pparam, self.db.pparam, self.db.pparam)
                    self.cur.execute(sql,((firstID, secondID, type)))
                debug("CVideoDatabase AddToLinkTable insert sql",sql)
                self.db.con.commit()
                return self.cur.lastrowid
            else:
                return row[0]

    #remove the connection between two records
    def RemoveFromLinkTable(self, table, firstField, firstID, secondField, secondID, typeField, type):
        debug("CVideoDatabase RemoveFromLinkTable: table:{0} firstField:{1} firstID:{2} secondField:{3} secondID:{4} typeField:{5} type:{6} ".format(table, firstField, firstID, secondField, secondID, typeField, type))
        #sql = "DELETE FROM {0} WHERE {1} = {2} AND {3} = {4}".format(table, firstField, firstID, secondField, secondID)
        sql = "DELETE FROM %s WHERE %s = %s AND %s = %s" % (table, firstField, firstID, secondField, secondID)
        if ((typeField is not None) and (type is not None)):
           sql = sql + " and %s =%s" % (typeField, self.db.pparam)
        self.cur.execute(sql,((type),))
        self.db.con.commit()

    #Add a Tag to the table
    def AddTagToItem(self, idMovie, tag_id, type):
        debug("CVideoDatabase AddTagToItem: idMovie:{0} tag_id:{1} type:{2}".format(idMovie, tag_id, type))
        if type is None:
            xbmc.log('CVideoDatabase AddTagToItem: Type is None', xbmc.LOGERROR)
            return
        return self.AddToLinkTable("tag_link", "tag_id", tag_id, "media_id", idMovie, "media_type", type)

    #Remove the connection between tag and movie
    def RemoveTagFromItem(self, idMovie, tag_id, type):
        debug("CVideoDatabase RemoveTagFromItem: idMovie:{0} tag_id:{1} type:{2}".format(idMovie, tag_id, type))
        if type is None:
            xbmc.log('CVideoDatabase RemoveTagFromItem: Type is None', xbmc.LOGERROR)
            return
        self.RemoveFromLinkTable("tag_link", "tag_id", tag_id, "media_id", idMovie, "media_type", type);

    def Removetag_link(self, tag_id):
        sql = "delete from tag_link where tag_id = %s" % (self.db.pparam)
        debug("CVideoDatabase Removetag_link: sql:{0}".format(sql))
        self.cur.execute(sql,((tag_id),))
        self.db.con.commit()

    def RemoveTag(self, tag_id):
        sql = "delete from tag where tag_id = %s" % (self.db.pparam)
        debug("CVideoDatabase RemoveTag: sql:{0}".format(sql))
        self.cur.execute(sql,((tag_id),))
        self.db.con.commit()

    #get all existing tags
    def GetAllTags(self):
        sql = "select tag_id, name from tag ORDER BY tag.name"
        debug("CVideoDatabase GetAllTags: sql:{0}".format(sql))
        self.cur.execute(sql)
        return self.cur.fetchall()

    def GetTagById(self, id):
        sql = "select tag_id, name from tag where tag_id = %s" % (self.db.pparam)
        debug("CVideoDatabase gettagbyid: sql:{0}".format(sql))
        self.cur.execute(sql,((id),))
        return self.cur.fetchall()

    #get all tags from a movie
    def GetVideoTags(self, id, type):
        #sql = "SELECT tag.tag_id, tag.name FROM tag, tag_link WHERE tag_link.media_id = {0} AND tag_link.media_type = '{1}' AND tag_link.tag_id = tag.tag_id ORDER BY tag.tag_id".format(id,type)
        sql = "SELECT tag.tag_id, tag.name FROM tag, tag_link WHERE tag_link.media_id = %s AND tag_link.media_type ='%s' AND tag_link.tag_id = tag.tag_id ORDER BY tag.name" % (id,type)
        debug("CVideoDatabase getvideotags: sql:{0}".format(sql))
        self.cur.execute(sql)
        return self.cur.fetchall()

    def GetCountedTags(self):
        sql = "select tag.name,tag_link.media_type,count(tag_link.media_id),tag.tag_id from tag left join tag_link on tag.tag_id = tag_link.tag_id group by tag.name, tag_link.media_type order by tag.name, tag_link.media_type"
        debug("CVideoDatabase getcountedtags: sql:{0}".format(sql))
        self.cur.execute(sql)
        return self.cur.fetchall()

    def GetAllMovies(self):
        sql = 'SELECT movie.idMovie, movie.c00 FROM movie order by movie.c00'
        debug("CVideoDatabase getallmovies: sql:{0}".format(sql))
        self.cur.execute(sql)
        return self.cur.fetchall()

    def GetAllMusicvideos(self):
        sql = 'SELECT musicvideo.idMVideo, musicvideo.c00 FROM musicvideo order by musicvideo.c00'
        debug("CVideoDatabase GetAllmusicvideos: sql:{0}".format(sql))
        self.cur.execute(sql)
        return self.cur.fetchall()

    def GetAllTVShows(self):
        sql = 'SELECT tvshow.idShow, tvshow.c00 FROM tvshow order by tvshow.c00'
        debug("CVideoDatabase GetAlltvshows: sql:{0}".format(sql))
        self.cur.execute(sql)
        return self.cur.fetchall()

    def getAllMoviesWithTag(self, tag_id, type):
        if type == PROPERTY_MOVIE:
            sql = 'SELECT movie.idMovie, movie.c00 FROM tag_link INNER JOIN movie ON tag_link.media_id = movie.idMovie WHERE (((tag_link.tag_id)= %s ) AND ((tag_link.media_type)="movie")) order by movie.c00' % (self.db.pparam)
        elif type == PROPERTY_MUSICVIDEO:
            sql = 'SELECT musicvideo.idMVideo, musicvideo.c00 FROM tag_link INNER JOIN musicvideo ON tag_link.media_id = musicvideo.idMVideo WHERE (((tag_link.tag_id)= %s ) AND ((tag_link.media_type)="musicvideo")) order by musicvideo.c00' % (self.db.pparam)
        elif type == PROPERTY_TVSHOW:
            sql = 'SELECT tvshow.idShow, tvshow.c00 FROM tag_link INNER JOIN tvshow ON tag_link.media_id = tvshow.idShow WHERE (((tag_link.tag_id)= %s) AND ((tag_link.media_type)="tvshow")) order by tvshow.c00' % (self.db.pparam)
        debug("CVideoDatabase GetAllmovieswithtag: sql:{0}".format(sql))
        self.cur.execute(sql,((tag_id),))
        return self.cur.fetchall()

    def getAllMoviesWithoutTag(self, type):
        if type == PROPERTY_MOVIE:
            sql = "SELECT movie.idMovie , movie.c00 from movie where movie.idMovie NOT IN (select tag_link.media_id from tag_link where tag_link.media_type='movie') order by movie.c00"
        elif type == PROPERTY_MUSICVIDEO:
            sql = "SELECT musicvideo.idMVideo, musicvideo.c00 from musicvideo where musicvideo.idMVideo NOT IN (select tag_link.media_id from tag_link where tag_link.media_type='musicvideo') order by musicvideo.c00"
        elif type == PROPERTY_TVSHOW:
            sql = "SELECT tvshow.idShow, tvshow.c00 from tvshow where tvshow.idShow NOT IN (select tag_link.media_id from tag_link where tag_link.media_type='tvshow') order by tvshow.c00"
        debug("CVideoDatabase getallmovieswithouttag: sql:{0}".format(sql))
        self.cur.execute(sql)
        return self.cur.fetchall()

    def getMovieById(self, id):
        #sql = "select * from movie where idMovie = {0}".format(id)
        sql = "select * from movie where idMovie = %s order by movie.c00" % (self.db.pparam)
        debug("CVideoDatabase getmoviebyid: sql:{0}".format(sql))
        self.cur.execute(sql,((id),))
        return self.cur.fetchall()

    def getMusicvideosById(self, id):
        #sql = "select * from musicvideo where idMVideo = {0}".format(id)
        sql = "select * from musicvideo where idMVideo = %s order by musicvideo.c00" % (self.db.pparam)
        debug("CVideoDatabase getmusicvideosbyid: sql:{0}".format(sql))
        self.cur.execute(sql,((id),))
        return self.cur.fetchall()

    def getTVShowsById(self, id):
        sql = "select idShow,0,c00 from tvshow where idShow = %s  order by tvshow.c00" % (self.db.pparam)
        debug("CVideoDatabase gettvshowsbyid: sql:{0}".format(sql))
        self.cur.execute(sql,((id),))
        return self.cur.fetchall()

    #get the pathid
    def GetPathId(self, pathname):
        sql = "select path.idPath from path where  path.strPath  = %s" %(self.db.pparam)
        debug("CVideoDatabase getpahtid: sql:{0}".format(sql))
        self.cur.execute(sql,((pathname),))
        row = self.cur.fetchone()
        if row:
            return row[0]
        else:
            return 0

    #get the fileid
    def GetFileId(self, pathid):
        sql = u"select movie_view.idFile from movie_view where %s = %s" % (self.db.concatrows("movie_view.strPath","movie_view.strFileName"), self.db.pparam)
        debug("CVideoDatabase getfileid: sql:%s %s" % (type(pathid),pathid))
        self.cur.execute(sql,((pathid),))
        row = self.cur.fetchone()
        debug("CVideoDatabase getfileid: ROW:{0}".format(row))
        if row:
            return row[0]
        else:
            return 0

    #get type (tvshow, movie, musicvideo) and movieid in that table
    def GetTypeAndId(self, fileId, path):
        r = ['',0,'']
        if fileId>0:
            r = ['',0,'']
            sql = "select idMovie, c00 from movie where idFile = %s order by movie.c00" % (self.db.pparam)
            #sql = "select idMovie, c00 from movie where idFile = {0}".format(fileId)
            debug("CVideoDatabase typeandid movies: sql:{0}".format(sql))
            self.cur.execute(sql,((fileId),))
            row = self.cur.fetchone()
            if row:
                id = row[0]
                name = row[1]
                if id != 0:
                    r[0] = "movie"
                    r[1] = id
                    r[2] = name
                    return r
            #sql = "select idMVideo, c00 from musicvideo where idFile = {0}".format(fileId)
            sql = "select idMVideo, c00 from musicvideo where idFile = %s" % (self.db.pparam)
            debug("CVideoDatabase typeandid musicvideo: sql:{0}".format(sql))
            self.cur.execute(sql,((fileId),))
            row = self.cur.fetchone()
            if row:
                id = row[0]
                name = row[1]
                if id != 0:
                    r[0] = "musicvideo"
                    r[1] = id
                    r[2] = name
                    return r
        else:
            #sql = "select idShow, c00 from tvshow_view where strPath = '{0}'".format(path)
            sql = "select idShow, c00 from tvshow_view where strPath = %s" % (self.db.pparam)
            debug("CVideoDatabase typeandid tvshow: sql:{0}".format(sql))
            self.cur.execute(sql,((path),))
            row = self.cur.fetchone()
            if row:
                id = row[0]
                name = row[1]
                if id != 0:
                    r[0] = "tvshow"
                    r[1] = id
                    r[2] = name
                    return r
        return 0
