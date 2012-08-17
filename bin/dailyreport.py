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
import sys
import subprocess

from time import gmtime, strftime

from dpatch.models import GitRepo, GitTag, Type, Status, CocciReport, ExceptFile, Report, ScanLog
from logger import MyLogger

logger = None

def error(msg):
    if logger != None:
        logger.logger.error(msg)

def info(msg):
    if logger != None:
        logger.logger.info(msg)

def warning(msg):
    if logger != None:
        logger.logger.info(msg)

def execute_shell(args):
    if isinstance(args, basestring):
        shelllog = subprocess.Popen(args, shell=True, stdout=subprocess.PIPE)
    else:
        shelllog = subprocess.Popen(args, stdout=subprocess.PIPE)
    shellOut = shelllog.communicate()[0]

    lines = shellOut.split("\n")
    lines = lines[0:-1]

    return lines

def commit_from_repo(repo):
    commits = execute_shell('cd %s; git log -n 1 --pretty=format:%%H%%n' % repo.dirname())
    return commits[-1]

def repo_get_changelist(repo, scommit, ecommit):
    if len(scommit) == 0 or scommit is None:
        scommit = '1da177e4c3f41524e886b7f1b8a0c1fc7321cac2'
    lines = execute_shell('cd %s; git diff --name-only %s...%s' % (repo.dirname(), scommit, ecommit))
    return lines

def is_source_file(sfile):
    if re.search(r"\.c$", sfile) != None:
        return True
    if re.search(r"\.h$", sfile) != None:
        return True
    return False

def checkreport(repo, rtag, cocci, flists):
    spfile = cocci.fullpath()
    if not os.path.exists(spfile):
        print('sp_file %s does not exists' % spfile)
        return 0

    rtype = Type.objects.filter(id = (cocci.id + 10000))[0]
    if rtype.status == False:
        return 0

    info('Starting scan type %d' % rtype.id)

    new = Status.objects.filter(name = 'New')[0]
    fixed = Status.objects.filter(name = 'Fixed')[0]
    removed = Status.objects.filter(name = 'Removed')[0]

    exceptfiles = []
    for fn in ExceptFile.objects.filter(type = rtype):
        exceptfiles.append(fn.file)

    rcount = 0
    for fname in flists:
        if is_source_file(fname) == False:
            continue

        if exceptfiles.count(fname) != 0:
            continue

        reports = Report.objects.filter(file = fname, type = rtype)
        if not os.path.exists(os.path.join(repo.dirname(), fname)):
            for r in reports:
                if r.status.name == 'New' or r.status.name == 'Patched':
                    r.status = removed
                    r.save()
            continue

        args = '/usr/bin/spatch %s -I %s -timeout 1 -very_quiet -sp_file %s %s' % (cocci.options,
                        os.path.join(repo.dirname(), 'include'), spfile,
                        os.path.join(repo.dirname(), fname))

        reportlog = execute_shell(args)
        if len(reportlog) == 0:
            for r in reports:
                if r.status.name == 'New' or r.status.name == 'Patched':
                    r.status = fixed
                    r.save()
            continue

        count = 0
        for r in reports:
            if r.status.name == 'New' or r.status.name == 'Patched':
                count += 1

        if count > 0:
            continue

        report = Report(tag = rtag, file = fname, type = rtype, 
                        status = new, reportlog = '\n'.join(reportlog))
        report.title = rtype.ptitle
        report.desc = rtype.pdesc
        report.save()
        rcount += 1

    info('End scan type %d, report %d' % (rtype.id, rcount))

    return rcount

def main(args):
    for repo in GitRepo.objects.filter(id = 1):
        tags = GitTag.objects.filter(repo = repo).order_by("-id")
        if len(tags) == 0:
            continue
        rtag = tags[0]
        if len(rtag.flist) == 0:
            continue

        logger = MyLogger()
        logs = ScanLog(reponame = repo.name, tagname = rtag.name,
                       starttime = strftime("%Y-%m-%d %H:%M:%S", gmtime()),
                       desc = 'Processing, please wait...')
        logs.save()

        flists = rtag.flist.split(',')
        print "Check Report for repo %s" % os.path.basename(repo.url)
        rcount = 0

        rtag.running = True
        rtag.save()

        for cocci in CocciReport.objects.all():
            rcount += checkreport(repo, rtag, cocci, flists)

        rtag.rptotal += rcount
        rtag.running = False
        rtag.save()

        logs.logs = logger.getlog()
        logs.save()

        print "Total Report %d" % rcount

    return 0

if __name__ == '__main__':
    sys.exit(main(sys.argv))
