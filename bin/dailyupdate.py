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

from dpatch.models import GitRepo, GitTag, Status, Type, Patch, ScanLog, ExceptFile, GitCommit
from dpatch.patchformat import PatchFormat 
from checkversion import CheckVersionDetector
from checkinclude import CheckIncludeDetector
from checkcocci import CheckCocciDetector
from logger import MyLogger

def execute_shell(args):
    if isinstance(args, basestring):
        shelllog = subprocess.Popen(args, shell=True, stdout=subprocess.PIPE)
    else:
        shelllog = subprocess.Popen(args, stdout=subprocess.PIPE)
    shellOut = shelllog.communicate()[0]

    lines = shellOut.split("\n")
    lines = lines[0:-1]

    return lines

def check_repo_update(repo):
    dpath = repo.dirname()
    if not os.path.exists(dpath):
        rpath = os.path.dirname(dpath)
        execute_shell('cd %s ; git clone %s' % (rpath, repo.url))
    else:
        #execute_shell('cd %s ; git pull' % dpath)
        os.system('cd %s ; git pull' % dpath)

    return True

def commit_from_repo(repo):
    commits = execute_shell('cd %s; git log -n 1 --pretty=format:%%H%%n' % repo.dirname())
    return commits[-1]

def tag_to_commit(repo, tag):
    commits = execute_shell('cd %s; git log -n 1 %s --pretty=format:%%H%%n' % (tag, repo.dirname()))
    return commits[-1]

def tag_from_repo(repo):
    if not os.path.exists(repo.dirname()):
        return None
    tags = execute_shell('cd %s; git tag' % repo.dirname())
    tag = tags[-1]
    if re.search(r'-rc\d+$', tag) != None:
        tag = re.sub('-rc\d+$', '', tag)
        if tags.count(tag) > 0:
            return tag
    return tags[-1]

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

def check_patch(repo, rtag, flists, commit):
    new = Status.objects.filter(name = 'New')[0]
    sent = Status.objects.filter(name = 'Sent')[0]
    fixed = Status.objects.filter(name = 'Fixed')[0]
    removed = Status.objects.filter(name = 'Removed')[0]
    count = 0

    logger = MyLogger()
    logs = ScanLog(reponame = repo.name, tagname = rtag.name,
                   starttime = strftime("%Y-%m-%d %H:%M:%S", gmtime()),
                   desc = 'Processing, please wait...')
    logs.save()

    scaninfo = []
    logger.logger.info('File changes:')
    logger.logger.info('=' * 40)
    logger.logger.info('%s' % '\n'.join(flists))
    logger.logger.info('=' * 40)
    for dot in [CheckVersionDetector, CheckIncludeDetector, CheckCocciDetector]:
        scount = 0
        test = dot(repo.dirname(), logger.logger)
        for i in range(test.tokens()):
            logger.logger.info('Starting scan type %d' % test.get_type())
            rtype = Type.objects.filter(id = test.get_type())[0]
            if rtype.status == False:
                test.next_token()
                continue

            cmt = None

            if repo.delta == False:
                # for new type, the commit may not sync with repo
                # we need to scan all the files from last type commit
                # per repo has own commit config
                cmts = GitCommit.objects.filter(repo = repo, type = rtype)
                if len(cmts) == 0:
                    cmt = GitCommit(repo = repo, type = rtype)
                    cmt.save()
                    # rtype save the first repo's commit
                    if repo.id == 1:
                        oldcommit = rtype.commit
                    else:
                        oldcommit = cmt.commit
                else:
                    cmt = cmts[0]
                    oldcommit = cmt.commit
    
                if oldcommit != repo.commit:
                    rflists = repo_get_changelist(repo, oldcommit, commit)
                else:
                    rflists = flists
            else:
                # delta check only
                rflists = flists

            exceptfiles = []
            for fn in ExceptFile.objects.filter(type = rtype):
                exceptfiles.append(fn.file)

            for sfile in rflists:
                if not is_source_file(sfile):
                    continue

                if exceptfiles.count(sfile) != 0:
                    logger.logger.info('skip except file %s, type %d' % (sfile, rtype.id))
                    continue

                patchs = Patch.objects.filter(file = sfile, type = rtype)
                rpatchs = []
                opatchs = []
                for p in patchs:
                    if p.status != new and p.status != sent:
                        continue
                    
                    # repo id == 1 is the main kernel tree, so only
                    # allow other tree update main kernel tree's patch
                    if repo == p.tag.repo or p.tag.repo.id == 1:
                        rpatchs.append(p)
                    # the patch found by the same repo
                    if repo == p.tag.repo:
                        opatchs.append(p)

                test.set_filename(sfile)
                # source file maybe removed
                if len(rpatchs) != 0 and not os.path.exists(test._get_file_path()):
                    for p in rpatchs:
                        p.status = removed
                        p.save()

                # if the same file has a patch for this type, ignore it
                # because the last patch does not accepted
                should_patch = test.should_patch()
                if len(rpatchs) != 0 and should_patch == False:
                    for p in rpatchs:
                        p.status = fixed
                        p.save()

                if len(opatchs) == 0 and should_patch == True:
                    text = test.format_patch()
                    patch = Patch(tag = rtag, file = sfile, type = rtype, 
                                  status = new, diff = text)
                    patch.save()

                    # format patch and cache to patch
                    user = patch.username()
                    email = patch.email()
                    formater = PatchFormat(repo.dirname(), sfile, user, email,
                                           rtype.ptitle, rtype.pdesc, text)
                    patch.content = formater.format_patch()
                    patch.title = formater.format_title()
                    patch.desc = rtype.pdesc
                    patch.emails = formater.get_mail_list()
                    patch.save()

                    scount += 1

            if cmt != None:
                # save last scan commit to type
                cmt.commit = commit
                cmt.save()

            # we only save the first repo's commit to rtype
            if repo.id == 1:
                rtype.commit = commit
                rtype.save()

            logger.logger.info('End scan type %d' % test.get_type())
            test.next_token()

        count += scount
        if test.__class__.__name__ == 'CheckVersionDetector':
            scanname = "check version engine"
        elif test.__class__.__name__ == 'CheckIncludeDetector':
            scanname = "check dup include engine"
        elif test.__class__.__name__ == 'CheckCocciDetector':
            scanname = "coccinelle engine"
        scaninfo.append("%s: %d" % (scanname, scount))

    scaninfo.append("total: %d" % (count))
    logs.desc = ', '.join(scaninfo)
    logs.endtime = strftime("%Y-%m-%d %H:%M:%S", gmtime())
    logs.logs = logger.getlog()
    logs.save()

    return count

def main(args):
    for repo in GitRepo.objects.all():
        # repo is disabled
        if repo.status == False:
            continue

        # the last tag name
        otag = tag_from_repo(repo)
        check_repo_update(repo)
        # the tag name after git pull
        ntag = tag_from_repo(repo)
        if otag is None:
            otag = ntag

        tag = otag
        if otag != ntag:
            # we got a new tag, just scan from last commit to otag
            # as common, new tag is the last commit, so does not need
            # to scan twice
            commit = tag_to_commit(repo, tag)
        else:
            commit = commit_from_repo(repo)

        # if delta scan is enbled, skip the first time since we git clone
        # the tree, treat there is no file change
        if repo.delta == True:
            if repo.commit is None or len(repo.commit) == 0:
                repo.commit = commit
                repo.save()
                continue

            # no file change
            if repo.commit == commit:
                continue

        # file change list from last update
        flists = repo_get_changelist(repo, repo.commit, commit)

        tags = GitTag.objects.filter(repo = repo, name = tag)
        rtag = None
        if tags.count() == 0:
            rtag = GitTag(repo = repo, name = tag, flist = ','.join(flists), total = 0)
            rtag.save()
        else:
            rtag = tags[0]

        if rtag.running == True:
            continue

        rtag.running = True
        rtag.save()

        print "Check for repo %s" % os.path.basename(repo.url)
        pcount = check_patch(repo, rtag, flists, commit)

        rtag.total += pcount
        rtag.flist = ','.join(flists)
        rtag.running = False
        rtag.save()

        repo.commit = commit
        repo.save()
        print "Total patch %d" % pcount

    return 0

if __name__ == '__main__':
    sys.exit(main(sys.argv))
