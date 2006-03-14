## Copyright 2005-2006 Luc Saffre 

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

import keeper_tables as tables
#from lino.apps.keeper.tables import TABLES
#from lino.apps.keeper.tables import *
from lino.adamo.ddl import STRING, BOOL
from lino.adamo.dbreports import DataReport
from lino.adamo.filters import Contains, NotEmpty
from lino.forms.forms import ReportForm, DbMainForm
from lino.forms.gui import DbApplication



def preview(s):
    if len(s) < 100: return s
    return s[:100]+" (...)"

class FoundFilesReport(DataReport):
    leadTable=tables.File
    #width=70
    
    def setupReport(self):
        assert len(self.columns) == 0
        #files = self.query.session.query(tables.File) #,"name")
        self.addDataColumn("name",width=20)
        occsColumn=self.addDataColumn(
            "occurences",
            formatter=lambda pq: str(len(pq())),\
            #searchColumns="words.id",
            label="occs",
            width=5)
        self.addDataColumn("content",
                           width=40,
                           formatter=lambda x: preview(x))

        self.occsColumn=occsColumn.datacol
        self.query.addFilter(NotEmpty(self.occsColumn))
        #self.occs=col.getDetailQuery()
        self.occsColumn._queryParams['searchColumns']="word.id"
        
    def setSearch(self,s):
        self.occsColumn._queryParams['search'] = s


class SearchForm(ReportForm):
    
    title="Search"
    
    def setupForm(self):
        
        dbsess=self.rpt.query.session
        #words = sess.query(tables.Word)
        #files = sess.query(tables.File) #,"name")
        #grid=None # referenced in search(), defined later
        

        self.searchString=self.addEntry(
            STRING,
            label="&Words to look for")
        self.anyWord=self.addEntry(BOOL,label="&any word (OR)")
        
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
            self.rpt.setSearch(self.searchString.getValue())
            self.grid.enabled=self.searchString.getValue() is not None
            self.refresh()



        #bbox = frm.addHPanel()
        bbox = frm
        self.go = bbox.addButton("search",
                                 label="&Search",
                                 action=search).setDefault()
        #bbox.addButton("exit",
        #               label="&Exit",
        #               action=frm.close)
        self.grid=bbox.addDataGrid(rpt)
        #ReportForm.setupForm(self)
        self.grid.enabled=False



class KeeperMainForm(DbMainForm):
    """

This is the Keeper main menu.


    """
    def setupMenu(self):

        m = self.addMenu("search","&Suchen")
        m.addItem("search",label="&Suchen").setHandler(
            self.showForm,
            SearchForm(FoundFilesReport(self.dbsess)))

        
    
        m = self.addMenu("db","&Datenbank")

        self.addReportItem(
            m,"volumes",tables.VolumesReport,
            label="&Authors")
        self.addReportItem(
            m,"files",tables.FilesReport,
            label="&Files")
        self.addReportItem(
            m,"dirs",tables.DirectoriesReport,
            label="&Directories")
        self.addReportItem(
            m, "words",tables.WordsReport,
            label="&Words")
        
        self.addProgramMenu()


class Keeper(DbApplication):
    
    name="Lino Keeper"
    version="0.0.1"
    copyright="""\
Copyright (c) 2004-2006 Luc Saffre.
This software comes with ABSOLUTELY NO WARRANTY and is
distributed under the terms of the GNU General Public License.
See file COPYING.txt for more information."""
    schemaClass=tables.KeeperSchema
    mainFormClass=KeeperMainForm

        


## if __name__ == '__main__':
##     from lino.forms import gui
##     app=Keeper()
##     sess=app.quickStartup()
##     sess.populate(TestPopulator())
##     gui.run(sess)