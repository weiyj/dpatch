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
import datetime

from django.db import models
#from django.contrib.auth.models import User

#class UserProfile(models.Model):
#    user = models.ForeignKey(User, unique = True)

#    def name(self):
#        if self.user.first_name or self.user.last_name:
#            names = filter(bool, [self.user.first_name, self.user.last_name])
#            return u' '.join(names)
#        return self.user.username

class GitRepo(models.Model):
    id = models.AutoField(primary_key = True)
    name = models.CharField(max_length = 60)
    url = models.CharField(max_length = 256)
    user = models.CharField(max_length = 60)
    email = models.CharField(max_length = 256)
    delta = models.BooleanField(default = True)
    build = models.BooleanField(default = False)
    commit = models.CharField(max_length = 256, blank = True)
    status = models.BooleanField(default = False)

    def __unicode__(self):
        return u'%s' %(self.url)

    def dirname(self):
        dname = os.path.basename(self.url).replace('.git', '')
        return '/var/lib/dpatch/repo/' + dname

    def builddir(self):
        dname = os.path.basename(self.url).replace('.git', '')
        return '/var/lib/dpatch/build/' + dname

class GitTag(models.Model):
    id = models.AutoField(primary_key = True)
    repo = models.ForeignKey(GitRepo)
    name = models.CharField(max_length = 60)
    total = models.IntegerField()
    rptotal = models.IntegerField(default = 0)
    flist = models.TextField(blank = True)
    running = models.BooleanField(default = False)

    def __unicode__(self):
        return u'%s %s' %(self.name, self.total)

class Status(models.Model):
    id = models.AutoField(primary_key = True)
    name = models.CharField(max_length = 60)

    def __unicode__(self):
        return u'%s' %(self.name)

class CocciEngine(models.Model):
    id = models.AutoField(primary_key = True)
    file = models.CharField(max_length = 256)
    options = models.CharField(max_length = 256, blank = True)
    fixed = models.CharField(max_length = 256, blank = True)
    content = models.TextField(blank = True)

    def __unicode__(self):
        return u'%d %s' %(self.id, self.file)#, self.options)

    def fullpath(self):
        return os.path.join('/var/lib/dpatch/pattern/cocci/%s' % self.file)

    def rawformat(self, title, desc, exceptinfo = []):
        spctx = '/// %s\n' %  title
        spctx += '///\n'
        if len(self.options) > 0:
            spctx += '/// Options: %s\n' % self.options
            spctx += '///\n'
        if len(self.fixed) > 0:
            spctx += '/// Fixed: %s\n' % self.fixed
            spctx += '///\n'
        for einfo in exceptinfo:
            if einfo.has_key('reason'):
                spctx += '/// Except File: %s : %s\n' %  (einfo['file'], einfo['reason'])
            else:
                spctx += '/// Except File: %s\n' % einfo['file']
        if len(exceptinfo) > 0:
            spctx += '///\n'
        for line in desc.split('\n'):
            spctx += '/// %s\n' %  line
        spctx += '///\n'
        spctx += self.content
        return spctx

class CocciReport(models.Model):
    id = models.AutoField(primary_key = True)
    file = models.CharField(max_length = 256)
    options = models.CharField(max_length = 256, blank = True)
    content = models.TextField(blank = True)

    def __unicode__(self):
        return u'%d %s' %(self.id, self.file)

    def fullpath(self):
        return os.path.join('/var/lib/dpatch/pattern/cocci/report/%s' % self.file)

    def rawformat(self, title, desc, exceptinfo = []):
        spctx = '/// %s\n' %  title
        spctx += '///\n'
        if len(self.options) > 0:
            spctx += '/// Options: %s\n' % self.options
            spctx += '///\n'
        for einfo in exceptinfo:
            if einfo.has_key('reason'):
                spctx += '/// Except File: %s : %s\n' %  (einfo['file'], einfo['reason'])
            else:
                spctx += '/// Except File: %s\n' % einfo['file']
        if len(exceptinfo) > 0:
            spctx += '///\n'
        for line in desc.split('\n'):
            spctx += '/// %s\n' %  line
        spctx += '///\n'
        spctx += self.content
        return spctx

class Type(models.Model):
    id = models.IntegerField(primary_key = True)
    name = models.CharField(max_length = 256, blank = True)
    ptitle = models.CharField(max_length = 256)
    pdesc = models.TextField(blank = True)
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

class ExceptFile(models.Model):
    id = models.AutoField(primary_key = True)
    type = models.ForeignKey(Type)
    file = models.CharField(max_length = 256)
    reason = models.CharField(max_length = 256, blank = True)

    def __unicode__(self):
        return u'%d %s %s %s' %(self.id, self.type.name, self.file, self.reason)

class Patch(models.Model):
    id = models.AutoField(primary_key = True)
    tag = models.ForeignKey(GitTag)
    type = models.ForeignKey(Type)
    status = models.ForeignKey(Status)
    file = models.CharField(max_length = 256)
    date = models.DateTimeField(default = datetime.datetime.now())
    mergered = models.IntegerField(default = 0)
    mglist = models.CharField(max_length = 256, blank = True)
    commit = models.CharField(max_length = 60, blank = True)
    diff = models.TextField()
    title = models.CharField(max_length = 256, blank = True)
    desc = models.TextField(max_length = 256, blank = True)
    emails = models.CharField(max_length = 256, blank = True)
    content = models.TextField(blank = True)
    build = models.IntegerField(default = 0)
    buildlog = models.TextField(blank = True)

    def __unicode__(self):
        return u'%s %s' %(self.tag, self.file)

    def filename(self, prefix = 1):
        fname = re.sub(r'[ .:/\\<>\(\)]+', '-', self.title)
        fname = re.sub(r'[\(\)]+', '', fname)
        if len(fname) > 52:
            fname = fname[:52]
        return "%04d-%s.patch" % (prefix, fname)

    def dirname(self):
        return '/var/lib/dpatch/repo/PATCH/'

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

    def fullpath(self):
        return '/var/lib/dpatch/repo/PATCH/%s' % self.filename()

class Report(models.Model):
    id = models.AutoField(primary_key = True)
    tag = models.ForeignKey(GitTag)
    type = models.ForeignKey(Type)
    status = models.ForeignKey(Status)
    file = models.CharField(max_length = 256)
    date = models.DateTimeField(default = datetime.datetime.now())
    mergered = models.IntegerField(default = 0)
    mglist = models.CharField(max_length = 256, blank = True)
    commit = models.CharField(max_length = 60, blank = True)
    reportlog = models.TextField()
    diff = models.TextField(default = '')
    title = models.CharField(max_length = 256, blank = True)
    desc = models.TextField(max_length = 256, blank = True)
    emails = models.CharField(max_length = 256, blank = True)
    content = models.TextField(blank = True)
    build = models.IntegerField(default = 0)
    buildlog = models.TextField(blank = True)

    def __unicode__(self):
        return u'%s %s' %(self.tag, self.file)

    def filename(self, prefix = 1):
        fname = re.sub(r'[ .:/\\<>\(\)]+', '-', self.title)
        fname = re.sub(r'[\(\)]+', '', fname)
        if len(fname) > 52:
            fname = fname[:52]
        return "%04d-%s.patch" % (prefix, fname)

    def dirname(self):
        return '/var/lib/dpatch/repo/PATCH/'

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
        return '/var/lib/dpatch/repo/PATCH/%s' % self.filename()

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
