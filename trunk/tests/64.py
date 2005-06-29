#coding: latin1
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

import os
from lino.console import syscon
from lino.misc import tsttools
from lino.oogen import TextDocument, elements

class Case(tsttools.TestCase):
    
    def test01(self):
        "First styles"
        fn = self.addTempFile("2.sxw", showOutput=True)
        doc = TextDocument(fn)
        
        s = doc.addStyle(name="Rechts",
                         family="paragraph",
                         parentStyleName="Standard",
                         className="text")
        s.addProperties(textAlign="end",
                        justifySingleWord=False)
        
        
        doc.h(1,"Defining custom styles")
        doc.p("This is a right-aligned paragraph.",styleName="Rechts")
        doc.p("Here is a standard paragraph.")
    
        doc.save(syscon)
        
if __name__ == "__main__":
    tsttools.main()