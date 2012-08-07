#!/usr/bin/python
#
# Patchmaker - automated kernel patch maker system
# Copyright (C) 2012 Wei Yongjun <weiyj.lk@gmail.com>
#
# This file is part of the Patchmaker package.
#
# Patchmaker is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# Patchmaker is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Patchwork; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA

from django.contrib import admin

from models import GitRepo, GitTag, Status, Type, CocciEngine, Patch, ScanLog, Event

class GitRepoAdmin(admin.ModelAdmin):
    list_display = ('url', 'user', 'email', 'commit')

class GitTagAdmin(admin.ModelAdmin):
    list_display = ('id', 'repo', 'name', 'total')

class StatusAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')

class TypeAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'ptitle', 'pdesc')

class CocciEngineAdmin(admin.ModelAdmin):
    list_display = ('id', 'file')

class PatchAdmin(admin.ModelAdmin):
    list_display = ('id', 'tag', 'file', 'type', 'diff', 'mergered', 'mglist', 'status')

class ScanLogAdmin(admin.ModelAdmin):
    list_display = ('id', 'tagname', 'starttime', 'endtime', 'desc')

class EventAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'date', 'event', 'status')

admin.site.register(GitRepo, GitRepoAdmin)
admin.site.register(GitTag, GitTagAdmin)
admin.site.register(Status, StatusAdmin)
admin.site.register(Type, TypeAdmin)
admin.site.register(CocciEngine, CocciEngineAdmin)
admin.site.register(Patch, PatchAdmin)
admin.site.register(ScanLog, ScanLogAdmin)
admin.site.register(Event, EventAdmin)
