#coding: latin1

## Copyright 2005 Luc Saffre.
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
import shutil
import stat


try:
    import win32file
except:
    win32file = None


from lino.ui import console

class SyncError(Exception):
    pass

class Sync:
    def __init__(self,srcroot,destroot):
        self.must_mkdir = []
        self.must_rmdir = []
        self.must_copy = []
        self.must_update = []
        self.must_delete = []

        self.ignore_times = False
        self.modify_window = 2
 
        srcroot = os.path.normpath(srcroot)
        destroot = os.path.normpath(destroot)
       
        if not os.path.isdir(srcroot):
            raise SyncError(srcroot+" is not a directory")
        self.srcroot = srcroot
        self.destroot = destroot

    def mkdir(self,name):
        self.must_mkdir.append(name)
        
    def rmdir(self,name):
        #self.must_rmdir.append(name)
        self.must_rmdir.insert(0,name)

    def removeFile(self, name):
        self.must_delete.append( name )
        
    def copyFile(self, src, target):
        self.must_copy.append( (src,target) )

    def updateFile(self, src, target):
        self.must_update.append( (src,target) )



    def shouldUpdate(self, src, target):
        try:
            src_st = os.stat(src)
            src_sz = src_st.st_size
            src_mt = src_st.st_mtime
        except Exception,e:
            console.error(str(e))
            return False

        try:
            target_st = os.stat(target)
            target_sz = target_st.st_size
            target_mt = target_st.st_mtime
        except Exception,e:
            console.error(str(e))
            return False

        if target_sz != src_sz:
            return True

        if self.ignore_times:
            return True

        if abs(target_mt - src_mt) > self.modify_window:
    ##         print "%s to %s:\nabs(%s - %s) > %s" % (
    ##             src,target,
    ##             target_mt, src_mt,
    ##             cookie.modify_window)
            return True
        
        return False


    def utime(self,src,target):
        # Note: The utime api of the 2.3 version of python is
        # not unicode compliant.    
        try:
            s = os.stat(src)
            os.utime(target, (s.st_atime, s.st_mtime))
            #print "os.utime(%s,%s,%s)" % (
            #    target, s.st_atime, s.st_mtime)
        except Exception,e:
            console.error(str(e))


    def visitDest(self,dirname,names):
        for name in names:
            target = os.path.join(dirname, name)
            src = self.srcroot + target[len(self.destroot):]
            if not os.path.exists(src):
                if os.path.isfile(target):
                    self.removeFile(target)
                elif os.path.isdir(target):
                    self.rmdir(target)
                else:
                    raise SyncError(
                        "%s is neither file nor directory" % src)
            if os.path.isdir(target):
                self.visitDest(target,os.listdir(target))


    def visitSource(self,dirname,names):
        for name in names:
            src = os.path.join(dirname, name)
            target = self.destroot + src[len(self.srcroot):]
            if os.path.isfile(src):
                if os.path.isfile(target):
                    if self.shouldUpdate(src, target):
                        self.updateFile(src, target)
                    elif console.isVerbose():
                        console.info(target+" is up-to-date")
                elif os.path.isdir(target):
                    self.rmdir(target)
                    self.copyFile(src, target)
                else:
                    self.copyFile(src, target)

            elif os.path.isdir(src):
                if os.path.isfile(target):
                    self.removeFile(target)
                    self.mkdir(target)
                elif os.path.isdir(target):
                    pass
                else:
                    self.mkdir(target)
                    
                self.visitSource(src,os.listdir(src))
                
            else:
                raise SyncError(
                    "%s is neither file nor directory" % src)



    def reallycopy(self,src,target):
        try:
            shutil.copyfile(src, target)
            self.utime(src,target)
        except Exception,e:
            console.error(str(e))
        

    def analyze(self):
            
        if os.path.isdir(self.destroot):
            self.visitDest(self.destroot,os.listdir(self.destroot))
            
        self.visitSource(self.srcroot,os.listdir(self.srcroot))
        
        
        
        
    def summary(self):
        s = "delete %d files and %d directories" % (
            len(self.must_delete), len(self.must_rmdir))
        s += "\n" + \
             "create %d files and %d directories" % (
            len(self.must_copy), len(self.must_mkdir))
        
        s += "\n" + \
             "update %d files" % len(self.must_update)
        return s
    
    
    def doit(self):
        
        for name in self.must_delete:
            if win32file:
                filemode = win32file.GetFileAttributesW(name)
                win32file.SetFileAttributesW(
                    name, filemode & \
                    ~win32file.FILE_ATTRIBUTE_READONLY & \
                    ~win32file.FILE_ATTRIBUTE_HIDDEN & \
                    ~win32file.FILE_ATTRIBUTE_SYSTEM)
            else:
                os.chmod(name, stat.S_IWUSR)

            try:
                os.remove(name)
            except Exception,e:
                console.error(str(e))
            
        for name in self.must_mkdir:
            try:
                os.makedirs(name)
            except Exception,e:
                console.error(str(e))
            
        for src,target in self.must_copy:
            self.reallycopy(src,target)

        for src,target in self.must_update:
            if win32file:
                filemode = win32file.GetFileAttributesW(target)
                win32file.SetFileAttributesW(
                    target,
                    filemode & \
                    ~win32file.FILE_ATTRIBUTE_READONLY & \
                    ~win32file.FILE_ATTRIBUTE_HIDDEN & \
                    ~win32file.FILE_ATTRIBUTE_SYSTEM)
            else:
                os.chmod(target, stat.S_IWUSR)

            self.reallycopy(src,target)

            if win32file:
                win32file.SetFileAttributesW(target, filemode)

        
        for name in self.must_rmdir:
            try:
                os.rmdir(name)
            except Exception,e:
                console.error(str(e))
            
        


                



def main(argv):
    console.copyleft(name="Lino/sync",
                     years='2005',
                     author='Luc Saffre')
    
    parser = console.getOptionParser(
        usage="usage: lino sync [options] SRC DEST",
        description="""\
where SRC and DEST are two directories to be synchronized.
""" )
    
    (options, args) = parser.parse_args(argv)

    if len(args) != 2:
        parser.print_help() 
        sys.exit(-1)

    sync = Sync(args[0],args[1])

    sync.analyze()
    
    print sync.summary()
    
    if console.confirm("do it?"):
        sync.doit()



if __name__ == '__main__':
    try:
        main(sys.argv[1:])
    except SyncError,e:
        console.error(str(e))
        sys.exit(-1)
        

