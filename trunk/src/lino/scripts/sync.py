#coding: latin1

## Copyright 2005-2009 Luc Saffre.
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

from lino.console.application import Application, \
     UsageError, UserAborted
from lino.tools.synchronizer import Synchronizer
from lino import __url__

class Sync(Application):

    name="Lino/Sync"
    copyright="""\
Copyright (c) 2005-2009 Luc Saffre.
This software comes with ABSOLUTELY NO WARRANTY and is
distributed under the terms of the GNU General Public License.
See file COPYING.txt for more information."""
    url=__url__+"/sync.html"
    
    usage="usage: lino sync [options] SRC DEST"
    
    description="""\
where SRC and DEST are two directories to be synchronized.
""" 
    
    def setupOptionParser(self,parser):
        Application.setupOptionParser(self,parser)

        parser.add_option(
            "-n", "--noaction",
            help="no action, just say what to do",
            action="store_true",
            dest="noaction",
            default=False)
        
        parser.add_option(
            "-u", "--unsafely",
            help="skip safety loop",
            action="store_false",
            dest="safely",
            default=True)
        
        parser.add_option(
            "-r", "--recurse",
            help="recurse into subdirs",
            action="store_true",
            dest="recurse",
            default=False)

        parser.add_option(
            "-i", "--ignore",
            help="ignore files that match the pattern",
            action="append",
            type="string",
            dest="ignore")

    def run(self):

        job=Synchronizer()
        
        if len(self.args) == 2:
            job.addProject(
                self.args[0],self.args[1],
                self.options.recurse, self.options.ignore)

        
        elif len(self.args) == 1:
            #tasks=[]
            for ln in open(self.args[0]).readlines():
                ln=ln.strip()
                if len(ln):
                    if not ln.startswith("#"):
                        a=ln.split()
                        assert len(a) == 2
                        job.addProject(
                            a[0],a[1],
                            self.options.recurse,
                            self.options.ignore)
                        
                        
        else:
            raise UsageError("needs 1 or 2 arguments")

        self.runtask(job,safely=self.options.safely,
                     noaction=self.options.noaction)
                     

def main(*args,**kw):
    Sync().main(*args,**kw)

if __name__ == '__main__': main() 
