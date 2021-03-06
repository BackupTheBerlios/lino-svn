# -*- coding: iso-8859-1 -*-

## Copyright 2004-2009 Luc Saffre

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

import sys, os

from lino.textprinter import winprn
from lino.console.application import Application, UsageError


class PrnPrint(Application):
    
    name="Lino prnprint"
    copyright="""\
Copyright (c) 2004-2009 Luc Saffre.
This software comes with ABSOLUTELY NO WARRANTY and is
distributed under the terms of the GNU General Public License.
See file COPYING.txt for more information."""
    url="http://lino.saffre-rumma.ee/prnprint.html"
    
    usage="usage: lino prnprint [options] FILE [FILE ...]"
    description="""

where FILE is a textprinter input file to be printed on your Windows
Printer.

""" 
    configfile="prnprint.ini" 
    configdefaults=dict(
      fontWeights=(400,700) 
      # a tuple of fontweight values expressing the boldnesses of 
      # normal and bold text.
      # Default is (400,700). Another reasonable value is (600,800).
    )
    
    def setupConfigParser(self,parser):
        
        parser.add_option("fontWeights",
                          help="""\
a tuple of fontweight values expressing the boldnesses of 
normal and bold text.
Default is (400,700). Another reasonable value is (600,800).
""",
                          dest="fontWeights",
                          default=None,
                          metavar="(NORMAL,BOLD)")

        Application.setupConfigParser(self,parser)
        
    def setupOptionParser(self,parser):
        Application.setupOptionParser(self,parser)
    
        parser.add_option("-p", "--printer",
                          help="""\
print on PRINTERNAME rather than on Default Printer.""",
                          action="store",
                          type="string",
                          dest="printerName",
                          default=None)
    
        parser.add_option("-e", "--encoding",
                          help="""\
FILE is encoded using ENCODING rather than sys.stdin.encoding.""",
                          action="store",
                          type="string",
                          dest="encoding",
                          default=sys.stdin.encoding)
    
        parser.add_option("-c", "--copies",
                          help="""\
print NUM copies.""",
                          action="store",
                          type="int",
                          dest="copies",
                          default=1)
    
        parser.add_option("--fontName",
                          help="""\
Name of font to be used. This sould be a fixed-pitch font. 
Default is "Courier New".""",
                          action="store",
                          type="string",
                          dest="fontName")

        parser.add_option("-o", "--output",
                          help="""\
write to SPOOLFILE instead of really printing.""",
                          action="store",
                          type="string",
                          dest="spoolFile",
                          default=None)
        
        parser.add_option("-s", "--fontSize",
                          help="use FONTSIZE characters per inch as default font size.",
                          action="store",
                          type="int",
                          dest="fontSize",
                          default=12)
##         parser.add_option(
##             "-u", "--useWorldTransform",
##             help="use SetWorldTransform() to implement landscape",
##             action="store_true",
##             dest="useWorldTransform",
##             default=False)
    
    def run(self):
        if len(self.args) == 0:
            raise UsageError("no arguments specified")
        if self.options.copies < 0:
            raise UsageError("wrong value for --copies")
        for inputfile in self.args:
            for cp in range(self.options.copies):
                d = winprn.Win32TextPrinter(
                    self.options.printerName,
                    self.options.spoolFile,
                    #useWorldTransform=self.options.useWorldTransform,
                    encoding=self.options.encoding,
                    fontName=self.options.fontName,
                    fontWeights=self.options.fontWeights,
                    cpi=self.options.fontSize,
                    session=self)
                    #charset=winprn.OEM_CHARSET)
                d.readfile(inputfile)
                d.close()
                if d.page == 1:
                    self.notice("%s : 1 page has been printed",
                                inputfile)
                else:
                    self.notice("%s : %d pages have been printed",
                                inputfile,d.page)


def main(*args,**kw):
    PrnPrint().main(*args,**kw)

if __name__ == '__main__':
    main()
