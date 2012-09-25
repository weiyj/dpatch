#!/usr/bin/python
#
# Dailypatch - automated kernel patch create engine
# Copyright (C) 2012 Wei Yongjun <weiyj.lk@gmail.com>
#
# This file is part of the Dailypatch package.
#
# Dailypatch is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# Dailypatch is distributed in the hope that it will be useful,
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

from patchdetector import PatchDetector
from dpatch.models import CocciEngine

class CheckCocciDetector(PatchDetector):
    def __init__(self, repo, logger = None):
        PatchDetector.__init__(self, repo, logger)
        self._type = 3000
        self._diff = []

        self._coccis = CocciEngine.objects.all()
        #self._coccis = ['kmem_cache_zalloc.cocci',
        #                'kfree_skb.cocci']
        #self._descs = ['Useing kmem_cache_zalloc() instead of kmem_cache_alloc() and memset()',
        #               'Remove pointless conditional before kfree().']

    def _execute_shell(self, args):
        if isinstance(args, basestring):
            shelllog = subprocess.Popen(args, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        else:
            shelllog = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        shellOut = shelllog.communicate()[0]

        if shelllog.returncode != 0:
            self.warning("cocci engine fail at %s" % (self._fname))
            self.warning(shellOut)

        lines = shellOut.split("\n")
        #lines = lines[0:-1]

        return lines

    def tokens(self):
        return len(self._coccis)

    def next_token(self):
        self._token += 1

    def get_type(self):
        cocci = self._coccis[self._token]
        return self._type + cocci.id

    def _engine_fixed(self):
        cocci = self._coccis[self._token]
        if cocci.fixed is None or len(cocci.fixed) == 0:
            return self._diff

        fixed = cocci.fixed.split('...')
        regexpr = fixed[0].strip()
        target = fixed[1].strip()
        cpl = re.compile(regexpr)
        diff = []
        for line in self._diff:
            line = cpl.sub(target, line)
            diff.append(line)
        return diff

    def _modify_source_file(self):
        # sometimes the engine give as a diff that does not pass
        # the checkpatch, we need fix it first.
        diff = self._engine_fixed()

        temp = tempfile.mktemp()
        cfg = open(temp, "w")
        cfg.write('\n'.join(diff))
        cfg.close()

        self._execute_shell('patch %s < %s' %(self._get_file_path(), temp))
        os.remove(temp)

    def _should_patch(self):
        cocci = self._coccis[self._token]
        spfile = cocci.fullpath()
        if not os.path.exists(spfile):
            self.warning('sp_file %s does not exists' % spfile)
            return False

        args = '/usr/bin/spatch %s -I %s -timeout 60 -very_quiet -sp_file %s %s' % (cocci.options,
                        os.path.join(self._repo, 'include'), spfile,
                        self._get_file_path())
        #args = ['/usr/bin/spatch', '-I', os.path.join(self._repo, 'include'), 
        #        '-very_quiet', '-sp_file', spfile, self._get_file_path()]
        #print ' '.join(args)
        self._diff = self._execute_shell(args)
        if len(self._diff) > 1:
            if self._diff[0].find('diff ') == 0 or self._diff[0].find('--- ') == 0:
                return True
            else:
                self.warning('spatch output for %s' % self._fname)
                self.warning('\n'.join(self._diff))

        return False

if __name__ == "__main__":
    repo = "/pub/scm/source/linux-latest/"
    #repo = "/var/lib/patchmaker/repo/linux-next"
    findlog = subprocess.Popen("cd %s ; find arch/arm/mach-at91/gpio.c -type f" % (repo),
                                  shell=True, stdout=subprocess.PIPE)
    findOut = findlog.communicate()[0]

    files = findOut.split("\n")
    files = files[0:-1]

    count = 0
    for sfile in files:
        if re.search(r"\.c$", sfile) == None and re.search(r"\.h$", sfile) == None:
            continue
        detector = CheckCocciDetector(repo)
        detector.set_filename(sfile)
        for i in range(detector.tokens()):
            if detector.should_patch():
                count += 1
                print detector.format_patch()
            detector.next_token()

    print "patch files: %d" % count
