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

import datetime

from django.db import models

class GitRepoOld(models.Model):
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

    class Meta:
        app_label = 'dpatch'
        db_table = 'dpatch_gitrepo'

class GitTagOld(models.Model):
    id = models.AutoField(primary_key = True)
    repo = models.ForeignKey(GitRepoOld)
    name = models.CharField(max_length = 60)
    total = models.IntegerField()
    rptotal = models.IntegerField(default = 0)
    flist = models.TextField(blank = True)
    running = models.BooleanField(default = False)

    def __unicode__(self):
        return u'%s - %s' %(self.name, self.repo.name)

    class Meta:
        app_label = 'dpatch'
        db_table = 'dpatch_gittag'

class StatusOld(models.Model):
    id = models.AutoField(primary_key = True)
    name = models.CharField(max_length = 60)

    def __unicode__(self):
        return u'%s' %(self.name)

    class Meta:
        app_label = 'dpatch'
        db_table = 'dpatch_status'

class CocciEngineOld(models.Model):
    id = models.AutoField(primary_key = True)
    file = models.CharField(max_length = 256)
    options = models.CharField(max_length = 256, blank = True)
    fixed = models.CharField(max_length = 256, blank = True)
    content = models.TextField(blank = True)

    def __unicode__(self):
        return u'%d %s' %(self.id, self.file)#, self.options)

    class Meta:
        app_label = 'dpatch'
        db_table = 'dpatch_cocciengine'

class CocciReportOld(models.Model):
    id = models.AutoField(primary_key = True)
    file = models.CharField(max_length = 256)
    options = models.CharField(max_length = 256, blank = True)
    content = models.TextField(blank = True)

    def __unicode__(self):
        return u'%d %s' %(self.id, self.file)

    class Meta:
        app_label = 'dpatch'
        db_table = 'dpatch_coccireport'

class TypeOld(models.Model):
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

    class Meta:
        app_label = 'dpatch'
        db_table = 'dpatch_type'

class GitCommitOld(models.Model):
    id = models.AutoField(primary_key = True)
    repo = models.ForeignKey(GitRepoOld)
    type = models.ForeignKey(TypeOld)
    commit = models.CharField(max_length = 256, default = '1da177e4c3f41524e886b7f1b8a0c1fc7321cac2')

    class Meta:
        app_label = 'dpatch'
        db_table = 'dpatch_gitcommit'

class ExceptFileOld(models.Model):
    id = models.AutoField(primary_key = True)
    type = models.ForeignKey(TypeOld)
    file = models.CharField(max_length = 256)
    reason = models.CharField(max_length = 256, blank = True)

    def __unicode__(self):
        return u'%d %s %s %s' %(self.id, self.type.name, self.file, self.reason)

    class Meta:
        app_label = 'dpatch'
        db_table = 'dpatch_exceptfile'

class PatchOld(models.Model):
    id = models.AutoField(primary_key = True)
    tag = models.ForeignKey(GitTagOld)
    type = models.ForeignKey(TypeOld)
    status = models.ForeignKey(StatusOld)
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

    class Meta:
        app_label = 'dpatch'
        db_table = 'dpatch_patch'

class ReportOld(models.Model):
    id = models.AutoField(primary_key = True)
    tag = models.ForeignKey(GitTagOld)
    type = models.ForeignKey(TypeOld)
    status = models.ForeignKey(StatusOld)
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

    class Meta:
        app_label = 'dpatch'
        db_table = 'dpatch_report'

class ScanLogOld(models.Model):
    id = models.AutoField(primary_key = True)
    reponame = models.CharField(max_length = 60)
    tagname = models.CharField(max_length = 60)
    starttime = models.CharField(max_length = 60)
    endtime = models.CharField(max_length = 60, default = '-')
    desc = models.CharField(max_length = 256, blank = True)
    logs = models.TextField(blank = True)

    def __unicode__(self):
        return u'%s' %(self.tagname)

    class Meta:
        app_label = 'dpatch'
        db_table = 'dpatch_scanlog'

class EventOld(models.Model):
    id = models.AutoField(primary_key = True)
    user = models.CharField(max_length = 60, default = 'admin')
    date = models.DateTimeField(default = datetime.datetime.now())
    event = models.CharField(max_length = 256, blank = True)
    status = models.BooleanField(default = True)

    class Meta:
        app_label = 'dpatch'
        db_table = 'dpatch_event'

