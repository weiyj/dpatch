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

from time import gmtime, strftime

from dpatch.models import GitRepo, Patch, Report, ScanLog
from logger import MyLogger

def execute_shell(args, logger = None):
    shelllog = subprocess.Popen(args, shell=True, stdout=subprocess.PIPE,
                                stderr=subprocess.STDOUT)
    shellOut = shelllog.communicate()[0]

    lines = shellOut.split("\n")
    lines = lines[0:-1]

    if logger != None:
        logger.logger.info(args)
        logger.logger.info(shellOut)

    return shelllog.returncode, lines

def main(args):
    for repo in GitRepo.objects.filter(status = True, build = True):
        logger = MyLogger()
        logs = ScanLog(reponame = repo.name, tagname = '-',
                       starttime = strftime("%Y-%m-%d %H:%M:%S", gmtime()),
                       desc = 'Building, please wait...')
        logs.save()

        pcount = {'total': 0, 'pass': 0, 'fail': 0}
        rcount = {'total': 0, 'pass': 0, 'fail': 0}
        # prepare build env
        gitlog = ''
        if not os.path.exists(repo.builddir()):
            os.system("cd /var/lib/dpatch/build/; git clone file://%s" % repo.dirname())
            os.system("cd %s; make allmodconfig" % repo.builddir())
        else:
            os.system("cd %s; git diff | patch -p1 -R" % repo.builddir())
            ret, tmplog = execute_shell("cd %s; git pull" % repo.builddir(), logger)
            gitlog = '\n'.join(tmplog)

        if gitlog.find('Already up-to-date.') == -1:
            execute_shell("cd %s; make" % repo.builddir(), logger)

        for patch in Patch.objects.filter(tag__repo = repo, build = 0, mergered = 0, status__name = 'New'):
            buildlog = ''

            if patch.file.find('arch/') == 0 and patch.file.find('arch/x86') != 0:
                patch.build = 3
                patch.save()
                continue

            pcount['total'] += 1
            fname = os.path.join(patch.dirname(), patch.filename())
            cocci = open(fname, "w")
            cocci.write(patch.content)
            cocci.close()

            print "build for patch %s...\n" % os.path.basename(fname)
            logger.logger.info("build for patch %s..." % os.path.basename(fname))

            execute_shell("cd %s; git reset --hard %s" % (repo.builddir(), repo.commit), logger)
            if os.path.exists(os.path.join(repo.builddir(), '.git/rebase-apply')):
                execute_shell("cd %s; rm -rf .git/rebase-apply" % repo.builddir())

            ret, log = execute_shell("cd %s; git am %s" % (repo.builddir(), fname), logger)
            buildlog += '# git am %s\n' % os.path.basename(fname)
            buildlog += '\n'.join(log)
            if ret != 0:
                pcount['fail'] += 1
                patch.build = 2
                patch.buildlog = buildlog
                patch.save()
                continue

            if patch.file.find('include/') != 0:
                dname = os.path.dirname(patch.file)
                buildlog += '\n# make M=%s\n' % dname
                ret, log = execute_shell("cd %s; make M=%s" % (repo.builddir(), dname), logger)
                buildlog += '\n'.join(log)
                if ret != 0:
                    pcount['fail'] += 1
                    patch.build = 2
                    patch.buildlog = buildlog
                    patch.save()
                    continue

            output = '\n'.join(log)
            if patch.file.find('include/') == 0 or output.find('LD [M]') == -1:
                buildlog += '\n# make vmlinux\n'
                ret, log = execute_shell("cd %s; make vmlinux" % (repo.builddir()), logger)
                buildlog += '\n'.join(log)
                if ret != 0:
                    pcount['fail'] += 1
                    patch.build = 2
                    patch.buildlog = buildlog
                    patch.save()
                    continue

            pcount['pass'] += 1
            patch.build = 1
            patch.buildlog = buildlog
            patch.save()

        for report in Report.objects.filter(tag__repo = repo, build = 0, mergered = 0, status__name = 'Patched'):
            buildlog = ''

            if report.file.find('arch/') == 0 and report.file.find('arch/x86') != 0:
                report.build = 3
                report.save()
                continue

            rcount['total'] += 1
            fname = os.path.join(report.dirname(), report.filename())
            cocci = open(fname, "w")
            cocci.write(report.content)
            cocci.close()

            print "build for report patch %s...\n" % os.path.basename(fname)
            logger.logger.info("build for report patch %s..." % os.path.basename(fname))

            execute_shell("cd %s; git reset --hard %s" % (repo.builddir(), repo.commit), logger)
            if os.path.exists(os.path.join(repo.builddir(), '.git/rebase-apply')):
                execute_shell("cd %s; rm -rf .git/rebase-apply" % repo.builddir())

            ret, log = execute_shell("cd %s; git am %s" % (repo.builddir(), fname), logger)
            buildlog += '# git am %s\n' % os.path.basename(fname)
            buildlog += '\n'.join(log)
            if ret != 0:
                rcount['fail'] += 1
                report.build = 2
                report.buildlog = buildlog
                report.save()
                continue

            if report.file.find('include/') != 0:
                dname = os.path.dirname(report.file)
                buildlog += '\n# make M=%s\n' % dname
                ret, log = execute_shell("cd %s; make M=%s" % (repo.builddir(), dname), logger)
                buildlog += '\n'.join(log)
                if ret != 0:
                    rcount['fail'] += 1
                    report.build = 2
                    report.buildlog = buildlog
                    report.save()
                    continue

            output = '\n'.join(log)
            if report.file.find('include/') == 0 or output.find('LD [M]') == -1:
                buildlog += '\n# make vmlinux\n'
                ret, log = execute_shell("cd %s; make vmlinux" % (repo.builddir()), logger)
                buildlog += '\n'.join(log)
                if ret != 0:
                    rcount['fail'] += 1
                    report.build = 2
                    report.buildlog = buildlog
                    report.save()
                    continue

            rcount['pass'] += 1
            report.build = 1
            report.buildlog = buildlog
            report.save()

        logs.desc = 'build patch: %d, pass: %d fail:%d, build report: %s, pass: %d, fail: %s' \
                    % (pcount['total'], pcount['pass'], pcount['fail'], rcount['total'], rcount['pass'], rcount['fail'])
        logs.endtime = strftime("%Y-%m-%d %H:%M:%S", gmtime())
        logs.logs = logger.getlog()
        logs.save()

        os.system("cd %s; git reset --hard %s" % (repo.builddir(), repo.commit))

if __name__ == '__main__':
    sys.exit(main(sys.argv))
