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
import datetime

from django.db import models
from django.conf import settings

class SysConfig(models.Model):
    id = models.AutoField(primary_key = True)
    name = models.CharField(max_length = 256)
    value = models.CharField(max_length = 256)

    def __unicode__(self):
        return u'%s' %(self.name)

class GitRepo(models.Model):
    id = models.AutoField(primary_key = True)
    name = models.CharField(max_length = 60)
    url = models.CharField(max_length = 256)
    user = models.CharField(max_length = 60)
    email = models.CharField(max_length = 256)
    delta = models.BooleanField(default = False)
    build = models.BooleanField(default = True)
    commit = models.CharField(max_length = 256, blank = True)
    stable = models.CharField(max_length = 256, blank = True)
    update = models.DateTimeField(default = datetime.datetime.now())
    status = models.BooleanField(default = False)

    def __unicode__(self):
        return u'%s' %(self.name)

    def dirname(self):
        dname = os.path.basename(self.url).replace('.git', '')
        return os.path.join(settings.DATA_DIR, 'repo', dname)

    def builddir(self):
        dname = os.path.basename(self.url).replace('.git', '')
        return os.path.join(settings.DATA_DIR, 'build', dname)

class GitTag(models.Model):
    id = models.AutoField(primary_key = True)
    repo = models.ForeignKey(GitRepo)
    name = models.CharField(max_length = 60)
    total = models.IntegerField()
    rptotal = models.IntegerField(default = 0)
    flist = models.TextField(blank = True)
    running = models.BooleanField(default = False)

    def __unicode__(self):
        return u'%s - %s' %(self.name, self.repo.name)

class Type(models.Model):
    id = models.IntegerField(primary_key = True)
    name = models.CharField(max_length = 256, blank = True)
    ptitle = models.CharField(max_length = 256)
    pdesc = models.TextField(blank = True)
    type = models.IntegerField(default = 0)
    flags = models.IntegerField(default = 0)
    commit = models.CharField(max_length = 256, default = '1da177e4c3f41524e886b7f1b8a0c1fc7321cac2')
    user = models.CharField(max_length = 60, blank = True)
    email = models.CharField(max_length = 60, blank = True)
    status = models.BooleanField(default = True)

    def __unicode__(self):
        return u'%s' %(self.name)

class GitCommit(models.Model):
    id = models.AutoField(primary_key = True)
    repo = models.ForeignKey(GitRepo)
    type = models.ForeignKey(Type)
    commit = models.CharField(max_length = 256, default = '1da177e4c3f41524e886b7f1b8a0c1fc7321cac2')

    def __unicode__(self):
        return u'%s' %(self.repo)

class ExceptFile(models.Model):
    id = models.AutoField(primary_key = True)
    type = models.ForeignKey(Type)
    file = models.CharField(max_length = 256)
    reason = models.CharField(max_length = 256, blank = True)

    def __unicode__(self):
        return u'%d %s %s %s' %(self.id, self.type.name, self.file, self.reason)

class CocciPatchEngine(models.Model):
    id = models.AutoField(primary_key = True)
    file = models.CharField(max_length = 256)
    options = models.CharField(max_length = 256, blank = True)
    fixed = models.CharField(max_length = 256, blank = True)
    content = models.TextField(blank = True)

    def __unicode__(self):
        return u'%d %s' %(self.id, self.file)

    def fullpath(self):
        return os.path.join(settings.DATA_DIR, 'pattern', 'cocci', 'patchs', self.file)

class CocciReportEngine(models.Model):
    id = models.AutoField(primary_key = True)
    file = models.CharField(max_length = 256)
    options = models.CharField(max_length = 256, blank = True)
    content = models.TextField(blank = True)

    def __unicode__(self):
        return u'%d %s' %(self.id, self.file)

    def fullpath(self):
        return os.path.join(settings.DATA_DIR, 'pattern', 'cocci', 'reports', self.file)

class Module(models.Model):
    id = models.AutoField(primary_key = True)
    name = models.CharField(max_length = 60)
    file = models.CharField(max_length = 256)

    def __unicode__(self):
        return u'%s %s' %(self.name, self.file)

class Patch(models.Model):
    id = models.AutoField(primary_key = True)
    tag = models.ForeignKey(GitTag)
    type = models.ForeignKey(Type)
    status = models.IntegerField(default = 1)
    file = models.CharField(max_length = 256)
    date = models.DateTimeField(default = datetime.datetime.now())
    mergered = models.IntegerField(default = 0)
    mglist = models.CharField(max_length = 256, blank = True)
    commit = models.CharField(max_length = 60, blank = True)
    module = models.CharField(max_length = 60, blank = True)
    diff = models.TextField()
    title = models.CharField(max_length = 256, blank = True)
    desc = models.TextField(max_length = 512, blank = True)
    emails = models.CharField(max_length = 256, blank = True)
    comment = models.CharField(max_length = 256, blank = True)
    content = models.TextField(blank = True)
    build = models.IntegerField(default = 0)
    buildlog = models.TextField(blank = True)
    process = models.BooleanField(default = False)

    def __unicode__(self):
        return u'%s %s' %(self.tag, self.file)

    def filename(self, prefix = 1):
        fname = re.sub(r'\[[^\]]*\]', '', self.title)
        fname = re.sub(r'\W+', '-', fname.strip())
        if len(fname) > 52:
            fname = fname[:52]
        return "%04d-%s.patch" % (prefix, fname)

    def dirname(self):
        return os.path.join(settings.DATA_DIR, 'repo', 'PATCH')

    def username(self):
        if len(self.type.user) == 0:
            return self.tag.repo.user
        else:
            return self.type.user

    def email(self):
        if len(self.type.email) == 0:
            return self.tag.repo.email
        else:
            return self.type.email

    def sourcefile(self):
        return os.path.join(self.tag.repo.dirname(), self.file)

    def fullpath(self):
        return os.path.join(settings.DATA_DIR, 'repo', 'PATCH', self.filename())

class Report(models.Model):
    id = models.AutoField(primary_key = True)
    tag = models.ForeignKey(GitTag)
    type = models.ForeignKey(Type)
    status = models.IntegerField(default = 1)
    file = models.CharField(max_length = 256)
    date = models.DateTimeField(default = datetime.datetime.now())
    mergered = models.IntegerField(default = 0)
    mglist = models.CharField(max_length = 256, blank = True)
    commit = models.CharField(max_length = 60, blank = True)
    reportlog = models.TextField()
    module = models.CharField(max_length = 60, blank = True)
    diff = models.TextField(default = '')
    title = models.CharField(max_length = 256, blank = True)
    desc = models.TextField(max_length = 256, blank = True)
    emails = models.CharField(max_length = 256, blank = True)
    comment = models.CharField(max_length = 256, blank = True)
    content = models.TextField(blank = True)
    build = models.IntegerField(default = 0)
    buildlog = models.TextField(blank = True)
    process = models.BooleanField(default = False)

    def __unicode__(self):
        return u'%s %s' %(self.tag, self.file)

    def filename(self, prefix = 1):
        fname = re.sub(r'\[[^\]]*\]', '', self.title)
        fname = re.sub(r'\W+', '-', fname.strip())
        if len(fname) > 52:
            fname = fname[:52]
        return "%04d-%s.patch" % (prefix, fname)

    def dirname(self):
        return os.path.join(settings.DATA_DIR, 'repo', 'PATCH')

    def username(self):
        if len(self.type.user) == 0:
            return self.tag.repo.user
        else:
            return self.type.user

    def email(self):
        if len(self.type.email) == 0:
            return self.tag.repo.email
        else:
            return self.type.email

    def sourcefile(self):
        return os.path.join(self.tag.repo.dirname(), self.file)

    def fullpath(self):
        return os.path.join(settings.DATA_DIR, 'repo', 'PATCH', self.filename())

class ScanLog(models.Model):
    id = models.AutoField(primary_key = True)
    reponame = models.CharField(max_length = 60)
    tagname = models.CharField(max_length = 60)
    starttime = models.CharField(max_length = 60)
    endtime = models.CharField(max_length = 60, default = '-')
    desc = models.CharField(max_length = 256, blank = True)
    logs = models.TextField(blank = True)

    def __unicode__(self):
        return u'%s' %(self.tagname)

class Event(models.Model):
    id = models.AutoField(primary_key = True)
    user = models.CharField(max_length = 60, default = 'admin')
    date = models.DateTimeField(default = datetime.datetime.now())
    event = models.CharField(max_length = 256, blank = True)
    status = models.BooleanField(default = True)
