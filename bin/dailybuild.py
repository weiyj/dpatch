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

def execute_shell_log(args, logger = None):
    shelllog = subprocess.Popen(args, shell=True, stdout=subprocess.PIPE,
                                stderr=subprocess.STDOUT)
    shellOut = shelllog.communicate()[0]

    if not isinstance(shellOut, unicode):
        shellOut = unicode(shellOut, errors='ignore')

    if logger != None:
        logger.logger.info(args)
        logger.logger.info(shellOut)

    return shelllog.returncode, shellOut


def commit_from_repo(repo):
    ret, commits = execute_shell('cd %s; git log -n 1 --pretty=format:%%H%%n' % repo.builddir())
    return commits[-1]

def is_linux_next_update(repo):
    ret, commits = execute_shell('diff %s/.git/refs/remotes/origin/stable %s/.git/refs/remotes/stable' % (repo.dirname(), repo.builddir()))
    return ret

def get_linux_next_stable(repo):
    ret, commits = execute_shell('cd %s; cat .git/refs/remotes/stable' % (repo.builddir()))
    return commits[0]

def is_c_file(filename):
    if filename.find('include/') != 0 and filename.find('tools/') != 0 and filename[-2:] == '.c':
        return True
    else:
        return False

def is_module_build(filename, output):
    if not isinstance(output, unicode):
        output = unicode(output, errors='ignore')

    if output.find('LD [M]') == -1:
        return False

    objfile = "%s.o" % filename[:-2]
    if filename[-2:] == '.c' and output.find(objfile) != -1:
        return True
    else:
        return False

def main(args):
    buildpatch = True
    buildreport = True
    rebuildrepo = True
    repoid = None
    if len(args) > 1:
        arg = args[1]
        if arg == 'patch':
            buildreport = False
            rebuildrepo = False
        elif arg == 'report':
            buildpatch = False
            rebuildrepo = False

    if len(args) > 2:
        repoid = int(args[2])

    for repo in GitRepo.objects.filter(status = True, build = True):
        if repoid != None and repoid != repo.id:
            continue

        patchcnt = Patch.objects.filter(tag__repo = repo, build = 0, mergered = 0, status__name = 'New').count()
        reportcnt = Report.objects.filter(tag__repo = repo, build = 0, mergered = 0, status__name = 'Patched').count()
        if (buildpatch == False or patchcnt == 0) and (buildreport == False or reportcnt == 0):
            continue

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
            os.system("cd %s; git clone file://%s" % (os.path.dirname(repo.builddir()), repo.dirname()))
            if repo.name == 'linux-next.git':
                os.system("cd %s; cp %s/.git/refs/remotes/origin/stable .git/refs/remotes/stable" % (repo.builddir(), repo.dirname()))
            os.system("cd %s; make allmodconfig" % repo.builddir())
            rebuildrepo = True
        elif rebuildrepo == True:
            if repo.name == 'linux-next.git':
                if is_linux_next_update(repo):
                    os.system("cd %s; git reset --hard %s" % (repo.builddir(), get_linux_next_stable(repo)))
                    ret, tmplog = execute_shell_log("cd %s; git pull" % repo.builddir(), logger)
                    gitlog = tmplog
                    os.system("cd %s; make allmodconfig" % repo.builddir())
                else:
                    gitlog = 'Already up-to-date.'
            else:
                os.system("cd %s; git reset --hard" % repo.builddir())
                ret, tmplog = execute_shell_log("cd %s; git pull" % repo.builddir(), logger)
                gitlog = tmplog

        if rebuildrepo == True and gitlog.find('Already up-to-date.') == -1:
            execute_shell("cd %s; make" % repo.builddir(), logger)

        commit = commit_from_repo(repo)

        if buildpatch == True:
            for patch in Patch.objects.filter(tag__repo = repo, build = 0, mergered = 0, status__name = 'New'):
                buildlog = ''
    
                if patch.file.find('arch/') == 0 and patch.file.find('arch/x86') != 0:
                    patch.build = 3
                    patch.save()
                    continue

                pcount['total'] += 1
                fname = os.path.join(patch.dirname(), patch.filename())
                pdiff = open(fname, "w")
                try:
                    pdiff.write(patch.content)
                except:
                    pdiff.write(unicode.encode(patch.content, 'utf-8'))
                pdiff.close()
    
                print "build for patch %s...\n" % os.path.basename(fname)
                logger.logger.info("build for patch %s..." % os.path.basename(fname))
    
                execute_shell("cd %s; git reset --hard %s" % (repo.builddir(), commit), logger)
                if os.path.exists(os.path.join(repo.builddir(), '.git/rebase-apply')):
                    execute_shell("cd %s; rm -rf .git/rebase-apply" % repo.builddir())
    
                ret, log = execute_shell_log("cd %s; git am %s" % (repo.builddir(), fname), logger)
                buildlog += '# git am %s\n' % os.path.basename(fname)
                buildlog += log
                if ret != 0:
                    pcount['fail'] += 1
                    patch.build = 2
                    patch.buildlog = buildlog
                    patch.save()
                    continue

                objfile = "%s.o" % patch.file[:-2]
                if patch.file.find('tools/') == 0:
                    dname = os.path.dirname(patch.file)
                    while len(dname) != 0 and not os.path.exists(os.path.join(repo.builddir(), dname, 'Makefile')):
                        dname = os.path.dirname(dname)
                    if len(dname) != 0:
                        buildlog += '\n# cd %s; make\n' % dname
                        ret, log = execute_shell_log("cd %s; make" % (os.path.join(repo.builddir(), dname)), logger)
                        buildlog += log
                        if ret != 0:
                            pcount['fail'] += 1
                            patch.build = 2
                            patch.buildlog = buildlog
                            patch.save()
                            continue
                    else:
                        buildlog += 'do not known how to build\n'
                    log += '\nLD [M] %s\n' % objfile

                if patch.file.find('include/') != 0 and patch.file.find('tools/') != 0:
                    dname = os.path.dirname(patch.file)
                    while len(dname) != 0 and not os.path.exists(os.path.join(repo.builddir(), dname, 'Makefile')):
                        dname = os.path.dirname(dname)
                    if len(dname) != 0:
                        buildlog += '\n# make M=%s\n' % dname
                        ret, log = execute_shell_log("cd %s; make M=%s" % (repo.builddir(), dname), logger)
                        buildlog += log
                        if ret != 0:
                            pcount['fail'] += 1
                            patch.build = 2
                            patch.buildlog = buildlog
                            patch.save()
                            continue
    
                output = log
                if is_c_file(patch.file) and is_module_build(patch.file, output) == False:
                    buildlog += '\n# make %s\n' % objfile
                    ret, log = execute_shell_log("cd %s; make %s" % (repo.builddir(), objfile), logger)
                    buildlog += log
                    if ret != 0:
                        pcount['fail'] += 1
                        patch.build = 2
                        patch.buildlog = buildlog
                        patch.save()
                        if buildlog.find("Run 'make oldconfig' to update configuration.") != -1:
                            os.system("cd %s; make allmodconfig" % repo.builddir())
                        continue
                    output = log
                    if output.find(objfile) != -1:
                        log += '\nLD [M] %s\n' % objfile

                output = log
                if patch.file.find('include/') == 0 or is_module_build(patch.file, output) == False:
                    buildlog += '\n# make vmlinux\n'
                    ret, log = execute_shell_log("cd %s; make vmlinux" % (repo.builddir()), logger)
                    buildlog += log
                    if ret != 0:
                        pcount['fail'] += 1
                        patch.build = 2
                        patch.buildlog = buildlog
                        patch.save()
                        if buildlog.find("Run 'make oldconfig' to update configuration.") != -1:
                            os.system("cd %s; make allmodconfig" % repo.builddir())
                        continue
    
                pcount['pass'] += 1
                if buildlog.find(': warning: ') != -1:
                    patch.build = 4
                else:
                    patch.build = 1
                patch.buildlog = buildlog
                patch.save()

        if buildreport == True:
            for report in Report.objects.filter(tag__repo = repo, build = 0, mergered = 0, status__name = 'Patched'):
                buildlog = ''
    
                if report.file.find('arch/') == 0 and report.file.find('arch/x86') != 0:
                    report.build = 3
                    report.save()
                    continue

                rcount['total'] += 1
                fname = os.path.join(report.dirname(), report.filename())
                pdiff = open(fname, "w")
                try:
                    pdiff.write(report.content)
                except:
                    pdiff.write(unicode.encode(report.content, 'utf-8'))
                pdiff.close()

                print "build for report patch %s...\n" % os.path.basename(fname)
                logger.logger.info("build for report patch %s..." % os.path.basename(fname))
    
                execute_shell("cd %s; git reset --hard %s" % (repo.builddir(), commit), logger)
                if os.path.exists(os.path.join(repo.builddir(), '.git/rebase-apply')):
                    execute_shell("cd %s; rm -rf .git/rebase-apply" % repo.builddir())
    
                ret, log = execute_shell_log("cd %s; git am %s" % (repo.builddir(), fname), logger)
                buildlog += '# git am %s\n' % os.path.basename(fname)
                buildlog += log
                if ret != 0:
                    rcount['fail'] += 1
                    report.build = 2
                    report.buildlog = buildlog
                    report.save()
                    continue

                if report.file.find('tools/') == 0:
                    dname = os.path.dirname(report.file)
                    while len(dname) != 0 and not os.path.exists(os.path.join(repo.builddir(), dname, 'Makefile')):
                        dname = os.path.dirname(dname)
                    if len(dname) != 0:
                        buildlog += '\n# cd %s; make\n' % dname
                        ret, log = execute_shell_log("cd %s; make" % (os.path.join(repo.builddir(), dname)), logger)
                        buildlog += log
                        if ret != 0:
                            pcount['fail'] += 1
                            report.build = 2
                            report.buildlog = buildlog
                            report.save()
                            continue
                    else:
                        buildlog += 'do not known how to build\n'
                    log += '\nLD [M] %s\n' % objfile

                objfile = "%s.o" % report.file[:-2]
                if report.file.find('include/') != 0 and report.file.find('tools/') != 0:
                    dname = os.path.dirname(report.file)
                    while len(dname) != 0 and not os.path.exists(os.path.join(repo.builddir(), dname, 'Makefile')):
                        dname = os.path.dirname(dname)
                    if len(dname) != 0:
                        buildlog += '\n# make M=%s\n' % dname
                        ret, log = execute_shell_log("cd %s; make M=%s" % (repo.builddir(), dname), logger)
                        buildlog += log
                        if ret != 0:
                            rcount['fail'] += 1
                            report.build = 2
                            report.buildlog = buildlog
                            report.save()
                            continue

                output = log
                if is_c_file(report.file) and is_module_build(report.file, output) == False:
                    buildlog += '\n# make %s\n' % objfile
                    ret, log = execute_shell_log("cd %s; make %s" % (repo.builddir(), objfile), logger)
                    buildlog += log
                    if ret != 0:
                        pcount['fail'] += 1
                        report.build = 2
                        report.buildlog = buildlog
                        report.save()
                        if buildlog.find("Run 'make oldconfig' to update configuration.") != -1:
                            os.system("cd %s; make allmodconfig" % repo.builddir())
                        continue
                    output = log
                    if output.find(objfile) != -1:
                        log += '\nLD [M] %s\n' % objfile

                output = log
                if report.file.find('include/') == 0 or is_module_build(report.file, output) == False:
                    buildlog += '\n# make vmlinux\n'
                    ret, log = execute_shell_log("cd %s; make vmlinux" % (repo.builddir()), logger)
                    buildlog += log
                    if ret != 0:
                        rcount['fail'] += 1
                        report.build = 2
                        report.buildlog = buildlog
                        report.save()
                        continue
    
                rcount['pass'] += 1
                if buildlog.find(': warning: ') != -1:
                    report.build = 4
                else:
                    report.build = 1
                report.buildlog = buildlog
                report.save()

        logs.desc = 'build patch: %d, pass: %d fail:%d, build report: %s, pass: %d, fail: %s' \
                    % (pcount['total'], pcount['pass'], pcount['fail'], rcount['total'], rcount['pass'], rcount['fail'])
        logs.endtime = strftime("%Y-%m-%d %H:%M:%S", gmtime())
        logs.logs = logger.getlog()
        logs.save()

        os.system("cd %s; git reset --hard %s" % (repo.builddir(), commit))

if __name__ == '__main__':
    sys.exit(main(sys.argv))
