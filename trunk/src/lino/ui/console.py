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

raise """moved to
lino.console.syscon
lino.console.console
lino.console.application
"""

import os
import sys
import atexit
import codecs
import time

from optparse import OptionParser
from cStringIO import StringIO

from lino import __version__, __author__



# if frozen (with py2exe or McMillan), sys.setdefaultencoding() has
# not been deleted.  And site.py and sitecustomize.py haven't been
# executed.

if hasattr(sys,'setdefaultencoding'):

    import locale
    loc = locale.getdefaultlocale()
    if loc[1]:
        #print "sys.setdefaultencoding(%s)" % repr(loc[1])
        sys.setdefaultencoding(loc[1])
    

try:
    import msvcrt
except ImportError:
    msvcrt = False


#class JobAborted(Exception):
#    pass





"""

A Console instance represents the console and encapsulates some
often-used things that have to do with the console.

"""

try:
    import sound
except ImportError,e:
    sound = False

from lino.misc.jobs import Job #, PurzelConsoleJob


## class ConsoleJob(Job):
##     # for RawConsole
        
##     def onInit(self):
##         if self._label is not None:
##             self.ui.notice(self._label)
        
##     def onDone(self):
##         if self._label is not None:
##             self.ui.notice('\n')
##         Job.onDone(self,job)
        
## class DecentStreamJob(StreamJob):
##     def onStatus(self):
##         self.writer(self._status)
        
##     def onInc(self):
##         self.writer('.')
        

            
class UI:
    pass
    
class CLI:
    name = None
    years = None
    author = None
    usage = None
    description = None
    
    def parse_args(self,args=None): #,**kw):
        p = OptionParser(
            usage=self.usage,
            description=self.description)
            
        self.setupOptionParser(p)
        options,args = p.parse_args(args)
        self.applyOptions(options,args)
        

    def applyOptions(self,options,args):
        pass
    
    def setupOptionParser(self,parser):
        pass

##     def __init__(self):
##         self._progressBar = None

##     def job(self,label,maxval=0):
##         if self._progressBar is None:
##             self._progressBar = self.make_progressbar()
##         return self._progressBar.addJob(self,label,maxval)



class UsageError(Exception):
    pass
class ApplicationError(Exception):
    pass

class Application(CLI):
    """
    
    vocabulary:
    
    main() processes command-line arguments ("get the
    instructions") runs the application and returns a system error
    code (usually forwarded to sys.exit())

    run() expects that all instructions are known and performs the
    actual task.
    
    
    """
    def __init__(self,console=None):
        if console is None:
            console = _syscon
        self.console = console
        #self.ui = ui
        if self.name is not None:
            console.copyleft(name=self.name,
                             years=self.years,
                             author=self.author)

        
    def setupOptionParser(self,parser):
        self.console.setupOptionParser(parser)

    def applyOptions(self,options,args):
        self.options=options
        self.args=args

    def addProgramMenu(self,frm):
        m = frm.addMenu("&Programm")
        m.addItem(label="&Beenden",action=frm.close)
        m.addItem(label="Inf&o").setHandler(self.showAbout)
        #m.addItem(label="show &Console").setHandler(self.showConsole)
        return m


    def showAbout(self):
        frm = self.form(label="About",doc=self.aboutString())
        frm.addOkButton()
        frm.show()
        
        
    def aboutString(self):
        s = self.name
        if self.version is not None:
            s += " version " + self.version
        if self.author is not None:
            s += "Copyright (c) %s %s." % self.years, self.author
        from lino import __copyright__,  __url__
        s += "\n\n" + __copyright__
        s += "\n\nHomepage:\n" + __url__
        s += "\n\nCredits:\n"
        s += "Python %d.%d.%d %s\n" % sys.version_info[0:4]

        if sys.modules.has_key('wx'):
            wx = sys.modules['wx']
            s += "wxPython " + wx.__version__ + "\n"
    
        if sys.modules.has_key('sqlite'):
            sqlite = sys.modules['sqlite']
            s += "PySQLLite " + sqlite.version + "\n"
    
        if sys.modules.has_key('reportlab'):
            reportlab = sys.modules['reportlab']
            s += "The Reportlab PDF generation library " + \
                           reportlab.Version + "\n"

        if sys.modules.has_key('win32print'):
            win32print = sys.modules['win32print']
            s += "Python Windows Extensions " + "\n"
        
        return s
    
        
        
    def main(self,args=None):
        """
        meant to be called
        
            if __name__ == '__main__':
                MyApplication().main()
                
        but lino.runscript calls it with args=sys.argv[:2] (command-line
        arguments are shifted by one)
        
        """
        if args is None:
            args = sys.argv[1:]
        
        p = OptionParser(
            usage=self.usage,
            description=self.description)
            
        self.setupOptionParser(p)
        
        try:
            options,args = p.parse_args(args)
            self.applyOptions(options,args)
            return self.run(self.console)
        
        except UsageError,e:
            p.print_help()
            return -1
        except ApplicationError,e:
            self.console.error(str(e))
            return -1

    def run(self,ui):
        raise NotImplementedError
        


class Console(UI,CLI):

    jobClass = Job

    def __init__(self, stdout, stderr,**kw):
        self._stdout = stdout
        self._stderr = stderr
        self._logfile = None
        self._verbosity = 0
        self._batch = False
        #self._started = time.time()
        #self._dumping = None
        # UI.__init__(self)
        self.set(**kw)

    def redirect(self,stdout,stderr):
        old = (self._stdout, self._stderr)
        self._stdout = stdout
        self._stderr = stderr
        return old

    def set(self, verbosity=None, batch=None, logfile=None):
        if verbosity is not None:
            self._verbosity += verbosity
            #print "verbositiy %d" % self._verbosity
        if batch is not None:
            self._batch = batch
        if logfile is not None:
            if self._logfile is not None:
                self._logfile.close()
            self._logfile = open(logfile,"a")
##         if ui is not None:
##             self._ui = ui
        #if debug is not None:
        #    self._debug = debug

##     def startDump(self,**kw):
##         assert self._dumping is None
##         self._dumping = (StringIO(), self._stdout)
##         self._stdout = self._dumping[0].write

##     def stopDump(self):
##         assert self._dumping is not None, "dumping was not started"
##         s = self._dumping[0].getvalue()
##         self._stdout = self._dumping[1]
##         self._dumping = None
##         return s

        
    def isBatch(self):
        return self._batch
    def isInteractive(self):
        return not self._batch
    
    def isVerbose(self):
        return (self._verbosity > 0)
    
    def isQuiet(self):
        return (self._verbosity < 0)
    
    def isVeryQuiet(self):
        return (self._verbosity < -1)
    

    def write(self,msg):
        self._stdout(msg)
        
    def writeout(self,msg):
        self._stdout(msg+"\n")

    def writelog(self,msg):
        if self._logfile:
            #t = strftime("%a %Y-%m-%d %H:%M:%S")
            t = time.strftime("%H:%M:%S")
            self._logfile.write(t+" "+msg+"\n")
            self._logfile.flush()
            
    def status(self,*args,**kw):
        self.verbose(*args,**kw)

    def error(self,msg,*args,**kw):
        msg = self.buildMessage(msg,*args,**kw)
        self._stderr(msg + "\n")
        self.writelog(msg)

    def buildMessage(self,msg,*args,**kw):
        assert len(kw) == 0, "kwargs not yet implemented"
        if len(args) == 0:
            return msg
        return msg % args
    
    def critical(self,msg,*args,**kw):
        "Something terrible has happened..."
        #self.writelog(msg)
        #if sound:
        #    sound.asterisk()
        self.error("critical: " + msg,*args,**kw)

##     def handleException(self,e):
##         self.error(str(e))
    
        

    def warning(self,msg,*args,**kw):
        "Display message if verbosity is normal. Logged."
        msg = self.buildMessage(msg,*args,**kw)
        self.writelog(msg)
        if self._verbosity >= 0:
            self.writeout(msg)

    def notice(self,msg,*args,**kw):
        "Display message if verbosity is normal. Not logged."
        if self._verbosity >= 0:
            msg = self.buildMessage(msg,*args,**kw)
            self.writeout(msg)

    def verbose(self,msg,*args,**kw):
        "Display message if verbosity is high. Not logged."
        if self._verbosity > 0:
            msg = self.buildMessage(msg,*args,**kw)
            self.writeout(msg)
        
    def debug(self,msg,*args,**kw):
        "Display message if verbosity is very high. Not logged."
        if self._verbosity > 1:
            msg = self.buildMessage(msg,*args,**kw)
            self.writeout(msg)
            #self.out.write(msg + "\n")

            


    def onJobRefresh(self,job):
        pass
    
    def onJobInit(self,job):
        if job._label is not None:
            self.notice(job._label)

##     def onJobStatus(self,job):
##         pass

    def onJobDone(self,job,msg):
        self.status(None)
        job.summary()
        if msg is not None:
            self.notice(job.getLabel() + ": " + msg)
    
    def onJobAbort(self,job,msg):
        self.status(None)
        job.summary()
        self.error(job.getLabel() + ": " + msg)

            
        
##      def notify(self,msg):

##          """Notify the user about something just for information.

##          Without acknowledgment request.

##          examples: why a requested action was not executed
##          """
##          if sound:
##              sound.asterisk()
##          #notifier(msg)
##          self.out.write(msg + "\n")
##          #self.out.write('[note] ' + msg + "\n")

##      def progress(self,msg):
##          """as notify, but only if verbose """
##          if self.verbose:
##              self.notify(msg)
            
    def setupOptionParser(self,p):
        def call_set(option, opt_str, value, parser,**kw):
            self.set(**kw)

        def set_logfile(option, opt_str, value, parser,**kw):
            self.set(logfile=value)

        p.add_option("-v",
                     "--verbose",
                     help="increase verbosity",
                     action="callback",
                     callback=call_set,
                     callback_kwargs=dict(verbosity=1)
                     )

        p.add_option("-q",
                     "--quiet",
                     help="decrease verbosity",
                     action="callback",
                     callback=call_set,
                     callback_kwargs=dict(verbosity=-1)
                     )

        p.add_option("-b",
                     "--batch",
                     help="not interactive (don't ask anything)",
                     default=self.isBatch(),
                     action="callback",
                     callback=call_set,
                     callback_kwargs=dict(batch=True)
                     )
        p.add_option("-l", "--logfile",
                     help="log a report to FILE",
                     type="string",
                     dest="logFile",
                     action="callback",
                     callback=set_logfile)

    def message(self,msg):
##         if self.app is not None:
##             return self.app.warning(msg)
        
        #if sound:
        #    sound.asterisk()
        self.writeout(msg)
        #self.alert(msg)
        if not self._batch:
            raw_input("Press ENTER to continue...")
            
            
    def confirm(self,prompt,default="y"):
        """Ask user a yes/no question and return only when she has
        given her answer. returns True or False.
        
        """
        #print self._stdout
##         if self.app is not None:
##             return self.app.confirm(prompt,default)
        if self._batch:
            return (default=='y')
        
        if sound:
            sound.asterisk()
        if default == "y":
            prompt += " [Y,n]"
        else:
            assert default == "n"
            prompt += " [y,N]"
        while True:
            s = raw_input(prompt)
            if s == "":
                s = default
            s = s.lower()
            if s == "y":
                return True
            if s == "n":
                return False
            self.error("wrong answer, must be 'y' or 'n': "+s)
            

    def decide(self,prompt,answers,
               default=None,
               ignoreCase=True):
        
        """Ask user a question and return only when she has given her
        answer. Returns the index of chosen answer or -1 if user
        refused to answer.
        
        """
        if default is None:
            default = answers[0]
            
        if self._batch:
            return default
        
        if sound:
            sound.asterisk()
        while True:
            s = raw_input(prompt+(" [%s]" % ",".join(answers)))
            if s == "":
                s = default
            if ignoreCase:
                s = s.lower()
            if s in answers:
                return s
            self.warning("wrong answer: "+s)

    def shutdown(self):
        #self.verbose("Done after %f seconds.",
        #             time.time() - self._started)
        if sys.platform == "win32":
            utime, stime, cutime, cstime, elapsed_time = os.times()
            self.verbose("%.2f+%.2f=%.2f seconds used",
                         utime,stime,utime+stime)
        else:
            self.verbose( "+".join([str(x) for x in os.times()])
                          + " seconds used")
        if self._logfile:
            self._logfile.close()
        

    def form(self,*args,**kw):
        raise NotImplementedError

    def job(self,*args,**kw):
        job = Job()
        job.init(self,*args,**kw)
        return job
    
    def textprinter(self):
        from lino.textprinter.plain import PlainTextPrinter
        return PlainTextPrinter(self._stdout)
        
##     def report(self,**kw):
##         from lino.reports.plain import Report
##         return Report(writer=self._stdout,**kw)


    def report(self,rpt,*args,**kw):
        from lino.gendoc.plain import PlainDocument
        gd = PlainDocument(writer=self._stdout)
        gd.beginDocument()
        gd.report(rpt)
        gd.endDocument()
    


    def abortRequested(self):
        return False
        

class TtyConsole(Console):

    width = 78  # 
    purzelMann = "|/-\\"
    #jobClass = PurzelConsoleJob

    

    def __init__(self,*args,**kw):
        self._status = None
        Console.__init__(self,*args,**kw)


##     def onJobStatus(self,job):
##         self._display_job(job)

    def onJobRefresh(self,job):
        self._display_job(job)
        if self.abortRequested():
            if job.confirmAbort():
                job.abort()
                #raise JobAborted()
                
    def _display_job(self,job):
        if job.maxval == 0:
            s = '[' + self.purzelMann[job.curval % 4] + "] "
        else:
            if job.pc is None:
                s = "[    ] " 
            else:
                s = "[%3d%%] " % job.pc
        self.status(s+job.getStatus())
##         if abortRequested():
##             if self.confirm("Are you sure you want to abort?"):
##                 job.abort() # raises JobAborted
    
    def abortRequested(self):
        if not msvcrt: return False
        # print "abortRequested"
        while msvcrt.kbhit():
            ch = msvcrt.getch()
            #print ch
            if ord(ch) == 0: #'\000':
                ch = msvcrt.getch()
                if ord(ch) == 27:
                    return True
            elif ord(ch) == 27:
                return True
        return False

    def warning(self,msg,*args,**kw):
        msg = self.buildMessage(msg,*args,**kw)
        Console.warning(self,msg.ljust(self.width))
        self._refresh()
        
    def message(self,msg,*args,**kw):
        msg = self.buildMessage(msg,*args,**kw)
        Console.message(self,msg.ljust(self.width))
        self._refresh()
        
    def notice(self,msg,*args,**kw):
        msg = self.buildMessage(msg,*args,**kw)
        Console.notice(self,msg.ljust(self.width))
        self._refresh()
        
    def verbose(self,msg,*args,**kw):
        msg = self.buildMessage(msg,*args,**kw)
        Console.verbose(self,msg.ljust(self.width))
        self._refresh()
        
    def error(self,msg,*args,**kw):
        msg = self.buildMessage(msg,*args,**kw)
        Console.error(self,msg.ljust(self.width))
        self._refresh()
        
    def critical(self,msg,*args,**kw):
        msg = self.buildMessage(msg,*args,**kw)
        Console.critical(self,msg.ljust(self.width))
        self._refresh()
        
        
    def status(self,msg,*args,**kw):
        if msg is None:
            self._status = None
        else:
            msg = self.buildMessage(msg,*args,**kw)
            self._status = msg[:self.width]
            self._stdout(self._status.ljust(self.width)+"\r")

    def _refresh(self):
        if self._status is not None:
            self._stdout(self._status+"\r")

    def copyleft(self,name="Lino",
                 version=__version__,
                 years="2002-2005",
                 author=__author__):
        self.notice("""\
%s version %s.
Copyright (c) %s %s.
This software comes with ABSOLUTELY NO WARRANTY and is
distributed under the terms of the GNU General Public License.
See file COPYING.txt for more information.""" % (
            name, version, years, author))




class CaptureConsole(Console):
    
    def __init__(self,**kw):
        self.buffer = StringIO()
        Console.__init__(self,
                         self.buffer.write,
                         self.buffer.write,**kw)

    def getConsoleOutput(self):
        s = self.buffer.getvalue()
        self.buffer.close()
        self.buffer = StringIO()
        self.redirect(self.buffer.write,self.buffer.write)
        return s
    
_syscon = None


# rewriter() inspired by a snippet in Marc-Andr� Lemburg's Python
# Unicode Tutorial
# (http://www.reportlab.com/i18n/python_unicode_tutorial.html)

def rewriter(to_stream):
    if to_stream.encoding is None:
        return to_stream
    if to_stream.encoding == sys.getdefaultencoding():
        return to_stream

    (e,d,sr,sw) = codecs.lookup(to_stream.encoding)
    unicode_to_fs = sw(to_stream)

    (e,d,sr,sw) = codecs.lookup(sys.getdefaultencoding())
    class StreamRewriter(codecs.StreamWriter):

        encode = e
        decode = d

        def write(self,object):
            data,consumed = self.decode(object,self.errors)
            self.stream.write(data)
            return len(data)

    return StreamRewriter(unicode_to_fs)

def setSystemConsole(c):
    g = globals()
    g['_syscon'] = c

    for funcname in (
        'debug','message','notice','status',
        'job', 'verbose', 'error','critical',
        'confirm','warning','copyleft',
        'report','textprinter',
        #'startDump','stopDump',
        'isInteractive','isVerbose', 'set',
        'parse_args', ):
        g[funcname] = getattr(_syscon,funcname)

def getSystemConsole():
    return _syscon



if hasattr(sys.stdout,"encoding") \
      and sys.getdefaultencoding() != sys.stdout.encoding:
    sys.stdout = rewriter(sys.stdout)
    sys.stderr = rewriter(sys.stderr)


#_syscon = Console(sys.stdout.write, sys.stderr.write)
setSystemConsole(
    TtyConsole(sys.stdout.write, sys.stderr.write))



atexit.register(_syscon.shutdown)









