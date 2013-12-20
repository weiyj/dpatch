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

from time import localtime, strftime

from dpatch.models import Module
from dpatch.lib.db.sysconfig import read_config
from dpatch.lib.common.utils import execute_shell

class PatchFormater(object):
    def __init__(self, repo, fname, user, email, title, desc, content, comment = None):
        self._repo = repo
        self._fname = fname
        self._user = user
        self._email = email
        self._title = title
        self._desc = desc
        self._comment = comment
        self._content = content
        self._module = None
        self._patch = ''
        self._mlist = None

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
        lists = execute_shell("cd %s ; git log -n 20 --pretty=format:%%s %s ; echo" % (self._repo, self._fname))

        modules = {}
        mcount = 0
        module = ''
        for m in lists:
            if m.find(":") != -1:
                if re.match('\w+\s*:\s*\w+\s*- ', m):
                    mname = re.match('\w+\s*:\s*\w+\s*-', m).group(0).strip()
                else:
                    mname = re.sub(':[^:]*$', "", m).strip()
                # start with 'Merge ....'
                if mname.find('Merge ') != -1:
                    continue
                if len(mname) == 0:
                    continue
                if module.find("%s:" % mname) != -1:
                    continue
                if modules.has_key(mname):
                    modules[mname] += 1
                    if mcount < modules[mname]:
                        mcount = modules[mname]
                        module = mname
                    elif mname.find("%s:" % module) != -1:
                        # make sure 'module: submodule:' exists at least twice
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
        commit_signer = ''
        commit_signer_list = []
        _re_list = [{'cc': ['linux-wireless@vger.kernel.org', 'linux-bluetooth@vger.kernel.org'],
                     'rmto': ['David S. Miller <davem@davemloft.net>', '"David S. Miller" <davem@davemloft.net>'],
                     'rmcc': ['netdev@vger.kernel.org']},
                    {'cc': ['devicetree@vger.kernel.org'], 'rmto': [],
                     'rmcc': ['devicetree@vger.kernel.org']}]

        lists = execute_shell("cd %s ; /usr/bin/perl ./scripts/get_maintainer.pl -f %s --remove-duplicates --nogit" % (self._repo, self._fname))
        for m in lists:
            # skip User <mail> (commit_signer:1/15=7%)
            if re.search('\(commit_signer:', m) != None:
                csm = re.sub('\([^>]*\)$', '', m)
                if len(commit_signer) == 0:
                    commit_signer = csm
                commit_signer_list.append(csm)
                continue
            m = re.sub('\([^>]*\)$', '', m).strip()
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
                if len(m.strip()) != 0:
                    mailcc.append(m)

        if nolkml == True and skiplkml == True:
            mailcc.append('linux-kernel@vger.kernel.org')

        for rml in _re_list:
            for cc in rml['cc']:
                if mailcc.count(cc) != 0:
                    for rto in rml['rmto']:
                        if mailto.count(rto) != 0:
                            mailto.remove(rto)
                    for rcc in rml['rmcc']:
                        if mailcc.count(rcc) != 0:
                            mailcc.remove(rcc)
                    break

        if mailcc.count('linux-wireless@vger.kernel.org') != 0 or mailcc.count('linux-bluetooth@vger.kernel.org') != 0:
            if mailcc.count('netdev@vger.kernel.org') != 0:
                mailcc.remove('netdev@vger.kernel.org')
            if mailto.count('David S. Miller <davem@davemloft.net>') != 0:
                mailto.remove('David S. Miller <davem@davemloft.net>')
            if mailto.count('"David S. Miller" <davem@davemloft.net>') != 0:
                mailto.remove('"David S. Miller" <davem@davemloft.net>')

        if len(mailto) == 0 and mailcc.count('netdev@vger.kernel.org') != 0:
            mailto.append('David S. Miller <davem@davemloft.net>')

        if read_config('git.use_commit_singer', True):
            for m in commit_signer_list:
                mailto.append(m)
        else:
            if len(mailto) == 0 and len(commit_signer) != 0:
                mailto.append(commit_signer)

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

    def _weak_email_list(self):
        lists = self._mlist.split('\n')
        for i in range(len(lists)):
            if lists[i].find('To:') != -1:
                lists[i] = re.sub('[^<]*<(.*)>([,]*)', 'To: \g<1>\g<2>', lists[i])
            elif lists[i].find('Cc:') != -1:
                break
            else:
                lists[i] = re.sub('[^<]*<(.*)>([,]*)', '    \g<1>\g<2>', lists[i])

        return '\n'.join(lists)

    def _guest_function_name(self):
        funcname = []
        if self._content is None:
            return funcname
        lastfun = None
        for line in self._content.split('\n'):
            line = line.strip()
            if re.match(r"@@[^@]*@@", line):
                if lastfun != None and funcname.count("%s()" % lastfun) == 0:
                    funcname.append("%s()" % lastfun)

                lastfun = None
                line = re.sub("@@[^@]*@@", "", line)
                line = re.sub("\(.*", "", line).strip()
                line = re.sub("\*", "", line)
                if len(line) != 0:
                    fun = line.split(' ')[-1]
                    # skip lable
                    if re.match(r".*:$", fun):
                        continue
                    lastfun = fun
            elif line.find('-') == 0 and line[-1] != ';':
                line = re.sub("-", '', line).strip()
                if re.search('\w+\s*\(\w+\s+\w+', line) or re.search('\w+\s+\w+\s*\(', line):
                    line = re.sub('\(.*', '', line).strip()
                    if len(line) != 0:
                        fun = line.split(' ')[-1]
                        fun = re.sub('\W+', '', fun)
                        if len(fun) != 0 and funcname.count("%s()" % fun) == 0:
                            lastfun = None
                            funcname.append("%s()" % fun)

        if lastfun != None and funcname.count("%s()" % lastfun) == 0:
            funcname.append("%s()" % lastfun)
                    
        return funcname

    def _guest_struct_name(self):
        structnames = []
        if self._content is None:
            return structnames

        wname = None
        for line in self._content.split('\n'):
            line = line.strip()
            if re.search('struct\s+\w+\s+\w+\s*=\s*{', line):
                structname = re.search('struct\s+\w+', line).group(0).strip()
                if re.match(r"^@@[^@]*@@", line):
                    wname = structname
                elif structnames.count(structname) == 0:
                    wname = None
                    structnames.append(structname)
            elif re.match(r"^@@[^@]*@@", line):
                if not wname is None:
                    if structnames.count(wname) == 0:
                        structnames.append(wname)
                wname = None

        if not wname is None:
            if structnames.count(wname) == 0:
                structnames.append(wname)

        return structnames

    def _guest_field_name(self):
        fields = []
        if self._content is None:
            return fields

        for line in self._content.split('\n'):
            line = line.strip()
            if re.match(r"@@[^@]*@@", line):
                continue
            if re.search('^\+\s*.\w+\s+=\s+[^,]+,', line):
                field = re.search('\s*.\w+\s+', line).group(0).strip()
                if fields.count(field) == 0:
                    fields.append(field)

        return fields

    def _guest_new_field_name(self):
        fields = []
        if self._content is None:
            return fields

        oldfields = []
        for line in self._content.split('\n'):
            line = line.strip()
            if re.match(r"@@[^@]*@@", line):
                continue
            if re.search('^-\s*.\w+\s+=\s+[^,]+,', line) or re.search('^-\s*.\w+\s+=\s+[^,]+$', line):
                field = re.search('\s*.\w+\s+', line).group(0).strip()
                if oldfields.count(field) == 0:
                    oldfields.append(field)
            if re.search('^\+\s*.\w+\s+=\s+[^,]+,', line):
                field = re.search('\s*.\w+\s+', line).group(0).strip()
                if fields.count(field) == 0:
                    fields.append(field)

        return filter(lambda x : oldfields.count(x) == 0, fields)

    def _guest_variable_name(self):
        types = ['struct', 'int', 'long', 'char', 'unsigned', 'u64', 'u32', 'size_t']
        varname = []
        if self._content is None:
            return varname
        for line in self._content.split('\n'):
            line = line.strip()
            if line.find('-') != 0:
                continue
            line = re.sub("-", "", line).strip()
            if line.split(' ')[0] in types:
                if line.find('=') != -1:
                    line = re.sub("=.*", "", line)
                line = re.sub(";", "", line)
                line = re.sub("\*", " ", line)
                name = line.strip().split(' ')[-1]
                name = re.sub(r'\W+', '', name)
                if len(name) != 0 and varname.count(name) == 0:
                        varname.append("%s" % name)

        return varname

    def _format_value(self, value):
        if re.search(r'{{[^}]*}}', value):
            if os.path.isdir(self._fullpath()):
                value = re.sub(r'\s+from\s*{{\s*file\s*}}', '', value)
                value = re.sub(r'{{\s*file\s*}}', '', value)
            else:
                value = re.sub(r'{{\s*file\s*}}', self._basename(), value)
    
            if re.search(r'{{\s*function\s*}}', value):
                funcs = self._guest_function_name()
                if len(funcs) == 1:
                    value = re.sub(r'{{\s*function\s*}}', funcs[0], value)
                else:
                    value = re.sub(r'\s+from\s*{{\s*function\s*}}', '', value)
                    value = re.sub(r'\s+of\s*{{\s*function\s*}}', '', value)
                    value = re.sub(r'\s+in\s*{{\s*function\s*}}', '', value)
                    value = re.sub(r'{{\s*function\s*}}', '', value)

            if re.search(r'{{\s*variable\s*}}', value):
                varnames = self._guest_variable_name()
                if len(varnames) == 1:
                    value = re.sub(r'{{\s*variable\s*}}', ', '.join(varnames), value)
                elif len(varnames) > 1:
                    value = re.sub(r'\s+variable\s+', " variables ", value)
                    value = re.sub(r'{{\s*variables\*}}\s*is\s*', "%s are " % ', '.join(varnames), value)
                    value = re.sub(r'{{\s*variable\*}}\s*is\s*', "%s are " % ', '.join(varnames), value)
                    value = re.sub(r'{{\s*variables\s*}}', ', '.join(varnames), value)
                    value = re.sub(r'{{\s*variable\s*}}', ', '.join(varnames), value)
                else:
                    value = re.sub(r'{{\s*variable\s*}}', '', value)                    

            if re.search(r'{{\s*struct\s*}}', value):
                structs = self._guest_struct_name()
                value = re.sub(r'{{\s*struct\s*}}', ', '.join(structs), value)

            if re.search(r'{{\s*field\s*}}', value):
                fields = self._guest_field_name()
                value = re.sub(r'{{\s*field\s*}}', ', '.join(fields), value)

            if re.search(r'{{\s*newfield\s*}}', value):
                fields = self._guest_new_field_name()
                value = re.sub(r'{{\s*newfield\s*}}', ', '.join(fields), value)

        return value

    def format_title(self):
        title = self._format_value(self._title)

        target = os.path.basename(self._repo)
        if len(self._module) > 1 and self._module[-1] == '-':
            seq = ''
        else:
            seq = ':'
        if title.find('[PATCH') != -1:
            return title
        elif target == 'linux':
            return '[PATCH] %s%s %s' % (self._module, seq, title)            
        elif target == 'linux-next':
            return '[PATCH -next] %s%s %s' % (self._module, seq, title)
        else:
            return '[PATCH %s] %s%s %s' % (target, self._module, seq, title)

    def format_desc(self):
        return self._format_value(self._desc)

    def get_mail_list(self):
        if self._mlist is None:
            self._guest_email_list()

        return self._mlist

    def set_module_name(self, module):
        self._module = module

    def set_mail_list(self, mlist):
        self._mlist = mlist

    def get_module(self):
        if not self._module is None:
            return self._module
        if not os.path.isdir(self._fullpath()):
            mnames = Module.objects.filter(file = self._fname)
            if len(mnames) != 0:
                self._module = mnames[0].name
                return self._module
        return self._guest_module_name()

    def format_patch(self):
        self.get_module()

        patch = "Content-Type: text/plain; charset=ISO-8859-1\n"
        patch += "Content-Transfer-Encoding: 7bit\n"
        patch += "From: %s <%s>\n" % (self._user, self._email)
        patch += "Date: %s\n" % strftime("%a, %d %b %Y %H:%M:%S +0000", localtime())
        patch += "Subject: %s\n" % self.format_title()
        try:
            patch += self.get_mail_list()
        except:
            patch += self._weak_email_list()
        try:
            patch += "\n%s\n\n" % self.format_desc()
        except:
            patch += "\n%s\n\n" % unicode(self.format_desc(), 'utf-8')
        patch += "Signed-off-by: %s <%s>\n" % (self._user, self._email)
        if self._comment != None and len(self._comment) > 0:
            patch += "%s\n" % self._comment
        patch += "---\n"
        try:
            patch += "%s" % self._content
        except:
            patch += "%s" % unicode(self._content, 'utf-8')

        self._patch = patch

        return patch
