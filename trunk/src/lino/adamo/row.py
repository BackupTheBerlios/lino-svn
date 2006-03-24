## Copyright 2003-2006 Luc Saffre

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
     NoSuchField

## from lino.adamo.rowattrs import RowAttribute,\
##      Field, BabelField, Pointer, Detail, FieldContainer


class DataRow:
    def __init__(self,query,values,dirty=False):
        #assert isinstance(fc,FieldContainer)
        #assert isinstance(clist,BaseColumnList)
        #instance=self._query._store._peekQuery._instanceClass()
        #self.__dict__["_instance"] = 
        #for k,v in values.items():
            
        assert type(values) == types.DictType
        self.__dict__["_values"] = values
        self.__dict__["_query"] = query
        #self.__dict__["_store"] = store
        #self.__dict__["_fc"] = fc
        #self.__dict__["_clist"] = clist
        #self.__dict__["_dirty"] = dirty
        self.__dict__['_dirtyRowAttrs']={}
        #if query is not None:
        #    for col in query._store._peekQuery.getVisibleColumns():
        #        values.setdefault(col.name)
        
    def __getattr__(self,name):
        #assert self.__dict__.has_key("_fc")
        #print repr(self._fc)
        #col=self._query.findColumn(name)
        #if col is None:
        #    col=self._query._store._peekQuery.getColumnByName(name)
        col=self._query._store._peekQuery.getColumnByName(name)
        return col.getCellValue(self)
        #rowattr = self.__dict__['_fc'].getRowAttr(name)
        #return rowattr.getCellValue(self)
    
    def __setattr__(self,name,value):
        #if self.__dict__.has_key(name):
        #    self.__dict__[name] = value
        #    return
        if not self.isLocked():
            raise InvalidRequestError("row is not locked")
        #col=self._query.findColumn(name)
        #if col is None:
        col=self._query._store._peekQuery.getColumnByName(name)
        if col in self._query._store._peekQuery._pkColumns:
            raise InvalidRequestError("Cannot change the primary key")
        col.setCellValue(self,value)
        #self.__dict__['_dirty'] = True

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
        #print repr(v)
        return str(v)
    format=staticmethod(format)
        

##     def makeDataCell(self,colIndex,col):
##         #return self.getSession()._dataCellFactory(self,colIndex,col)
##         return DataCell(self,colIndex,col)


##     def setDirty(self):
##         assert self.isLocked(), "row is not locked"
##         self.__dict__["_dirty"] = True

    def setDirtyRowAttr(self,rowattr):
        assert self.isLocked(), "row is not locked"
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
        
    def update(self,**kw):
        self.lock()
        for (k,v) in kw.items():
            setattr(self,k,v)
        self.validate()
        self.unlock()


    def canWrite(self):
        return True
    
    def validate(self):
        #print "Row.validate()"
        for col in self._query._store._peekQuery._columns:
            v=col.getCellValue(self)
            col.validate(v)
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

    def getContext(self):
        return self._query.getContext()

    def getDatabase(self):
        return self._query.getDatabase()

    def getTableName(self):
        return self._query.getTableName()
    
##     def getContext(self):
##         return self._ds.getContext()
    

class StoredDataRow(DataRow):
    # base class for Table.Row
    
    def __init__(self,qry,values,new,pseudo=False):
        """
        """
        assert type(new) == types.BooleanType
        DataRow.__init__(self,qry,values,dirty=new)

        #self.__dict__["_ds"] = ds
        self.__dict__["_new"] = new
        self.__dict__["_pseudo"] = pseudo
        self.__dict__["_complete"] = False #ds.isComplete()
        self.__dict__["_locked"] = False
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
        
    def getRenderer(self,rsc,req,writer=None):
        return self._query.getLeadTable()._rowRenderer(
            rsc,req,self,writer)

##  def writeParagraph(self,parentResponder):
##      rsp = self.getRenderer(parentResponder.resource,
##                                    parentResponder.request,
##                                    parentResponder._writer)
##      #assert rsp.request is self.request
##      rsp.writeParagraph()
    
    def printRow(self,doc):
        rpt = doc.report(label=str(self))
        for c in self:
            rpt.addColumn(lambda cell: cell.col.getLabel(),
                          width=20,
                          label="fieldName")
            rpt.addColumn(lambda cell: str(cell),
                          width=50,
                          label="value")
        rpt.execute(self)
    
    def isComplete(self):
        return self._complete
    
    def isLocked(self):
        return (self._locked or self._new or self._pseudo)

    def isNew(self):
        return self._new
    
    def getRowId(self):
        id = [None] * len(self._query.getLeadTable().getPrimaryAtoms())
        for col in self._query._pkColumns:
            col.row2atoms(self,id)
        return id
        
##     def __str__(self):
##         return str(self.getLabel())

##     def getLabel(self):
##         return str(tuple(self.getRowId()))
##         #return self._ds._table.getRowLabel(self)
        
    def __str__(self):
        return str(tuple(self.getRowId()))
        
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
            for attrname in self._query.getLeadTable().getAttrList():
                self._values.setdefault(attrname,None)
        else:
            atomicRow = self._query._store.executePeek(
                self._query._store._peekQuery,id)
            if atomicRow is None:
                raise DataVeto(
                    "Cannot find %s row %s" \
                    % (self._query.getLeadTable().getTableName(), id))
            self._query._store._peekQuery.atoms2row(atomicRow,self)
                
        
        """maybe a third argument `fillMode` to atoms2dict() which
        indicates whether existing (known) values should be
        overwritten, checked for equality or ignored...  """

        self.__dict__['_complete'] = True
        self.__dict__["_isCompleting"] = False

    def checkIntegrity(self):
        #if not self._complete:
        self.makeComplete()
        for name,attr in self._query.getLeadTable()._rowAttrs.items():
            msg = attr.checkIntegrity(self)
            if msg is not None:
                return msg
        
##  def getAtomicValue(self,i):
##      return self._values[i]

##  def atomicValues(self):
##      return self._values
        

    def getAttrValues(self,columnNames=None):
        l = []
        if columnNames is None:
            q = self._area._query()
            for col in q.getColumns():
                attr = col.rowAttr 
                l.append( (attr,attr.getValueFromRow(self)) )
        else:
            for name in columnNames.split():
                col = q.getColumn(name)
                attr = col.rowAttr
                #attr = self._area._table.__getattr__(name) 
                l.append( (attr,attr.getValueFromRow(self)) )
        return tuple(l)
        
    
    def __repr__(self):
        if self._isCompleting:
            return "Uncomplete " + repr(self._query) + "Row(" \
                     + str(self._values)+")"
        #return self._query.getName() \
        #       + "Row(" + str(self._values)+")"
        return self._query.getName() + "Row" + repr(
            tuple(self.getRowId()))



    def lock(self):
        if self._new:
            raise RowLockFailed("Cannot lock a new row")
        if self._locked:
            raise RowLockFailed("Already locked")
            # , "already locked"
            # return True
        self.__dict__["_locked"] = True
        self._query._store.lockRow(self,self._query)
            

    def unlock(self):
        #print "unlock()", self
        assert self._locked, "Row was not locked"
            
##          msg = self.validate()
##          if msg:
##              raise DataVeto(repr(self) + ': ' + msg)
            
        #assert not None in self.getRowId(), "incomplete pk"
        self.__dict__["_locked"] = False
        #self._query._store.unlockRow(self,self._query)
        self._query._store.unlockRow(*self.getRowId())
        self.commit()
        

    def commit(self):
        if not self.isDirty():
            return
        #print "writeToStore()", self
        for a in self._dirtyRowAttrs.values():
            a.trigger(self)
            
        if self._new:
            self._query._store.setAutoRowId(self)
            
        for rowattr in self._query.getLeadTable()._mandatoryColumns:
            if self.getFieldValue(rowattr.name) is None:
                raise DataVeto("Column '%s.%s' may not be empty"\
                               % (self._query.getTableName(),
                                  rowattr.name))
            
        
        try:
            self.validate()
        except DataVeto,e:
            raise DataVeto(repr(self) + ': ' + str(e))
        
        if self._new:
            self._query._connection.executeInsert(self)
            self.__dict__["_new"] = False
        else:
            if not self.isDirty(): return
            self._query._connection.executeUpdate(self)
        #self.__dict__["_dirty"] = False
        self.__dict__["_dirtyRowAttrs"] = {}
        self._query._store.touch()
        

    def delete(self):        
        self._query._connection.executeDelete(self)

    def makeComplete(self):
        if self._pseudo or self._complete or self._isCompleting:
            return 
        self._readFromStore()

    def exists(self):
        if not self._complete:
            self._readFromStore()
        return not self.isNew()

    
    


    def defineMenus(self,win):
        #self.initQuery()
        mb = win.addMenuBar("row","&Row menu")
        mnu = mb.addMenu("&Row")
        mnu.addItem("&Edit",self.mnu_toggleEdit,win)
        # mnu.addItem("&Delete",self.mnu_deleteRow)
        # w.addGrid(self)
        # return mb
        mnu = mb.addMenu("&File")
        mnu.addItem("E&xit",win.close)

    def mnu_toggleEdit(self,win):
        pass

    def vetoDelete(self):
        return self._query.getLeadTable().vetoDeleteRow(self)
        #for col in self._query._columns:
        #    msg=col.vetoDeleteRow(self)
        #    if msg: return msg
            
##         for name,attr in self._query.getLeadTable()._rowAttrs.items():
##             msg = attr.vetoDeleteIn(self)
##             if msg: return msg


## class RowIterator:

##     def __init__(self,row,columns):
##         self.row = row
##         self.colIndex = 0
##         self._columns = columns
        
##     def __iter__(self):
##         return self
    
##     def next(self):
##         if self.colIndex == len(self._columns):
##             raise StopIteration
##         col = self._columns[self.colIndex]
##         self.colIndex += 1
##         return self.row.makeDataCell(self.colIndex,col) 


## class DataCell:
##     def __init__(self,row,colIndex,col):
##         #self.colIndex = colIndex
##         self.row = row
##         self.col = col

##     def getValue(self):
##         return self.col.getCellValue(self.row)
        
## ##     def __str__(self):
## ##         return str(self.col.getCellValue(self.row))
## ##         #~ v = self.col.getCellValue(self.row)
## ##         #~ if v is None:
## ##             #~ return "None"
## ##         #~ return self.col.rowAttr.format(v)
    
## ##     def format(self):
## ##         v = self.col.getCellValue(self.row)
## ##         if v is None:
## ##             return ""
## ##         return self.col.rowAttr.format(v)

##     def canWrite(self):
##         if self.row.canWrite():
##             return self.col.canWrite(self.row)
##         return False
    
##     def __repr__(self):
##         return repr(self.col.getCellValue(self.row))
##         #~ v = self.col.getCellValue(self.row)
##         #~ if v is None:
##             #~ return "None"
##         #~ return self.col.rowAttr.format(v)
    
##     def __str__(self):
##         v = self.col.getCellValue(self.row)
##         if v is None:
##             return ""
##         return self.col.rowAttr.format(v)
    
##     #def parseAndSet(self,s):
##     def setValueFromString(self,s):
##         self.col.rowAttr.setValueFromString(self.row,s)
        
##     def setValue(self,value):
##         self.col.setCellValue(self.row,value)

