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

from django.contrib import admin

from models import SysConfig, GitRepo, GitTag, GitCommit, Type, ExceptFile, Patch, Report
from models import CocciPatchEngine, CocciReportEngine, ScanLog, Event, Module

class SysConfigAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'value')

class GitRepoAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'url', 'user', 'email', 'commit', 'update', 'build', 'status')

class GitTagAdmin(admin.ModelAdmin):
    list_display = ('id', 'repo', 'name', 'total', 'rptotal', 'running')

class GitCommitAdmin(admin.ModelAdmin):
    list_display = ('id', 'repo', 'type', 'commit')

class StatusAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')

class TypeAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'ptitle', 'pdesc', 'type', 'user', 'email', 'status')

class ExceptFileAdmin(admin.ModelAdmin):
    list_display = ('id', 'type', 'file', 'reason')

class ModuleAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'file')

class CocciPatchEngineAdmin(admin.ModelAdmin):
    list_display = ('id', 'file', 'options', 'fixed')

class CocciReportEngineAdmin(admin.ModelAdmin):
    list_display = ('id', 'file', 'options')

class PatchAdmin(admin.ModelAdmin):
    list_display = ('id', 'tag', 'file', 'type', 'diff', 'mergered', 'mglist', 'status')

class ReportAdmin(admin.ModelAdmin):
    list_display = ('id', 'tag', 'file', 'type', 'diff', 'mergered', 'mglist', 'status')

class ScanLogAdmin(admin.ModelAdmin):
    list_display = ('id', 'tagname', 'starttime', 'endtime', 'desc')

class EventAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'date', 'event', 'status')

admin.site.register(SysConfig, SysConfigAdmin)
admin.site.register(GitRepo, GitRepoAdmin)
admin.site.register(GitTag, GitTagAdmin)
admin.site.register(GitCommit, GitCommitAdmin)
admin.site.register(Type, TypeAdmin)
admin.site.register(ExceptFile, ExceptFileAdmin)
admin.site.register(Module, ModuleAdmin)
admin.site.register(CocciPatchEngine, CocciPatchEngineAdmin)
admin.site.register(CocciReportEngine, CocciReportEngineAdmin)
admin.site.register(Patch, PatchAdmin)
admin.site.register(Report, ReportAdmin)
admin.site.register(ScanLog, ScanLogAdmin)
admin.site.register(Event, EventAdmin)