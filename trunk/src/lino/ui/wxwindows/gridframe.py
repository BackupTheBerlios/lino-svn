#----------------------------------------------------------------------
# $Id: gridframe.py,v 1.2 2004/03/04 12:30:24 lsaffre Exp $
# Created:	 2003-10-27
# Copyright: (c) 2003 Luc Saffre
# License:	 GPL
#----------------------------------------------------------------------

import wx
import wx.grid

from lino.adamo.rowattrs import Pointer

pointerDataType = "Pointer"


class MyDataTable(wx.grid.PyGridTableBase):

	def __init__(self, report):
		wx.grid.PyGridTableBase.__init__(self)
		self.report = report
		self.columns = report.getVisibleColumns()
		self.loadData()

	def loadData(self):
		self.rows = [ [cell.format()
							for cell in row]
						  for row in self.report]
		#self.rows = [row for row in self.report]

	def GetNumberRows(self): return len(self.rows) + 1
	def GetNumberCols(self): return len(self.columns)
		
	def IsEmptyCell(self, row, col):
		
		""" bool IsEmptyCell(int row, int col) -- Returning a true value
		will result in the cell being "blank". No renderer or editor
		will be assigned, the table will not be asked for the
		corresponding value. Navigation keys will skip the cell,
		programmatic selection using the wxGrid::MoveCursor*Block
		commands will also skip the cell.  """
		
		return False
		# required
		#r = (self.GetValue(row,col) is None) 
		#print "IsEmptyCell(%d,%d) --> %s" % (row, col,repr(r))
		#return r

		  
	# Get/Set values in the table.  The Python version of these
	# methods can handle any data-type, (as long as the Editor and
	# Renderer understands the type too,) not just strings as in the
	# C++ version.
	def GetValue(self, rowIndex, colIndex):
		"required"
		try:
			return self.rows[rowIndex][colIndex]
			# ret = self.columns[colIndex].GetCellValue(row)
		except IndexError:
			return None

	def SetValue(self, rowIndex, colIndex, value):
		"required"
		#print "SetValue(%d,%d,%s)" % (rowIndex, colIndex, repr(value))
		try:
			row = self.report[rowIndex]
			cell = row[colIndex]
			#row = self.rows[rowIndex]
			cell.parse(value)
			#row.setCellValue(colIndex, value)
			#row[colIndex] = value
			self.rows[rowIndex][colIndex] = cell.format()
		except IndexError:
			row = [None] * len(self.columns)
			raise "todo: append row"
		
	def GetTypeName(self,row,col):
		rowAttr = self.columns[col].rowAttr
		if isinstance(rowAttr,Pointer):
			#print "Pointer"
			return pointerDataType
		return "string"
	


	def GetColLabelValue(self, col):
		"Called when the grid needs to display labels"
		#print "GetColLabelValue(%d) -> %s" % (col, self.columns[col].name)
		return self.columns[col].getLabel()

## 	def ResetView(self, grid):
## 		"""
## 		(wxGrid) -> Reset the grid view.	  Call this to
## 		update the grid if rows and columns have been added or deleted
## 		"""
## 		grid.BeginBatch()
## 		for current, new, delmsg, addmsg in [
## 			(self._rows, self.GetNumberRows(),
## 			 wx.GRIDTABLE_NOTIFY_ROWS_DELETED,
## 			 wx.GRIDTABLE_NOTIFY_ROWS_APPENDED),
## 			(self._cols, self.GetNumberCols(),
## 			 wx.GRIDTABLE_NOTIFY_COLS_DELETED,
## 			 wx.GRIDTABLE_NOTIFY_COLS_APPENDED),
## 			]:
## 			if new < current:
## 				msg = wx.GridTableMessage(self,delmsg,new,current-new)
## 				grid.ProcessTableMessage(msg)
## 			elif new > current:
## 				msg = wx.GridTableMessage(self,addmsg,new-current)
## 				grid.ProcessTableMessage(msg)
## 				self.UpdateValues(grid)
## 		grid.EndBatch()

## 		self._rows = self.GetNumberRows()
## 		self._cols = self.GetNumberCols()
## 		# update the column rendering plugins
## 		self._updateColAttrs(grid)

## 		# update the scrollbars and the displayed part of the grid
## 		grid.AdjustScrollbars()
## 		grid.ForceRefresh()


## 	def DeleteRows(self, rows):
## 		"""
## 		rows -> delete the rows from the dataset
## 		rows hold the row indices
## 		"""
## 		deleteCount = 0
## 		rows = rows[:]
## 		rows.sort()
## 		for i in rows:
## 			self.data.pop(i-deleteCount)
## 			# we need to advance the delete count
## 			# to make sure we delete the right rows
## 			deleteCount += 1

	def setOrderBy(self,colIndexes):
		cols = [self.columns[i].queryCol for i in colIndexes]
		self.report.setOrderByColumns(cols)
		self.loadData()

class PointerRenderer(wx.grid.PyGridCellRenderer):
	def __init__(self):
		#print "__init__"
		# copied and adapted from wxoo.table.baseviewer.BaseViewer
		self.BACKGROUND_SELECTED = wx.SystemSettings_GetColour(
			wx.SYS_COLOUR_HIGHLIGHT )
		self.TEXT_SELECTED = wx.SystemSettings_GetColour(
			wx.SYS_COLOUR_HIGHLIGHTTEXT )
		self.BACKGROUND = wx.SystemSettings_GetColour(
			wx.SYS_COLOUR_WINDOW  )
		self.TEXT = wx.SystemSettings_GetColour(
			wx.SYS_COLOUR_WINDOWTEXT  )
		# end copy
		wx.grid.PyGridCellRenderer.__init__(self)

	def GetValueAsText( self, grid, row, col ):
		"""Customisation Point: Retrieve the current value for row,col as a text string"""
		row = grid.GetTable().GetValue(row, col)		
		#value = self.GetCurrentTableValue( row, col )
		if row is None:
			return ""
		return row.getLabel()

	def Draw(self, grid, attr, dc, rect, row, col, isSelected):
		
		"""Draw the data from grid in the rectangle with attributes
		using the dc"""
		
		self.Clip(dc, rect)
		self.Background( grid, attr, dc, rect, row, col, isSelected)
		try:
			value = self.GetValueAsText( grid, row, col )
			dc.SetFont( wx.NORMAL_FONT )
			return self.SimpleText( value, attr, dc, rect, isSelected)
		finally:
			self.Unclip(dc)

	def SimpleText( self, value, attr, dc, rect, isSelected):
		
		"""Draw a simple text label in appropriate colours with
		background.  Uses the system settings at application load to
		draw a rectangle (rect) in either system window background or
		system selected window background.  Then draws the string
		"value" using either selected text or normal text colours.  """
		
		previousText = dc.GetTextForeground()
		if isSelected:
			dc.SetTextForeground( self.TEXT_SELECTED )
		else:
			dc.SetTextForeground( self.TEXT )
		try:
			dc.DrawText( value, rect.x+2,rect.y+2 )
		finally:
			dc.SetTextForeground( previousText )

	def Background( self, grid, attr, dc, rect, row, col, isSelected):
		"""Draw an appropriate background based on selection state"""
		if isSelected:
			dc.SetBrush( wx.Brush( self.BACKGROUND_SELECTED, wx.SOLID) )
		else:
			dc.SetBrush( wx.Brush( self.BACKGROUND, wx.SOLID) )
		try:
			dc.SetPen(wx.TRANSPARENT_PEN)
			dc.DrawRectangle( rect.x, rect.y, rect.width, rect.height )
			if attr.IsReadOnly():
				pass
## 				dc.DrawBitmap(
## 					READONLYBITMAP,
## 					rect.x+rect.width-READONLYBITMAP.GetWidth(),
## 					rect.y+rect.height-READONLYBITMAP.GetHeight(),
## 					1,
##				)
		finally:
			dc.SetPen( wx.NullPen )
			dc.SetBrush( wx.NullBrush )
		

	def Clip( self, dc, rect ):
		"""Setup the clipping rectangle"""
		dc.SetClippingRegion( rect.x, rect.y, rect.width, rect.height )
	def Unclip( self, dc ):
		"""Destroy the clipping rectangle"""
		dc.DestroyClippingRegion()
			
		

## 	def Draw(self, grid, attr, dc, rect, row, col, isSelected):
## 		dc.SetBackgroundMode(wx.SOLID)
## 		dc.SetBrush(wx.Brush(wx.WHITE, wx.SOLID))
## 		dc.SetPen(wx.TRANSPARENT_PEN)
## 		dc.DrawRectangle(rect.x, rect.y, rect.width, rect.height)

## 		dc.SetBackgroundMode(wx.TRANSPARENT)
## 		dc.SetFont(attr.GetFont())

## 		row = grid.GetTable().GetValue(row, col)
## 		if row is not None:
## 			text = row.getLabel()
## 		   #colors = [wxRED, wxWHITE, wxCYAN]
## 			x = rect.x + 1
## 			y = rect.y + 1
## 			dc.DrawText(text, x, y)


	def GetBestSize(self, grid, attr, dc, row, col):
		row = grid.GetTable().GetValue(row, col)
		#row = grid.GetCellValue(row, col)
		if row is None:
			return wx.Size(0,0)
		text = row.getLabel()
		dc.SetFont(attr.GetFont())
		w, h = dc.GetTextExtent(text)
		return wx.Size(w, h)


	def Clone(self):
		return PointerRenderer()

#from wxoo.resources import readonly_png
#READONLYBITMAP = readonly_png.getBitmap()

		
class RptGrid(wx.grid.Grid):
	def __init__(self, parent, report):
		wx.grid.Grid.__init__(self, parent, -1)
		self.RegisterDataType(pointerDataType,
									 PointerRenderer(),
									 wx.grid.GridCellTextEditor())
		#report.setupReport()
		self.table = MyDataTable(report)
		self.SetTable(self.table,True)
##		for col in table.columns:
## 		i = 0
## 		for col in self.table.columns:
## 			cellattr = wx.grid.GridCellAttr()
## 			if isinstance(col.queryCol.rowAttr,Pointer):
## 				cellattr.SetRenderer(PointerRenderer())
## 				cellattr.SetEditor(wx.grid.GridCellTextEditor())
## 			else:
## 				cellattr.SetEditor(wx.grid.GridCellTextEditor())
## 				cellattr.SetRenderer(wx.grid.GridCellStringRenderer())
## 			#self.cellattrs.append(cellattr)
## 			self.SetColAttr(i,cellattr)
## 			i += 1
			
		self.SetRowLabelSize(0)
		self.SetMargins(0,0)
		#print "RptGrid.__init__()"
		self.AutoSizeColumns(True)
		
		wx.grid.EVT_GRID_CELL_LEFT_DCLICK(self, self.OnLeftDClick)
		wx.grid.EVT_GRID_LABEL_RIGHT_CLICK(self, self.OnLabelRightClicked)

	# I do this because I don't like the default behaviour of not starting the
	# cell editor on double clicks, but only a second click.
	def OnLeftDClick(self, evt):
		if self.CanEnableCellControl():
			 self.EnableCellEditControl()



	def Reset(self):
		"""reset the view based on the data in the table.	Call
		this when rows are added or destroyed"""
		self.table.ResetView(self)

	def OnLabelRightClicked(self, evt):
		# Did we click on a row or a column?
		row, col = evt.GetRow(), evt.GetCol()
		if row == -1: self.colPopup(col, evt)
		elif col == -1:
			print "OnLabelRightClicked(%d,%d)" % (row,col)
			return
			self.rowPopup(row, evt)


	def colPopup(self, col, evt):
		"""(col, evt) -> display a popup menu when a column label is
		right clicked"""
		x = self.GetColSize(col)/2
		menu = wx.Menu()
		sortID = wx.NewId()

		xo, yo = evt.GetPosition()
		#self.SelectCol(col)
		#cols = self.GetSelectedCols()
		#print cols
		#self.Refresh()
		#menu.Append(id1, "Delete Col(s)")
		menu.Append(sortID, "set SortColumn(s)")

## 		def delete(event, self=self, col=col):
## 			cols = self.GetSelectedCols()
## 			self._table.DeleteCols(cols)
## 			self.Reset()

		def setSortColumn(event, self=self):
			#print "setSortColumn"
			self.table.setOrderBy(self.GetSelectedCols())
			self.ForceRefresh()
			#print "ForceRefresh"

		#EVT_MENU(self, id1, delete)
		#if len(cols) == 1:
		wx.EVT_MENU(self, sortID, setSortColumn)
		self.PopupMenu(menu, wx.Point(xo, 0))
		menu.Destroy()
			 
	def rowPopup(self, row, evt):
		
		"""(row, evt) -> display a popup menu when a row label is right clicked"""
		
		appendID = wx.NewId()
		deleteID = wx.NewId()
		x = self.GetRowSize(row)/2
		if not self.GetSelectedRows():
			self.SelectRow(row)
		xo, yo = evt.GetPosition()
		menu = wxMenu()
		menu.Append(appendID, "Append Row")
		menu.Append(deleteID, "Delete Row(s)")

		def append(event, self=self, row=row):
			self._table.AppendRow(row)
			self.Reset()

		def delete(event, self=self, row=row):
			rows = self.GetSelectedRows()
			self._table.DeleteRows(rows)
			self.Reset()

		EVT_MENU(self, appendID, append)
		EVT_MENU(self, deleteID, delete)
		self.PopupMenu(menu, wxPoint(x, yo))
		menu.Destroy()

		
		
class RptFrame(wx.Frame):
	def __init__(self, parent, id, report):
		title = report.getLabel()
		# print title
		#print parent, id, title
		wx.Frame.__init__(self, parent, id, title)
## 			size=wx.Size(400,200),
## 			style = wx.DEFAULT_FRAME_STYLE | wx.WANTS_CHARS |
## 			wx.NO_FULL_REPAINT_ON_RESIZE)
	
		
  		grid = RptGrid(self,report)
		
	


## def showReport(rptname):
	
## 	rpt = table.
		
