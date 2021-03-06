## Copyright 2003-2007 Luc Saffre

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

import types

from lino.adamo.exceptions import DataVeto, InvalidRequestError, \
     NoSuchField, RowLockFailed, LockRequired
from lino.adamo import datatypes

## from lino.adamo.rowattrs import RowAttribute,\
##      Field, BabelField, Pointer, Detail, FieldContainer

from PyQt4.QtCore import QString


class DataRow:
    def __init__(self,dbc,store,values,dirty=False):
        assert type(values) == types.DictType
        self.__dict__["_values"] = values
        self.__dict__["_context"] = dbc
        self.__dict__["_store"] = store
        self.__dict__['_dirtyRowAttrs']={}
       
##     def __getattr__(self,name):
##         attr=self._store._table.getRowAttr(name)
##         return attr.getCellValue(self)
    
##     def __setattr__(self,name,value):
##         attr=self._store._table.getRowAttr(name)
##         attr.setCellValue(self,value)
    
    def __getattr__(self,name):
        col=self._store._peekQuery.getColumnByName(name)
        return col.getCellValue(self)
    
    def __setattr__(self,name,value):
        col=self._store._peekQuery.getColumnByName(name)
        if col in self._store._peekQuery._pkColumns:
            raise InvalidRequestError("Cannot change the primary key")
        col.setCellValue(self,value)

    def initTable(self,table):
        raise NotImplementedError
    
    def setupMenu(self,frm):
        pass
    
    def getFieldValue(self,name):
        # overridden by StoredDataRow
        try:
            return self._values[name]
        except KeyError:
            raise NoSuchField,name
        
##     def detail(self,tcl,*args,**kw):
##         return self.getSession().query(tcl,*args,**kw)

    def format(v):
        assert v is not None, datatypes.ERR_FORMAT_NONE
        #print repr(v)
        try:
            return unicode(v)
        except Exception,e:
            print repr(v)
            raise
    format=staticmethod(format)

##     def parse(self,s):
##         """Return the row instance represented by string s.

##         """
##         return self._store._peekQuery.parse(s)
##         l=s.split(",")
##         i=0
##         for col in self._store._peekQuery._pkColumns:
        

##     def makeDataCell(self,colIndex,col):
##         #return self.getSession()._dataCellFactory(self,colIndex,col)
##         return DataCell(self,colIndex,col)


##     def setDirty(self):
##         assert self.isLocked(), "row is not locked"
##         self.__dict__["_dirty"] = True

    def setDirtyRowAttr(self,rowattr):
        #print self,self.mustlock(),self._locked
        if self.mustlock() and not self.isLocked():
            raise LockRequired("%r is not locked" % self)
        self.__dict__['_dirtyRowAttrs'][rowattr.name]=rowattr

##     def __getitem__(self,i):
##         col = self._query.visibleColumns[i]
##         # 20050222 return self.makeDataCell(i,col)
##         return col.getCellValue(self)
        
##     def __setitem__(self,i,value):
##         col = self._query.visibleColumns[i]
##         assert self._pseudo or self._locked or self._new
##         col.setCellValue(self,value)
##         #self.__dict__["_dirty"] = True
        
##     def __len__(self):
##         return len(self._query.visibleColumns)
    
    #def getCells(self,columnNames=None):
    #    return RowIterator(self,self._query.getColumns(columnNames))
        

    def canWrite(self):
        return True
    
##     def validate(self):
##         # may override
##         pass

##     def lock(self):
##         return False
    
##     def unlock(self):
##         pass
    
    
    def isLocked(self):
        return True

    def isDirty(self):
        if self._new:
            return True
        return len(self._dirtyRowAttrs)>0
        #return self.__dict__['_dirty']

    def getSession(self):
        return self._store._db.schema.session
        
    def getContext(self):
        #return self._query.getContext()
        return self._context

    def getDatabase(self):
        return self._store._db
        #return self._query.getDatabase()

    def getTableName(self):
        return self._store._table.getTableName()
    
##     def getContext(self):
##         return self._ds.getContext()
    

class StoredDataRow(DataRow):
    # base class for Table.Row
    
    def __init__(self,dbc,store,values,new,pseudo=False):
        """
        """
        assert type(new) == types.BooleanType
        DataRow.__init__(self,dbc,store,values,dirty=new)

        #self.__dict__["_ds"] = ds
        self.__dict__["_new"] = new
        self.__dict__["_pseudo"] = pseudo
        self.__dict__["_complete"] = False #ds.isComplete()
        #self.__dict__["_locked"] = False
        self.__dict__["_isCompleting"] = False
        

    def __eq__(self, other):
        if (other is None):# or (other is self._query.ANY_VALUE):
            return False
        return self.getRowId() == other.getRowId()
        #return tuple(self.getRowId()) == tuple(other.getRowId())
        
    def __ne__(self, other):
        if (other is None):# or (other is self._query.ANY_VALUE):
            return True
        return self.getRowId() != other.getRowId()
        #return tuple(self.getRowId()) == tuple(other.getRowId())
        
##     def getRenderer(self,rsc,req,writer=None):
##         return self._query.getLeadTable()._rowRenderer(
##             rsc,req,self,writer)

##  def writeParagraph(self,parentResponder):
##      rsp = self.getRenderer(parentResponder.resource,
##                                    parentResponder.request,
##                                    parentResponder._writer)
##      #assert rsp.request is self.request
##      rsp.writeParagraph()


##         rpt = doc.report(label=str(self))
##         for c in self:
##             rpt.addColumn(lambda cell: cell.col.getLabel(),
##                           width=20,
##                           label="fieldName")
##             rpt.addColumn(lambda cell: str(cell),
##                           width=50,
##                           label="value")
##         rpt.execute(self)
    
    def isComplete(self):
        return self._complete
    
    def isNew(self):
        return self._new
    
    def validate(self):
        #print "Row.validate()"
        #assert self._complete or self._new, \
        #       "seems that lock() did not makeComplete() "
        for col in self._store._peekQuery._columns:
            v=col.getCellValue(self)
            col.validate(v)
            
    def getRowId(self):
        id = [None] * len(self._store.getTable().getPrimaryAtoms())
        for col in self._store._peekQuery._pkColumns:
            col.row2atoms(self,id)
        #for i in id:
        #    assert type(i) is not QString, str(id)
        return id
        
##     def __str__(self):
##         return str(self.getLabel())

##     def getLabel(self):
##         return str(tuple(self.getRowId()))
##         #return self._ds._table.getRowLabel(self)
        
    def __repr__(self):
        if self._isCompleting:
            return "Uncomplete "+self.__class__.__name__\
                   +'('+str(self._values)+")"
        return self.__class__.__name__+'('\
               +','.join([str(i) for i in self.getRowId()])+')'

    def __unicode__(self):
        s=self.getLabel()
        if s is None:
            return repr(self)
        return s

    def getLabel(self):
        return None
        

    def getFieldValue(self,name):
        # overrides DataRow
        try:
            return self._values[name]
        except KeyError:
            if self._isCompleting:
                return None
            self.makeComplete()
            try:
                return self._values[name]
            except KeyError:
                raise NoSuchField("%r has no field '%s'"%(self,name))


    def _readFromStore(self):
        """
        make this row complete using a single database lookup
        """
        assert not self._pseudo,\
               "%s : readFromStore() called for a pseudo row" \
               % repr(self)
        assert not self._complete,\
               "%s : readFromStore() called a second time" % repr(self)
        assert not self._isCompleting
        #assert not self._new
        
        # but what if atoms2row() causes __getattr__ to be called
        # again? maybe a switch _isCompleting to check this.
        self.__dict__["_isCompleting"] = True
        
        # print "makeComplete() : %s" % repr(self)
        id = self.getRowId()
        if self._new:
##             atomicRow = self._query._store.executePeek(
##                 self._query._store._peekQuery,id)
##             if atomicRow is not None:
##                 raise DataVeto("Cannot create another %s row %s" \
##                                     % (self.__class__.__name__, id))
            for attrname in self._store.getTable().getAttrList():
                self._values.setdefault(attrname,None)
        else:
            atomicRow = self._store.executePeek(
                self._store._peekQuery,id)
            if atomicRow is None:
                raise DataVeto(
                    "Cannot find %s row %s" \
                    % (self._store.getTable().getTableName(), id))
            self._store._peekQuery.atoms2row(atomicRow,self)
                
        
        """maybe a third argument `fillMode` to atoms2dict() which
        indicates whether existing (known) values should be
        overwritten, checked for equality or ignored...  """

        self.__dict__['_complete'] = True
        self.__dict__["_isCompleting"] = False

    def checkIntegrity(self):
        #if not self._complete:
        self.makeComplete()
        for name,attr in self._store.getTable()._rowAttrs.items():
            msg = attr.checkIntegrity(self)
            if msg is not None:
                return msg
        
##  def getAtomicValue(self,i):
##      return self._values[i]

##  def atomicValues(self):
##      return self._values
        

##     def getAttrValues(self,columnNames=None):
##         l = []
##         if columnNames is None:
##             q = self._area._query()
##             for col in q.getColumns():
##                 attr = col.rowAttr 
##                 l.append( (attr,attr.getValueFromRow(self)) )
##         else:
##             for name in columnNames.split():
##                 col = q.getColumn(name)
##                 attr = col.rowAttr
##                 #attr = self._area._table.__getattr__(name) 
##                 l.append( (attr,attr.getValueFromRow(self)) )
##         return tuple(l)
        
    
    def mustlock(self):
        return not (self._new or self._pseudo)

    def lock(self):
        #print "Row.lock()",repr(self)
        if not self.mustlock():
            return #raise RowLockFailed("Cannot lock a new row")
        self.makeComplete()
        #if self._locked:
        #    raise RowLockFailed("Already locked")
            # , "already locked"
            # return True
        #self.__dict__["_locked"] = True
        self._store.lockRow(self)
        #print "Row.lock()",self,self._locked, self.mustlock()
            

    def unlock(self):
        self.commit(unlock=True)
        #print "Row.unlock()",self,self._locked, self.mustlock()
##         if self.isDirty():
##             self.commit()
##         if not self.mustlock():
##             return #raise RowLockFailed("Cannot lock a new row")
##         self._store.unlockRow(self)

    def commit(self,unlock=False):
        #if not self.isDirty():
        #    return
        #print "writeToStore()", self
        for a in self._dirtyRowAttrs.values():
            a.trigger(self)
            
        if self._new:
            self._store.setAutoRowId(self)
            
        for rowattr in self._store.getTable()._mandatoryColumns:
            if self.getFieldValue(rowattr.name) is None:
                raise DataVeto(
                    "Column '%s.%s' is mandatory"\
                    % (self._store.getTable().getTableName(),
                       rowattr.name))
            
        
        try:
            self.validate()
        except DataVeto,e:
            raise DataVeto(repr(self) + ': ' + str(e))
        
        if self._new:
            self._store._connection.executeInsert(self)
            self.__dict__["_new"] = False
            if not unlock:
                self._store.lockRow(self)
        else:
            if unlock:
                self._store.unlockRow(self)
            if not self.isDirty():
                return
            self._store._connection.executeUpdate(self)
        #self.__dict__["_dirty"] = False
        self.__dict__["_dirtyRowAttrs"] = {}
        self._store.touch()


    def isLocked(self):
        return self._store.isLockedRow(*self.getRowId())
        #return (self._locked or self._new or self._pseudo)
        #return self._locked

        
        
    def makeComplete(self):
        if self._pseudo or self._complete or self._isCompleting:
            return 
        self._readFromStore()


        

    def update(self,**kw):
        self.lock()
        for (k,v) in kw.items():
            #print "update %s.%s = %r" % (self,k,v)
            setattr(self,k,v)
        self.validate()
        self.unlock()

    def delete(self):        
        self._store._connection.executeDelete(self)

    def exists(self):
        if not self._complete:
            self._readFromStore()
        return not self.isNew()

    
    


##     def defineMenus(self,win):
##         #self.initQuery()
##         mb = win.addMenuBar("row","&Row menu")
##         mnu = mb.addMenu("&Row")
##         mnu.addItem("&Edit",self.mnu_toggleEdit,win)
##         # mnu.addItem("&Delete",self.mnu_deleteRow)
##         # w.addGrid(self)
##         # return mb
##         mnu = mb.addMenu("&File")
##         mnu.addItem("E&xit",win.close)

##     def mnu_toggleEdit(self,win):
##         pass

    def vetoDelete(self):
        return self._store.getTable().vetoDeleteRow(self)
        #for col in self._query._columns:
        #    msg=col.vetoDeleteRow(self)
        #    if msg: return msg
            
##         for name,attr in self._query.getLeadTable()._rowAttrs.items():
##             msg = attr.vetoDeleteIn(self)
##             if msg: return msg


class LinkingRow(StoredDataRow):

    def initTable(self,table):
        table.addPointer('p',self.fromClass)
        table.addPointer('c',self.toClass)
        table.setPrimaryKey("p c")


class MemoRow(StoredDataRow):
        
    def initTable(self,table):
        table.addField('title',datatypes.STRING)
        table.addField('abstract',datatypes.MEMO)
        table.addField('body',datatypes.MEMO)

    def getLabel(self):
        return self.title

    

class TreeRow(StoredDataRow):
        
    def initTable(self,table):
        table.addField('seq',datatypes.INT)
        table.addPointer('super',self.__class__)

    def getUpTree(self):
        l = []
        super = self.super
        while super:
            l.insert(0,super)
            super = super.super
        return l

class MemoTreeRow(MemoRow,TreeRow):
    def initTable(self,table):
        MemoRow.initTable(self,table)
        TreeRow.initTable(self,table)

    def getLabel(self):
        return self.title

        
        

class BabelRow(StoredDataRow):
    
    def initTable(self,table):
        table.addBabelField('name',datatypes.STRING).setMandatory()
        
    def getLabel(self):
        return self.name


#from lino.reports.reports import Report

        
    
