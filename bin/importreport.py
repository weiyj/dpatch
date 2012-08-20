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
import sys
import tarfile

from dpatch.models import CocciReport, Type, ExceptFile

def importsemantic(fname, title, options, desc, content, exceptfiles):
    name = os.path.splitext(fname)[0]
    
    if CocciReport.objects.filter(file = fname).count() != 0:
        print 'skip %s, already exists' % fname
        return

    engine = CocciReport(file = fname, content = content, options = options)
    ctx = engine.rawformat(title, desc, exceptfiles)
    try:
        cocci = open(engine.fullpath(), "w")
        cocci.write(ctx)
        cocci.close()
    except:
        print 'ERROR: can not write file %s' % engine.fullpath()
        return

    engine.save()

    rtype = Type(id = engine.id + 10000, name = name, ptitle = title, pdesc = desc, status = False)
    rtype.save()
    
    for finfo in exceptfiles:
        efile = ExceptFile(type = rtype, file = finfo['file'], reason = finfo['reason'])
        efile.save()

def importcoccifile(fname, lines):
    if len(lines) < 5:
        return False
    
    options = ''
    desc = []
    content = []
    exceptfiles = []
    isdesc = False
    isctx = False
    for i in range(len(lines)):
        if i == 1 or i == 3:
            continue

        if i == 0:
            title = lines[i]
            title = title.replace('///', '').strip()
            continue

        if isdesc == False and isctx == False:
            line = lines[i]
            if line.find('/// Options:') == 0:
                options = line
                options = options.replace('/// Options:', '').strip()
            elif line.find('/// Except File:') == 0:
                exceptfile = line
                exceptfile = exceptfile.replace('/// Except File:', '').strip()
                efileinfo = exceptfile.split(':')
                if len(efileinfo) == 1:
                    efileinfo.append('')
                exceptfiles.append({'file': efileinfo[0].strip(), 'reason': efileinfo[1].strip()})
            else:
                descline = line
                descline = descline.replace('///', '').strip()
                if len(descline) != 0:
                    desc.append(descline)
                    isdesc = True
            continue

        if isdesc == True:
            descline = lines[i]
            if descline.find('///') != -1:
                descline = descline.replace('///', '').strip()
                if len(descline) == 0:
                    isdesc = False
                    isctx = True
                else:
                    desc.append(descline)
                continue
            else:
                isdesc = False
                isctx = True

        if isctx == False:
            continue
        line = lines[i]
        line = line.replace('///', '').strip()
        content.append(line)

    if len(title) == 0 or len(desc) == 0 or len(content) == 0:
        return False

    importsemantic(fname, title, options, '\n'.join(desc), '\n'.join(content), exceptfiles)
    
    return True

def main(args):
    if len(args) < 1:
        print 'No filename specified.'
    for fname in args:
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
                if importcoccifile(tarinfo.name, fp.readlines()):
                    print 'import succeed: %s' % tarinfo.name
                else:
                    print 'import fail: %s is not a cocci file' % tarinfo.name
        else:
            if os.path.splitext(fname)[1] != ".cocci":
                print "import fail: file %s is not a *.cocci file" % fname
                continue
            fp = open(fname, 'r')
            if importcoccifile(os.path.basename(fname), fp.readlines()):
                print 'import succeed: %s' % fname
            else:
                print 'import fail: %s is not a cocci file' % fname

if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
