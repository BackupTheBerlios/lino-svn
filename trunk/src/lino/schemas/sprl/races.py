## Copyright Luc Saffre 2004-2005.

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

from lino.adamo import *
from babel import Languages
from addrbook import Persons, SEX

class Races(Table):
    def init(self):
        self.name1 = Field(STRING,width=30)
        self.name2 = Field(STRING,width=30)
        self.date = Field(DATE)
        self.status = Field(STRING,width=1)
        self.tpl  = Field(STRING,width=6)
        self.type  = Pointer(RaceTypes)
        self.startTime  = Field(TIME)

    class Instance(Table.Instance):
        def getLabel(self):
            return self.name1
        
class RaceTypes(Table):
    def init(self):
        self.id = Field(STRING,width=5)
        self.name = Field(STRING,width=30)

    class Instance(Table.Instance):
        def getLabel(self):
            return self.name
        
class Categories(Table):
    def init(self):
        self.type  = Pointer(RaceTypes)
        self.id = Field(STRING,width=3)
        self.seq = Field(ROWID)
        self.name = Field(STRING,width=30)
        self.sex  = Field(SEX)
        self.ageLimit  = Field(INT)
        self.setPrimaryKey('type id')

    class Instance(Table.Instance):
        def getLabel(self):
            return self.id + " ("+self.name+")"
        
class Participants(Table):
    def init(self):
        self.setPrimaryKey("race dossard")
        self.race = Pointer(Races)
        self.dossard = Field(STRING)
        self.person = Pointer(Persons)
        self.time = Field(TIME)
        self.cat = Pointer(Categories)
        self.payment = Field(STRING,width=1)
        
