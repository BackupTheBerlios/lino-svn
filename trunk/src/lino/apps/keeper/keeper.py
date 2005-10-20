#coding: latin1
## Copyright 2005 Luc Saffre 

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

import os

#from lino.apps.keeper.tables import *
#from lino.apps.keeper.tables import TABLES
from lino.apps.keeper import tables
from lino.adamo.ddl import Schema, Populator, STRING, BOOL
from lino.reports import DataReport
from lino.adamo.filters import Contains, NotEmpty



def preview(s):
    if len(s) < 100: return s
    return s[:100]+" (...)"


class SearchFormCtrl:
    
    formLabel="Search"
    
    def setupForm(self,frm):
        sess=frm.session
        words = sess.query(tables.Word)
        files = sess.query(tables.File) #,"name")
        grid=None # referenced in search(), defined later
        
        #files.addColumn("content")
        
        rpt=DataReport(files,width=70)#,columnWidths="30 15 30")
        #rpt=DataReport(files,columnWidths="30 15")

        #rpt.setupReport() # 
        rpt.addDataColumn("name",width=20)
        occsColumn=rpt.addDataColumn("occurences",
                                     width=15)
        rpt.addDataColumn("content",
                          formatter=lambda x: preview(x))

        col=occsColumn.datacol
        files.addFilter(NotEmpty(col))
        occs=col.getDetailQuery()
        occs.setSearchColumns("word.id")
        
        
        #frm = sess.form(label="Search")

        self.searchString = frm.addEntry(STRING,
                                         label="&Words to look for")
                                    #value="")
        self.anyWord = frm.addEntry(BOOL,label="&any word (OR)")
        
        def search():
##             files.clearFilters()
##             for word in searchString.getValue().split():
##                 w=words.peek(word)
##                 if w is None:
##                     sess.notice("ignored '%s'"%w)
##                 else:
##                     occs.addFilter(Contains,w)
                
            #files.setSearch(searchString.getValue())
            #occs._queryParams["search"]=searchString.getValue()
            occs.setSearch(self.searchString.getValue())
            grid.enabled=self.searchString.getValue() is not None
            frm.refresh()



        #bbox = frm.addHPanel()
        bbox = frm
        self.go = bbox.addButton("search",
                                 label="&Search",
                                 action=search).setDefault()
        #bbox.addButton("exit",
        #               label="&Exit",
        #               action=frm.close)
        grid=bbox.addDataGrid(rpt)
        grid.enabled=False



class Keeper(Schema):
    
    years='2005'
    author="Luc Saffre"
    
    #tables = TABLES

    def setupSchema(self):
        for cl in tables.TABLES:
            self.addTable(cl)

    def showSearchForm(self,sess):
        raise "no longer used"
        words = sess.query(tables.Word)
        files = sess.query(tables.File,"name")
        grid=None # referenced in search(), defined later
        col=files.addColumn("occurences")
        files.addFilter(NotEmpty(col))
        occs=col.getDetailQuery()
        occs.setSearchColumns("word.id")
        files.addColumn("content")
        
        rpt=DataReport(files,columnWidths="30 30 15")
        #rpt=DataReport(files,columnWidths="30 15")
        
        frm = sess.form(label="Search")

        searchString = frm.addEntry(STRING,
                                    label="&Words to look for")
                                    #value="")
        anyWord = frm.addEntry(BOOL,label="&any word (OR)")
        
        def search():
##             files.clearFilters()
##             for word in searchString.getValue().split():
##                 w=words.peek(word)
##                 if w is None:
##                     sess.notice("ignored '%s'"%w)
##                 else:
##                     occs.addFilter(Contains,w)
                
            #files.setSearch(searchString.getValue())
            #occs._queryParams["search"]=searchString.getValue()
            occs.setSearch(searchString.getValue())
            grid.enabled=searchString.getValue() is not None
            frm.refresh()



        #bbox = frm.addHPanel()
        bbox = frm
        bbox.addButton("search",
                       label="&Search",
                       action=search).setDefault()
        #bbox.addButton("exit",
        #               label="&Exit",
        #               action=frm.close)
        grid=bbox.addDataGrid(rpt)
        grid.enabled=False

        frm.show()
        #frm.showModal()



    def showMainForm(self,sess):
        frm = sess.form(
            label="Main menu",
            doc="""\
This is the Keeper main menu.                                    
"""+("\n"*10))

        m = frm.addMenu("search","&Suchen")
        #m.addItem("search",label="&Suchen").setHandler(
        #    self.showSearchForm,sess)
        m.addItem("search",label="&Suchen").setHandler(
            sess.showForm,SearchFormCtrl())
    
        m = frm.addMenu("db","&Datenbank")
        m.addItem("volumes",label="&Volumes").setHandler(
            sess.showViewGrid, tables.Volume)
        m.addItem("files",label="&Files").setHandler(
            sess.showViewGrid, tables.File)
        m.addItem("dirs",label="&Directories").setHandler(
            sess.showViewGrid, tables.Directory)
        m.addItem("words",label="&Words").setHandler(
            sess.showViewGrid, tables.Word)
        
        self.addProgramMenu(sess,frm)

        frm.addOnClose(sess.close)

        frm.show()


## if __name__ == '__main__':
##     from lino.forms import gui
##     app=Keeper()
##     sess=app.quickStartup()
##     sess.populate(TestPopulator())
##     gui.run(sess)
