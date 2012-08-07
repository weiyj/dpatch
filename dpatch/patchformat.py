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
import subprocess

from time import gmtime, strftime

class PatchFormat:
    def __init__(self, repo, fname, user, email, title, desc, content):
        self._repo = repo
        self._fname = fname
        self._user = user
        self._email = email
        self._title = title
        self._desc = desc
        self._content = content
        self._module = ''
        self._patch = ''
        self._mlist = None

    def _execute_shell(self, args):
        if isinstance(args, basestring):
            shelllog = subprocess.Popen(args, shell=True, stdout=subprocess.PIPE)
        else:
            shelllog = subprocess.Popen(args, stdout=subprocess.PIPE)
        shellOut = shelllog.communicate()[0]
    
        lines = shellOut.split("\n")
        lines = lines[0:-1]
    
        return lines

    def _fullpath(self):
        return os.path.join(self._repo, self._fname)

    def _patchdir(self):
        return os.path.join(self._repo, '../PATCH')

    def _basename(self):
        return os.path.basename(self._fname)

    def _dirname(self):
        if os.path.isdir(self._fname):
            return os.path.basename(self._fname)
        else:
            return os.path.basename(os.path.dirname(self._fname))

    def _guest_module_name(self):
        lists = self._execute_shell("cd %s ; git log -n 20 --pretty=format:%%s %s" % (self._repo, self._fname))

        modules = {}
        mcount = 0
        module = ''
        for m in lists:
            if m.find(":") != -1:
                mname = re.sub(':[^:]*$', "", m).strip()
                # start with 'Merge ....'
                if mname.find('Merge ') != -1:
                    continue
                if len(mname) == 0:
                    continue
                if modules.has_key(mname):
                    modules[mname] += 1
                    if mcount < modules[mname]:
                        mcount = modules[mname]
                        module = mname
                else:
                    modules[mname] = 1
                    if module == '':
                        module = mname

        if len(module) == 0:
            module = self._dirname()

        self._module = module

        return module

    def _guest_email_list(self):
        mailto = []
        mailcc = []
        nolkml = True
        skiplkml = False

        lists = self._execute_shell("cd %s ; /usr/bin/perl ./scripts/get_maintainer.pl -f %s --remove-duplicates --nogit" % (self._repo, self._fname))
        for m in lists:
            # skip User <mail> (commit_signer:1/15=7%)
            if re.search('\(commit_signer:', m) != None:
                continue
            m = re.sub('\(.*\)', '', m)
            if re.search(r'<.*>', m) != None:
                mailto.append(m)
            elif re.search('linux-kernel@vger.kernel.org', m) != None:
                if len(mailcc) == 0:
                    mailcc.append(m)
                else:
                    skiplkml = True
            else:
                if re.search('@vger.kernel.org', m) != None:
                    nolkml = False
                mailcc.append(m)

        if nolkml == True and skiplkml == True:
            mailcc.append('linux-kernel@vger.kernel.org')

        elist = ""
        if len(mailto) != 0:
            elist += "To: %s" % mailto[0].strip()
            to = mailto[1:]
            for t in to:
                elist += ",\n    %s" % t.strip()
        if len(mailcc) != 0:
            prefix = 'Cc'
            # to list may be null
            if len(mailto) == 0:
                prefix = 'To'
            elist += "\n%s: %s" % (prefix, mailcc[0].strip())
            cc = mailcc[1:]
            for c in cc:
                elist += ",\n    %s" % c.strip()
        elist += '\n'

        self._mlist = elist

        return elist

    def get_mail_list(self):
        if self._mlist is None:
            self._guest_email_list()

        return self._mlist

    def format_title(self):
        title = self._title
        if os.path.isdir(self._fullpath()):
            title = re.sub(r'\s+from\s*{{\s*file\s*}}', '', title)
            title = re.sub(r'{{\s*file\s*}}', '', title)
        else:
            title = re.sub(r'{{\s*file\s*}}', self._basename(), title)

        return '%s: %s' % (self._module, title)

    def format_patch(self):
        self._guest_module_name()

        patch = "Content-Type: text/plain; charset=ISO-8859-1\n"
        patch += "Content-Transfer-Encoding: 7bit\n"
        patch += "From: %s <%s>\n" % (self._user, self._email)
        patch += "Date: %s\n" % strftime("%a, %d %b %Y %H:%M:%S +0000", gmtime())
        patch += "Subject: [PATCH] %s\n" % self.format_title()
        patch += "%s\n" % self._guest_email_list()
        patch += "From: %s <%s>\n\n" % (self._user, self._email)
        patch += "%s\n\n" % self._desc
        patch += "Signed-off-by: %s <%s>\n" % (self._user, self._email)
        patch += "---\n"
        patch += "%s" % self._content

        self._patch = patch

        return patch

    def save_patch(self):
        title = self.format_title()
        title = re.sub(r'[ .:]+', '-', title)
        if len(title) > 52:
            title = title[:52]
        fname = os.path.join(self._patchdir(), "0001-%s.patch" % title)
        pfile = open(fname, "w+")
        pfile.write(self._patch)
        pfile.close()
