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
import subprocess

from patchengine import PatchEngine
from dpatch.lib.common.const import CHECK_SPARSE_TYPE

class CheckSparseEngine(PatchEngine):
    def __init__(self, repo, logger = None, build = None):
        PatchEngine.__init__(self, repo, logger, build)
        self._nochk_dirs = ["arch", "Documentation", "include", "tools", "usr", "samples", "scripts"]
        self._type = CHECK_SPARSE_TYPE
        self._diff = []
        self._includes = []
        self._recheck = False

    def _execute_shell(self, args):
        if isinstance(args, basestring):
            shelllog = subprocess.Popen(args, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        else:
            shelllog = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        shellOut = shelllog.communicate()[0]

        if shelllog.returncode != 0 and len(shellOut) > 0:
            self.warning(shellOut)

        lines = shellOut.split("\n")
        lines = lines[0:-1]

        return lines

    def name(self):
        return 'check sparse'

    def has_error(self):
        for line in self._diff:
            if re.search('\s+Error\s+\d', line):
                return True
        return False

    def _get_patch_title(self):
        _cnt = {'total': 0, 'symbol': 0, 'null': 0, 'unused': 0,
                'non_ansi': 0, 'duplicate': 0, 'dubious_not': 0}
        title = 'fix sparse warning'
        _dubious_type = []
        for line in self._diff:
            if self._is_symbol_not_declared(line): 
                _cnt['symbol'] += 1
                _cnt['total'] += 1
            elif self._is_plain_integer_as_null(line):
                _cnt['null'] += 1
                _cnt['total'] += 1
            elif self._is_non_ansi_function_declaration(line):
                _cnt['non_ansi'] += 1
                _cnt['total'] += 1
            elif self._is_duplicate_symbol(line):
                _cnt['duplicate'] += 1
                _cnt['total'] += 1
            elif self._is_dubious_bitwise_with_not(line):
                _cnt['dubious_not'] += 1
                _cnt['total'] += 1
                _type = line.split(':')[-1].strip()
                if _dubious_type.count(_type) == 0:
                    _dubious_type.append(_type)

        if _cnt['symbol'] == _cnt['total']:
            title = 'fix sparse non static symbol warning'
        elif _cnt['unused'] == _cnt['total']:
            title = 'fix sparse unused variable warning'
        elif _cnt['null'] == _cnt['total']:
            title = 'fix sparse NULL pointer warning'
        elif _cnt['non_ansi'] == _cnt['total']:
            title = 'fix sparse non-ANSI function warning'
        elif _cnt['duplicate'] == _cnt['total']:
            title = 'fix sparse duplicate const warning'
        elif _cnt['dubious_not'] == _cnt['total']:
            if len(_dubious_type) == 1:
                title = 'fix sparse dubious %s warning' % _dubious_type[0]
            else:
                title = 'fix sparse dubious bitwise operation on !x warning'
        # fix sparse endianness warnings

        if _cnt['total'] > 1:
            title += 's'

        if self._recheck is True:
            title = 'cHECK-' + title

        return title

    def _get_patch_description(self):
        if len(self._diff) > 1:
            _desc = 'Fixes the following sparse warnings:\n'
        else:
            _desc = 'Fixes the following sparse warning:\n'

        for line in self._diff:
            if len(line) > 80:
                a = line.split(':')
                if len(a) > 4:
                    _desc += '\n' + ':'.join(a[:4])
                    _desc += ':\n' + ':'.join(a[4:])
                else:
                    _desc += '\n' + line
            else:
                _desc += '\n' + line

        #_desc += '\n'

        return _desc

    def _is_skip_type_list(self, line):
        _objname = re.sub("\.c$", ".o", self._fname)
        if re.search('make: \*\*\* \[%s\] Error' % _objname, line):
            return True
        return False

    def _is_symbol_function(self, nr, sym):
        _lines = self._execute_shell("sed -n '%s,1p' %s" % (nr, self._get_build_path()))
        _line = _lines[0]
        if re.search('%s\s*\(' % sym, _line):
            return True
        return False

    def _make_line_static(self, _nr):
        self._execute_shell("sed -i '%ds/^/static /' %s" % (_nr, self._get_build_path()))
        return True

    def _make_line_static_indent(self, _nr):
        self._execute_shell("sed -i -e '%ds/^\(\s*\)/\\1       /' -e '%ds/        /\t/' %s" % (_nr, _nr, self._get_build_path()))
        return True

    def _is_symbol_not_declared(self, line):
        if re.search("symbol '\w+' was not declared", line):
            return True
        return False

    def _is_fake_symbol_not_declared(self, line, sym = None, fread = True):
        if fread is True:
            a = line.split(':')
            if len(a) < 5:
                return True
            _nr = a[1]
            _sym = re.sub("'", "", a[-1].strip().split(' ')[1])
            _inlines = self._execute_shell("sed -n '%s,1p' %s" % (_nr, self._get_build_path()))
            if len(_inlines) < 1:
                return False
            _line = _inlines[0]
        else:
            _line = line
            _sym = sym
        if re.search('^static ', _line) or re.search('\s+static\s+', _line):
            if not fread is None:
                self.warning('FAKE WARNING: %s\n  %s' % (line, _line))
            return True
        if re.search('^__weak ', _line) or re.search('\s+__weak\s+', _line):
            if not fread is None:
                self.warning('FAKE WARNING: %s\n  %s' % (line, _line))
            return True
        if re.search('\(\s*weak\s*\)', _line):
            return True
        if re.search('^EXPORT_SYMBOL\w*\(', _line):
            return True
        _cmd = "grep -r 'EXPORT_SYMBOL\w*(%s)' %s > /dev/null" % (_sym, self._get_build_path())
        if subprocess.call(_cmd, shell=True) == 0:
            if not fread is None:
                self.warning('FAKE WARNING: %s\n  %s  ==> EXPORT_SYMBOL(%s)' % (line, _line, _sym))
            return True
        return False

    def _is_symbol_declared_not_include(self, _sym):
        _incfiles = self._execute_shell("/usr/bin/grep --include=*.h -r '\W%s\W' %s" %
                                        (_sym, os.path.dirname(self._get_build_path())))
        if len(_incfiles) != 0:
            _incfile = os.path.basename(_incfiles[0].split(':')[0])
            if self._includes.count(_incfile) == 0:
                self._includes.append(_incfile)
            return True
        return False

    def _fix_symbol_not_declared(self, line):
        a = line.split(':')
        if len(a) < 5:
            return
        _nr = int(a[1])
        _sym = re.sub("'", "", a[-1].strip().split(' ')[1])
        if _nr < 5:
            return
        _inlines = self._execute_shell("sed -n '%d,%dp' %s" % (_nr -4, _nr + 4, self._get_build_path()))
        if len(_inlines) < 9:
            return
        if self._is_fake_symbol_not_declared(_inlines[4], _sym, False):
            return
        if self._is_symbol_declared_not_include(_sym):
            return
        if re.search('%s\s*\(' % _sym, _inlines[4]):
            _fix = False
            for i in [0, 1, 2, 3]:
                line = _inlines[3 - i]
                if not re.search("\w+\s*$", line):
                    self._make_line_static(_nr - i)
                    _fix = True
                    break
            if not re.search('\)\s*$', _inlines[4]) and not re.search('\(\s*$', _inlines[4]):
                for i in [1, 2, 3, 4]:
                    line = _inlines[4 + i]
                    if re.search('^\t\w+', line):
                        break
                    self._make_line_static_indent(_nr + i)
                    if re.search('\)\s*$', line):
                        break
            if _fix is False:
                self._make_line_static(_nr)
        else:
            self._make_line_static(_nr)

    def _is_unused_variable(self, line):
        if re.search("warning: unused variable ", line):
            return True
        return False

    def _fix_unused_variable(self, line):
        a = line.split(':')
        if len(a) < 4:
            return []
        _nr = int(a[1])
        _sym = re.sub("'", "", a[-1].strip().split(' ')[2])
	try:
            line = self._execute_shell("sed -n '%d,1p' %s" % (_nr, self._get_build_path()))[0]
        except:
            return []
        if line.find(',') != -1:
            self._execute_shell("sed -i '%ds/\(\w\)%s, /\\1/' %s" % (_nr, _sym, self._get_build_path()))
            self._execute_shell("sed -i '%ds/, %s\(\w\)/\\1/' %s" % (_nr, _sym, self._get_build_path()))
            return []
        else:
            return [_nr]

    def _is_plain_integer_as_null(self, line):
        if re.search("Using plain integer as NULL pointer", line):
            return True
        return False

    def _fix_plain_integer_as_null(self, line):
        a = line.split(':')
        if len(a) < 5:
            return False
        # E == 0 => !E sed -e '%ss/\([^ \(]*\)\s*==\s*0\([^0-9]\)/!\\1\\2/'
        self._execute_shell("sed -i '%ss/\([^ \(]*\)\s*==\s*0\([^0-9]\)/!\\1\\2/' %s" % (a[1], self._get_build_path()))
        # E != 0 => E sed -e '%ss/\s*!=\s*0\([^0-9]\)/\\1/'
        self._execute_shell("sed -i '%ss/\s*!=\s*0\([^0-9]\)/\\1/' %s" % (a[1], self._get_build_path()))
        # return 0 => return NULL
        self._execute_shell("sed -i '%ss/\([^0-9]\)0\([^0-9]\)/\\1NULL\\2/' %s" % (a[1], self._get_build_path()))
        return True

    def _is_non_ansi_function_declaration(self, line):
        if re.search("non-ANSI function declaration of function", line):
            return True
        return False

    def _fix_non_ansi_function_declaration(self, line):
        a = line.split(':')
        if len(a) < 5:
            return False
        _fun = re.sub("'", "", a[-1].strip().split(' ')[-1])
        self._execute_shell("sed -i '%ss/%s\s*(\s*)/%s(void)/' %s" % (a[1], _fun, _fun, self._get_build_path()))
        return True

    def _is_duplicate_symbol(self, line):
        a = line.split(':')
        if a[0] != self._fname:
            return False
        if re.search("warning: duplicate", line):
            return True
        return False

    def _fix_duplicate_symbol(self, line):
        a = line.split(':')
        if len(a) < 5:
            return False
        _sym = a[-1].strip().split(' ')[-1]
        self._execute_shell("sed -i '%ss/\(\s*%s\s*\)%s\s*/\\1/' %s" % (a[1], _sym, _sym, self._get_build_path()))
        self._execute_shell("sed -i '%ss/const char const \*/const char * const/' %s" % (a[1], self._get_build_path()))
        return True

    def _is_dubious_bitwise_with_not(self, line):
        a = line.split(':')
        if a[0] != self._fname:
            return False
        if re.search("warning: dubious: ", line):
            return True
        return False

    def _fix_dubious_bitwise_with_not(self, line):
        a = line.split(':')
        if len(a) < 6:
            return False
        line = a[1]
        dtype = a[5].strip()

        if dtype == '!x & y':
            #ok1  = !1 &&  2;
            #bad1 = !1 &   2;
            #!rtlpriv->dm.dm_flag & DYNAMIC_FUNC_DIG
            self._execute_shell("sed -i '%ss/!\(\w[a-zA-Z_.>-]*\)\s*\&\s*\([A-Z_][A-Z_]*\)/!(\\1 \\& \\2)/' %s" % (line, self._get_build_path()))
            # !rtlpriv->dm.dm_flag & rtlpriv->dm.dm_flag
            self._execute_shell("sed -i '%ss/!\(\w[a-zA-Z_.>-]*\)\s*\&\s*\(\w[a-zA-Z_.>-]*\)/!\\1 \\&\\& \\2/' %s" % (line, self._get_build_path()))
        elif dtype == '!x | y':
            #ok2  = !1 ||  2;
            #bad2 = !1 |   2;
            # !rtlpriv->dm.dm_flag | rtlpriv->dm.dm_flag
            self._execute_shell("sed -i '%ss/!\(\w[a-zA-Z_.>-]*\)\s*|\s*\(\w[a-zA-Z_.>-]*\)/!\\1 || \\2/' %s" % (line, self._get_build_path()))
        elif dtype == 'x & !y':
            #ok3  =  1 && !2;
            #bad3 =  1 &  !2;
            #DYNAMIC_FUNC_DIG & !rtlpriv->dm.dm_flag
            self._execute_shell("sed -i '%ss/\([A-Z_][A-Z_]*\)\s*\&\s*!\(\w[a-zA-Z_.>-]*\)/!(\\1 \\& \\2)/' %s" % (line, self._get_build_path()))
            # !rtlpriv->dm.dm_flag & rtlpriv->dm.dm_flag
            self._execute_shell("sed -i '%ss/\(\w[a-zA-Z_.>-]*\)\s*\&\s*!\(\w[a-zA-Z_.>-]*\)/\\1 \\&\\& !\\2/' %s" % (line, self._get_build_path()))
        elif dtype == 'x | !y':
            #ok4  =  1 || !2;
            #bad4 =  1 |  !2;
            self._execute_shell("sed -i '%ss/\(\w[a-zA-Z_.>-]*\)\s*|\s*!\(\w[a-zA-Z_.>-]*\)/\\1 || !\\2/' %s" % (line, self._get_build_path()))
        elif dtype == '!x & !y':
            #ok5  = !1 && !2;
            #bad5 = !1 &  !2;
            self._execute_shell("sed -i '%ss/!\(\w[a-zA-Z_.>-]*\)\s*&\s*!\(\w[a-zA-Z_.>-]*\)/!\\1 \\&\\& !\\2/' %s" % (line, self._get_build_path()))
        elif dtype == '!x | !y':
            #ok6  = !1 || !2;
            #bad6 = !1 |  !2;
            self._execute_shell("sed -i '%ss/!\(\w[a-zA-Z_.>-]*\)\s*|\s*!\(\w[a-zA-Z_.>-]*\)/!\\1 || !\\2/' %s" % (line, self._get_build_path()))

        return True

    def _modify_source_file(self):
        _rmlines = []
        self._includes = []
        try:
            for line in self._diff:
                if self._is_symbol_not_declared(line): 
                    self._fix_symbol_not_declared(line)
                elif self._is_plain_integer_as_null(line):
                    self._fix_plain_integer_as_null(line)
                elif self._is_unused_variable(line):
                    _rmlines.extend(self._fix_unused_variable(line))
                elif self._is_non_ansi_function_declaration(line):
                    self._fix_non_ansi_function_declaration(line)
                elif self._is_duplicate_symbol(line):
                    self._fix_duplicate_symbol(line)
                elif self._is_dubious_bitwise_with_not(line):
                    self._fix_dubious_bitwise_with_not(line)
            for _nr in sorted(_rmlines, reverse = True):
                self._execute_shell("sed -i '%dd' %s" % (_nr, self._get_build_path()))
        except:
            return false

        if len(self._includes) != 0:
            _incs = self._execute_shell("/usr/bin/grep -nr '^[\\s]*#include\\s' %s" % self._get_build_path())
            if len(_incs) != 0:
                _nr = _incs[-1].split(':')[0]
            else:
                _nr = "1"
            for _finc in self._includes:
                self._execute_shell("sed -i '%s a#include \"%s\"' %s" % (_nr, _finc, self._get_build_path()))

    def _is_buildable(self):
        #_objname = re.sub("\.c$", ".o", self._fname)
        if not os.path.exists(self._build):
            return False
        if not os.path.exists(os.path.join(self._build, 'vmlinux')):
            return False
        #if not os.path.exists(os.path.join(self._build, _objname)):
        #    return False
        return True

    def _should_patch(self):
        if re.search(r"\.c$", self._fname) == None:
            return False
        if self._build is None:
            return False
        if not self._is_buildable():
            return False
        for _skip in self._nochk_dirs:
            if self._fname.find(_skip) == 0:
                return False
        _objname = re.sub("\.c$", ".o", self._fname)
        args = "cd %s; make C=2 %s | grep '^%s'" % (self._build, _objname, self._fname)
        self._diff = self._execute_shell(args)
        self._recheck = False
        logresult = '\n'.join(self._diff)
        # make may error and need make allmodconfig
        if logresult.find('include/config/auto.conf') != -1:
            self._execute_shell("cd %s; make allmodconfig" % self._build)
            args = "cd %s; make C=2 %s | grep '^%s'" % (self._build, _objname, self._fname)
            self._diff = self._execute_shell(args)
        if len(os.path.dirname(self._fname).split(os.sep)) > 2:
            args = "cd %s; make C=2 M=%s" % (self._build, os.path.dirname(self._fname))
            _modresult = self._execute_shell(args)
        else:
            _modresult = None
        if self._is_skip_type_list('\n'.join(self._diff)):
            return
        for line in self._diff:
            # module build does not exists for this one?
            if not _modresult is None and not line in _modresult:
                self._recheck = True
            if self._is_symbol_not_declared(line):
                if not self._is_fake_symbol_not_declared(line):
                    return True
            elif self._is_plain_integer_as_null(line):
                return True
            elif self._is_unused_variable(line):
                return True
            elif self._is_non_ansi_function_declaration(line):
                return True
            elif self._is_duplicate_symbol(line):
                return True
            elif self._is_dubious_bitwise_with_not(line):
                return True
            elif self._is_skip_type_list(line):
                return False
        return False

    def _revert_soure_file(self):
        os.system("cd %s ; git diff %s | patch -p1 -R > /dev/null" % (self._build, self._fname))

    def _get_diff(self):
        diff = subprocess.Popen("cd %s ; LC_ALL=en_US git diff --patch-with-stat %s" % (self._build, self._fname),
                                shell=True, stdout=subprocess.PIPE)
        diffOut = diff.communicate()[0]
        return diffOut

if __name__ == "__main__":
    repo = "/pub/scm/build/linux-test"
    files = ['drivers/mfd/ab8500-debugfs.c', 'init/main.c']

    count = 0
    for sfile in files:
        detector = CheckSparseEngine("/pub/scm/build/linux-next", None, repo)
        detector.set_filename(sfile)
        #print detector._guess_mail_list()
        if detector.should_patch():
            count += 1
            print detector.get_patch_title()
            print detector.get_patch_description()
            print detector.get_patch()

    print "patch files: %d" % count
