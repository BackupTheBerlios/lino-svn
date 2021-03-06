## Copyright Luc Saffre 2003-2005

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

"""

bug 20040914: tables LANGS and NATIONS of demo db seemed empty (their
len() was 0) because Datasource.rowcount (which is a cached value) was
not re-read from database when some other Datasource on same store did
an appendRow().

"""

from lino.misc.tsttools import TestCase, main

from lino.apps.pinboard.pinboard_demo import startup
from lino.apps.pinboard.pinboard_tables import *

class Case(TestCase):

    def setUp(self):
        TestCase.setUp(self)
        self.sess = startup()

    def tearDown(self):
        self.sess.shutdown()


    def test01(self):
        #for lang in self.sess.tables.LANGS:
        #   print lang
        self.assertEqual(len(self.sess.query(Language)),5)
        

if __name__ == '__main__':
    main()
