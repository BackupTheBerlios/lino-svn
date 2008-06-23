# -*- coding: iso-8859-1 -*-

## Copyright 2005-2008 Luc Saffre 

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
import time
import datetime
from PIL import Image, ImageWin
from PIL.TiffImagePlugin import DATE_TIME

from lino.console.application import Application, UsageError


class MyException(Exception):
    pass

def avinewname(root,name):
    pass

def wavnewname(root,name):
    # this is wrong.
    # i want to know how the creation date is stored in .wav files
    filename=os.path.join(root, name)
    sti=os.stat(filename)
    ct=time.localtime(sti.st_ctime)
    return time.strftime("%Y_%m_%d-%H_%M_%S.wav",ct)
    

class JpgRename(Application):

    name="Lino/jpgrename"

    copyright="""\
Copyright (c) 2002-2008 Luc Saffre.
This software comes with ABSOLUTELY NO WARRANTY and is
distributed under the terms of the GNU General Public License.
See file COPYING.txt for more information."""
    
    usage="usage: lino jpgrename [options] [DIR]"
    description="""\
where DIR (default .) is a directory with .jpg files to rename.
"""
    def setupOptionParser(self,parser):
        Application.setupOptionParser(self,parser)

        parser.add_option(
            "-s", "--simulate",
            help="simulate only, don't do it",
            action="store_true",
            dest="simulate",
            default=False)

        parser.add_option(
            "-d", "--timediff",
            help="correct EXIF time by adding TIMEDIFF minutes",
            action="store", type="int",
            dest="timediff",
            default=0)
        
        parser.add_option(
            "--suffix",
            help="add SUFFIC to each filename",
            action="store", type="string",
            dest="suffix",
            default="")

    def run(self):
         
        self.converters = {
            '.jpg' : self.jpgnewname,
            '.avi' : avinewname,
            '.wav' : wavnewname,
            }

        if len(self.args) == 0:
            dirs=['.']
        else:
            dirs=self.args

        for dirname in dirs:
            self.walk(dirname)
            
    def walk(self,dirname):
        for root, dirs, files in os.walk(dirname):
            okay=True
            filenames = {}
            for name in files:
                base,ext = os.path.splitext(name)
                cv = self.converters.get(ext.lower(),None)
                if cv is not None:
                    try:
                        nfn=cv(root,name)
                    except MyException,e:
                        self.warning(str(e))
                    else:
                        if nfn is None: pass
                        elif nfn == name: pass
                        elif filenames.has_key(nfn):
                            okay=False
                            self.warning(
                                '%s/%s: duplicate time %s', \
                                root,name,nfn)
                        else:
                            filenames[nfn] = name
            if not okay: return
            if len(filenames) == 0:
                self.notice("Nothing to do.")
                return
            
            if not self.confirm(
                "Rename %d files in directory %s ?" % \
                (len(filenames),root)):
                return
            
            for nfn,ofn in filenames.items():
                o=os.path.join(root,ofn)
                n=os.path.join(root,nfn)
                if self.options.simulate:
                    self.notice("Would rename %s to %s", o,n)
                else:
                    self.notice("Rename %s to %s", o,n)
                    os.rename(o,n)
                                   
    def dt2filename(self,s):
        a = s.split()
        if len(a) != 2: return None
        d=a[0].split(':')
        if len(d) != 3: return None
        t=a[1].split(':')
        if len(t) != 3: return None
        args=[int(x) for x in d] + [int(x) for x in t]
        dt=datetime.datetime(*args)
        dt += datetime.timedelta(0,0,0,0,self.options.timediff)
        #print '_'.join(d)+'-'+'_'.join(t)+'.jpg', "->", dt.strftime("%Y_%m_%d-%H_%M_%S.jpg")
        #return '_'.join(d)+'-'+'_'.join(t)+'.jpg'
        return dt.strftime("%Y_%m_%d-%H_%M_%S")

    def jpgnewname(self,root,name):
        filename=os.path.join(root, name)
        try:
            img = Image.open(filename)
        except IOError,e:
            raise MyException(filename + ":" + str(e))
        exif=img._getexif()
        if exif is None:
            raise MyException(filename+ ': no EXIF information found')
        if not exif.has_key(DATE_TIME):
            raise MyException(filename+ ':'+ str(exif.keys()))
        nfn=self.dt2filename(exif[DATE_TIME])
        if nfn is None:
            raise MyException(
                '%s: could not parse DATE_TIME "%s"' \
                % (filename, exif[DATE_TIME]))
        nfn+= self.options.suffix
        return nfn + ".jpg"




#JpgRename().main()

## # lino.runscript expects a name consoleApplicationClass
## consoleApplicationClass = JpgRename

## if __name__ == '__main__':
##     consoleApplicationClass().main() 
    
def main(*args,**kw):
    JpgRename().main(*args,**kw)
