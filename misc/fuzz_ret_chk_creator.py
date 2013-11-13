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
import datetime
import subprocess

from misc import is_source_file, _execute_shell

ROOT_DIR = os.path.dirname(os.path.realpath(__file__))
DATAFILE = os.path.join(ROOT_DIR, 'data/fuzz_ret_chk_list.txt')
SCRIPTFILE = os.path.join(ROOT_DIR, 'script/fuzz_ret_chk_finder.cocci')
NULLFILE = os.path.join(ROOT_DIR, 'data/NULL_RET_FUNC_LIST.txt')
ERRFILE = os.path.join(ROOT_DIR, 'data/ERR_PTR_RET_FUNC_LIST.txt')

def is_config_debug_fs(fname):
    cmd = "/usr/bin/grep -r \"CONFIG_DEBUG_FS\" %s > /dev/null" % (fname)
    if subprocess.call(cmd, shell=True) == 0:
        return True
    return False

def main(args):
    kdir = '/var/lib/dpatch/repo/linux-next/'

    skip_list = ['malloc',
                 'readb',
                 'xchg',
                 'PDE_DATA',
                 'ioread32',
                 'in_be32',
                 'nv_ro16',
                 'be32_to_cpu',
                 'le32_to_cpu',
                 'min',
                 'min_t',
                 'inl',
                 'inb',
                 'container_of',
                 'ERR_CAST',
                 'ERR_PTR',
                 'list_entry',
                 'list_first_entry',
                 'key_ref_to_ptr',
                 # skip special function
                 'posix_acl_from_xattr',
                 'skb_gso_segment',
                 'd_hash_and_lookup']

    _fix_table = {"clk_get": "IS_ERR",
                  "dma_buf_attach": "IS_ERR",
                  "platform_device_register_resndata": "IS_ERR",
                  "syscon_node_to_regmap": "IS_ERR",
                  "clk_get_parent": "NULL",
                  "container_of": "NULL",
                  "devm_request_and_ioremap": "NULL",
                  "scsi_host_lookup": "NULL",
                  "ubifs_fast_find_freeable": "NULL",
                  "ubifs_fast_find_frdi_idx": "NULL",
                  "btrfs_get_acl": "IS_ERR_OR_NULL",
                  "btrfs_lookup_xattr": "IS_ERR_OR_NULL",
                  "ext2_get_acl": "IS_ERR_OR_NULL",
                  "ext3_get_acl": "IS_ERR_OR_NULL",
                  "ext4_get_acl": "IS_ERR_OR_NULL",
                  "f2fs_get_acl": "IS_ERR_OR_NULL",
                  "flow_cache_lookup": "IS_ERR_OR_NULL",
                  "gfs2_get_acl": "IS_ERR_OR_NULL",
                  "gfs2_lookupi": "IS_ERR_OR_NULL",
                  "hfsplus_get_posix_acl": "IS_ERR_OR_NULL",
                  "jffs2_get_acl": "IS_ERR_OR_NULL",
                  "jfs_get_acl": "IS_ERR_OR_NULL",
                  "nfs3_proc_getacl": "IS_ERR_OR_NULL",
                  "posix_acl_from_xattr": "IS_ERR_OR_NULL",
                  "reiserfs_get_acl": "IS_ERR_OR_NULL",
                  "xfs_get_acl": "IS_ERR_OR_NULL",}

    if not os.path.exists(DATAFILE):
        sfiles = _execute_shell("find %s -type f" % kdir)[0:-1]
        count = 0
        fp = open(DATAFILE, "w")
        for sfile in sfiles:
            if not is_source_file(sfile):
                continue
            if count > 0 and count % 100 == 0:
                print 'total: %d, current: %d' % (count, len(sfiles))
            count += 1
            sargs = '/usr/bin/spatch -I %s -timeout 20 -very_quiet -sp_file %s %s | sort -u' % (
                        os.path.join(kdir, 'include'), SCRIPTFILE, sfile)
            lines = []
            for line in _execute_shell(sargs):
                if line.find('|') == -1:
                    continue
                #if not re.search('\w+', line):
                #    continue
                #if lines.count(line) != 0:
                #    continue
                if line in skip_list:
                    continue
                lines.append("%s|%s" % (line, sfile))

            if len(lines):
                fp.write('\n'.join(lines))
                fp.write('\n')
        fp.close()

    fp = open(DATAFILE, "r")
    lines = fp.readlines()
    fp.close()

    # merge data
    mlines = []
    lastfile = None
    mfuncs = {}
    for line in lines:
        if line.find('|') == -1:
            continue
        line = line.replace('\n', '')
        a = line.split('|')
        if len(a) < 3:
            continue
        if a[0] in skip_list:
            continue
        if a[1] == 'IS_ERR_OR_NULL':
            continue
        if lastfile != a[2]:
            for fun in mfuncs.keys():
                mlines.append("%s|%s|%s" % (fun, mfuncs[fun], lastfile))
            mfuncs.clear()
            lastfile = a[2]
        if mfuncs.has_key(a[0]) and mfuncs[a[0]] != a[1]:
            #print 'fix for function: %s in file %s' %(a[0], a[2])
            mfuncs[a[0]] = 'IS_ERR_OR_NULL'
        else:
            mfuncs[a[0]] = a[1]
    if not lastfile is None:
        for fun in mfuncs.keys():
            mlines.append("%s|%s|%s" % (fun, mfuncs[fun], lastfile))

    funcs = {}
    for line in mlines:
        if line.find('|') == -1:
            continue
        line = line.replace('\n', '')
        a = line.split('|')
        if len(a) < 3:
            continue
        if a[0] in skip_list:
            continue
        if funcs.has_key(a[0]):
            funcs[a[0]]['cnt'] += 1
            if funcs[a[0]]['type'] != a[1]:
                if a[1] == 'IS_ERR_OR_NULL':
                    #print "WARN: %s, type: %s, real type: %s, file: %s" % (a[0], a[1], funcs[a[0]]['type'], a[2])
                    continue 
                if a[0].find('debugfs_') == 0 and not is_config_debug_fs(a[2]):
                    continue
                print "ERROR: %s, type: %s, real type: %s, file: %s" % (a[0], a[1], funcs[a[0]]['type'], a[2])
        else:
            if _fix_table.has_key(a[0]):
                if _fix_table[a[0]] != a[1]:
                    if a[1] == 'IS_ERR_OR_NULL':
                        #print "WARN: %s, type: %s, real type: %s, file: %s" % (a[0], a[1], _fix_table[a[0]], a[2])
                        continue 
                    if a[0].find('debugfs_') == 0 and not is_config_debug_fs(a[2]):
                        continue
                    print "ERROR: %s, type: %s, real type: %s, file: %s" % (a[0], a[1], _fix_table[a[0]], a[2])
                    funcs[a[0]] = {'type': _fix_table[a[0]], 'cnt': 1}
                else:
                    funcs[a[0]] = {'type': a[1], 'cnt': 1}
            else:
                funcs[a[0]] = {'type': a[1], 'cnt': 1}

    if not os.path.exists(ERRFILE):
        tmps = []
        for fn in funcs.keys():
            if funcs[fn]['type'] != 'IS_ERR':
                continue
            tmps.append("%s|%s|%s" % (fn, funcs[fn]['type'], funcs[fn]['cnt']))
     
        fp = open(ERRFILE, "w")
        fp.write("// Update: %s\n" % datetime.datetime.now())
        fp.write('\n'.join(tmps))
        fp.close()
   
    if not os.path.exists(NULLFILE):
        tmps = []
        for fn in funcs.keys():
            if funcs[fn]['type'] != 'NULL' or funcs[fn]['cnt'] < 2:
                continue
            tmps.append("%s|%s|%s" % (fn, funcs[fn]['type'], funcs[fn]['cnt']))
    
        fp = open(NULLFILE, "w")
        fp.write("// Update: %s\n" % datetime.datetime.now())
        fp.write('\n'.join(tmps))
        fp.close()

    return 0

if __name__ == '__main__':
    sys.exit(main(sys.argv))