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

import re
class PatchParser(object):
    def __init__(self, content):
        self._content = content
        self._title = 'undefined'
        self._ftitle = ''
        self._desc = 'undefined'
        self._module = 'undefined'
        self._emails = 'undefined'
        self._user = ''
        self._mail = ''
        self._diff = ''
        self._comment = ''

    def parser(self):
        start_mail = False
        start_desc = False
        start_diff = False
        for line in self._content.split('\n'):
            if start_mail is True:
                self._emails += '\n' + line
                if not re.search(',$', line):
                    start_mail = False
                continue

            if start_desc is True:
                if re.search('---$', line):
                    self._diff = '\n' + line
                    start_desc = False
                    start_diff = True
                    continue
                elif re.search('Signed-off-by:', line):
                    start_desc = False
                    start_diff = True
                    line = re.sub('Signed-off-by:', '', line)
                    self._user = re.sub('<[^@]+@[^>]+>', '', line).strip()
                    line = re.sub('^[^<]+', '', line)
                    self._mail = re.sub('[<>]', '', line).strip()
                    continue
                self._desc += '\n' + line
                continue

            if start_diff is True:
                if re.search('---$', line):
                    self._comment += self._diff
                    self._diff = '\n' + line
                else:
                    self._diff += '\n' + line
                continue
            if line.find('Content-Type: ') == 0:
                continue
            if line.find('Content-Transfer-Encoding:') == 0:
                continue
            if re.search('From: [^<]+<[^@]+@[^>]+>', line):
                continue
            if re.search('Date: \w+, \d+ \w+ \d+ \d+:\d+:\d+', line):
                continue
            if re.search('Subject: \[PATCH', line):
                self._ftitle = re.sub('Subject:', '', line).strip()
                line = re.sub('Subject: \[PATCH[^\]]*]', '', line).strip()
                if re.match('\w+\s*:\s*\w+\s*-', line):
                    self._title = re.sub('^.*-', '', line).strip()
                    self._module = re.match('\w+\s*:\s*\w+\s*-', line).group(0).strip()
                else:
                    self._title = re.sub('^.*:', '', line).strip()
                    self._module = re.sub(':[^:]*$', '', line).strip()
                continue
            if re.search('To: [^<]*<[^@]+@[^>]+>', line) or re.search('To: [^@]+@.*', line):
                self._emails = line
                if re.search('To: [^<]*<[^@]+@[^>]+>,', line) or re.search('To: [^@]+@.*', line):
                    start_mail = True
                continue
            if re.search('Cc: [^@]+@.*', line):
                self._emails += '\n' + line
                if re.search('Cc: [^@]+@.*,', line):
                    start_mail = True
                continue
            if start_desc is False and len(line) == 0:
                start_desc = True
                self._desc = ''
                continue

        if len(self._desc) > 0:
            self._desc = '\n'.join(self._desc.split('\n')[1:-1])
        if len(self._emails) > 0:
            self._emails += '\n'
        if len(self._comment) > 0:
            self._comment = '\n'.join(self._comment.split('\n')[1:])
        if len(self._diff) > 0:
            self._diff = '\n'.join(self._diff.split('\n')[2:])

    def get_title(self):
        return self._title

    def get_title_full(self):
        return self._ftitle

    def get_description(self):
        return self._desc

    def get_module_name(self):
        return self._module

    def get_email_list(self):
        return self._emails

    def get_comment(self):
        return self._comment

    def get_diff(self):
        return self._diff

    def get_user(self):
        return self._user

    def get_mail(self):
        return self._mail