#coding: latin1
## Copyright 2004-2005 Luc Saffre 

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

import sys
import os
opj = os.path.join

from lino import adamo
#from lino.forms import gui

from lino.apps.raceman import races, loaders

from lino.forms.application import MirrorLoaderApplication



class Raceman(MirrorLoaderApplication):

    def getLoaders(self):
        return [lc(self.loadfrom) for lc in loaders.LOADERS]

    def init(self,toolkit):
        races.setupSchema(self.schema)
        self.schema.registerLoaders(self.getLoaders())
        
        self.sess = self.schema.quickStartup(
            ui=toolkit, filename=self.filename)
        
        assert self.mainForm is None
        
        self.mainForm = frm = self.form(
            label="Main menu",
            doc="""\
This is the Raceman main menu.                                     
"""+("\n"*10))

        m = frm.addMenu("&Stammdaten")
        
        m.addItem(label="&Events").setHandler(
            self.showViewGrid,frm,
            races.Events,"std")
        
        m.addItem(label="&Races").setHandler(
            self.showViewGrid,frm,
            races.Races,"std")

        m.addItem(label="&Clubs").setHandler(
            self.showTableGrid,frm,
            races.Clubs)
        m.addItem(label="&Personen").setHandler(
            self.showTableGrid,frm,
            races.Persons)
    
        #m = frm.addMenu("&Arrivals")
        #m.addItem(label="&Erfassen").setHandler(self.arrivals)

        m = frm.addMenu("&Programm")
        m.addItem(label="&Beenden",action=frm.close)
        m.addItem(label="Inf&o").setHandler(self.showAbout)

        frm.addOnClose(self.close)


        

def main(argv):

    app = Raceman(name="Raceman", years='2005')
    app.parse_args(argv)
    #gui.run(app)
    app.run()





if __name__ == '__main__':
    main(sys.argv[1:])



