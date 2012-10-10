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

from django.db.models import Q

from dpatch.models import GitRepo, Type, Status, Patch, CocciReport, Report, ScanLog
from checkversion import CheckVersionDetector
from checkrelease import CheckReleaseDetector
from checkinclude import CheckIncludeDetector
from checkcocci import CheckCocciDetector
from logger import MyLogger

def update_patch_status(patch, status):
    patch.status = status
    patch.save()
    if patch.mergered != 0:
        mpatch = Patch.objects.filter(id = patch.mergered)
        if len(mpatch) != 0:
            mpatch[0].status = status
            mpatch[0].save()

def update_report_status(report, status):
    report.status = status
    report.save()
    if report.mergered != 0:
        mreport = Report.objects.filter(id = report.mergered)
        if len(mreport) != 0:
            mreport[0].status = status
            mreport[0].save()

def execute_shell(args):
    if isinstance(args, basestring):
        shelllog = subprocess.Popen(args, shell=True, stdout=subprocess.PIPE)
    else:
        shelllog = subprocess.Popen(args, stdout=subprocess.PIPE)
    shellOut = shelllog.communicate()[0]

    lines = shellOut.split("\n")
    lines = lines[0:-1]

    return lines

def is_report_fixed(repo, cocci, spfile, fname):
    args = '/usr/bin/spatch %s -I %s -timeout 10 -very_quiet -sp_file %s %s' % (cocci.options,
                    os.path.join(repo.dirname(), 'include'), spfile,
                    os.path.join(repo.dirname(), fname))

    reportlog = execute_shell(args)
    if len(reportlog) == 0:
        return True
    else:
        return False

def main(args):
    baserepo = None

    fixed = Status.objects.filter(name = 'Fixed')[0]
    removed = Status.objects.filter(name = 'Removed')[0]
    applied = Status.objects.filter(name = 'Accepted')[0]

    for repo in GitRepo.objects.filter(status = True):
        if baserepo is None:
            baserepo = repo

        logger = MyLogger()
        logs = ScanLog(reponame = repo.name, tagname = '-',
                       starttime = strftime("%Y-%m-%d %H:%M:%S", gmtime()),
                       desc = 'Processing, please wait...')
        logs.save()

        pcount = {'total': 0, 'removed': 0, 'fixed': 0, 'applied': 0}
        for dot in [CheckVersionDetector, CheckReleaseDetector, CheckIncludeDetector, CheckCocciDetector]:
            test = dot(repo.dirname(), logger.logger)
            for i in range(test.tokens()):
                logger.logger.info('Starting update type %d' % test.get_type())

                rtype = None
                try:
                    rtype = Type.objects.filter(id = test.get_type())[0]
                except:
                    continue

                if rtype.status == False:
                    test.next_token()
                    continue

                patchs = Patch.objects.filter(Q(tag__repo = baserepo), Q(type = rtype),
                                              Q(status__name = 'New') | Q(status__name = 'Sent'))
                for patch in patchs:
                    if not patch.mglist is None and len(patch.mglist) != 0:
                        continue
                    test.set_filename(patch.file)
                    pcount['total'] += 1
                    print "check for %s\n" % patch.filename()
                    if not os.path.exists(test._get_file_path()):
                        update_patch_status(patch, removed)
                        pcount['removed'] += 1
                        logger.logger.info('removed patch %d' % patch.id)
                        continue

                    if test.should_patch() == False:
                        if patch.status.name == 'New':
                            if patch.mergered != 0:
                                mpatch = Patch.objects.filter(id = patch.mergered)
                                if len(mpatch) != 0:
                                    if mpatch[0].status.name == 'Sent':
                                        update_patch_status(patch, applied)
                                        pcount['applied'] += 1
                                        logger.logger.info('applied patch %d' % patch.id)
                                    else:
                                        update_patch_status(patch, fixed)
                                        pcount['fixed'] += 1
                                        logger.logger.info('fixed patch %d' % patch.id)
                                else:
                                    update_patch_status(patch, fixed)
                                    pcount['fixed'] += 1
                                    logger.logger.info('fixed patch %d' % patch.id)
                            else:
                                update_patch_status(patch, fixed)
                                pcount['fixed'] += 1
                                logger.logger.info('fixed patch %d' % patch.id)
                        elif patch.status.name == 'Sent':
                            update_patch_status(patch, applied)
                            pcount['applied'] += 1
                            logger.logger.info('applied patch %d' % patch.id)

                logger.logger.info('End scan type %d' % test.get_type())
                test.next_token()

        for cocci in CocciReport.objects.all():
            spfile = cocci.fullpath()
            if not os.path.exists(spfile):
                continue

            rtype = Type.objects.get(id = (cocci.id + 10000))
            if rtype.status == False:
                continue

            logger.logger.info('Starting update type %d' % rtype.id)
            patchs = Report.objects.filter(Q(tag__repo = baserepo), Q(type = rtype),
                                           Q(status__name = 'New') | Q(status__name = 'Patched') | Q(status__name = 'Sent'))
            for patch in patchs:
                if not patch.mglist is None and len(patch.mglist) != 0:
                    continue

                if not os.path.exists(os.path.join(repo.dirname(), patch.file)):
                    update_report_status(patch, removed)
                    pcount['removed'] += 1
                    logger.logger.info('removed patch %d' % patch.id)
                    continue
    
                if is_report_fixed(repo, cocci, spfile, patch.file) == True:
                    if patch.status.name == 'New':
                        update_report_status(patch, fixed)
                        pcount['fixed'] += 1
                        logger.logger.info('fixed patch %d' % patch.id)
                    elif patch.status.name == 'Sent':
                        update_report_status(patch, applied)
                        pcount['applied'] += 1
                        logger.logger.info('applied patch %d' % patch.id)
                    elif patch.status.name == 'Patched':
                        if patch.mergered != 0:
                            mpatch = Report.objects.filter(id = patch.mergered)
                            if len(mpatch) != 0:
                                if mpatch[0].status.name == 'Sent':
                                    update_report_status(patch, applied)
                                    pcount['applied'] += 1
                                    logger.logger.info('applied patch %d' % patch.id)
                                else:
                                    update_report_status(patch, fixed)
                                    pcount['fixed'] += 1
                                    logger.logger.info('fixed patch %d' % patch.id)
                            else:
                                update_report_status(patch, fixed)
                                pcount['fixed'] += 1
                                logger.logger.info('fixed patch %d' % patch.id)
                        else:
                            update_report_status(patch, fixed)
                            pcount['fixed'] += 1
                            logger.logger.info('fixed patch %d' % patch.id)

            logger.logger.info('End scan type %d' % rtype.id)

        logs.desc = 'total checked: %d, removed: %d, fixed: %d, applied: %d' % (
                        pcount['total'], pcount['removed'], pcount['fixed'], pcount['applied'])
        logs.endtime = strftime("%Y-%m-%d %H:%M:%S", gmtime())
        logs.logs = logger.getlog()
        logs.save()

    return 0

if __name__ == '__main__':
    sys.exit(main(sys.argv))
