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
DATAFILE = os.path.join(ROOT_DIR, 'data/release_func_missing_list.txt')
SCRIPTFILE = os.path.join(ROOT_DIR, 'script/release_func_missing_finder.cocci')

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
            afuncs = []
            bfuncs = []
            funcinfo = {}
            tfuncinfo = {}
            for line in _execute_shell(sargs):
                if line.find('|') == -1:
                    continue
                a = line.split('|')
                if len(a) < 3:
                    continue
                afuncs.append(a[0])
                bfuncs.append(a[1])
                if afuncs.count(a[0]) > 1:
                    funcinfo[a[0]] = None
                else:
                    funcinfo[a[0]] = a[1]
                    tfuncinfo[a[0]] = a[2]
            for func in funcinfo.keys():
                if funcinfo[func] is None:
                    continue
                if func in ['PTR_RET', 'IS_ERR']:
                    continue
                if afuncs.count(func) > 1:
                    continue
                if bfuncs.count(funcinfo[func]) > 1 and not funcinfo[func] in ['kfree']:
                    continue
                lines.append("%s|%s|%s|%s" % (func, funcinfo[func], tfuncinfo[func], sfile))
                print "%s|%s|%s|%s" % (func, funcinfo[func], tfuncinfo[func], sfile)
        fp = open(DATAFILE, "w")
        fp.write('\n'.join(lines))
        fp.close()

    fp = open(DATAFILE, "r")
    lines = fp.readlines()
    fp.close()

    print '/// add missing {{function1}} on error path in {{function}}\n\
///\n\
/// Add the missing {{function1}} before return from\n\
/// {{function}} in the error handling case.\n'

    fixlist = {
        'lpfc_sli4_rb_alloc': 'lpfc_sli4_rb_free',
        'lpfc_els_hbq_alloc': 'lpfc_els_hbq_free',
        'init_bch': 'free_bch',
        'usb_create_hcd': 'usb_create_hcd',
        'scsi_host_alloc': 'scsi_host_put'
    }
    # skip entry
    _extlist = ['vmalloc|kfree|1',
                'request_mem_region|release_resource|1',
                'device_register|put_device|2',
                'ad7606_reset|ad7606_free_gpios|2',
                'ahci_stop_engine|ahci_start_engine|2',
                'apei_exec_pre_map_gars|apei_exec_post_unmap_gars|2',
                'ast_mm_init|kfree|2',
                'ath10k_hif_power_up|ath10k_hif_power_down|2',
                'ath10k_htt_tx_alloc_msdu_id|ath10k_htt_tx_dec_pending|2',
                'ath10k_pci_wake|ath10k_pci_sleep|2',
                'ath6kl_htc_start|ath6kl_htc_stop|2',
                'ath6kl_wmi_init|ath6kl_wmi_shutdown|1',
                'bch_cache_set_alloc|bch_cache_set_unregister|1',
                'be_chk_reset_complete|beiscsi_unmap_pci_function|2',
                'bnx2fc_send_fw_fcoe_init_msg|bnx2fc_unbind_adapter_devices|2',
                'brcmf_p2p_attach|wl_deinit_priv|2',
                'chp_update_desc|kfree|2',
                'clk_prepare_enable|clk_unprepare|2',
                'CMD_SP|fc_fcp_pkt_release|1',
                'cpia2_init_camera_struct|kfree|1',
                'create_wlan|kfree|1',
                'cryp_check|kfree|2',
                'device_bind_driver|device_unregister|2',
                'device_register|device_del|2',
                'device_register|put_device|2',
                'dgrp_tty_init|kfree|2',
                'dsp_reload|kfree|2',
                'ehea_sense_port_attr|ehea_unregister_port|2',
                'es|ecard_release_resources|2',
                'exynos_drm_gem_init|kfree|1',
                'get_cpu_device|put_cluster_clk_and_freq_table|1',
                'gpio_to_irq|gpio_free|2',
                'hash_check_hw|kfree|2',
                'i1480_mac_fw_upload|i1480_print_state|2',
                'i915_gem_init_hw|i915_gem_cleanup_ringbuffer|2',
                'i915_gem_object_get_pages|i915_gem_object_unpin_pages|2',
                'init_ft1000_netdev|kfree|2',
                'intelfbhw_check_non_crt|cleanup|2',
                'inv_mpu6050_probe_trigger|iio_triggered_buffer_cleanup|2',
                'ioat_dma_setup_interrupts|ioat_disable_interrupts|2',
                'iwl_run_init_ucode|iwl_down|2',
                'ldlm_handle2lock|LDLM_LOCK_PUT|1',
                '_malloc|kfree|1',
                'mantis_pci_init|kfree|2',
                'mdesc_grab|mdesc_release|1',
                'mempool_alloc|fc_exch_hold|1',
                'nand_scan_tail|nand_release|2',
                'NCR_700_detect|scsi_host_put|1',
                'of_device_alloc|platform_device_put|1',
                'pch_gbe_hal_read_mac_addr|pch_gbe_hal_phy_hw_reset|2',
                'pci_alloc_dev|pci_stop_and_remove_bus_device|1',
                'pcibios_add_platform_entries|pci_remove_resource_files|2',
                'pci_create_sysfs_dev_files|pci_dev_put|2',
                'pci_get_domain_bus_and_slot|pci_dev_put|1',
                'pcmcia_request_io|pcmcia_disable_device|2',
                'pm_runtime_get_sync|pm_runtime_disable|2',
                'ptlrpc_queue_wait|ptlrpc_req_finished|2',
                'pwc_init_controls|kfree|2',
                'qlcnic_83xx_enable_flash_write|qlcnic_83xx_unlock_flash|2',
                'r600_parse_extended_power_table|ci_dpm_fini|2',
                'radeon_dummy_page_init|radeon_gart_fini|2',
                'register_sja1000dev|free_sja1000dev|2',
                'rsxx_creg_setup|kfree|2',
                's3c_camif_create_subdev|s3c_camif_unregister_subdev|2',
                's3c_camif_create_subdev|s3c_camif_unregister_subdev|2',
                'sas_end_device_alloc|sas_rphy_free|1',
                'sas_port_add|sas_port_mark_backlink|2',
                'sdhci_add_host|sdhci_bcm_kona_sd_reset|2',
                'setup_fritz|kfree|2',
                'skb_unshare|kfree_skb|1',
                'snd_cx18_pcm_create|kfree|2',
                'snd_ivtv_pcm_create|kfree|2',
                'st5481_setup_b|st5481_release_b|2',
                'stk1160_vb2_setup|kfree|2',
                't4_l2t_alloc_switching|cxgb4_l2t_release|1',
                't4_prep_adapter|kfree|2',
                'ubi_wl_get_peb|ubi_ro_mode|2',
                'usb_create_hcd|kfree|1',
                'usb_phy_init|usb_phy_shutdown|2',
                'vb2_queue_init|kfree|2',
                'wl1251_ps_elp_wakeup|wl1251_ps_elp_sleep|2',
                'wl1271_ps_elp_wakeup|wl1271_ps_elp_sleep|2',
                'xhci_halt|kfree|2',
                'xhci_reset|kfree|2',
                'xillybus_init_endpoint|kfree|1',
      ]
    # skip alloc or release
    skiplist = ['alloc_etherdev',
                'cdev_alloc',
                'clk_disable_unprepare',
                'clk_put',
                'csio_get_scsi_ioreq_lock',
                'destroy_workqueue',
                'drm_fb_helper_fini',
                'free',
                'free_netdev',
                'hid_add_device',
                'hid_parse',
                'i915_gem_init_hw',
                'i915_gem_object_unpin',
                'iounmap',
                'IS_ERR',
                'KMEM_CACHE',
                'lpfc_selective_reset',
                'misc_deregister',
                'pci_disable_device',
                'pcmcia_enable_device',
                'platform_device_del',
                'platform_device_unregister',
                'platform_driver_unregister',
                'platform_device_put',
                'platform_get_resource',
                's5p_mfc_reset',
                'spi_get_ctldata',
                'uart_unregister_driver',
                'ubi_dump_vid_hdr',
                'udl_gem_alloc_object',
                'vfree',
                'videobuf_alloc_vb',
                'videobuf_sg_alloc',
                'vzalloc' ]

    funcs = {}
    # prepare data
    for line in lines:
        if line.find('|') == -1:
            continue
        line = line.replace('\n', '')
        if line in _extlist:
            continue
        a = line.split('|')
        if skiplist.count(a[0]) != 0:
            continue
        if skiplist.count(a[1]) != 0:
            continue
        if len(a) < 3:
            continue
        if "%s|%s|%s" % (a[0], a[1], a[2]) in _extlist:
            continue
        if len(a[0]) < 1:
            continue
        if funcs.has_key(a[0]):
            if funcs[a[0]]['key'] != a[2]:
                #print "wrong key: %s|%s|%s|%s" % (a[0], a[1], a[2], a[3])
                continue
            if funcs[a[0]]['func'].count(a[1]) == 0:
                funcs[a[0]]['func'].append(a[1])
        else:
            if fixlist.has_key(a[0]):
                funcs[a[0]] = {'key': a[2], 'func': [fixlist[a[0]]]}
                if funcs[a[0]]['func'].count(a[1]) == 0:
                    funcs[a[0]]['func'].append(a[1])
            else:
                funcs[a[0]] = {'key': a[2], 'func': [a[1]]}

    # write script
    for _func in funcs.keys():
        _release = funcs[_func]['func'][0]
        if funcs[_func]['key'] == '1':
            continue
            print '\
@r1__%s exists@\n\
expression nm;\n\
expression E != {0};\n\
statement S;\n\
position p1, p2;\n\
@@\n\
 nm = %s(...);\n\
 if (nm == NULL) S\n\
  ... when != %s(nm)\n\
 if@p1 (...) {\n\
   ... when != %s(nm)' % (_func, _func, _release, _release)
            for _ref in funcs[_func]['func'][1:]:
                print '       when != %s(nm)' % _ref
            print '       when forall\n\
   return@p2 E;\n\
  }\n\
\n\
@depends on r1__%s@\n\
expression r1__%s.nm, r1__%s.E;\n\
position r1__%s.p2;\n\
@@\n\
+ %s(nm);\n\
  return@p2 E;\n\
' % (_func, _func, _func, _func, _release)

        elif funcs[_func]['key'] == '2':
            print '\
@r1__%s exists@\n\
expression ret, nm;\n\
expression E != {0};\n\
statement S;\n\
position p1, p2;\n\
@@\n\
 ret = %s(nm);\n\
 if (\(ret < 0\|ret != 0\)) S\n\
  ... when != %s(nm)\n\
 if@p1 (...) {\n\
   ... when != %s(nm)' % (_func, _func, _release, _release)
            for _ref in funcs[_func]['func'][1:]:
                print '       when != %s(nm)' % _ref
            print '       when forall\n\
   return@p2 E;\n\
  }\n\
\n\
@depends on r1__%s@\n\
expression r1__%s.nm, r1__%s.E;\n\
position r1__%s.p2;\n\
@@\n\
+ %s(nm);\n\
  return@p2 E;\n\
' % (_func, _func, _func, _func, _release)

    #print json.dumps(funcs, indent=4)
    return 0

if __name__ == '__main__':
    sys.exit(main(sys.argv))
