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

from misc import is_source_file, _execute_shell

ROOT_DIR = os.path.dirname(os.path.realpath(__file__))
DATAFILE = 'data/struct_module_field_list.txt'
SCRIPTFILE = os.path.join(ROOT_DIR, 'script/struct_module_field_finder.cocci')

def main(args):

    kdir = '/var/lib/dpatch/repo/linux-next/drivers/'

    if not os.path.exists(DATAFILE):
        lines = []
        sfiles = _execute_shell("find %s -type f" % kdir)[0:-1]
        count = 0
        for sfile in sfiles:
            if not is_source_file(sfile):
                continue
            if count > 0 and count % 100 == 0:
                print 'total: %d, current: %d' % (count, len(sfiles))
            count += 1
            sargs = '/usr/bin/spatch -I %s -timeout 30 -very_quiet -sp_file %s %s' % (
                            os.path.join(kdir, 'include'), SCRIPTFILE, sfile)
            for line in _execute_shell(sargs):
                if line.find('|') == -1:
                    continue
                a = line.split('|')
                if len(a) < 2:
                    continue
                lines.append(line)
        fp = open(DATAFILE, "w")
        fp.write('\n'.join(lines))
        fp.close()

    fp = open(DATAFILE, "r")
    lines = fp.readlines()
    fp.close()

    print '@r1@\n\
declarer name module_init;\n\
identifier fn_init;\n\
@@\n\
module_init(fn_init);\n\
\n\
@r2@\n\
declarer name module_exit;\n\
identifier fn_exit;\n\
@@\n\
module_exit(fn_exit);\n\
\n\
@r3@\n\
declarer name module_acpi_driver;\n\
declarer name module_comedi_pcmcia_driver;\n\
declarer name module_pci_driver;\n\
declarer name module_usb_driver;\n\
declarer name module_comedi_usb_driver;\n\
declarer name module_platform_driver;\n\
declarer name module_virtio_driver;\n\
declarer name module_amba_driver;\n\
declarer name module_gameport_driver;\n\
declarer name module_platform_driver_probe;\n\
declarer name module_comedi_driver;\n\
declarer name module_hid_driver;\n\
declarer name module_serio_driver;\n\
declarer name module_comedi_pci_driver;\n\
declarer name module_i2c_driver;\n\
declarer name module_spi_driver;\n\
identifier i_driver;\n\
@@\n\
(\n\
module_acpi_driver(i_driver);\n\
|\n\
module_comedi_pcmcia_driver(i_driver);\n\
|\n\
module_pci_driver(i_driver);\n\
|\n\
module_usb_driver(i_driver);\n\
|\n\
module_comedi_usb_driver(i_driver);\n\
|\n\
module_platform_driver(i_driver);\n\
|\n\
module_virtio_driver(i_driver);\n\
|\n\
module_amba_driver(i_driver);\n\
|\n\
module_gameport_driver(i_driver);\n\
|\n\
module_platform_driver_probe(i_driver);\n\
|\n\
module_comedi_driver(i_driver);\n\
|\n\
module_hid_driver(i_driver);\n\
|\n\
module_serio_driver(i_driver);\n\
|\n\
module_comedi_pci_driver(i_driver);\n\
|\n\
module_i2c_driver(i_driver);\n\
|\n\
module_spi_driver(i_driver);\n\
)\n\n'


    skiplist = ['snd_soc_card', #special
                'dvb_usb_device_properties','hotplug_slot_ops',
                'i2c_driver', 'pci_driver', 'usb_driver', 'platform_driver', 'gameport_driver',
                'scsi_host_template',
                'file_operations']
    for line in lines:
        if line.find('|') == -1:
            continue
        line = line.replace('\n', '')
        a = line.split('|')
        if skiplist.count(a[0]) != 0:
            continue
        if len(a) == 3:
            print '\
@r1__%s depends on (r1 && r2) || r3@\n\
identifier nm;\n\
position p;\n\
@@\n\
struct %s nm@p = {\n\
...,\n\
  .%s = {\n\
    ...,\n\
    .%s = THIS_MODULE,\n\
    ...\n\
   },\n\
...\n\
};\n\
\n\
@r2__%s depends on (r1 && r2) || r3@\n\
identifier nm;\n\
position p;\n\
@@\n\
struct %s nm@p = {\n\
...,\n\
  .%s.%s = THIS_MODULE,\n\
...\n\
};\n\
\n\
@depends on (r1 && r2) || r3@\n\
identifier nm;\n\
position p != {r1__%s.p, r2__%s.p};\n\
@@\n\
(\n\
struct %s nm@p = {\n\
...,\n\
  .%s = {\n\
    ...,\n\
+   .%s = THIS_MODULE,\n\
   },\n\
...\n\
};\n\
|\n\
struct %s nm@p = {\n\
...,\n\
+  .%s.%s = THIS_MODULE,\n\
};\n)\n\
' % (a[0], a[0], a[1], a[2], a[0], a[0], a[1], a[2], a[0], a[0], a[0], a[1], a[2], a[0], a[1], a[2])
        else:
            print '\
@r__%s depends on (r1 && r2) || r3@\n\
identifier nm;\n\
position p;\n\
@@\n\
struct %s nm@p = {\n\
...,\n\
  .%s = THIS_MODULE,\n\
...\n\
};\n\
\n\
@depends on (r1 && r2) || r3@\n\
identifier nm;\n\
position p != {r__%s.p};\n\
@@\n\
struct %s nm@p = {\n\
...,\n\
+ .%s = THIS_MODULE,\n\
};\n' % (a[0], a[0], a[1], a[0], a[0], a[1])

    return 0

def usage(prog):
    print "usage: %s discover | create" % prog

if __name__ == '__main__':
    sys.exit(main(sys.argv))
