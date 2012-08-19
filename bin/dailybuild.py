#!/bin/sh
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
import sys
import subprocess

from time import gmtime, strftime

from dpatch.models import GitRepo, Patch, Type, Report
from logger import MyLogger

def execute_shell(args):
    if isinstance(args, basestring):
        shelllog = subprocess.Popen(args, shell=True, stdout=subprocess.PIPE)
    else:
        shelllog = subprocess.Popen(args, stdout=subprocess.PIPE)
    shellOut = shelllog.communicate()[0]

    lines = shellOut.split("\n")
    lines = lines[0:-1]

    return shelllog.returncode, lines

def commit_from_repo(repo):
    ret, commits = execute_shell('cd %s; git log -n 1 --pretty=format:%%H%%n' % repo.dirname())
    return commits[-1]

def main(args):
    for repo in GitRepo.objects.filter(status = True):
        # prepare build env
        if not os.path.exists(repo.builddir()):
            os.system("/usr/bin/cp -rf %s /var/lib/dpatch/build/", repo.dirname())
            os.system("cd %s; make allmodconfig" % repo.builddir())

        os.system("cd %s; make" % repo.builddir())
        commit = commit_from_repo(repo)

        for patch in Patch.objects.filter(tag__repo = repo, build = 0, status__name = 'New'):
            buildlog = ''

            fname = os.path.join(patch.dirname(), patch.filename())
            cocci = open(fname, "w")
            cocci.write(patch.content)
            cocci.close()

            os.system("cd %s; git reset --hard %s" % (repo.builddir(), commit))

            ret, log = execute_shell("cd %s; git am %s" % (repo.builddir(), fname))
            buildlog += '\n'.join(log)
            if ret != 0:
                patch.build = 2
                patch.buildlog = buildlog
                patch.save()
                continue

            ret, log = execute_shell("cd %s; make" % (repo.builddir()))
            buildlog += '\n'.join(log)
            if ret != 0:
                patch.build = 2
                patch.buildlog = buildlog
                patch.save()
                continue

            os.system("cd %s; git reset --hard %s" % (repo.builddir(), commit))
            patch.build = 1
            patch.buildlog = buildlog
            patch.save()

if __name__ == '__main__':
    sys.exit(main(sys.argv))
