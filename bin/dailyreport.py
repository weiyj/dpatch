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
import sys

from time import localtime, strftime

from dpatch.models import GitRepo, GitTag, GitCommit, Type, ExceptFile, Report, ScanLog
from dpatch.lib.common.logger import MyLogger
from dpatch.lib.common.gittree import GitTree
from dpatch.lib.engine.manager import report_engine_list
from dpatch.lib.common.utils import is_source_file
from dpatch.lib.common.status import *

def checkreport(repo, rtag, flists):
    git = GitTree(repo.name, repo.dirname(), repo.url, repo.commit, repo.stable)
    count = 0
    scaninfo = []

    logs = ScanLog(reponame = repo.name, tagname = rtag.name,
                   starttime = strftime("%Y-%m-%d %H:%M:%S", localtime()),
                   desc = 'Processing, please wait...')
    logs.save()
    logger = MyLogger()
    logger.info('%d Files changed.' % len(flists))

    for dot in report_engine_list():
        scount = 0
        test = dot(repo.dirname(), logger.logger, repo.builddir())
        for i in range(test.tokens()):
            rtype = None
            try:
                rtype = Type.objects.filter(id = test.get_type())[0]
            except:
                test.next_token()
                continue
            if rtype.status == False:
                test.next_token()
                continue

            cmts = GitCommit.objects.filter(repo = repo, type = rtype)
            if len(cmts) == 0:
                cmt = GitCommit(repo = repo, type = rtype)
                cmt.save()
            else:
                cmt = cmts[0]

            rflists = flists
            if repo.delta == False:
                oldcommit = cmt.commit
                if oldcommit != repo.commit:
                    if git.is_linux_next():
                        oldcommit = git.get_stable()
                    rflists = git.get_changelist(oldcommit, repo.commit, None, True)
                else:
                    rflists = flists

            logger.info('Starting scan type %d, total %d files' % (test.get_type(), len(rflists)))

            exceptfiles = []
            for fn in ExceptFile.objects.filter(type = rtype):
                exceptfiles.append(fn.file)

            rcount = 0
            for fname in rflists:
                if is_source_file(fname) == False:
                    continue

                if exceptfiles.count(fname) != 0:
                    continue
    
                reports = Report.objects.filter(file = fname, type = rtype)
                if not os.path.exists(os.path.join(repo.dirname(), fname)):
                    for r in reports:
                        if r.status in [STATUS_NEW, STATUS_PATCHED]:
                            r.status = STATUS_REMOVED
                            r.save()
                    continue

                test.set_filename(fname)
                should_report = test.should_report()
                if should_report is False:
                    for r in reports:
                        if r.status in [STATUS_NEW, STATUS_PATCHED]:
                            if r.mergered == 0:
                                r.status = STATUS_FIXED
                                r.save()
                            else:
                                mreport = Report.objects.filter(id = r.mergered)
                                if len(mreport) != 0:
                                    if mreport[0].status in [STATUS_SENT]:
                                        mreport[0].status = STATUS_ACCEPTED
                                        r.status = STATUS_ACCEPTED
                                    else:
                                        mreport[0].status = STATUS_FIXED
                                        r.status = STATUS_FIXED
                                    mreport[0].save()
                                else:
                                    r.status = STATUS_FIXED
                                r.save()
                        elif r.status in [STATUS_SENT]:
                            r.status = STATUS_ACCEPTED
                            r.save()
                    continue

                lcount = 0
                for r in reports:
                    if r.status in [STATUS_NEW, STATUS_PATCHED, STATUS_SENT]:
                        lcount += 1

                if lcount > 0:
                    continue

                text = test.get_report()
                report = Report(tag = rtag, file = fname, type = rtype, 
                                status = STATUS_NEW, reportlog = '\n'.join(text))
                report.title = rtype.ptitle
                report.desc = rtype.pdesc
                report.save()
                rcount += 1
                scount += 1

            cmt.commit = repo.commit
            cmt.save()
            rtype.commit = repo.commit
            rtype.save()

            logger.info('End scan type %d, report %d' % (rtype.id, rcount))
            logs.logs = logger.getlog()
            logs.save()
            test.next_token()

        count += scount
        scaninfo.append("%s: %d" % (test.name(), scount))

    scaninfo.append("total report: %d" % (count))
    logs.desc = ', '.join(scaninfo)
    logs.endtime = strftime("%Y-%m-%d %H:%M:%S", localtime())
    logs.logs = logger.getlog()
    logs.save()

    return count

def main(args):
    for repo in GitRepo.objects.filter(status = True):
        tags = GitTag.objects.filter(repo = repo).order_by("-id")
        if len(tags) == 0:
            continue
        rtag = tags[0]
        if len(rtag.flist) == 0:
            continue

        if rtag.running == True:
            continue

        flists = rtag.flist.split(',')

        rtag.running = True
        rtag.save()

        print "Check Report for repo %s" % os.path.basename(repo.url)
        rcount = checkreport(repo, rtag, flists)

        rtag.rptotal += rcount
        rtag.running = False
        rtag.save()

        print "Total Report %d" % rcount

    return 0

if __name__ == '__main__':
    sys.exit(main(sys.argv))
