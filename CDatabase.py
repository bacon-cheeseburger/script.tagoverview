import os, xbmc, xbmcvfs, glob, string
import xml.dom.minidom
from strings import *

ADVSETTINGS_FILE = "advancedsettings.xml"
PROFILE_PATH = "special://profile/"
MASTERPROFILE_PATH = "special://masterprofile/"
DATABASE_PATH = "special://profile/"
VIDEO_SEARCHPATTERN_SQLITE = "MyVideos1??.db"
VIDEO_SEARCHPATTERN_DB = "MyVideos1__"
MINVER=75

class CDatabase:

    baseconfig = {
        'type': 'sqlite',
        'host': '127.0.0.1',
        'port': '3306',
        #'name': 'MyVideos116',
        'user': 'xbmc',
        'password': 'xbmc',
        'database': None,
        'charset': 'utf8',
        'use_unicode': True,
        'get_warnings': True
    }

    pparam = "?"

    #type       sqlite or mysql
    #host       sqlite: path to database            mysql: ip of host
    #port       sqlite: ignored                     mysql: port
    #name       sqlite: name of db-file or empty    mysql: databasename
    #name       if empty then fallback to standard file or db-names
    #user       sqlite: ignored                     mysql: user of db
    #password   sqlite: ignored                     mysql: password of db

    def __init__(self):
        debug("CDatabase init settings")
        self.config = self.baseconfig.copy()
        debug("CDatabase init settings",self.config)
        self.getConfig()
        self.type = self.config['type']
        del self.config['type']
        if self.type == 'sqlite':
            debug("CDatabase init using sqlite")
            self.init_sqlite()
        else:
            debug("CDatabase init using mysql")
            self.init_mysql()

    def init_mysql(self):
        debug("CDatabase init mysql")
        import mysql.connector
        if self.config['database'] == None:
            self.config['database'] = self.getMySQLDBName(VIDEO_SEARCHPATTERN_DB)
        else:
            db=self.config['database']+'%'
            del self.config['database']
            self.config['database'] = self.getMySQLDBName(db)
        debug("CDatabase init dbname",self.config['database'])
        try:
            self.con = mysql.connector.Connect(**self.config)
            debug("CDatabase Using built-in MySQL")
        except:
            error("CDatabase MySQL not found")
            exit()
        self.pparam = "%s"

    def getMySQLDBName(self,pattern):
        debug("CDatabase getmysqlname")
        import mysql.connector
        debug("CDatabase befor connect")
        con = mysql.connector.Connect(**self.config)
        cur = con.cursor()
        debug("CDatabase after alldb","SHOW DATABASES LIKE '%s'" % pattern)
        cur.execute("SHOW DATABASES LIKE '%s'" % pattern)
        db = sorted(cur.fetchall(),reverse=True)[0][0]
        debug("CDatabase after alldb",str(db))
        self.pparam = "?"
        if db is None:
            error("CDatabase: No Database available")
            exit()
        elif int(db[-3:]) < MINVER:
            error("CDatabase: XBMC Databaseversion must be greater than 74")
            exit()
        else:
            return str(db)

    def init_sqlite(self):
        debug("CDatabase init sqlite")
        from sqlite3 import dbapi2 as sqlite
        print(self.config['database'])
        if self.config['database'] == None:
            self.config['database'] = self.getSQLiteFileName(VIDEO_SEARCHPATTERN_SQLITE)
        else:
            db=self.config['database']+'*.db'
            del self.config['database']
            self.config['database'] = self.getSQLiteFileName(db)
        debug("CDatabase init dbname",self.config['database'])
        self.con = sqlite.connect(self.config['database'])
        self.cur = self.con.cursor()
        sqlite.enable_callback_tracebacks(True)
        debug("CDatabase Using built-in SQLite via sqlite3!")
        try:
            pass
        except:
            debug("CDatabase SQLite not found")
            return

    def getSQLiteFileName(self,pattern):
        debug("CDatabase getsqlitefilename")
        os.chdir(xbmcvfs.translatePath(DATABASE_PATH+"Database/"))
        maxver=0
        file = sorted(glob.glob(pattern),reverse=True)[0]
        if int( file[-6:-3]) < MINVER:
            error("CDatabase: XBMC Databaseversion %s must be grater than 74" % file)
            exit()
        else:
            dbfilename = file
        return xbmcvfs.translatePath(DATABASE_PATH +"Database/" + dbfilename)

    def concatrows(self, *args):
        txt=''
        if self.type == "sqlite":
            txt = " || ".join(map(str,args))
        elif self.type == "mysql":
            txt = ", ".join(map(str,args))
            txt = "CONCAT( %s )" % txt
        return txt
    def getConfig(self):
        debug("CDatabase getconfig")
        path = self.getASpath()
        if path is not None:
            asxml = xml.dom.minidom.parse(path)
            vdb = asxml.getElementsByTagName('videodatabase').item(0)
            if vdb is not None:
                for node in vdb.childNodes:
                    if node.nodeType == node.ELEMENT_NODE:
                        if node.tagName == 'type':
                            self.config['type'] = self.getText(node)
                        if node.tagName == 'host':
                            self.config['host'] = self.getText(node)
                        if node.tagName == 'port':
                            self.config['port'] = self.getText(node)
                        if node.tagName == 'name':
                            self.config['database'] = str(self.getText(node))
                        if node.tagName == 'user':
                            self.config['user'] = self.getText(node)
                        if node.tagName == 'pass':
                                self.config['password'] = self.getText(node)
        debug("CDatabase getconfig",self.config)

    def getText(self,node):
        rc = []
        for node in node.childNodes:
            if node.nodeType == node.TEXT_NODE:
                rc.append(node.data)
        return ''.join(rc)

    def getASpath(self):
        path = xbmcvfs.translatePath(PROFILE_PATH+ADVSETTINGS_FILE)
        if os.path.exists(path):
            debug("CDatabase getaspath:",path)
            return path
        path = xbmcvfs.translatePath(MASTERPROFILE_PATH+ADVSETTINGS_FILE)
        if os.path.exists(path):
            debug("CDatabase getaspath:",path)
            return path
        debug("CDatabase getaspath: None")
        return None
