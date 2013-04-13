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

from django import forms

from dpatch.models import ExceptFile, Patch, Report, Type, GitTag

class GitRepoForm(forms.Form):
    name = forms.CharField(max_length = 30)
    user = forms.CharField(max_length = 30)
    email = forms.CharField(max_length = 30)
    url = forms.CharField(max_length = 256)

class ExceptFileForm(forms.ModelForm):
    class Meta:
        model = ExceptFile
        fields = ['type', 'file', 'reason']

class PatchNewForm(forms.ModelForm):
    class Meta:
        model = Patch
        fields = ['tag', 'type', 'file']

    def __init__(self, repoid, tagname, **kwargs):
        super(PatchNewForm, self).__init__(**kwargs)
        self.fields['type'].queryset = Type.objects.filter(id__lte = 10000)
        self.fields['tag'].queryset = GitTag.objects.filter(repo__id = repoid, name__icontains = tagname)

class ReportNewForm(forms.ModelForm):
    class Meta:
        model = Report
        fields = ['tag', 'type', 'file']

    def __init__(self, repoid, tagname, **kwargs):
        super(ReportNewForm, self).__init__(**kwargs)
        self.fields['type'].queryset = Type.objects.filter(id__gt = 10000)
        self.fields['tag'].queryset = GitTag.objects.filter(repo__id = repoid, name__icontains = tagname)