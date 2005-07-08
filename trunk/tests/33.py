# coding: latin1

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

import types
from lino.misc.tsttools import TestCase, main, Toolkit
from lino.console import syscon

#from lino.forms.session import Session
from lino.console.task import Task

from lino import i18n
i18n.setUserLang(None)

class TestTask(Task):
    
    def getMaxVal(self):
        return 10
    
    def getLabel(self):
        return "Testing uncomplete tasks"
    
    def run(self):
        self.status("Running...")
        for i in range(5):
            for c in "abc":
                self.status("Performing step %d%s)",i+1,c)
            self.increment()
        self.status("Done in only 5 steps.")
        

class Case(TestCase):

    verbosity=1
    
    def test01(self):
        #
        #sess=Session(Toolkit())
        #sess=syscon._session
        syscon.runTask(TestTask())
        #job=syscon.job("Testing uncomplete jobs",10)
        #for i in range(5):
        #    job.increment()
        #job.done("done in only 5 steps.")
        s=self.getConsoleOutput()
        #print s
        self.assertEquivalent(s,"""
Testing uncomplete tasks
[  0%] Running...
[  0%] Performing step 1a)
[  0%] Performing step 1b)
[  0%] Performing step 1c)
[ 10%] Performing step 1c)
[ 10%] Performing step 2a)
[ 10%] Performing step 2b)
[ 10%] Performing step 2c)
[ 20%] Performing step 2c)
[ 20%] Performing step 3a)
[ 20%] Performing step 3b)
[ 20%] Performing step 3c)
[ 30%] Performing step 3c)
[ 30%] Performing step 4a)
[ 30%] Performing step 4b)
[ 30%] Performing step 4c)
[ 40%] Performing step 4c)
[ 40%] Performing step 5a)
[ 40%] Performing step 5b)
[ 40%] Performing step 5c)
[ 50%] Performing step 5c)
[100%] Performing step 5c)
0 warnings
0 errors
Testing uncomplete tasks: Done in only 5 steps.
""")
        

if __name__ == '__main__':
    main()

