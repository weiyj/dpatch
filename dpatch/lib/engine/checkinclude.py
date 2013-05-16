#!/usr/bin/python
#
# DailyPatch - Automated Linux Kernel Patch Generate Engine
# Copyright (C) 2012, 2013 Wei Yongjun <weiyj.lk@gmail.com>
#
# This file is part of the DailyPatch package.
#
# DailyPatch is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# DailyPatch is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Patchwork; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA

import os
import re
import tempfile
import subprocess

from patchengine import PatchEngine
from dpatch.lib.common.const import CHECK_INCLUDE_TYPE

class CheckIncludeEngine(PatchEngine):
    def __init__(self, repo, logger = None):
        PatchEngine.__init__(self, repo, logger)
        self._content = []
        self._type = CHECK_INCLUDE_TYPE
        self._mvlist = []
        # the following file can be included twice in special file
        self._except_list = {"drivers/input/misc/yealink.c": ["yealink.h"],
                             "arch/x86/kvm/mmu.c": ["paging_tmpl.h"],
                             "arch/mips/txx9/generic/setup.c": ["asm/txx9/boards.h"],
                             "arch/xtensa/kernel/syscall.c": ["asm/unistd.h"]}
        # the following file can be included twice in any file
        self._except_safe = ["linux/drbd_nl.h", "asm/syscalls_32.h", "asm/syscalls_64.h"]

    def name(self):
        return 'check include'

    def _is_special_file(self, filename):
        # change <linux/test.h> to linux/test.h
        rfile = filename[1:-1]
        srcfile = self._fname
        if self._except_list.has_key(srcfile):
            if self._except_list[srcfile].count(rfile) != 0:
                return True

        if self._except_safe.count(rfile) != 0:
            return True

        return False

    def _get_include_list(self):
        grep1 = subprocess.Popen(["/usr/bin/grep", "-n", "^[ ]*#[a-z]", self._get_file_path()],
                                  stdout=subprocess.PIPE)

        grepOutput = grep1.communicate()[0]
        #print grepOutput
        #skip #ifdef etc
        inclist = []
        depth = 0
        inlineinc = []
        for line in grepOutput.split("\n"):
            # change '# if' to '#if'
            line = re.sub('#[ \t]+', "#", line)
            # skip the include file between #ifXXX and #endif
            # this may missing the dup like #ifdef XXX #include <a> #include <b> #endif
            if len(line) == 0:
                continue
            if line.find("#include") != -1:
                if depth == 0:
                    inclist.append(line)
                elif inlineinc[-1].count(line) != 0:
                    inclist.append(line)
                else:
                    inlineinc[-1].append(line)
            elif line.find("#ifndef") != -1 or line.find("#ifdef") != -1 or line.find("#if") != -1:
                depth += 1
                inlineinc.append([])
            elif line.find("#else") != -1:
                if depth == 0:
                    continue
                inlineinc[-1] = []
            elif line.find("#endif") != -1:
                depth -= 1
                if depth >= 0:
                    inlineinc.pop(depth)
                #else:
                #    print "ERROR endif?\n%s" % grepOutput
            #elif line.find("#define") != -1 or line.find("#undef") != -1 or line.find("#else") != -1 or line.find("#elif") != -1 or line.find("#error") != -1:
            #    continue
            #else:
            #    print "unknow line " + line
        #print  inclist

        # return the list of <filename.h> or "filename.h"
        return re.findall(r'["<][a-zA-Z0-9_\\/\\.]+[">]', "\n".join(inclist))

    def _can_include_twice(self, filename):
        rfile = filename[1:-1]
        fullpath = self._repo + '/include/' + rfile
        #print fullpath

        # common idea of using gcc
        # each inculde file may have the following format:
        # #ifndef _HEADER_H_
        # #define _HEADER_H_
        # coding ...
        # #endif
        # if we define _HEADER_H_ before include this file
        # gcc -E will output nothing but comment
        defines = ""
        if os.path.exists(fullpath):
            grep1 = subprocess.Popen(["/usr/bin/grep", "#ifndef", fullpath],
                                     stdout=subprocess.PIPE)

            defines = grep1.communicate()[0]
        elif os.path.exists(os.path.dirname(self._get_file_path()) + '/' + rfile):
            grep1 = subprocess.Popen(["/usr/bin/grep", "#ifndef", 
                                      os.path.dirname(self._get_file_path()) + '/' + rfile],
                                     stdout=subprocess.PIPE)

            defines = grep1.communicate()[0]
        elif os.path.exists('/usr/include/' + rfile):
            # mybe exists in system?
            grep1 = subprocess.Popen(["/usr/bin/grep", "#ifndef", 
                                      '/usr/include/' + rfile],
                                     stdout=subprocess.PIPE)

            defines = grep1.communicate()[0]
        else:
            # not found, treat as can include twice
            self.warning("Ignore %s include file (not found) %s" % (self._fname, rfile))
            return True

        tmpsrc = defines.replace('#ifndef', '#define')
        tmpsrc += "\n#include " + filename + "\n"
        #print tmpsrc

        tempfilename = tempfile.mktemp()
        #print tempfilename
        cfg = open(tempfilename, "w")
        cfg.write(tmpsrc)
        cfg.close()

        # gcc with define will output empty source file is dup include has no mean        
        gcc = subprocess.Popen(["/usr/bin/gcc", "-x", "c", "-E", tempfilename,
                                "-D", "__KERNEL__",  # some header file need __KERNEL__ define
                                "-I" + self._repo + "/include/",
                                "-I" + os.path.dirname(self._get_file_path())],
                                  stdout=subprocess.PIPE)
        tmpsrc = gcc.communicate()[0]
        if gcc.returncode != 0:
            self.warning("Ignore %s include file (gcc error) %s" % (self._fname, rfile))
            self.warning(tmpsrc)
            return True

        os.remove(tempfilename)
        #print tmpsrc
        # remove '# XXXXX'
        tmpsrc = re.sub('#.*', "", tmpsrc)
        # remove blank line
        tmpsrc = re.sub('\s*\n', "", tmpsrc)
        #print len(tmpsrc)

        if len(tmpsrc) == 0:
            return False

        return True

    def _should_patch(self):
        files = self._get_include_list()
        if len(files) == 0:
            return False

        # reset global values
        self._mvlist = []

        inclists = {}
        duplist = []
        for ifile in files:
            if inclists.has_key(ifile):
                duplist.append(ifile)
            else:
                inclists[ifile] = 1

        if len(duplist) == 0:
            return False

        chklist = filter(lambda x : duplist.count(x) == 1, duplist)
        for chk in chklist:
            if self._is_special_file(chk):
                continue
            if not self._can_include_twice(chk):
                self._mvlist.append(chk)
        if len(self._mvlist) == 0:
            return False

        return True

    def _modify_source_file(self):
        self._content = self._read_from_file()
        _target = {}
        newctx = []
        for line in self._content:
            #print line
            tline = re.sub('#[ \t]+', "#", line)
            if tline.find("#include") != -1:
                incfile = re.sub('#include', "", tline).strip()
                # comment may exists after include : '#include <file> /* test */'
                incfile = re.sub('\t+.*', "", incfile).strip()
                #print incfile
                if self._mvlist.count(incfile) > 0:
                    if _target.has_key(incfile):
                        continue
                    else:
                        _target[incfile] = 1
            newctx.append(line)
        self._write_to_file(''.join(newctx))

if __name__ == "__main__":
    repo = "/var/lib/patchmaker/repo/linux"
    #repo = "/var/lib/patchmaker/repo/linux-next"
    findlog = subprocess.Popen("cd %s ; find arch/x86/kernel/syscall_32.c -type f" % (repo),
                                  shell=True, stdout=subprocess.PIPE)
    findOut = findlog.communicate()[0]

    files = findOut.split("\n")
    files = files[0:-1]

    count = 0
    for sfile in files:
        if re.search(r"\.c$", sfile) == None and re.search(r"\.h$", sfile) == None:
            continue
        detector = CheckIncludeEngine(repo)
        detector.set_filename(sfile)
        #print detector._guess_mail_list()
        if detector.should_patch():
            count += 1
            print detector.format_patch()

    print "patch files: %d" % count
