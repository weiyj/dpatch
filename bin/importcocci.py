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
import sys
import tarfile

from dpatch.lib.common.cocciparser import CocciParser
from dpatch.models import CocciPatchEngine, CocciReportEngine, Type, ExceptFile

def importcoccipatch(fname, lines, title, fixed, options, desc, content, efiles):
    name = os.path.splitext(fname)[0]
    
    if CocciPatchEngine.objects.filter(file = fname).count() != 0:
        print 'skip %s, already exists' % fname
        return False

    engine = CocciPatchEngine(file = fname, content = content, options = options, fixed = fixed)
    try:
        cocci = open(engine.fullpath(), "w")
        cocci.writelines(lines)
        cocci.close()
    except:
        print 'ERROR: can not write file %s' % engine.fullpath()
        return False

    engine.save()

    rtype = Type(id = engine.id + 3000, name = name, ptitle = title, pdesc = desc, status = False)
    rtype.save()
    
    for finfo in efiles:
        efile = ExceptFile(type = rtype, file = finfo['file'], reason = finfo['reason'])
        efile.save()

    return True

def importcoccireport(fname, lines, title, options, desc, content, efiles):
    name = os.path.splitext(fname)[0]
    
    if CocciReportEngine.objects.filter(file = fname).count() != 0:
        print 'skip %s, already exists' % fname
        return False

    engine = CocciReportEngine(file = fname, content = content, options = options)
    try:
        cocci = open(engine.fullpath(), "w")
        cocci.writelines(lines)
        cocci.close()
    except:
        print 'ERROR: can not write file %s' % engine.fullpath()
        return False

    engine.save()

    rtype = Type(id = engine.id + 10000, name = name, ptitle = title, pdesc = desc, status = False)
    rtype.save()
    
    for finfo in efiles:
        efile = ExceptFile(type = rtype, file = finfo['file'], reason = finfo['reason'])
        efile.save()

    return True

def importcoccifile(target, fname, lines):
    if len(lines) < 5:
        return False

    cocci = CocciParser(lines)
    cocci.parser()

    if len(cocci.get_title()) == 0 or len(cocci.get_description()) == 0:
        return False
    if len(cocci.get_content()) == 0:
        return False

    if target == 'patch':
        return importcoccipatch(fname, lines, cocci.get_title(), cocci.get_fixed(), cocci.get_options(),
                                cocci.get_description(), cocci.get_content(), cocci.get_efiles())
    elif target == 'report':
        return importcoccireport(fname, lines, cocci.get_title(), cocci.get_options(), cocci.get_description(),
                                cocci.get_content(), cocci.get_efiles())
    else:
        return False
def main(args):
    if len(args) < 3:
        print 'Usage: python %s patch|report file...' % args[0]
        return 0

    if args[1] != 'patch' and args[1] != 'report':
        print 'Usage: python %s patch|report file...' % args[0]
        return 0

    target = args[1]
    for fname in args[2:]:
        if not os.path.isfile(fname):
            print 'file %s does not exists or is not a file' % fname
            continue

        if tarfile.is_tarfile(fname):
            tar = tarfile.open(fname, "r:gz")
            for tarinfo in tar:
                if os.path.splitext(tarinfo.name)[1] != ".cocci":
                    print "import fail: file %s is not a *.cocci file" % tarinfo.name
                    continue
                if not tarinfo.isreg():
                    continue
                print tarinfo.name
                fp = tar.extractfile(tarinfo)
                if importcoccifile(target, tarinfo.name, fp.readlines()):
                    print 'import succeed: %s' % tarinfo.name
                else:
                    print 'import fail: %s is not a cocci file' % tarinfo.name
        else:
            if os.path.splitext(fname)[1] != ".cocci":
                print "import fail: file %s is not a *.cocci file" % fname
                continue
            fp = open(fname, 'r')
            if importcoccifile(target, os.path.basename(fname), fp.readlines()):
                print 'import succeed: %s' % fname
            else:
                print 'import fail: %s is not a cocci file' % fname

if __name__ == '__main__':
    sys.exit(main(sys.argv))
