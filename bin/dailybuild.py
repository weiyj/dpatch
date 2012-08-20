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
import sys
import subprocess

from dpatch.models import GitRepo, Patch, Report

def execute_shell(args):
    if isinstance(args, basestring):
        shelllog = subprocess.Popen(args, shell=True, stdout=subprocess.PIPE,
                                    stderr=subprocess.STDOUT)
    else:
        shelllog = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    shellOut = shelllog.communicate()[0]

    lines = shellOut.split("\n")
    lines = lines[0:-1]

    return shelllog.returncode, lines

def main(args):
    for repo in GitRepo.objects.filter(status = True):
        # prepare build env
        if not os.path.exists(repo.builddir()):
            os.system("cd /var/lib/dpatch/build/; git clone file://%s" % repo.dirname())
            os.system("cd %s; make allmodconfig" % repo.builddir())
        else:
            os.system("cd %s; git diff | patch -p1 -R" % repo.builddir())
            os.system("cd %s; git pull" % repo.builddir())

        os.system("cd %s; make" % repo.builddir())

        for patch in Patch.objects.filter(tag__repo = repo, build = 0, mergered = 0, status__name = 'New'):
            buildlog = ''

            if patch.file.find('arch/') == 0 and patch.file.find('arch/x86') != 0:
                continue

            fname = os.path.join(patch.dirname(), patch.filename())
            cocci = open(fname, "w")
            cocci.write(patch.content)
            cocci.close()

            print "build for patch %s...\n" % os.path.basename(fname)

            ret, log = execute_shell("cd %s; git am %s" % (repo.builddir(), fname))
            buildlog += '# git am %s\n' % os.path.basename(fname)
            buildlog += '\n'.join(log)
            if ret != 0:
                execute_shell("cd %s; rm -rf .git/rebase-apply" % repo.builddir())
                patch.build = 2
                patch.buildlog = buildlog
                patch.save()
                continue

            buildlog += '\n# make\n'
            ret, log = execute_shell("cd %s; make" % (repo.builddir()))
            buildlog += '\n'.join(log)
            if ret != 0:
                patch.build = 2
                patch.buildlog = buildlog
                patch.save()
                continue

            os.system("cd %s; patch -p1 -R < %s" % (repo.builddir(), fname))
            patch.build = 1
            patch.buildlog = buildlog
            patch.save()

        for report in Report.objects.filter(tag__repo = repo, build = 0, mergered = 0, status__name = 'Patched'):
            buildlog = ''

            if report.file.find('arch/') == 0 and report.file.find('arch/x86') != 0:
                continue

            fname = os.path.join(report.dirname(), report.filename())
            cocci = open(fname, "w")
            cocci.write(report.content)
            cocci.close()

            print "build for report patch %s...\n" % os.path.basename(fname)

            ret, log = execute_shell("cd %s; git am %s" % (repo.builddir(), fname))
            buildlog += '# git am %s\n' % os.path.basename(fname)
            buildlog += '\n'.join(log)
            if ret != 0:
                report.build = 2
                report.buildlog = buildlog
                report.save()
                continue

            if report.file.find('include/') != 0:
                dname = os.path.dirname(patch.file)
                buildlog += '\n# make M=%s\n' % dname
                ret, log = execute_shell("cd %s; make M=%s" % (repo.builddir(), dname))
                buildlog += '\n'.join(log)
                if ret != 0:
                    report.build = 2
                    report.buildlog = buildlog
                    report.save()
                    continue

            output = '\n'.join(log)
            if report.file.find('include/') == 0 or output.find('LD [M]') == -1:
                buildlog += '\n# make\n'
                ret, log = execute_shell("cd %s; make" % (repo.builddir()))
                buildlog += '\n'.join(log)
                if ret != 0:
                    report.build = 2
                    report.buildlog = buildlog
                    report.save()
                    continue

            os.system("cd %s; patch -p1 -R < %s" % (repo.builddir(), fname))
            report.build = 1
            report.buildlog = buildlog
            report.save()

if __name__ == '__main__':
    sys.exit(main(sys.argv))
