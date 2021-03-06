#coding: latin1

## Copyright 2002-2008 Luc Saffre.

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

#from lino.ui import console
from lino import __url__
from lino.textprinter.pdfprn import PdfTextPrinter

from lino.console.application import Application, UsageError

class Prn2pdf(Application):

    name="Lino prn2pdf"
    copyright="""\
Copyright (c) 2002-2008 Luc Saffre.
This software comes with ABSOLUTELY NO WARRANTY and is
distributed under the terms of the GNU General Public License.
See file COPYING.txt for more information."""
    url=__url__+"/prn2pdf.html"
    
    usage="usage: lino prn2pdf [options] FILE"
    description="""\
where FILE is the file to be converted to a pdf file.
It may contain plain text and simple formatting printer control sequences. """
    
    def setupOptionParser(self,parser):
        Application.setupOptionParser(self,parser)
    
        parser.add_option("-o", "--output",
                          help="""\
write to OUTFILE rather than FILE.pdf""",
                          action="store",
                          type="string",
                          dest="outFile",
                          default=None)
    
        parser.add_option("-e", "--encoding",
                          help="""\
FILE is encoded using ENCODING instead of sys.stdin.encoding.""",
                          action="store",
                          type="string",
                          dest="encoding",
                          default=sys.stdin.encoding)
        parser.add_option("--fontName",
                          help="""\
use the named font. Default is "Courier". Alternatives are "LucidaSansTypewriter".""",
                          action="store",
                          type="string",
                          dest="fontName",
                          default="Courier")

        parser.add_option("-s", "--fontSize",
                          help="use FONTSIZE characters per inch as default font size.",
                          action="store",
                          type="int",
                          dest="fontSize",
                          default=12)

    def run(self):
        
        if len(self.args) != 1:
            raise UsageError("needs 1 argument")
    
        inputfile = self.args[0]
        if self.options.outFile is None:
            (root,ext) = os.path.splitext(inputfile)
            self.options.outFile = root +".pdf"

        d = PdfTextPrinter(
            self.options.outFile,
            session=self,
            encoding=self.options.encoding,
            fontName=self.options.fontName,
            cpi=self.options.fontSize)
                           
        d.readfile(inputfile)#,coding=sys.stdin.encoding)
        
        d.close()


def main(*args,**kw):
    Prn2pdf().main(*args,**kw)

if __name__ == '__main__':
    main()
