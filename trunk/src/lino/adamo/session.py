## Copyright 2003-2005 Luc Saffre

## This file is part of the Lino project.

## Lino is free software; you can redistribute it and/or modify it
## under the terms of the GNU General Public License as published by
## the Free Software Foundation; either version 2 of the License, or
## (at your option) any later version.

## Lino is distributed in the hope that it will be useful, but WITHOUT
## ANY WARRANTY; without even the implied warranty of MERCHANTABILITY
## or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public
## License for more details.

## You should have received a copy of the GNU General Public License
## along with Lino; if not, write to the Free Software Foundation,
## Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307 USA

from lino.misc.attrdict import AttrDict
from lino.adamo import InvalidRequestError
#from lino.ui import console

class BabelLang:
    def __init__(self,index,id):
        self.index = index
        self.id = id

    def __repr__(self):
        return "<BabelLang %s(%d)>" % (self.id,self.index)



class Context:
    "interface implemented by Session and Database"
    def getBabelLangs(self):
        raise NotImplementedError

    def getLangs(self):
        return " ".join([lng.id for lng in self.getBabelLangs()])

    def supportsLang(self,lngId):
        for lng in self.getBabelLangs():
            if lng.id == lngId:
                return True
        return False
    

class Session(Context):
    
    #_dataCellFactory = DataCell
    #_windowFactory = lambda x: x
    
    def __init__(self,center,ui,**kw):
        # sessionManager is lino.adamo.center
        self.center = center
        #self.app = app
        assert ui is not None
        self.ui = ui
        self._user = None
        self.db = None
        #self.schema = None
        
##         if ui is None:
##             ui = console.getSystemConsole()
        
        
##         for m in (
##             'message', 'confirm','decide', 'form'
##             'debug','warning', 'info', 'job',
##             'error','critical',
##             'report','textprinter',
##             ):
##             setattr(self,m,getattr(ui,m))
            
##         for m in (
##             'startDump','stopDump'
##             ):
##             setattr(self,m,getattr(console,m))
        
        #self._setcon(console)
        self._ignoreExceptions = []
        
        self.use(**kw)

##     def _setcon(self,console):
##         self.console = console
##         for m in console.forwardables:
##             setattr(self,m,getattr(console,m))

    def hasAuth(self,*args,**kw):
        return True
            
##     def warning(self,msg):
##         """Log a warning message.  If interactive, make sure that she
##         has seen this message before returning.

##         """
##         if self.app is not None:
##             return self.app.warning(msg)
        
    def use(self,db=None): # ,langs=None):
        # if necessary, stop using current db
        if db != self.db and self.db is not None:
            self.db.commit()
            #self.db.removeSession(self)
            if self._user is not None:
                self.logout()
        if db is None:
            #self.schema = None
            #self.tables = None
            #self.forms = None
            self.db = None
        else:
            # start using new db
            #self.schema = db.schema # shortcut
            self.db = db
            # self.tables = AttrDict(factory=self.openTable)
            #self.forms = AttrDict(factory=self.openForm)
            #if langs is None:
            #    langs = db.getDefaultLanguage()
            #self.setBabelLangs(langs)
            self.setDefaultLanguage()
        
        #self._formStack = []

    def setDefaultLanguage(self):
        self.setBabelLangs(self.db.getDefaultLanguage())
        
        
    def handleException(self,e,details=None):
        if e.__class__ in self._ignoreExceptions:
            return
        raise e
        #self.ui.showException(e,details)
        

##  def spawn(self,**kw):
##      kw.setdefault('db',self.db)
##      kw.setdefault('langs',self.getLangs())
##      return center.center().createSession(**kw)

    def commit(self):
        return self.db.commit()

    def shutdown(self):
        # called in many TestCases during tearDown()
        # supposted to close all connections
        #
        self.end()
        self.center.shutdown()

    def setBabelLangs(self,langs):
        
        """langs is a string containing a space-separated list of babel
        language codes"""
        
        self.db.commit()
        self._babelLangs = []
        for lang_id in langs.split():
            self._babelLangs.append(self.db.findBabelLang(lang_id))
            
##         if self._babelLangs[0].index == -1:
##             raise InvalidRequestError(
##                 "First item of %s must be one of %s" % (
##                 repr(langs), repr(self.db.getBabelLangs())))

    def getBabelLangs(self):
        return self._babelLangs

    def getStore(self,leadTable):
        try:
            return self.db._stores[leadTable]
        except KeyError,e:
            raise InvalidRequestError("no such table: "+str(leadTable))
    
    def view(self,leadTable,*args,**kw):
        return self.getStore(leadTable).view(self,*args,**kw)
    
    def query(self,leadTable,columnNames=None,**kw):
        if columnNames is None:
            columnNames="*"
        return self.getStore(leadTable).query(self,columnNames,**kw)

    def peek(self,tableClass,*args):
        # used in raceman/report.py, cities_be.py...
        return self.query(tableClass).peek(*args)


    def end(self):
        self.use()
        self.center.closeSession(self)


    def onBeginSession(self):
        self.db.app.onBeginSession(self)
        
    
    def onLogin(self):
        return self.db.app.onLogin(self)
    
    def getUser(self):
        return self._user

    def login(self,user):
        if self._user is not None:
            self.logout()
        self._user = user
        
    def logout(self):
        assert self._user is not None
        self._user = None



##  def startSession(self):
##      if self.context is not None:
##          self.context.schema.onStartSession(self)


## class ConsoleSession(Session):

##     def showForm(self,formName,modal=False,**kw):
##         frm = self.openForm(formName,**kw)
##         wr = self.console.out.write
##         wr(frm.getLabel()+"\n")
##         wr("="*len(frm.getLabel())+"\n")
##         for cell in frm:
##             wr(cell.getLabel() + ":" + cell.format())
##             wr("\n")


##     def report(self,ds=None,**kw):
##         rpt = self.console.report(**kw)
##         if ds is not None:
##             ds.
        
##     def showReport(self,ds,*args,**kw):
##         rpt = self.report(ds,*args,**kw)
##         rpt.beginReport()
##         for row in ds:
##             rpt.renderRow(row)
##         rpt.endReport()
        
##     def showReport(self,ds,columnNames=None,showTitle=True,**kw):
##         raise "replaced by report()"
##         wr = self.console.out.write
##         #if len(kw):
##         rpt = ds.report(columnNames,**kw)
##         #print [col.name for col in rpt._clist.visibleColumns]
##         if showTitle:
##             wr(rpt.getLabel()+"\n")
##             wr("="*len(rpt.getLabel())+"\n")
##         columns = rpt.getVisibleColumns()
##         wr(" ".join(
##             [col.getLabel().ljust(col.getPreferredWidth()) \
##              for col in columns]).rstrip())
##         wr("\n")
##         wr(" ".join( ["-" * col.getPreferredWidth() \
##                               for col in columns]))
##         wr("\n")
##         for row in rpt:
##             l = []
##             for cell in row:
##                 #col = columns[i]
##                 l.append(cell.format())
##             wr(" ".join(l).rstrip())
##             wr("\n")





## class AbstractWebSession(Session):
    
##     def __init__(self,**kw):
##         Session.__init__(self,**kw)
##         self._messages = []

##     def errorMessage(self,msg):
##         self._messages.append(msg)

##     def notifyMessage(self,msg):
##         self._messages.append(msg)

##     def popMessages(self):
##         l = self._messages
##         self._messages = []
##         return l
        
##     def showForm(self,formName,modal=False,**kw):
##         raise NotImplementedError
        
##     def showReport(self,ds,columnNames=None,showTitle=True,**kw):
##         raise NotImplementedError
        
        
        
