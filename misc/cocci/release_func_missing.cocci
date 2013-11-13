/// add missing {{function1}} on error path in {{function}}
///
/// Add the missing {{function1}} before return from
/// {{function}} in the error handling case.

@r1__host1x_syncpt_init exists@
expression ret, nm;
expression E != {0};
statement S;
position p1, p2;
@@
 ret = host1x_syncpt_init(nm);
 if (\(ret < 0\|ret != 0\)) S
  ... when != host1x_syncpt_deinit(nm)
 if@p1 (...) {
   ... when != host1x_syncpt_deinit(nm)
       when forall
   return@p2 E;
  }

@depends on r1__host1x_syncpt_init@
expression r1__host1x_syncpt_init.nm, r1__host1x_syncpt_init.E;
position r1__host1x_syncpt_init.p2;
@@
+ host1x_syncpt_deinit(nm);
  return@p2 E;

@r1__ps3_ohci_driver_register exists@
expression ret, nm;
expression E != {0};
statement S;
position p1, p2;
@@
 ret = ps3_ohci_driver_register(nm);
 if (\(ret < 0\|ret != 0\)) S
  ... when != ps3_ohci_driver_unregister(nm)
 if@p1 (...) {
   ... when != ps3_ohci_driver_unregister(nm)
       when forall
   return@p2 E;
  }

@depends on r1__ps3_ohci_driver_register@
expression r1__ps3_ohci_driver_register.nm, r1__ps3_ohci_driver_register.E;
position r1__ps3_ohci_driver_register.p2;
@@
+ ps3_ohci_driver_unregister(nm);
  return@p2 E;

@r1__mlx4_en_map_buffer exists@
expression ret, nm;
expression E != {0};
statement S;
position p1, p2;
@@
 ret = mlx4_en_map_buffer(nm);
 if (\(ret < 0\|ret != 0\)) S
  ... when != mlx4_en_unmap_buffer(nm)
 if@p1 (...) {
   ... when != mlx4_en_unmap_buffer(nm)
       when forall
   return@p2 E;
  }

@depends on r1__mlx4_en_map_buffer@
expression r1__mlx4_en_map_buffer.nm, r1__mlx4_en_map_buffer.E;
position r1__mlx4_en_map_buffer.p2;
@@
+ mlx4_en_unmap_buffer(nm);
  return@p2 E;

@r1__sas_register_ports exists@
expression ret, nm;
expression E != {0};
statement S;
position p1, p2;
@@
 ret = sas_register_ports(nm);
 if (\(ret < 0\|ret != 0\)) S
  ... when != sas_unregister_ports(nm)
 if@p1 (...) {
   ... when != sas_unregister_ports(nm)
       when forall
   return@p2 E;
  }

@depends on r1__sas_register_ports@
expression r1__sas_register_ports.nm, r1__sas_register_ports.E;
position r1__sas_register_ports.p2;
@@
+ sas_unregister_ports(nm);
  return@p2 E;

@r1__fcoe_transport_attach exists@
expression ret, nm;
expression E != {0};
statement S;
position p1, p2;
@@
 ret = fcoe_transport_attach(nm);
 if (\(ret < 0\|ret != 0\)) S
  ... when != fcoe_transport_detach(nm)
 if@p1 (...) {
   ... when != fcoe_transport_detach(nm)
       when forall
   return@p2 E;
  }

@depends on r1__fcoe_transport_attach@
expression r1__fcoe_transport_attach.nm, r1__fcoe_transport_attach.E;
position r1__fcoe_transport_attach.p2;
@@
+ fcoe_transport_detach(nm);
  return@p2 E;

@r1__subsys_interface_register exists@
expression ret, nm;
expression E != {0};
statement S;
position p1, p2;
@@
 ret = subsys_interface_register(nm);
 if (\(ret < 0\|ret != 0\)) S
  ... when != subsys_interface_unregister(nm)
 if@p1 (...) {
   ... when != subsys_interface_unregister(nm)
       when forall
   return@p2 E;
  }

@depends on r1__subsys_interface_register@
expression r1__subsys_interface_register.nm, r1__subsys_interface_register.E;
position r1__subsys_interface_register.p2;
@@
+ subsys_interface_unregister(nm);
  return@p2 E;

@r1__crash_shutdown_register exists@
expression ret, nm;
expression E != {0};
statement S;
position p1, p2;
@@
 ret = crash_shutdown_register(nm);
 if (\(ret < 0\|ret != 0\)) S
  ... when != crash_shutdown_unregister(nm)
 if@p1 (...) {
   ... when != crash_shutdown_unregister(nm)
       when forall
   return@p2 E;
  }

@depends on r1__crash_shutdown_register@
expression r1__crash_shutdown_register.nm, r1__crash_shutdown_register.E;
position r1__crash_shutdown_register.p2;
@@
+ crash_shutdown_unregister(nm);
  return@p2 E;

@r1__rtnl_link_register exists@
expression ret, nm;
expression E != {0};
statement S;
position p1, p2;
@@
 ret = rtnl_link_register(nm);
 if (\(ret < 0\|ret != 0\)) S
  ... when != rtnl_link_unregister(nm)
 if@p1 (...) {
   ... when != rtnl_link_unregister(nm)
       when forall
   return@p2 E;
  }

@depends on r1__rtnl_link_register@
expression r1__rtnl_link_register.nm, r1__rtnl_link_register.E;
position r1__rtnl_link_register.p2;
@@
+ rtnl_link_unregister(nm);
  return@p2 E;

@r1__ccw_driver_register exists@
expression ret, nm;
expression E != {0};
statement S;
position p1, p2;
@@
 ret = ccw_driver_register(nm);
 if (\(ret < 0\|ret != 0\)) S
  ... when != ccw_driver_unregister(nm)
 if@p1 (...) {
   ... when != ccw_driver_unregister(nm)
       when forall
   return@p2 E;
  }

@depends on r1__ccw_driver_register@
expression r1__ccw_driver_register.nm, r1__ccw_driver_register.E;
position r1__ccw_driver_register.p2;
@@
+ ccw_driver_unregister(nm);
  return@p2 E;

@r1__register_virtio_driver exists@
expression ret, nm;
expression E != {0};
statement S;
position p1, p2;
@@
 ret = register_virtio_driver(nm);
 if (\(ret < 0\|ret != 0\)) S
  ... when != unregister_virtio_driver(nm)
 if@p1 (...) {
   ... when != unregister_virtio_driver(nm)
       when forall
   return@p2 E;
  }

@depends on r1__register_virtio_driver@
expression r1__register_virtio_driver.nm, r1__register_virtio_driver.E;
position r1__register_virtio_driver.p2;
@@
+ unregister_virtio_driver(nm);
  return@p2 E;

@r1__ath10k_htt_tx_attach exists@
expression ret, nm;
expression E != {0};
statement S;
position p1, p2;
@@
 ret = ath10k_htt_tx_attach(nm);
 if (\(ret < 0\|ret != 0\)) S
  ... when != ath10k_htt_tx_detach(nm)
 if@p1 (...) {
   ... when != ath10k_htt_tx_detach(nm)
       when forall
   return@p2 E;
  }

@depends on r1__ath10k_htt_tx_attach@
expression r1__ath10k_htt_tx_attach.nm, r1__ath10k_htt_tx_attach.E;
position r1__ath10k_htt_tx_attach.p2;
@@
+ ath10k_htt_tx_detach(nm);
  return@p2 E;

@r1____clk_prepare exists@
expression ret, nm;
expression E != {0};
statement S;
position p1, p2;
@@
 ret = __clk_prepare(nm);
 if (\(ret < 0\|ret != 0\)) S
  ... when != __clk_unprepare(nm)
 if@p1 (...) {
   ... when != __clk_unprepare(nm)
       when forall
   return@p2 E;
  }

@depends on r1____clk_prepare@
expression r1____clk_prepare.nm, r1____clk_prepare.E;
position r1____clk_prepare.p2;
@@
+ __clk_unprepare(nm);
  return@p2 E;

@r1__spi_register_driver exists@
expression ret, nm;
expression E != {0};
statement S;
position p1, p2;
@@
 ret = spi_register_driver(nm);
 if (\(ret < 0\|ret != 0\)) S
  ... when != spi_unregister_driver(nm)
 if@p1 (...) {
   ... when != spi_unregister_driver(nm)
       when forall
   return@p2 E;
  }

@depends on r1__spi_register_driver@
expression r1__spi_register_driver.nm, r1__spi_register_driver.E;
position r1__spi_register_driver.p2;
@@
+ spi_unregister_driver(nm);
  return@p2 E;

@r1__regulator_enable exists@
expression ret, nm;
expression E != {0};
statement S;
position p1, p2;
@@
 ret = regulator_enable(nm);
 if (\(ret < 0\|ret != 0\)) S
  ... when != regulator_disable(nm)
 if@p1 (...) {
   ... when != regulator_disable(nm)
       when forall
   return@p2 E;
  }

@depends on r1__regulator_enable@
expression r1__regulator_enable.nm, r1__regulator_enable.E;
position r1__regulator_enable.p2;
@@
+ regulator_disable(nm);
  return@p2 E;

@r1__rt2x00queue_allocate exists@
expression ret, nm;
expression E != {0};
statement S;
position p1, p2;
@@
 ret = rt2x00queue_allocate(nm);
 if (\(ret < 0\|ret != 0\)) S
  ... when != rt2x00lib_remove_dev(nm)
 if@p1 (...) {
   ... when != rt2x00lib_remove_dev(nm)
       when forall
   return@p2 E;
  }

@depends on r1__rt2x00queue_allocate@
expression r1__rt2x00queue_allocate.nm, r1__rt2x00queue_allocate.E;
position r1__rt2x00queue_allocate.p2;
@@
+ rt2x00lib_remove_dev(nm);
  return@p2 E;

@r1__i2c_add_adapter exists@
expression ret, nm;
expression E != {0};
statement S;
position p1, p2;
@@
 ret = i2c_add_adapter(nm);
 if (\(ret < 0\|ret != 0\)) S
  ... when != i2c_del_adapter(nm)
 if@p1 (...) {
   ... when != i2c_del_adapter(nm)
       when forall
   return@p2 E;
  }

@depends on r1__i2c_add_adapter@
expression r1__i2c_add_adapter.nm, r1__i2c_add_adapter.E;
position r1__i2c_add_adapter.p2;
@@
+ i2c_del_adapter(nm);
  return@p2 E;

@r1__register_keyboard_notifier exists@
expression ret, nm;
expression E != {0};
statement S;
position p1, p2;
@@
 ret = register_keyboard_notifier(nm);
 if (\(ret < 0\|ret != 0\)) S
  ... when != unregister_keyboard_notifier(nm)
 if@p1 (...) {
   ... when != unregister_keyboard_notifier(nm)
       when forall
   return@p2 E;
  }

@depends on r1__register_keyboard_notifier@
expression r1__register_keyboard_notifier.nm, r1__register_keyboard_notifier.E;
position r1__register_keyboard_notifier.p2;
@@
+ unregister_keyboard_notifier(nm);
  return@p2 E;

@r1__register_pernet_device exists@
expression ret, nm;
expression E != {0};
statement S;
position p1, p2;
@@
 ret = register_pernet_device(nm);
 if (\(ret < 0\|ret != 0\)) S
  ... when != unregister_pernet_device(nm)
 if@p1 (...) {
   ... when != unregister_pernet_device(nm)
       when forall
   return@p2 E;
  }

@depends on r1__register_pernet_device@
expression r1__register_pernet_device.nm, r1__register_pernet_device.E;
position r1__register_pernet_device.p2;
@@
+ unregister_pernet_device(nm);
  return@p2 E;

@r1__bus_register exists@
expression ret, nm;
expression E != {0};
statement S;
position p1, p2;
@@
 ret = bus_register(nm);
 if (\(ret < 0\|ret != 0\)) S
  ... when != bus_unregister(nm)
 if@p1 (...) {
   ... when != bus_unregister(nm)
       when forall
   return@p2 E;
  }

@depends on r1__bus_register@
expression r1__bus_register.nm, r1__bus_register.E;
position r1__bus_register.p2;
@@
+ bus_unregister(nm);
  return@p2 E;

@r1__register_key_type exists@
expression ret, nm;
expression E != {0};
statement S;
position p1, p2;
@@
 ret = register_key_type(nm);
 if (\(ret < 0\|ret != 0\)) S
  ... when != unregister_key_type(nm)
 if@p1 (...) {
   ... when != unregister_key_type(nm)
       when forall
   return@p2 E;
  }

@depends on r1__register_key_type@
expression r1__register_key_type.nm, r1__register_key_type.E;
position r1__register_key_type.p2;
@@
+ unregister_key_type(nm);
  return@p2 E;

@r1__pxa2xx_spi_dma_setup exists@
expression ret, nm;
expression E != {0};
statement S;
position p1, p2;
@@
 ret = pxa2xx_spi_dma_setup(nm);
 if (\(ret < 0\|ret != 0\)) S
  ... when != pxa2xx_spi_dma_release(nm)
 if@p1 (...) {
   ... when != pxa2xx_spi_dma_release(nm)
       when forall
   return@p2 E;
  }

@depends on r1__pxa2xx_spi_dma_setup@
expression r1__pxa2xx_spi_dma_setup.nm, r1__pxa2xx_spi_dma_setup.E;
position r1__pxa2xx_spi_dma_setup.p2;
@@
+ pxa2xx_spi_dma_release(nm);
  return@p2 E;

@r1__pm_runtime_get exists@
expression ret, nm;
expression E != {0};
statement S;
position p1, p2;
@@
 ret = pm_runtime_get(nm);
 if (\(ret < 0\|ret != 0\)) S
  ... when != pm_runtime_put(nm)
 if@p1 (...) {
   ... when != pm_runtime_put(nm)
       when forall
   return@p2 E;
  }

@depends on r1__pm_runtime_get@
expression r1__pm_runtime_get.nm, r1__pm_runtime_get.E;
position r1__pm_runtime_get.p2;
@@
+ pm_runtime_put(nm);
  return@p2 E;

@r1__ad_sd_setup_buffer_and_trigger exists@
expression ret, nm;
expression E != {0};
statement S;
position p1, p2;
@@
 ret = ad_sd_setup_buffer_and_trigger(nm);
 if (\(ret < 0\|ret != 0\)) S
  ... when != ad_sd_cleanup_buffer_and_trigger(nm)
 if@p1 (...) {
   ... when != ad_sd_cleanup_buffer_and_trigger(nm)
       when forall
   return@p2 E;
  }

@depends on r1__ad_sd_setup_buffer_and_trigger@
expression r1__ad_sd_setup_buffer_and_trigger.nm, r1__ad_sd_setup_buffer_and_trigger.E;
position r1__ad_sd_setup_buffer_and_trigger.p2;
@@
+ ad_sd_cleanup_buffer_and_trigger(nm);
  return@p2 E;

@r1__pm_runtime_get_sync exists@
expression ret, nm;
expression E != {0};
statement S;
position p1, p2;
@@
 ret = pm_runtime_get_sync(nm);
 if (\(ret < 0\|ret != 0\)) S
  ... when != pm_runtime_put_sync(nm)
 if@p1 (...) {
   ... when != pm_runtime_put_sync(nm)
       when != pm_runtime_put(nm)
       when forall
   return@p2 E;
  }

@depends on r1__pm_runtime_get_sync@
expression r1__pm_runtime_get_sync.nm, r1__pm_runtime_get_sync.E;
position r1__pm_runtime_get_sync.p2;
@@
+ pm_runtime_put_sync(nm);
  return@p2 E;

@r1__ccw_device_set_online exists@
expression ret, nm;
expression E != {0};
statement S;
position p1, p2;
@@
 ret = ccw_device_set_online(nm);
 if (\(ret < 0\|ret != 0\)) S
  ... when != ccw_device_set_offline(nm)
 if@p1 (...) {
   ... when != ccw_device_set_offline(nm)
       when forall
   return@p2 E;
  }

@depends on r1__ccw_device_set_online@
expression r1__ccw_device_set_online.nm, r1__ccw_device_set_online.E;
position r1__ccw_device_set_online.p2;
@@
+ ccw_device_set_offline(nm);
  return@p2 E;

@r1__macio_register_driver exists@
expression ret, nm;
expression E != {0};
statement S;
position p1, p2;
@@
 ret = macio_register_driver(nm);
 if (\(ret < 0\|ret != 0\)) S
  ... when != macio_unregister_driver(nm)
 if@p1 (...) {
   ... when != macio_unregister_driver(nm)
       when forall
   return@p2 E;
  }

@depends on r1__macio_register_driver@
expression r1__macio_register_driver.nm, r1__macio_register_driver.E;
position r1__macio_register_driver.p2;
@@
+ macio_unregister_driver(nm);
  return@p2 E;

@r1__qlcnic_attach exists@
expression ret, nm;
expression E != {0};
statement S;
position p1, p2;
@@
 ret = qlcnic_attach(nm);
 if (\(ret < 0\|ret != 0\)) S
  ... when != qlcnic_detach(nm)
 if@p1 (...) {
   ... when != qlcnic_detach(nm)
       when forall
   return@p2 E;
  }

@depends on r1__qlcnic_attach@
expression r1__qlcnic_attach.nm, r1__qlcnic_attach.E;
position r1__qlcnic_attach.p2;
@@
+ qlcnic_detach(nm);
  return@p2 E;

@r1__sdio_enable_func exists@
expression ret, nm;
expression E != {0};
statement S;
position p1, p2;
@@
 ret = sdio_enable_func(nm);
 if (\(ret < 0\|ret != 0\)) S
  ... when != sdio_disable_func(nm)
 if@p1 (...) {
   ... when != sdio_disable_func(nm)
       when forall
   return@p2 E;
  }

@depends on r1__sdio_enable_func@
expression r1__sdio_enable_func.nm, r1__sdio_enable_func.E;
position r1__sdio_enable_func.p2;
@@
+ sdio_disable_func(nm);
  return@p2 E;

@r1__register_netdevice exists@
expression ret, nm;
expression E != {0};
statement S;
position p1, p2;
@@
 ret = register_netdevice(nm);
 if (\(ret < 0\|ret != 0\)) S
  ... when != unregister_netdevice(nm)
 if@p1 (...) {
   ... when != unregister_netdevice(nm)
       when forall
   return@p2 E;
  }

@depends on r1__register_netdevice@
expression r1__register_netdevice.nm, r1__register_netdevice.E;
position r1__register_netdevice.p2;
@@
+ unregister_netdevice(nm);
  return@p2 E;

@r1__pfifo_request exists@
expression ret, nm;
expression E != {0};
statement S;
position p1, p2;
@@
 ret = pfifo_request(nm);
 if (\(ret < 0\|ret != 0\)) S
  ... when != pfifo_free(nm)
 if@p1 (...) {
   ... when != pfifo_free(nm)
       when forall
   return@p2 E;
  }

@depends on r1__pfifo_request@
expression r1__pfifo_request.nm, r1__pfifo_request.E;
position r1__pfifo_request.p2;
@@
+ pfifo_free(nm);
  return@p2 E;

@r1__beiscsi_process_mcc exists@
expression ret, nm;
expression E != {0};
statement S;
position p1, p2;
@@
 ret = beiscsi_process_mcc(nm);
 if (\(ret < 0\|ret != 0\)) S
  ... when != beiscsi_ue_detect(nm)
 if@p1 (...) {
   ... when != beiscsi_ue_detect(nm)
       when forall
   return@p2 E;
  }

@depends on r1__beiscsi_process_mcc@
expression r1__beiscsi_process_mcc.nm, r1__beiscsi_process_mcc.E;
position r1__beiscsi_process_mcc.p2;
@@
+ beiscsi_ue_detect(nm);
  return@p2 E;

@r1__ptp_populate_sysfs exists@
expression ret, nm;
expression E != {0};
statement S;
position p1, p2;
@@
 ret = ptp_populate_sysfs(nm);
 if (\(ret < 0\|ret != 0\)) S
  ... when != ptp_cleanup_sysfs(nm)
 if@p1 (...) {
   ... when != ptp_cleanup_sysfs(nm)
       when forall
   return@p2 E;
  }

@depends on r1__ptp_populate_sysfs@
expression r1__ptp_populate_sysfs.nm, r1__ptp_populate_sysfs.E;
position r1__ptp_populate_sysfs.p2;
@@
+ ptp_cleanup_sysfs(nm);
  return@p2 E;

@r1__wusbhc_create exists@
expression ret, nm;
expression E != {0};
statement S;
position p1, p2;
@@
 ret = wusbhc_create(nm);
 if (\(ret < 0\|ret != 0\)) S
  ... when != wusbhc_destroy(nm)
 if@p1 (...) {
   ... when != wusbhc_destroy(nm)
       when forall
   return@p2 E;
  }

@depends on r1__wusbhc_create@
expression r1__wusbhc_create.nm, r1__wusbhc_create.E;
position r1__wusbhc_create.p2;
@@
+ wusbhc_destroy(nm);
  return@p2 E;

@r1__ad799x_register_ring_funcs_and_init exists@
expression ret, nm;
expression E != {0};
statement S;
position p1, p2;
@@
 ret = ad799x_register_ring_funcs_and_init(nm);
 if (\(ret < 0\|ret != 0\)) S
  ... when != ad799x_ring_cleanup(nm)
 if@p1 (...) {
   ... when != ad799x_ring_cleanup(nm)
       when forall
   return@p2 E;
  }

@depends on r1__ad799x_register_ring_funcs_and_init@
expression r1__ad799x_register_ring_funcs_and_init.nm, r1__ad799x_register_ring_funcs_and_init.E;
position r1__ad799x_register_ring_funcs_and_init.p2;
@@
+ ad799x_ring_cleanup(nm);
  return@p2 E;

@r1__i2c_bit_add_bus exists@
expression ret, nm;
expression E != {0};
statement S;
position p1, p2;
@@
 ret = i2c_bit_add_bus(nm);
 if (\(ret < 0\|ret != 0\)) S
  ... when != i2c_del_adapter(nm)
 if@p1 (...) {
   ... when != i2c_del_adapter(nm)
       when forall
   return@p2 E;
  }

@depends on r1__i2c_bit_add_bus@
expression r1__i2c_bit_add_bus.nm, r1__i2c_bit_add_bus.E;
position r1__i2c_bit_add_bus.p2;
@@
+ i2c_del_adapter(nm);
  return@p2 E;

@r1__md_rdev_init exists@
expression ret, nm;
expression E != {0};
statement S;
position p1, p2;
@@
 ret = md_rdev_init(nm);
 if (\(ret < 0\|ret != 0\)) S
  ... when != md_rdev_clear(nm)
 if@p1 (...) {
   ... when != md_rdev_clear(nm)
       when forall
   return@p2 E;
  }

@depends on r1__md_rdev_init@
expression r1__md_rdev_init.nm, r1__md_rdev_init.E;
position r1__md_rdev_init.p2;
@@
+ md_rdev_clear(nm);
  return@p2 E;

@r1__lguest_setup_irq exists@
expression ret, nm;
expression E != {0};
statement S;
position p1, p2;
@@
 ret = lguest_setup_irq(nm);
 if (\(ret < 0\|ret != 0\)) S
  ... when != irq_free_desc(nm)
 if@p1 (...) {
   ... when != irq_free_desc(nm)
       when forall
   return@p2 E;
  }

@depends on r1__lguest_setup_irq@
expression r1__lguest_setup_irq.nm, r1__lguest_setup_irq.E;
position r1__lguest_setup_irq.p2;
@@
+ irq_free_desc(nm);
  return@p2 E;

@r1__input_register_device exists@
expression ret, nm;
expression E != {0};
statement S;
position p1, p2;
@@
 ret = input_register_device(nm);
 if (\(ret < 0\|ret != 0\)) S
  ... when != input_free_device(nm)
 if@p1 (...) {
   ... when != input_free_device(nm)
       when != input_unregister_device(nm)
       when forall
   return@p2 E;
  }

@depends on r1__input_register_device@
expression r1__input_register_device.nm, r1__input_register_device.E;
position r1__input_register_device.p2;
@@
+ input_free_device(nm);
  return@p2 E;

@r1__pinctrl_request_gpio exists@
expression ret, nm;
expression E != {0};
statement S;
position p1, p2;
@@
 ret = pinctrl_request_gpio(nm);
 if (\(ret < 0\|ret != 0\)) S
  ... when != pinctrl_free_gpio(nm)
 if@p1 (...) {
   ... when != pinctrl_free_gpio(nm)
       when forall
   return@p2 E;
  }

@depends on r1__pinctrl_request_gpio@
expression r1__pinctrl_request_gpio.nm, r1__pinctrl_request_gpio.E;
position r1__pinctrl_request_gpio.p2;
@@
+ pinctrl_free_gpio(nm);
  return@p2 E;

@r1__st_press_allocate_ring exists@
expression ret, nm;
expression E != {0};
statement S;
position p1, p2;
@@
 ret = st_press_allocate_ring(nm);
 if (\(ret < 0\|ret != 0\)) S
  ... when != st_press_deallocate_ring(nm)
 if@p1 (...) {
   ... when != st_press_deallocate_ring(nm)
       when forall
   return@p2 E;
  }

@depends on r1__st_press_allocate_ring@
expression r1__st_press_allocate_ring.nm, r1__st_press_allocate_ring.E;
position r1__st_press_allocate_ring.p2;
@@
+ st_press_deallocate_ring(nm);
  return@p2 E;

@r1__iwl_trans_start_hw exists@
expression ret, nm;
expression E != {0};
statement S;
position p1, p2;
@@
 ret = iwl_trans_start_hw(nm);
 if (\(ret < 0\|ret != 0\)) S
  ... when != iwl_trans_stop_device(nm)
 if@p1 (...) {
   ... when != iwl_trans_stop_device(nm)
       when forall
   return@p2 E;
  }

@depends on r1__iwl_trans_start_hw@
expression r1__iwl_trans_start_hw.nm, r1__iwl_trans_start_hw.E;
position r1__iwl_trans_start_hw.p2;
@@
+ iwl_trans_stop_device(nm);
  return@p2 E;

@r1__comedi_driver_register exists@
expression ret, nm;
expression E != {0};
statement S;
position p1, p2;
@@
 ret = comedi_driver_register(nm);
 if (\(ret < 0\|ret != 0\)) S
  ... when != comedi_driver_unregister(nm)
 if@p1 (...) {
   ... when != comedi_driver_unregister(nm)
       when forall
   return@p2 E;
  }

@depends on r1__comedi_driver_register@
expression r1__comedi_driver_register.nm, r1__comedi_driver_register.E;
position r1__comedi_driver_register.p2;
@@
+ comedi_driver_unregister(nm);
  return@p2 E;

@r1__transport_class_register exists@
expression ret, nm;
expression E != {0};
statement S;
position p1, p2;
@@
 ret = transport_class_register(nm);
 if (\(ret < 0\|ret != 0\)) S
  ... when != transport_class_unregister(nm)
 if@p1 (...) {
   ... when != transport_class_unregister(nm)
       when forall
   return@p2 E;
  }

@depends on r1__transport_class_register@
expression r1__transport_class_register.nm, r1__transport_class_register.E;
position r1__transport_class_register.p2;
@@
+ transport_class_unregister(nm);
  return@p2 E;

@r1__usb_autopm_get_interface exists@
expression ret, nm;
expression E != {0};
statement S;
position p1, p2;
@@
 ret = usb_autopm_get_interface(nm);
 if (\(ret < 0\|ret != 0\)) S
  ... when != usb_autopm_put_interface(nm)
 if@p1 (...) {
   ... when != usb_autopm_put_interface(nm)
       when forall
   return@p2 E;
  }

@depends on r1__usb_autopm_get_interface@
expression r1__usb_autopm_get_interface.nm, r1__usb_autopm_get_interface.E;
position r1__usb_autopm_get_interface.p2;
@@
+ usb_autopm_put_interface(nm);
  return@p2 E;

@r1__ep93xx_pwm_acquire_gpio exists@
expression ret, nm;
expression E != {0};
statement S;
position p1, p2;
@@
 ret = ep93xx_pwm_acquire_gpio(nm);
 if (\(ret < 0\|ret != 0\)) S
  ... when != ep93xx_pwm_release_gpio(nm)
 if@p1 (...) {
   ... when != ep93xx_pwm_release_gpio(nm)
       when forall
   return@p2 E;
  }

@depends on r1__ep93xx_pwm_acquire_gpio@
expression r1__ep93xx_pwm_acquire_gpio.nm, r1__ep93xx_pwm_acquire_gpio.E;
position r1__ep93xx_pwm_acquire_gpio.p2;
@@
+ ep93xx_pwm_release_gpio(nm);
  return@p2 E;

@r1__mmc_add_host exists@
expression ret, nm;
expression E != {0};
statement S;
position p1, p2;
@@
 ret = mmc_add_host(nm);
 if (\(ret < 0\|ret != 0\)) S
  ... when != mmc_remove_host(nm)
 if@p1 (...) {
   ... when != mmc_remove_host(nm)
       when forall
   return@p2 E;
  }

@depends on r1__mmc_add_host@
expression r1__mmc_add_host.nm, r1__mmc_add_host.E;
position r1__mmc_add_host.p2;
@@
+ mmc_remove_host(nm);
  return@p2 E;

@r1__e1000e_setup_rx_resources exists@
expression ret, nm;
expression E != {0};
statement S;
position p1, p2;
@@
 ret = e1000e_setup_rx_resources(nm);
 if (\(ret < 0\|ret != 0\)) S
  ... when != e1000e_free_rx_resources(nm)
 if@p1 (...) {
   ... when != e1000e_free_rx_resources(nm)
       when forall
   return@p2 E;
  }

@depends on r1__e1000e_setup_rx_resources@
expression r1__e1000e_setup_rx_resources.nm, r1__e1000e_setup_rx_resources.E;
position r1__e1000e_setup_rx_resources.p2;
@@
+ e1000e_free_rx_resources(nm);
  return@p2 E;

@r1__init_srcu_struct exists@
expression ret, nm;
expression E != {0};
statement S;
position p1, p2;
@@
 ret = init_srcu_struct(nm);
 if (\(ret < 0\|ret != 0\)) S
  ... when != cleanup_srcu_struct(nm)
 if@p1 (...) {
   ... when != cleanup_srcu_struct(nm)
       when forall
   return@p2 E;
  }

@depends on r1__init_srcu_struct@
expression r1__init_srcu_struct.nm, r1__init_srcu_struct.E;
position r1__init_srcu_struct.p2;
@@
+ cleanup_srcu_struct(nm);
  return@p2 E;

@r1__dma_async_device_register exists@
expression ret, nm;
expression E != {0};
statement S;
position p1, p2;
@@
 ret = dma_async_device_register(nm);
 if (\(ret < 0\|ret != 0\)) S
  ... when != dma_async_device_unregister(nm)
 if@p1 (...) {
   ... when != dma_async_device_unregister(nm)
       when forall
   return@p2 E;
  }

@depends on r1__dma_async_device_register@
expression r1__dma_async_device_register.nm, r1__dma_async_device_register.E;
position r1__dma_async_device_register.p2;
@@
+ dma_async_device_unregister(nm);
  return@p2 E;

@r1__bus_add_driver exists@
expression ret, nm;
expression E != {0};
statement S;
position p1, p2;
@@
 ret = bus_add_driver(nm);
 if (\(ret < 0\|ret != 0\)) S
  ... when != bus_remove_driver(nm)
 if@p1 (...) {
   ... when != bus_remove_driver(nm)
       when forall
   return@p2 E;
  }

@depends on r1__bus_add_driver@
expression r1__bus_add_driver.nm, r1__bus_add_driver.E;
position r1__bus_add_driver.p2;
@@
+ bus_remove_driver(nm);
  return@p2 E;

@r1__efx_mcdi_init exists@
expression ret, nm;
expression E != {0};
statement S;
position p1, p2;
@@
 ret = efx_mcdi_init(nm);
 if (\(ret < 0\|ret != 0\)) S
  ... when != efx_mcdi_fini(nm)
 if@p1 (...) {
   ... when != efx_mcdi_fini(nm)
       when forall
   return@p2 E;
  }

@depends on r1__efx_mcdi_init@
expression r1__efx_mcdi_init.nm, r1__efx_mcdi_init.E;
position r1__efx_mcdi_init.p2;
@@
+ efx_mcdi_fini(nm);
  return@p2 E;

@r1__pnp_activate_dev exists@
expression ret, nm;
expression E != {0};
statement S;
position p1, p2;
@@
 ret = pnp_activate_dev(nm);
 if (\(ret < 0\|ret != 0\)) S
  ... when != pnp_disable_dev(nm)
 if@p1 (...) {
   ... when != pnp_disable_dev(nm)
       when forall
   return@p2 E;
  }

@depends on r1__pnp_activate_dev@
expression r1__pnp_activate_dev.nm, r1__pnp_activate_dev.E;
position r1__pnp_activate_dev.p2;
@@
+ pnp_disable_dev(nm);
  return@p2 E;

@r1__ath9k_init_btcoex exists@
expression ret, nm;
expression E != {0};
statement S;
position p1, p2;
@@
 ret = ath9k_init_btcoex(nm);
 if (\(ret < 0\|ret != 0\)) S
  ... when != ath9k_eeprom_release(nm)
 if@p1 (...) {
   ... when != ath9k_eeprom_release(nm)
       when forall
   return@p2 E;
  }

@depends on r1__ath9k_init_btcoex@
expression r1__ath9k_init_btcoex.nm, r1__ath9k_init_btcoex.E;
position r1__ath9k_init_btcoex.p2;
@@
+ ath9k_eeprom_release(nm);
  return@p2 E;

@r1__ath5k_hw_init exists@
expression ret, nm;
expression E != {0};
statement S;
position p1, p2;
@@
 ret = ath5k_hw_init(nm);
 if (\(ret < 0\|ret != 0\)) S
  ... when != ath5k_hw_deinit(nm)
 if@p1 (...) {
   ... when != ath5k_hw_deinit(nm)
       when forall
   return@p2 E;
  }

@depends on r1__ath5k_hw_init@
expression r1__ath5k_hw_init.nm, r1__ath5k_hw_init.E;
position r1__ath5k_hw_init.p2;
@@
+ ath5k_hw_deinit(nm);
  return@p2 E;

@r1__uwb_rc_ie_setup exists@
expression ret, nm;
expression E != {0};
statement S;
position p1, p2;
@@
 ret = uwb_rc_ie_setup(nm);
 if (\(ret < 0\|ret != 0\)) S
  ... when != uwb_rc_ie_release(nm)
 if@p1 (...) {
   ... when != uwb_rc_ie_release(nm)
       when forall
   return@p2 E;
  }

@depends on r1__uwb_rc_ie_setup@
expression r1__uwb_rc_ie_setup.nm, r1__uwb_rc_ie_setup.E;
position r1__uwb_rc_ie_setup.p2;
@@
+ uwb_rc_ie_release(nm);
  return@p2 E;

@r1__sclp_register exists@
expression ret, nm;
expression E != {0};
statement S;
position p1, p2;
@@
 ret = sclp_register(nm);
 if (\(ret < 0\|ret != 0\)) S
  ... when != sclp_unregister(nm)
 if@p1 (...) {
   ... when != sclp_unregister(nm)
       when forall
   return@p2 E;
  }

@depends on r1__sclp_register@
expression r1__sclp_register.nm, r1__sclp_register.E;
position r1__sclp_register.p2;
@@
+ sclp_unregister(nm);
  return@p2 E;

@r1__stk1160_i2c_register exists@
expression ret, nm;
expression E != {0};
statement S;
position p1, p2;
@@
 ret = stk1160_i2c_register(nm);
 if (\(ret < 0\|ret != 0\)) S
  ... when != stk1160_i2c_unregister(nm)
 if@p1 (...) {
   ... when != stk1160_i2c_unregister(nm)
       when forall
   return@p2 E;
  }

@depends on r1__stk1160_i2c_register@
expression r1__stk1160_i2c_register.nm, r1__stk1160_i2c_register.E;
position r1__stk1160_i2c_register.p2;
@@
+ stk1160_i2c_unregister(nm);
  return@p2 E;

@r1__sa1111_driver_register exists@
expression ret, nm;
expression E != {0};
statement S;
position p1, p2;
@@
 ret = sa1111_driver_register(nm);
 if (\(ret < 0\|ret != 0\)) S
  ... when != sa1111_driver_unregister(nm)
 if@p1 (...) {
   ... when != sa1111_driver_unregister(nm)
       when forall
   return@p2 E;
  }

@depends on r1__sa1111_driver_register@
expression r1__sa1111_driver_register.nm, r1__sa1111_driver_register.E;
position r1__sa1111_driver_register.p2;
@@
+ sa1111_driver_unregister(nm);
  return@p2 E;

@r1__arizona_irq_init exists@
expression ret, nm;
expression E != {0};
statement S;
position p1, p2;
@@
 ret = arizona_irq_init(nm);
 if (\(ret < 0\|ret != 0\)) S
  ... when != arizona_irq_exit(nm)
 if@p1 (...) {
   ... when != arizona_irq_exit(nm)
       when forall
   return@p2 E;
  }

@depends on r1__arizona_irq_init@
expression r1__arizona_irq_init.nm, r1__arizona_irq_init.E;
position r1__arizona_irq_init.p2;
@@
+ arizona_irq_exit(nm);
  return@p2 E;

@r1__ipu_irq_map exists@
expression ret, nm;
expression E != {0};
statement S;
position p1, p2;
@@
 ret = ipu_irq_map(nm);
 if (\(ret < 0\|ret != 0\)) S
  ... when != ipu_irq_unmap(nm)
 if@p1 (...) {
   ... when != ipu_irq_unmap(nm)
       when forall
   return@p2 E;
  }

@depends on r1__ipu_irq_map@
expression r1__ipu_irq_map.nm, r1__ipu_irq_map.E;
position r1__ipu_irq_map.p2;
@@
+ ipu_irq_unmap(nm);
  return@p2 E;

@r1__of_device_register exists@
expression ret, nm;
expression E != {0};
statement S;
position p1, p2;
@@
 ret = of_device_register(nm);
 if (\(ret < 0\|ret != 0\)) S
  ... when != of_device_unregister(nm)
 if@p1 (...) {
   ... when != of_device_unregister(nm)
       when forall
   return@p2 E;
  }

@depends on r1__of_device_register@
expression r1__of_device_register.nm, r1__of_device_register.E;
position r1__of_device_register.p2;
@@
+ of_device_unregister(nm);
  return@p2 E;

@r1__ath10k_htc_start exists@
expression ret, nm;
expression E != {0};
statement S;
position p1, p2;
@@
 ret = ath10k_htc_start(nm);
 if (\(ret < 0\|ret != 0\)) S
  ... when != ath10k_htc_stop(nm)
 if@p1 (...) {
   ... when != ath10k_htc_stop(nm)
       when forall
   return@p2 E;
  }

@depends on r1__ath10k_htc_start@
expression r1__ath10k_htc_start.nm, r1__ath10k_htc_start.E;
position r1__ath10k_htc_start.p2;
@@
+ ath10k_htc_stop(nm);
  return@p2 E;

@r1__dsi_runtime_get exists@
expression ret, nm;
expression E != {0};
statement S;
position p1, p2;
@@
 ret = dsi_runtime_get(nm);
 if (\(ret < 0\|ret != 0\)) S
  ... when != dsi_runtime_put(nm)
 if@p1 (...) {
   ... when != dsi_runtime_put(nm)
       when forall
   return@p2 E;
  }

@depends on r1__dsi_runtime_get@
expression r1__dsi_runtime_get.nm, r1__dsi_runtime_get.E;
position r1__dsi_runtime_get.p2;
@@
+ dsi_runtime_put(nm);
  return@p2 E;

@r1__i2o_driver_register exists@
expression ret, nm;
expression E != {0};
statement S;
position p1, p2;
@@
 ret = i2o_driver_register(nm);
 if (\(ret < 0\|ret != 0\)) S
  ... when != i2o_driver_unregister(nm)
 if@p1 (...) {
   ... when != i2o_driver_unregister(nm)
       when forall
   return@p2 E;
  }

@depends on r1__i2o_driver_register@
expression r1__i2o_driver_register.nm, r1__i2o_driver_register.E;
position r1__i2o_driver_register.p2;
@@
+ i2o_driver_unregister(nm);
  return@p2 E;

@r1__dev_open exists@
expression ret, nm;
expression E != {0};
statement S;
position p1, p2;
@@
 ret = dev_open(nm);
 if (\(ret < 0\|ret != 0\)) S
  ... when != dev_close(nm)
 if@p1 (...) {
   ... when != dev_close(nm)
       when forall
   return@p2 E;
  }

@depends on r1__dev_open@
expression r1__dev_open.nm, r1__dev_open.E;
position r1__dev_open.p2;
@@
+ dev_close(nm);
  return@p2 E;

@r1__fw_core_add_descriptor exists@
expression ret, nm;
expression E != {0};
statement S;
position p1, p2;
@@
 ret = fw_core_add_descriptor(nm);
 if (\(ret < 0\|ret != 0\)) S
  ... when != fw_core_remove_descriptor(nm)
 if@p1 (...) {
   ... when != fw_core_remove_descriptor(nm)
       when forall
   return@p2 E;
  }

@depends on r1__fw_core_add_descriptor@
expression r1__fw_core_add_descriptor.nm, r1__fw_core_add_descriptor.E;
position r1__fw_core_add_descriptor.p2;
@@
+ fw_core_remove_descriptor(nm);
  return@p2 E;

@r1__dvb_dmx_init exists@
expression ret, nm;
expression E != {0};
statement S;
position p1, p2;
@@
 ret = dvb_dmx_init(nm);
 if (\(ret < 0\|ret != 0\)) S
  ... when != dvb_dmx_release(nm)
 if@p1 (...) {
   ... when != dvb_dmx_release(nm)
       when forall
   return@p2 E;
  }

@depends on r1__dvb_dmx_init@
expression r1__dvb_dmx_init.nm, r1__dvb_dmx_init.E;
position r1__dvb_dmx_init.p2;
@@
+ dvb_dmx_release(nm);
  return@p2 E;

@r1__device_add exists@
expression ret, nm;
expression E != {0};
statement S;
position p1, p2;
@@
 ret = device_add(nm);
 if (\(ret < 0\|ret != 0\)) S
  ... when != device_del(nm)
 if@p1 (...) {
   ... when != device_del(nm)
       when forall
   return@p2 E;
  }

@depends on r1__device_add@
expression r1__device_add.nm, r1__device_add.E;
position r1__device_add.p2;
@@
+ device_del(nm);
  return@p2 E;

@r1__device_register exists@
expression ret, nm;
expression E != {0};
statement S;
position p1, p2;
@@
 ret = device_register(nm);
 if (\(ret < 0\|ret != 0\)) S
  ... when != device_unregister(nm)
 if@p1 (...) {
   ... when != device_unregister(nm)
       when != get_device(nm)
       when forall
   return@p2 E;
  }

@depends on r1__device_register@
expression r1__device_register.nm, r1__device_register.E;
position r1__device_register.p2;
@@
+ device_unregister(nm);
  return@p2 E;

@r1__register_netdev exists@
expression ret, nm;
expression E != {0};
statement S;
position p1, p2;
@@
 ret = register_netdev(nm);
 if (\(ret < 0\|ret != 0\)) S
  ... when != unregister_netdev(nm)
 if@p1 (...) {
   ... when != unregister_netdev(nm)
       when forall
   return@p2 E;
  }

@depends on r1__register_netdev@
expression r1__register_netdev.nm, r1__register_netdev.E;
position r1__register_netdev.p2;
@@
+ unregister_netdev(nm);
  return@p2 E;

@r1__shmob_drm_backlight_init exists@
expression ret, nm;
expression E != {0};
statement S;
position p1, p2;
@@
 ret = shmob_drm_backlight_init(nm);
 if (\(ret < 0\|ret != 0\)) S
  ... when != shmob_drm_backlight_exit(nm)
 if@p1 (...) {
   ... when != shmob_drm_backlight_exit(nm)
       when forall
   return@p2 E;
  }

@depends on r1__shmob_drm_backlight_init@
expression r1__shmob_drm_backlight_init.nm, r1__shmob_drm_backlight_init.E;
position r1__shmob_drm_backlight_init.p2;
@@
+ shmob_drm_backlight_exit(nm);
  return@p2 E;

@r1__usb_autoresume_device exists@
expression ret, nm;
expression E != {0};
statement S;
position p1, p2;
@@
 ret = usb_autoresume_device(nm);
 if (\(ret < 0\|ret != 0\)) S
  ... when != usb_autosuspend_device(nm)
 if@p1 (...) {
   ... when != usb_autosuspend_device(nm)
       when forall
   return@p2 E;
  }

@depends on r1__usb_autoresume_device@
expression r1__usb_autoresume_device.nm, r1__usb_autoresume_device.E;
position r1__usb_autoresume_device.p2;
@@
+ usb_autosuspend_device(nm);
  return@p2 E;

@r1__st_gyro_allocate_ring exists@
expression ret, nm;
expression E != {0};
statement S;
position p1, p2;
@@
 ret = st_gyro_allocate_ring(nm);
 if (\(ret < 0\|ret != 0\)) S
  ... when != st_gyro_deallocate_ring(nm)
 if@p1 (...) {
   ... when != st_gyro_deallocate_ring(nm)
       when forall
   return@p2 E;
  }

@depends on r1__st_gyro_allocate_ring@
expression r1__st_gyro_allocate_ring.nm, r1__st_gyro_allocate_ring.E;
position r1__st_gyro_allocate_ring.p2;
@@
+ st_gyro_deallocate_ring(nm);
  return@p2 E;

@r1__crypto_register_alg exists@
expression ret, nm;
expression E != {0};
statement S;
position p1, p2;
@@
 ret = crypto_register_alg(nm);
 if (\(ret < 0\|ret != 0\)) S
  ... when != crypto_unregister_alg(nm)
 if@p1 (...) {
   ... when != crypto_unregister_alg(nm)
       when forall
   return@p2 E;
  }

@depends on r1__crypto_register_alg@
expression r1__crypto_register_alg.nm, r1__crypto_register_alg.E;
position r1__crypto_register_alg.p2;
@@
+ crypto_unregister_alg(nm);
  return@p2 E;

@r1__scsi_register_interface exists@
expression ret, nm;
expression E != {0};
statement S;
position p1, p2;
@@
 ret = scsi_register_interface(nm);
 if (\(ret < 0\|ret != 0\)) S
  ... when != scsi_unregister_interface(nm)
 if@p1 (...) {
   ... when != scsi_unregister_interface(nm)
       when forall
   return@p2 E;
  }

@depends on r1__scsi_register_interface@
expression r1__scsi_register_interface.nm, r1__scsi_register_interface.E;
position r1__scsi_register_interface.p2;
@@
+ scsi_unregister_interface(nm);
  return@p2 E;

@r1__il_alloc_txq_mem exists@
expression ret, nm;
expression E != {0};
statement S;
position p1, p2;
@@
 ret = il_alloc_txq_mem(nm);
 if (\(ret < 0\|ret != 0\)) S
  ... when != il3945_hw_txq_ctx_free(nm)
 if@p1 (...) {
   ... when != il3945_hw_txq_ctx_free(nm)
       when != il4965_hw_txq_ctx_free(nm)
       when forall
   return@p2 E;
  }

@depends on r1__il_alloc_txq_mem@
expression r1__il_alloc_txq_mem.nm, r1__il_alloc_txq_mem.E;
position r1__il_alloc_txq_mem.p2;
@@
+ il3945_hw_txq_ctx_free(nm);
  return@p2 E;

@r1__input_register_handle exists@
expression ret, nm;
expression E != {0};
statement S;
position p1, p2;
@@
 ret = input_register_handle(nm);
 if (\(ret < 0\|ret != 0\)) S
  ... when != input_unregister_handle(nm)
 if@p1 (...) {
   ... when != input_unregister_handle(nm)
       when forall
   return@p2 E;
  }

@depends on r1__input_register_handle@
expression r1__input_register_handle.nm, r1__input_register_handle.E;
position r1__input_register_handle.p2;
@@
+ input_unregister_handle(nm);
  return@p2 E;

@r1__ib_register_event_handler exists@
expression ret, nm;
expression E != {0};
statement S;
position p1, p2;
@@
 ret = ib_register_event_handler(nm);
 if (\(ret < 0\|ret != 0\)) S
  ... when != ib_unregister_event_handler(nm)
 if@p1 (...) {
   ... when != ib_unregister_event_handler(nm)
       when forall
   return@p2 E;
  }

@depends on r1__ib_register_event_handler@
expression r1__ib_register_event_handler.nm, r1__ib_register_event_handler.E;
position r1__ib_register_event_handler.p2;
@@
+ ib_unregister_event_handler(nm);
  return@p2 E;

@r1__rsxx_dma_setup exists@
expression ret, nm;
expression E != {0};
statement S;
position p1, p2;
@@
 ret = rsxx_dma_setup(nm);
 if (\(ret < 0\|ret != 0\)) S
  ... when != rsxx_dma_destroy(nm)
 if@p1 (...) {
   ... when != rsxx_dma_destroy(nm)
       when forall
   return@p2 E;
  }

@depends on r1__rsxx_dma_setup@
expression r1__rsxx_dma_setup.nm, r1__rsxx_dma_setup.E;
position r1__rsxx_dma_setup.p2;
@@
+ rsxx_dma_destroy(nm);
  return@p2 E;

@r1__ps3_open_hv_device exists@
expression ret, nm;
expression E != {0};
statement S;
position p1, p2;
@@
 ret = ps3_open_hv_device(nm);
 if (\(ret < 0\|ret != 0\)) S
  ... when != ps3_close_hv_device(nm)
 if@p1 (...) {
   ... when != ps3_close_hv_device(nm)
       when forall
   return@p2 E;
  }

@depends on r1__ps3_open_hv_device@
expression r1__ps3_open_hv_device.nm, r1__ps3_open_hv_device.E;
position r1__ps3_open_hv_device.p2;
@@
+ ps3_close_hv_device(nm);
  return@p2 E;

@r1__ieee80211_register_hw exists@
expression ret, nm;
expression E != {0};
statement S;
position p1, p2;
@@
 ret = ieee80211_register_hw(nm);
 if (\(ret < 0\|ret != 0\)) S
  ... when != ieee80211_unregister_hw(nm)
 if@p1 (...) {
   ... when != ieee80211_unregister_hw(nm)
       when != p54_unregister_common(nm)
       when forall
   return@p2 E;
  }

@depends on r1__ieee80211_register_hw@
expression r1__ieee80211_register_hw.nm, r1__ieee80211_register_hw.E;
position r1__ieee80211_register_hw.p2;
@@
+ ieee80211_unregister_hw(nm);
  return@p2 E;

@r1__apei_map_generic_address exists@
expression ret, nm;
expression E != {0};
statement S;
position p1, p2;
@@
 ret = apei_map_generic_address(nm);
 if (\(ret < 0\|ret != 0\)) S
  ... when != apei_unmap_generic_address(nm)
 if@p1 (...) {
   ... when != apei_unmap_generic_address(nm)
       when forall
   return@p2 E;
  }

@depends on r1__apei_map_generic_address@
expression r1__apei_map_generic_address.nm, r1__apei_map_generic_address.E;
position r1__apei_map_generic_address.p2;
@@
+ apei_unmap_generic_address(nm);
  return@p2 E;

@r1__scsi_setup_command_freelist exists@
expression ret, nm;
expression E != {0};
statement S;
position p1, p2;
@@
 ret = scsi_setup_command_freelist(nm);
 if (\(ret < 0\|ret != 0\)) S
  ... when != scsi_destroy_command_freelist(nm)
 if@p1 (...) {
   ... when != scsi_destroy_command_freelist(nm)
       when forall
   return@p2 E;
  }

@depends on r1__scsi_setup_command_freelist@
expression r1__scsi_setup_command_freelist.nm, r1__scsi_setup_command_freelist.E;
position r1__scsi_setup_command_freelist.p2;
@@
+ scsi_destroy_command_freelist(nm);
  return@p2 E;

@r1__drm_agp_acquire exists@
expression ret, nm;
expression E != {0};
statement S;
position p1, p2;
@@
 ret = drm_agp_acquire(nm);
 if (\(ret < 0\|ret != 0\)) S
  ... when != drm_agp_release(nm)
 if@p1 (...) {
   ... when != drm_agp_release(nm)
       when forall
   return@p2 E;
  }

@depends on r1__drm_agp_acquire@
expression r1__drm_agp_acquire.nm, r1__drm_agp_acquire.E;
position r1__drm_agp_acquire.p2;
@@
+ drm_agp_release(nm);
  return@p2 E;

@r1__v4l2_ctrl_handler_setup exists@
expression ret, nm;
expression E != {0};
statement S;
position p1, p2;
@@
 ret = v4l2_ctrl_handler_setup(nm);
 if (\(ret < 0\|ret != 0\)) S
  ... when != v4l2_ctrl_handler_free(nm)
 if@p1 (...) {
   ... when != v4l2_ctrl_handler_free(nm)
       when forall
   return@p2 E;
  }

@depends on r1__v4l2_ctrl_handler_setup@
expression r1__v4l2_ctrl_handler_setup.nm, r1__v4l2_ctrl_handler_setup.E;
position r1__v4l2_ctrl_handler_setup.p2;
@@
+ v4l2_ctrl_handler_free(nm);
  return@p2 E;

@r1__aer_init exists@
expression ret, nm;
expression E != {0};
statement S;
position p1, p2;
@@
 ret = aer_init(nm);
 if (\(ret < 0\|ret != 0\)) S
  ... when != aer_remove(nm)
 if@p1 (...) {
   ... when != aer_remove(nm)
       when forall
   return@p2 E;
  }

@depends on r1__aer_init@
expression r1__aer_init.nm, r1__aer_init.E;
position r1__aer_init.p2;
@@
+ aer_remove(nm);
  return@p2 E;

@r1__ath10k_hif_start exists@
expression ret, nm;
expression E != {0};
statement S;
position p1, p2;
@@
 ret = ath10k_hif_start(nm);
 if (\(ret < 0\|ret != 0\)) S
  ... when != ath10k_hif_stop(nm)
 if@p1 (...) {
   ... when != ath10k_hif_stop(nm)
       when forall
   return@p2 E;
  }

@depends on r1__ath10k_hif_start@
expression r1__ath10k_hif_start.nm, r1__ath10k_hif_start.E;
position r1__ath10k_hif_start.p2;
@@
+ ath10k_hif_stop(nm);
  return@p2 E;

@r1__st_accel_allocate_ring exists@
expression ret, nm;
expression E != {0};
statement S;
position p1, p2;
@@
 ret = st_accel_allocate_ring(nm);
 if (\(ret < 0\|ret != 0\)) S
  ... when != st_accel_deallocate_ring(nm)
 if@p1 (...) {
   ... when != st_accel_deallocate_ring(nm)
       when forall
   return@p2 E;
  }

@depends on r1__st_accel_allocate_ring@
expression r1__st_accel_allocate_ring.nm, r1__st_accel_allocate_ring.E;
position r1__st_accel_allocate_ring.p2;
@@
+ st_accel_deallocate_ring(nm);
  return@p2 E;

@r1__rt_mutex_trylock exists@
expression ret, nm;
expression E != {0};
statement S;
position p1, p2;
@@
 ret = rt_mutex_trylock(nm);
 if (\(ret < 0\|ret != 0\)) S
  ... when != rt_mutex_unlock(nm)
 if@p1 (...) {
   ... when != rt_mutex_unlock(nm)
       when forall
   return@p2 E;
  }

@depends on r1__rt_mutex_trylock@
expression r1__rt_mutex_trylock.nm, r1__rt_mutex_trylock.E;
position r1__rt_mutex_trylock.p2;
@@
+ rt_mutex_unlock(nm);
  return@p2 E;

@r1__drm_ctxbitmap_init exists@
expression ret, nm;
expression E != {0};
statement S;
position p1, p2;
@@
 ret = drm_ctxbitmap_init(nm);
 if (\(ret < 0\|ret != 0\)) S
  ... when != drm_lastclose(nm)
 if@p1 (...) {
   ... when != drm_lastclose(nm)
       when forall
   return@p2 E;
  }

@depends on r1__drm_ctxbitmap_init@
expression r1__drm_ctxbitmap_init.nm, r1__drm_ctxbitmap_init.E;
position r1__drm_ctxbitmap_init.p2;
@@
+ drm_lastclose(nm);
  return@p2 E;

@r1__sas_rphy_add exists@
expression ret, nm;
expression E != {0};
statement S;
position p1, p2;
@@
 ret = sas_rphy_add(nm);
 if (\(ret < 0\|ret != 0\)) S
  ... when != sas_rphy_remove(nm)
 if@p1 (...) {
   ... when != sas_rphy_remove(nm)
       when forall
   return@p2 E;
  }

@depends on r1__sas_rphy_add@
expression r1__sas_rphy_add.nm, r1__sas_rphy_add.E;
position r1__sas_rphy_add.p2;
@@
+ sas_rphy_remove(nm);
  return@p2 E;

@r1__sfw_load_test exists@
expression ret, nm;
expression E != {0};
statement S;
position p1, p2;
@@
 ret = sfw_load_test(nm);
 if (\(ret < 0\|ret != 0\)) S
  ... when != sfw_destroy_test_instance(nm)
 if@p1 (...) {
   ... when != sfw_destroy_test_instance(nm)
       when forall
   return@p2 E;
  }

@depends on r1__sfw_load_test@
expression r1__sfw_load_test.nm, r1__sfw_load_test.E;
position r1__sfw_load_test.p2;
@@
+ sfw_destroy_test_instance(nm);
  return@p2 E;

@r1__ath9k_hw_init exists@
expression ret, nm;
expression E != {0};
statement S;
position p1, p2;
@@
 ret = ath9k_hw_init(nm);
 if (\(ret < 0\|ret != 0\)) S
  ... when != ath9k_hw_deinit(nm)
 if@p1 (...) {
   ... when != ath9k_hw_deinit(nm)
       when forall
   return@p2 E;
  }

@depends on r1__ath9k_hw_init@
expression r1__ath9k_hw_init.nm, r1__ath9k_hw_init.E;
position r1__ath9k_hw_init.p2;
@@
+ ath9k_hw_deinit(nm);
  return@p2 E;

@r1__acpi_bus_register_driver exists@
expression ret, nm;
expression E != {0};
statement S;
position p1, p2;
@@
 ret = acpi_bus_register_driver(nm);
 if (\(ret < 0\|ret != 0\)) S
  ... when != acpi_bus_unregister_driver(nm)
 if@p1 (...) {
   ... when != acpi_bus_unregister_driver(nm)
       when forall
   return@p2 E;
  }

@depends on r1__acpi_bus_register_driver@
expression r1__acpi_bus_register_driver.nm, r1__acpi_bus_register_driver.E;
position r1__acpi_bus_register_driver.p2;
@@
+ acpi_bus_unregister_driver(nm);
  return@p2 E;

@r1__target_fabric_configfs_register exists@
expression ret, nm;
expression E != {0};
statement S;
position p1, p2;
@@
 ret = target_fabric_configfs_register(nm);
 if (\(ret < 0\|ret != 0\)) S
  ... when != target_fabric_configfs_deregister(nm)
 if@p1 (...) {
   ... when != target_fabric_configfs_deregister(nm)
       when forall
   return@p2 E;
  }

@depends on r1__target_fabric_configfs_register@
expression r1__target_fabric_configfs_register.nm, r1__target_fabric_configfs_register.E;
position r1__target_fabric_configfs_register.p2;
@@
+ target_fabric_configfs_deregister(nm);
  return@p2 E;

@r1__ecard_request_resources exists@
expression ret, nm;
expression E != {0};
statement S;
position p1, p2;
@@
 ret = ecard_request_resources(nm);
 if (\(ret < 0\|ret != 0\)) S
  ... when != ecard_release_resources(nm)
 if@p1 (...) {
   ... when != ecard_release_resources(nm)
       when forall
   return@p2 E;
  }

@depends on r1__ecard_request_resources@
expression r1__ecard_request_resources.nm, r1__ecard_request_resources.E;
position r1__ecard_request_resources.p2;
@@
+ ecard_release_resources(nm);
  return@p2 E;

@r1__ibmebus_register_driver exists@
expression ret, nm;
expression E != {0};
statement S;
position p1, p2;
@@
 ret = ibmebus_register_driver(nm);
 if (\(ret < 0\|ret != 0\)) S
  ... when != ibmebus_unregister_driver(nm)
 if@p1 (...) {
   ... when != ibmebus_unregister_driver(nm)
       when forall
   return@p2 E;
  }

@depends on r1__ibmebus_register_driver@
expression r1__ibmebus_register_driver.nm, r1__ibmebus_register_driver.E;
position r1__ibmebus_register_driver.p2;
@@
+ ibmebus_unregister_driver(nm);
  return@p2 E;

@r1__irda_register_dongle exists@
expression ret, nm;
expression E != {0};
statement S;
position p1, p2;
@@
 ret = irda_register_dongle(nm);
 if (\(ret < 0\|ret != 0\)) S
  ... when != irda_unregister_dongle(nm)
 if@p1 (...) {
   ... when != irda_unregister_dongle(nm)
       when forall
   return@p2 E;
  }

@depends on r1__irda_register_dongle@
expression r1__irda_register_dongle.nm, r1__irda_register_dongle.E;
position r1__irda_register_dongle.p2;
@@
+ irda_unregister_dongle(nm);
  return@p2 E;

@r1__vpfe_register_ccdc_device exists@
expression ret, nm;
expression E != {0};
statement S;
position p1, p2;
@@
 ret = vpfe_register_ccdc_device(nm);
 if (\(ret < 0\|ret != 0\)) S
  ... when != vpfe_unregister_ccdc_device(nm)
 if@p1 (...) {
   ... when != vpfe_unregister_ccdc_device(nm)
       when forall
   return@p2 E;
  }

@depends on r1__vpfe_register_ccdc_device@
expression r1__vpfe_register_ccdc_device.nm, r1__vpfe_register_ccdc_device.E;
position r1__vpfe_register_ccdc_device.p2;
@@
+ vpfe_unregister_ccdc_device(nm);
  return@p2 E;

@r1__dm_exception_store_type_register exists@
expression ret, nm;
expression E != {0};
statement S;
position p1, p2;
@@
 ret = dm_exception_store_type_register(nm);
 if (\(ret < 0\|ret != 0\)) S
  ... when != dm_exception_store_type_unregister(nm)
 if@p1 (...) {
   ... when != dm_exception_store_type_unregister(nm)
       when forall
   return@p2 E;
  }

@depends on r1__dm_exception_store_type_register@
expression r1__dm_exception_store_type_register.nm, r1__dm_exception_store_type_register.E;
position r1__dm_exception_store_type_register.p2;
@@
+ dm_exception_store_type_unregister(nm);
  return@p2 E;

@r1__avc_identify_subunit exists@
expression ret, nm;
expression E != {0};
statement S;
position p1, p2;
@@
 ret = avc_identify_subunit(nm);
 if (\(ret < 0\|ret != 0\)) S
  ... when != fdtv_unregister_rc(nm)
 if@p1 (...) {
   ... when != fdtv_unregister_rc(nm)
       when forall
   return@p2 E;
  }

@depends on r1__avc_identify_subunit@
expression r1__avc_identify_subunit.nm, r1__avc_identify_subunit.E;
position r1__avc_identify_subunit.p2;
@@
+ fdtv_unregister_rc(nm);
  return@p2 E;

@r1__driver_register exists@
expression ret, nm;
expression E != {0};
statement S;
position p1, p2;
@@
 ret = driver_register(nm);
 if (\(ret < 0\|ret != 0\)) S
  ... when != driver_unregister(nm)
 if@p1 (...) {
   ... when != driver_unregister(nm)
       when forall
   return@p2 E;
  }

@depends on r1__driver_register@
expression r1__driver_register.nm, r1__driver_register.E;
position r1__driver_register.p2;
@@
+ driver_unregister(nm);
  return@p2 E;

@r1__trylock_cch_handle exists@
expression ret, nm;
expression E != {0};
statement S;
position p1, p2;
@@
 ret = trylock_cch_handle(nm);
 if (\(ret < 0\|ret != 0\)) S
  ... when != unlock_cch_handle(nm)
 if@p1 (...) {
   ... when != unlock_cch_handle(nm)
       when forall
   return@p2 E;
  }

@depends on r1__trylock_cch_handle@
expression r1__trylock_cch_handle.nm, r1__trylock_cch_handle.E;
position r1__trylock_cch_handle.p2;
@@
+ unlock_cch_handle(nm);
  return@p2 E;

@r1__class_register exists@
expression ret, nm;
expression E != {0};
statement S;
position p1, p2;
@@
 ret = class_register(nm);
 if (\(ret < 0\|ret != 0\)) S
  ... when != class_unregister(nm)
 if@p1 (...) {
   ... when != class_unregister(nm)
       when forall
   return@p2 E;
  }

@depends on r1__class_register@
expression r1__class_register.nm, r1__class_register.E;
position r1__class_register.p2;
@@
+ class_unregister(nm);
  return@p2 E;

@r1__sclp_add_request exists@
expression ret, nm;
expression E != {0};
statement S;
position p1, p2;
@@
 ret = sclp_add_request(nm);
 if (\(ret < 0\|ret != 0\)) S
  ... when != cpi_free_req(nm)
 if@p1 (...) {
   ... when != cpi_free_req(nm)
       when forall
   return@p2 E;
  }

@depends on r1__sclp_add_request@
expression r1__sclp_add_request.nm, r1__sclp_add_request.E;
position r1__sclp_add_request.p2;
@@
+ cpi_free_req(nm);
  return@p2 E;

@r1__soc_camera_host_register exists@
expression ret, nm;
expression E != {0};
statement S;
position p1, p2;
@@
 ret = soc_camera_host_register(nm);
 if (\(ret < 0\|ret != 0\)) S
  ... when != soc_camera_host_unregister(nm)
 if@p1 (...) {
   ... when != soc_camera_host_unregister(nm)
       when forall
   return@p2 E;
  }

@depends on r1__soc_camera_host_register@
expression r1__soc_camera_host_register.nm, r1__soc_camera_host_register.E;
position r1__soc_camera_host_register.p2;
@@
+ soc_camera_host_unregister(nm);
  return@p2 E;

@r1__da9052_irq_init exists@
expression ret, nm;
expression E != {0};
statement S;
position p1, p2;
@@
 ret = da9052_irq_init(nm);
 if (\(ret < 0\|ret != 0\)) S
  ... when != da9052_irq_exit(nm)
 if@p1 (...) {
   ... when != da9052_irq_exit(nm)
       when forall
   return@p2 E;
  }

@depends on r1__da9052_irq_init@
expression r1__da9052_irq_init.nm, r1__da9052_irq_init.E;
position r1__da9052_irq_init.p2;
@@
+ da9052_irq_exit(nm);
  return@p2 E;

@r1__media_device_register exists@
expression ret, nm;
expression E != {0};
statement S;
position p1, p2;
@@
 ret = media_device_register(nm);
 if (\(ret < 0\|ret != 0\)) S
  ... when != media_device_unregister(nm)
 if@p1 (...) {
   ... when != media_device_unregister(nm)
       when forall
   return@p2 E;
  }

@depends on r1__media_device_register@
expression r1__media_device_register.nm, r1__media_device_register.E;
position r1__media_device_register.p2;
@@
+ media_device_unregister(nm);
  return@p2 E;

@r1__bcma_driver_register exists@
expression ret, nm;
expression E != {0};
statement S;
position p1, p2;
@@
 ret = bcma_driver_register(nm);
 if (\(ret < 0\|ret != 0\)) S
  ... when != bcma_driver_unregister(nm)
 if@p1 (...) {
   ... when != bcma_driver_unregister(nm)
       when forall
   return@p2 E;
  }

@depends on r1__bcma_driver_register@
expression r1__bcma_driver_register.nm, r1__bcma_driver_register.E;
position r1__bcma_driver_register.p2;
@@
+ bcma_driver_unregister(nm);
  return@p2 E;

@r1__ep93xx_ide_acquire_gpio exists@
expression ret, nm;
expression E != {0};
statement S;
position p1, p2;
@@
 ret = ep93xx_ide_acquire_gpio(nm);
 if (\(ret < 0\|ret != 0\)) S
  ... when != ep93xx_ide_release_gpio(nm)
 if@p1 (...) {
   ... when != ep93xx_ide_release_gpio(nm)
       when forall
   return@p2 E;
  }

@depends on r1__ep93xx_ide_acquire_gpio@
expression r1__ep93xx_ide_acquire_gpio.nm, r1__ep93xx_ide_acquire_gpio.E;
position r1__ep93xx_ide_acquire_gpio.p2;
@@
+ ep93xx_ide_release_gpio(nm);
  return@p2 E;

@r1__capi20_register exists@
expression ret, nm;
expression E != {0};
statement S;
position p1, p2;
@@
 ret = capi20_register(nm);
 if (\(ret < 0\|ret != 0\)) S
  ... when != capi20_release(nm)
 if@p1 (...) {
   ... when != capi20_release(nm)
       when forall
   return@p2 E;
  }

@depends on r1__capi20_register@
expression r1__capi20_register.nm, r1__capi20_register.E;
position r1__capi20_register.p2;
@@
+ capi20_release(nm);
  return@p2 E;

@r1__mutex_lock_interruptible exists@
expression ret, nm;
expression E != {0};
statement S;
position p1, p2;
@@
 ret = mutex_lock_interruptible(nm);
 if (\(ret < 0\|ret != 0\)) S
  ... when != mutex_unlock(nm)
 if@p1 (...) {
   ... when != mutex_unlock(nm)
       when forall
   return@p2 E;
  }

@depends on r1__mutex_lock_interruptible@
expression r1__mutex_lock_interruptible.nm, r1__mutex_lock_interruptible.E;
position r1__mutex_lock_interruptible.p2;
@@
+ mutex_unlock(nm);
  return@p2 E;

@r1__lu_context_key_register exists@
expression ret, nm;
expression E != {0};
statement S;
position p1, p2;
@@
 ret = lu_context_key_register(nm);
 if (\(ret < 0\|ret != 0\)) S
  ... when != lu_context_key_degister(nm)
 if@p1 (...) {
   ... when != lu_context_key_degister(nm)
       when forall
   return@p2 E;
  }

@depends on r1__lu_context_key_register@
expression r1__lu_context_key_register.nm, r1__lu_context_key_register.E;
position r1__lu_context_key_register.p2;
@@
+ lu_context_key_degister(nm);
  return@p2 E;

@r1__crypto_register_shash exists@
expression ret, nm;
expression E != {0};
statement S;
position p1, p2;
@@
 ret = crypto_register_shash(nm);
 if (\(ret < 0\|ret != 0\)) S
  ... when != crypto_unregister_shash(nm)
 if@p1 (...) {
   ... when != crypto_unregister_shash(nm)
       when forall
   return@p2 E;
  }

@depends on r1__crypto_register_shash@
expression r1__crypto_register_shash.nm, r1__crypto_register_shash.E;
position r1__crypto_register_shash.p2;
@@
+ crypto_unregister_shash(nm);
  return@p2 E;

@r1__register_pm_notifier exists@
expression ret, nm;
expression E != {0};
statement S;
position p1, p2;
@@
 ret = register_pm_notifier(nm);
 if (\(ret < 0\|ret != 0\)) S
  ... when != unregister_pm_notifier(nm)
 if@p1 (...) {
   ... when != unregister_pm_notifier(nm)
       when forall
   return@p2 E;
  }

@depends on r1__register_pm_notifier@
expression r1__register_pm_notifier.nm, r1__register_pm_notifier.E;
position r1__register_pm_notifier.p2;
@@
+ unregister_pm_notifier(nm);
  return@p2 E;

@r1__mxr_power_get exists@
expression ret, nm;
expression E != {0};
statement S;
position p1, p2;
@@
 ret = mxr_power_get(nm);
 if (\(ret < 0\|ret != 0\)) S
  ... when != mxr_power_put(nm)
 if@p1 (...) {
   ... when != mxr_power_put(nm)
       when forall
   return@p2 E;
  }

@depends on r1__mxr_power_get@
expression r1__mxr_power_get.nm, r1__mxr_power_get.E;
position r1__mxr_power_get.p2;
@@
+ mxr_power_put(nm);
  return@p2 E;

@r1__v4l2_device_register_subdev_nodes exists@
expression ret, nm;
expression E != {0};
statement S;
position p1, p2;
@@
 ret = v4l2_device_register_subdev_nodes(nm);
 if (\(ret < 0\|ret != 0\)) S
  ... when != v4l2_device_unregister(nm)
 if@p1 (...) {
   ... when != v4l2_device_unregister(nm)
       when forall
   return@p2 E;
  }

@depends on r1__v4l2_device_register_subdev_nodes@
expression r1__v4l2_device_register_subdev_nodes.nm, r1__v4l2_device_register_subdev_nodes.E;
position r1__v4l2_device_register_subdev_nodes.p2;
@@
+ v4l2_device_unregister(nm);
  return@p2 E;

@r1__i2c_add_driver exists@
expression ret, nm;
expression E != {0};
statement S;
position p1, p2;
@@
 ret = i2c_add_driver(nm);
 if (\(ret < 0\|ret != 0\)) S
  ... when != i2c_del_driver(nm)
 if@p1 (...) {
   ... when != i2c_del_driver(nm)
       when forall
   return@p2 E;
  }

@depends on r1__i2c_add_driver@
expression r1__i2c_add_driver.nm, r1__i2c_add_driver.E;
position r1__i2c_add_driver.p2;
@@
+ i2c_del_driver(nm);
  return@p2 E;

@r1__usb_register exists@
expression ret, nm;
expression E != {0};
statement S;
position p1, p2;
@@
 ret = usb_register(nm);
 if (\(ret < 0\|ret != 0\)) S
  ... when != usb_deregister(nm)
 if@p1 (...) {
   ... when != usb_deregister(nm)
       when forall
   return@p2 E;
  }

@depends on r1__usb_register@
expression r1__usb_register.nm, r1__usb_register.E;
position r1__usb_register.p2;
@@
+ usb_deregister(nm);
  return@p2 E;

@r1__register_inetaddr_notifier exists@
expression ret, nm;
expression E != {0};
statement S;
position p1, p2;
@@
 ret = register_inetaddr_notifier(nm);
 if (\(ret < 0\|ret != 0\)) S
  ... when != unregister_inetaddr_notifier(nm)
 if@p1 (...) {
   ... when != unregister_inetaddr_notifier(nm)
       when forall
   return@p2 E;
  }

@depends on r1__register_inetaddr_notifier@
expression r1__register_inetaddr_notifier.nm, r1__register_inetaddr_notifier.E;
position r1__register_inetaddr_notifier.p2;
@@
+ unregister_inetaddr_notifier(nm);
  return@p2 E;

@r1__e1000e_setup_tx_resources exists@
expression ret, nm;
expression E != {0};
statement S;
position p1, p2;
@@
 ret = e1000e_setup_tx_resources(nm);
 if (\(ret < 0\|ret != 0\)) S
  ... when != e1000e_free_tx_resources(nm)
 if@p1 (...) {
   ... when != e1000e_free_tx_resources(nm)
       when forall
   return@p2 E;
  }

@depends on r1__e1000e_setup_tx_resources@
expression r1__e1000e_setup_tx_resources.nm, r1__e1000e_setup_tx_resources.E;
position r1__e1000e_setup_tx_resources.p2;
@@
+ e1000e_free_tx_resources(nm);
  return@p2 E;

@r1__mdc_enter_request exists@
expression ret, nm;
expression E != {0};
statement S;
position p1, p2;
@@
 ret = mdc_enter_request(nm);
 if (\(ret < 0\|ret != 0\)) S
  ... when != mdc_exit_request(nm)
 if@p1 (...) {
   ... when != mdc_exit_request(nm)
       when forall
   return@p2 E;
  }

@depends on r1__mdc_enter_request@
expression r1__mdc_enter_request.nm, r1__mdc_enter_request.E;
position r1__mdc_enter_request.p2;
@@
+ mdc_exit_request(nm);
  return@p2 E;

@r1__max77693_irq_init exists@
expression ret, nm;
expression E != {0};
statement S;
position p1, p2;
@@
 ret = max77693_irq_init(nm);
 if (\(ret < 0\|ret != 0\)) S
  ... when != max77693_irq_exit(nm)
 if@p1 (...) {
   ... when != max77693_irq_exit(nm)
       when forall
   return@p2 E;
  }

@depends on r1__max77693_irq_init@
expression r1__max77693_irq_init.nm, r1__max77693_irq_init.E;
position r1__max77693_irq_init.p2;
@@
+ max77693_irq_exit(nm);
  return@p2 E;

@r1__pci_register_driver exists@
expression ret, nm;
expression E != {0};
statement S;
position p1, p2;
@@
 ret = pci_register_driver(nm);
 if (\(ret < 0\|ret != 0\)) S
  ... when != pci_unregister_driver(nm)
 if@p1 (...) {
   ... when != pci_unregister_driver(nm)
       when forall
   return@p2 E;
  }

@depends on r1__pci_register_driver@
expression r1__pci_register_driver.nm, r1__pci_register_driver.E;
position r1__pci_register_driver.p2;
@@
+ pci_unregister_driver(nm);
  return@p2 E;

@r1__register_pernet_subsys exists@
expression ret, nm;
expression E != {0};
statement S;
position p1, p2;
@@
 ret = register_pernet_subsys(nm);
 if (\(ret < 0\|ret != 0\)) S
  ... when != unregister_pernet_subsys(nm)
 if@p1 (...) {
   ... when != unregister_pernet_subsys(nm)
       when forall
   return@p2 E;
  }

@depends on r1__register_pernet_subsys@
expression r1__register_pernet_subsys.nm, r1__register_pernet_subsys.E;
position r1__register_pernet_subsys.p2;
@@
+ unregister_pernet_subsys(nm);
  return@p2 E;

@r1__iio_trigger_register exists@
expression ret, nm;
expression E != {0};
statement S;
position p1, p2;
@@
 ret = iio_trigger_register(nm);
 if (\(ret < 0\|ret != 0\)) S
  ... when != iio_trigger_unregister(nm)
 if@p1 (...) {
   ... when != iio_trigger_unregister(nm)
       when forall
   return@p2 E;
  }

@depends on r1__iio_trigger_register@
expression r1__iio_trigger_register.nm, r1__iio_trigger_register.E;
position r1__iio_trigger_register.p2;
@@
+ iio_trigger_unregister(nm);
  return@p2 E;

@r1__fsl_spi_cpm_init exists@
expression ret, nm;
expression E != {0};
statement S;
position p1, p2;
@@
 ret = fsl_spi_cpm_init(nm);
 if (\(ret < 0\|ret != 0\)) S
  ... when != fsl_spi_cpm_free(nm)
 if@p1 (...) {
   ... when != fsl_spi_cpm_free(nm)
       when forall
   return@p2 E;
  }

@depends on r1__fsl_spi_cpm_init@
expression r1__fsl_spi_cpm_init.nm, r1__fsl_spi_cpm_init.E;
position r1__fsl_spi_cpm_init.p2;
@@
+ fsl_spi_cpm_free(nm);
  return@p2 E;

@r1__lu_kmem_init exists@
expression ret, nm;
expression E != {0};
statement S;
position p1, p2;
@@
 ret = lu_kmem_init(nm);
 if (\(ret < 0\|ret != 0\)) S
  ... when != lu_kmem_fini(nm)
 if@p1 (...) {
   ... when != lu_kmem_fini(nm)
       when forall
   return@p2 E;
  }

@depends on r1__lu_kmem_init@
expression r1__lu_kmem_init.nm, r1__lu_kmem_init.E;
position r1__lu_kmem_init.p2;
@@
+ lu_kmem_fini(nm);
  return@p2 E;

@r1__dasd_alias_make_device_known_to_lcu exists@
expression ret, nm;
expression E != {0};
statement S;
position p1, p2;
@@
 ret = dasd_alias_make_device_known_to_lcu(nm);
 if (\(ret < 0\|ret != 0\)) S
  ... when != dasd_alias_disconnect_device_from_lcu(nm)
 if@p1 (...) {
   ... when != dasd_alias_disconnect_device_from_lcu(nm)
       when forall
   return@p2 E;
  }

@depends on r1__dasd_alias_make_device_known_to_lcu@
expression r1__dasd_alias_make_device_known_to_lcu.nm, r1__dasd_alias_make_device_known_to_lcu.E;
position r1__dasd_alias_make_device_known_to_lcu.p2;
@@
+ dasd_alias_disconnect_device_from_lcu(nm);
  return@p2 E;

@r1__pci_enable_msi exists@
expression ret, nm;
expression E != {0};
statement S;
position p1, p2;
@@
 ret = pci_enable_msi(nm);
 if (\(ret < 0\|ret != 0\)) S
  ... when != pci_disable_msi(nm)
 if@p1 (...) {
   ... when != pci_disable_msi(nm)
       when forall
   return@p2 E;
  }

@depends on r1__pci_enable_msi@
expression r1__pci_enable_msi.nm, r1__pci_enable_msi.E;
position r1__pci_enable_msi.p2;
@@
+ pci_disable_msi(nm);
  return@p2 E;

@r1__get_pinctrl_dev_from_of_node exists@
expression ret, nm;
expression E != {0};
statement S;
position p1, p2;
@@
 ret = get_pinctrl_dev_from_of_node(nm);
 if (\(ret < 0\|ret != 0\)) S
  ... when != of_node_put(nm)
 if@p1 (...) {
   ... when != of_node_put(nm)
       when forall
   return@p2 E;
  }

@depends on r1__get_pinctrl_dev_from_of_node@
expression r1__get_pinctrl_dev_from_of_node.nm, r1__get_pinctrl_dev_from_of_node.E;
position r1__get_pinctrl_dev_from_of_node.p2;
@@
+ of_node_put(nm);
  return@p2 E;

@r1__btree_init32 exists@
expression ret, nm;
expression E != {0};
statement S;
position p1, p2;
@@
 ret = btree_init32(nm);
 if (\(ret < 0\|ret != 0\)) S
  ... when != btree_destroy32(nm)
 if@p1 (...) {
   ... when != btree_destroy32(nm)
       when forall
   return@p2 E;
  }

@depends on r1__btree_init32@
expression r1__btree_init32.nm, r1__btree_init32.E;
position r1__btree_init32.p2;
@@
+ btree_destroy32(nm);
  return@p2 E;

@r1__usb_autopm_get_interface_async exists@
expression ret, nm;
expression E != {0};
statement S;
position p1, p2;
@@
 ret = usb_autopm_get_interface_async(nm);
 if (\(ret < 0\|ret != 0\)) S
  ... when != usb_autopm_put_interface_no_suspend(nm)
 if@p1 (...) {
   ... when != usb_autopm_put_interface_no_suspend(nm)
       when != usb_autopm_put_interface_async(nm)
       when forall
   return@p2 E;
  }

@depends on r1__usb_autopm_get_interface_async@
expression r1__usb_autopm_get_interface_async.nm, r1__usb_autopm_get_interface_async.E;
position r1__usb_autopm_get_interface_async.p2;
@@
+ usb_autopm_put_interface_no_suspend(nm);
  return@p2 E;

@r1__w1_register_family exists@
expression ret, nm;
expression E != {0};
statement S;
position p1, p2;
@@
 ret = w1_register_family(nm);
 if (\(ret < 0\|ret != 0\)) S
  ... when != w1_unregister_family(nm)
 if@p1 (...) {
   ... when != w1_unregister_family(nm)
       when forall
   return@p2 E;
  }

@depends on r1__w1_register_family@
expression r1__w1_register_family.nm, r1__w1_register_family.E;
position r1__w1_register_family.p2;
@@
+ w1_unregister_family(nm);
  return@p2 E;

@r1__down_interruptible exists@
expression ret, nm;
expression E != {0};
statement S;
position p1, p2;
@@
 ret = down_interruptible(nm);
 if (\(ret < 0\|ret != 0\)) S
  ... when != up(nm)
 if@p1 (...) {
   ... when != up(nm)
       when forall
   return@p2 E;
  }

@depends on r1__down_interruptible@
expression r1__down_interruptible.nm, r1__down_interruptible.E;
position r1__down_interruptible.p2;
@@
+ up(nm);
  return@p2 E;

@r1__c67x00_sched_start_scheduler exists@
expression ret, nm;
expression E != {0};
statement S;
position p1, p2;
@@
 ret = c67x00_sched_start_scheduler(nm);
 if (\(ret < 0\|ret != 0\)) S
  ... when != c67x00_sched_stop_scheduler(nm)
 if@p1 (...) {
   ... when != c67x00_sched_stop_scheduler(nm)
       when forall
   return@p2 E;
  }

@depends on r1__c67x00_sched_start_scheduler@
expression r1__c67x00_sched_start_scheduler.nm, r1__c67x00_sched_start_scheduler.E;
position r1__c67x00_sched_start_scheduler.p2;
@@
+ c67x00_sched_stop_scheduler(nm);
  return@p2 E;

@r1__claim_fiq exists@
expression ret, nm;
expression E != {0};
statement S;
position p1, p2;
@@
 ret = claim_fiq(nm);
 if (\(ret < 0\|ret != 0\)) S
  ... when != release_fiq(nm)
 if@p1 (...) {
   ... when != release_fiq(nm)
       when forall
   return@p2 E;
  }

@depends on r1__claim_fiq@
expression r1__claim_fiq.nm, r1__claim_fiq.E;
position r1__claim_fiq.p2;
@@
+ release_fiq(nm);
  return@p2 E;

@r1__whc_init exists@
expression ret, nm;
expression E != {0};
statement S;
position p1, p2;
@@
 ret = whc_init(nm);
 if (\(ret < 0\|ret != 0\)) S
  ... when != whc_clean_up(nm)
 if@p1 (...) {
   ... when != whc_clean_up(nm)
       when forall
   return@p2 E;
  }

@depends on r1__whc_init@
expression r1__whc_init.nm, r1__whc_init.E;
position r1__whc_init.p2;
@@
+ whc_clean_up(nm);
  return@p2 E;

@r1__hpet_register_irq_handler exists@
expression ret, nm;
expression E != {0};
statement S;
position p1, p2;
@@
 ret = hpet_register_irq_handler(nm);
 if (\(ret < 0\|ret != 0\)) S
  ... when != hpet_unregister_irq_handler(nm)
 if@p1 (...) {
   ... when != hpet_unregister_irq_handler(nm)
       when forall
   return@p2 E;
  }

@depends on r1__hpet_register_irq_handler@
expression r1__hpet_register_irq_handler.nm, r1__hpet_register_irq_handler.E;
position r1__hpet_register_irq_handler.p2;
@@
+ hpet_unregister_irq_handler(nm);
  return@p2 E;

@r1__register_netdevice_notifier exists@
expression ret, nm;
expression E != {0};
statement S;
position p1, p2;
@@
 ret = register_netdevice_notifier(nm);
 if (\(ret < 0\|ret != 0\)) S
  ... when != unregister_netdevice_notifier(nm)
 if@p1 (...) {
   ... when != unregister_netdevice_notifier(nm)
       when forall
   return@p2 E;
  }

@depends on r1__register_netdevice_notifier@
expression r1__register_netdevice_notifier.nm, r1__register_netdevice_notifier.E;
position r1__register_netdevice_notifier.p2;
@@
+ unregister_netdevice_notifier(nm);
  return@p2 E;

@r1__ib_register_client exists@
expression ret, nm;
expression E != {0};
statement S;
position p1, p2;
@@
 ret = ib_register_client(nm);
 if (\(ret < 0\|ret != 0\)) S
  ... when != ib_unregister_client(nm)
 if@p1 (...) {
   ... when != ib_unregister_client(nm)
       when forall
   return@p2 E;
  }

@depends on r1__ib_register_client@
expression r1__ib_register_client.nm, r1__ib_register_client.E;
position r1__ib_register_client.p2;
@@
+ ib_unregister_client(nm);
  return@p2 E;

@r1__cpci_hp_register_controller exists@
expression ret, nm;
expression E != {0};
statement S;
position p1, p2;
@@
 ret = cpci_hp_register_controller(nm);
 if (\(ret < 0\|ret != 0\)) S
  ... when != cpci_hp_unregister_controller(nm)
 if@p1 (...) {
   ... when != cpci_hp_unregister_controller(nm)
       when forall
   return@p2 E;
  }

@depends on r1__cpci_hp_register_controller@
expression r1__cpci_hp_register_controller.nm, r1__cpci_hp_register_controller.E;
position r1__cpci_hp_register_controller.p2;
@@
+ cpci_hp_unregister_controller(nm);
  return@p2 E;

@r1__cpuidle_register_driver exists@
expression ret, nm;
expression E != {0};
statement S;
position p1, p2;
@@
 ret = cpuidle_register_driver(nm);
 if (\(ret < 0\|ret != 0\)) S
  ... when != cpuidle_unregister_driver(nm)
 if@p1 (...) {
   ... when != cpuidle_unregister_driver(nm)
       when forall
   return@p2 E;
  }

@depends on r1__cpuidle_register_driver@
expression r1__cpuidle_register_driver.nm, r1__cpuidle_register_driver.E;
position r1__cpuidle_register_driver.p2;
@@
+ cpuidle_unregister_driver(nm);
  return@p2 E;

@r1__sdhci_add_host exists@
expression ret, nm;
expression E != {0};
statement S;
position p1, p2;
@@
 ret = sdhci_add_host(nm);
 if (\(ret < 0\|ret != 0\)) S
  ... when != sdhci_free_host(nm)
 if@p1 (...) {
   ... when != sdhci_free_host(nm)
       when forall
   return@p2 E;
  }

@depends on r1__sdhci_add_host@
expression r1__sdhci_add_host.nm, r1__sdhci_add_host.E;
position r1__sdhci_add_host.p2;
@@
+ sdhci_free_host(nm);
  return@p2 E;

@r1__usb_ep_enable exists@
expression ret, nm;
expression E != {0};
statement S;
position p1, p2;
@@
 ret = usb_ep_enable(nm);
 if (\(ret < 0\|ret != 0\)) S
  ... when != usb_ep_disable(nm)
 if@p1 (...) {
   ... when != usb_ep_disable(nm)
       when forall
   return@p2 E;
  }

@depends on r1__usb_ep_enable@
expression r1__usb_ep_enable.nm, r1__usb_ep_enable.E;
position r1__usb_ep_enable.p2;
@@
+ usb_ep_disable(nm);
  return@p2 E;

@r1__lpfc_alloc_sysfs_attr exists@
expression ret, nm;
expression E != {0};
statement S;
position p1, p2;
@@
 ret = lpfc_alloc_sysfs_attr(nm);
 if (\(ret < 0\|ret != 0\)) S
  ... when != lpfc_free_sysfs_attr(nm)
 if@p1 (...) {
   ... when != lpfc_free_sysfs_attr(nm)
       when forall
   return@p2 E;
  }

@depends on r1__lpfc_alloc_sysfs_attr@
expression r1__lpfc_alloc_sysfs_attr.nm, r1__lpfc_alloc_sysfs_attr.E;
position r1__lpfc_alloc_sysfs_attr.p2;
@@
+ lpfc_free_sysfs_attr(nm);
  return@p2 E;

@r1__flexcop_i2c_init exists@
expression ret, nm;
expression E != {0};
statement S;
position p1, p2;
@@
 ret = flexcop_i2c_init(nm);
 if (\(ret < 0\|ret != 0\)) S
  ... when != flexcop_device_exit(nm)
 if@p1 (...) {
   ... when != flexcop_device_exit(nm)
       when forall
   return@p2 E;
  }

@depends on r1__flexcop_i2c_init@
expression r1__flexcop_i2c_init.nm, r1__flexcop_i2c_init.E;
position r1__flexcop_i2c_init.p2;
@@
+ flexcop_device_exit(nm);
  return@p2 E;

@r1__watchdog_dev_register exists@
expression ret, nm;
expression E != {0};
statement S;
position p1, p2;
@@
 ret = watchdog_dev_register(nm);
 if (\(ret < 0\|ret != 0\)) S
  ... when != watchdog_dev_unregister(nm)
 if@p1 (...) {
   ... when != watchdog_dev_unregister(nm)
       when forall
   return@p2 E;
  }

@depends on r1__watchdog_dev_register@
expression r1__watchdog_dev_register.nm, r1__watchdog_dev_register.E;
position r1__watchdog_dev_register.p2;
@@
+ watchdog_dev_unregister(nm);
  return@p2 E;

@r1__omap3isp_video_queue_streamon exists@
expression ret, nm;
expression E != {0};
statement S;
position p1, p2;
@@
 ret = omap3isp_video_queue_streamon(nm);
 if (\(ret < 0\|ret != 0\)) S
  ... when != omap3isp_video_queue_streamoff(nm)
 if@p1 (...) {
   ... when != omap3isp_video_queue_streamoff(nm)
       when forall
   return@p2 E;
  }

@depends on r1__omap3isp_video_queue_streamon@
expression r1__omap3isp_video_queue_streamon.nm, r1__omap3isp_video_queue_streamon.E;
position r1__omap3isp_video_queue_streamon.p2;
@@
+ omap3isp_video_queue_streamoff(nm);
  return@p2 E;

@r1__create_stack exists@
expression ret, nm;
expression E != {0};
statement S;
position p1, p2;
@@
 ret = create_stack(nm);
 if (\(ret < 0\|ret != 0\)) S
  ... when != delete_stack(nm)
 if@p1 (...) {
   ... when != delete_stack(nm)
       when forall
   return@p2 E;
  }

@depends on r1__create_stack@
expression r1__create_stack.nm, r1__create_stack.E;
position r1__create_stack.p2;
@@
+ delete_stack(nm);
  return@p2 E;

@r1__open_candev exists@
expression ret, nm;
expression E != {0};
statement S;
position p1, p2;
@@
 ret = open_candev(nm);
 if (\(ret < 0\|ret != 0\)) S
  ... when != close_candev(nm)
 if@p1 (...) {
   ... when != close_candev(nm)
       when forall
   return@p2 E;
  }

@depends on r1__open_candev@
expression r1__open_candev.nm, r1__open_candev.E;
position r1__open_candev.p2;
@@
+ close_candev(nm);
  return@p2 E;

@r1__il_init_channel_map exists@
expression ret, nm;
expression E != {0};
statement S;
position p1, p2;
@@
 ret = il_init_channel_map(nm);
 if (\(ret < 0\|ret != 0\)) S
  ... when != il_free_channel_map(nm)
 if@p1 (...) {
   ... when != il_free_channel_map(nm)
       when forall
   return@p2 E;
  }

@depends on r1__il_init_channel_map@
expression r1__il_init_channel_map.nm, r1__il_init_channel_map.E;
position r1__il_init_channel_map.p2;
@@
+ il_free_channel_map(nm);
  return@p2 E;

@r1__lp55xx_init_device exists@
expression ret, nm;
expression E != {0};
statement S;
position p1, p2;
@@
 ret = lp55xx_init_device(nm);
 if (\(ret < 0\|ret != 0\)) S
  ... when != lp55xx_deinit_device(nm)
 if@p1 (...) {
   ... when != lp55xx_deinit_device(nm)
       when forall
   return@p2 E;
  }

@depends on r1__lp55xx_init_device@
expression r1__lp55xx_init_device.nm, r1__lp55xx_init_device.E;
position r1__lp55xx_init_device.p2;
@@
+ lp55xx_deinit_device(nm);
  return@p2 E;

@r1__crypto_register_ahash exists@
expression ret, nm;
expression E != {0};
statement S;
position p1, p2;
@@
 ret = crypto_register_ahash(nm);
 if (\(ret < 0\|ret != 0\)) S
  ... when != crypto_unregister_ahash(nm)
 if@p1 (...) {
   ... when != crypto_unregister_ahash(nm)
       when forall
   return@p2 E;
  }

@depends on r1__crypto_register_ahash@
expression r1__crypto_register_ahash.nm, r1__crypto_register_ahash.E;
position r1__crypto_register_ahash.p2;
@@
+ crypto_unregister_ahash(nm);
  return@p2 E;

@r1__clk_prepare exists@
expression ret, nm;
expression E != {0};
statement S;
position p1, p2;
@@
 ret = clk_prepare(nm);
 if (\(ret < 0\|ret != 0\)) S
  ... when != clk_unprepare(nm)
 if@p1 (...) {
   ... when != clk_unprepare(nm)
       when forall
   return@p2 E;
  }

@depends on r1__clk_prepare@
expression r1__clk_prepare.nm, r1__clk_prepare.E;
position r1__clk_prepare.p2;
@@
+ clk_unprepare(nm);
  return@p2 E;

@r1__clk_enable exists@
expression ret, nm;
expression E != {0};
statement S;
position p1, p2;
@@
 ret = clk_enable(nm);
 if (\(ret < 0\|ret != 0\)) S
  ... when != clk_disable(nm)
 if@p1 (...) {
   ... when != clk_disable(nm)
       when forall
   return@p2 E;
  }

@depends on r1__clk_enable@
expression r1__clk_enable.nm, r1__clk_enable.E;
position r1__clk_enable.p2;
@@
+ clk_disable(nm);
  return@p2 E;

@r1__scsi_register_driver exists@
expression ret, nm;
expression E != {0};
statement S;
position p1, p2;
@@
 ret = scsi_register_driver(nm);
 if (\(ret < 0\|ret != 0\)) S
  ... when != scsi_unregister_driver(nm)
 if@p1 (...) {
   ... when != scsi_unregister_driver(nm)
       when forall
   return@p2 E;
  }

@depends on r1__scsi_register_driver@
expression r1__scsi_register_driver.nm, r1__scsi_register_driver.E;
position r1__scsi_register_driver.p2;
@@
+ scsi_unregister_driver(nm);
  return@p2 E;

@r1__iommu_calculate_agaw exists@
expression ret, nm;
expression E != {0};
statement S;
position p1, p2;
@@
 ret = iommu_calculate_agaw(nm);
 if (\(ret < 0\|ret != 0\)) S
  ... when != unmap_iommu(nm)
 if@p1 (...) {
   ... when != unmap_iommu(nm)
       when forall
   return@p2 E;
  }

@depends on r1__iommu_calculate_agaw@
expression r1__iommu_calculate_agaw.nm, r1__iommu_calculate_agaw.E;
position r1__iommu_calculate_agaw.p2;
@@
+ unmap_iommu(nm);
  return@p2 E;

@r1__ep93xx_keypad_acquire_gpio exists@
expression ret, nm;
expression E != {0};
statement S;
position p1, p2;
@@
 ret = ep93xx_keypad_acquire_gpio(nm);
 if (\(ret < 0\|ret != 0\)) S
  ... when != ep93xx_keypad_release_gpio(nm)
 if@p1 (...) {
   ... when != ep93xx_keypad_release_gpio(nm)
       when forall
   return@p2 E;
  }

@depends on r1__ep93xx_keypad_acquire_gpio@
expression r1__ep93xx_keypad_acquire_gpio.nm, r1__ep93xx_keypad_acquire_gpio.E;
position r1__ep93xx_keypad_acquire_gpio.p2;
@@
+ ep93xx_keypad_release_gpio(nm);
  return@p2 E;

@r1__radeon_irq_kms_init exists@
expression ret, nm;
expression E != {0};
statement S;
position p1, p2;
@@
 ret = radeon_irq_kms_init(nm);
 if (\(ret < 0\|ret != 0\)) S
  ... when != radeon_irq_kms_fini(nm)
 if@p1 (...) {
   ... when != radeon_irq_kms_fini(nm)
       when forall
   return@p2 E;
  }

@depends on r1__radeon_irq_kms_init@
expression r1__radeon_irq_kms_init.nm, r1__radeon_irq_kms_init.E;
position r1__radeon_irq_kms_init.p2;
@@
+ radeon_irq_kms_fini(nm);
  return@p2 E;

@r1__cpuidle_add_device_sysfs exists@
expression ret, nm;
expression E != {0};
statement S;
position p1, p2;
@@
 ret = cpuidle_add_device_sysfs(nm);
 if (\(ret < 0\|ret != 0\)) S
  ... when != cpuidle_remove_device_sysfs(nm)
 if@p1 (...) {
   ... when != cpuidle_remove_device_sysfs(nm)
       when forall
   return@p2 E;
  }

@depends on r1__cpuidle_add_device_sysfs@
expression r1__cpuidle_add_device_sysfs.nm, r1__cpuidle_add_device_sysfs.E;
position r1__cpuidle_add_device_sysfs.p2;
@@
+ cpuidle_remove_device_sysfs(nm);
  return@p2 E;

@r1__ttm_pool_populate exists@
expression ret, nm;
expression E != {0};
statement S;
position p1, p2;
@@
 ret = ttm_pool_populate(nm);
 if (\(ret < 0\|ret != 0\)) S
  ... when != ttm_pool_unpopulate(nm)
 if@p1 (...) {
   ... when != ttm_pool_unpopulate(nm)
       when forall
   return@p2 E;
  }

@depends on r1__ttm_pool_populate@
expression r1__ttm_pool_populate.nm, r1__ttm_pool_populate.E;
position r1__ttm_pool_populate.p2;
@@
+ ttm_pool_unpopulate(nm);
  return@p2 E;

@r1__rt2x00queue_initialize exists@
expression ret, nm;
expression E != {0};
statement S;
position p1, p2;
@@
 ret = rt2x00queue_initialize(nm);
 if (\(ret < 0\|ret != 0\)) S
  ... when != rt2x00queue_uninitialize(nm)
 if@p1 (...) {
   ... when != rt2x00queue_uninitialize(nm)
       when forall
   return@p2 E;
  }

@depends on r1__rt2x00queue_initialize@
expression r1__rt2x00queue_initialize.nm, r1__rt2x00queue_initialize.E;
position r1__rt2x00queue_initialize.p2;
@@
+ rt2x00queue_uninitialize(nm);
  return@p2 E;

@r1__ps3_ehci_driver_register exists@
expression ret, nm;
expression E != {0};
statement S;
position p1, p2;
@@
 ret = ps3_ehci_driver_register(nm);
 if (\(ret < 0\|ret != 0\)) S
  ... when != ps3_ehci_driver_unregister(nm)
 if@p1 (...) {
   ... when != ps3_ehci_driver_unregister(nm)
       when forall
   return@p2 E;
  }

@depends on r1__ps3_ehci_driver_register@
expression r1__ps3_ehci_driver_register.nm, r1__ps3_ehci_driver_register.E;
position r1__ps3_ehci_driver_register.p2;
@@
+ ps3_ehci_driver_unregister(nm);
  return@p2 E;

@r1__qlcnic_fw_cmd_create_rx_ctx exists@
expression ret, nm;
expression E != {0};
statement S;
position p1, p2;
@@
 ret = qlcnic_fw_cmd_create_rx_ctx(nm);
 if (\(ret < 0\|ret != 0\)) S
  ... when != qlcnic_fw_cmd_del_rx_ctx(nm)
 if@p1 (...) {
   ... when != qlcnic_fw_cmd_del_rx_ctx(nm)
       when forall
   return@p2 E;
  }

@depends on r1__qlcnic_fw_cmd_create_rx_ctx@
expression r1__qlcnic_fw_cmd_create_rx_ctx.nm, r1__qlcnic_fw_cmd_create_rx_ctx.E;
position r1__qlcnic_fw_cmd_create_rx_ctx.p2;
@@
+ qlcnic_fw_cmd_del_rx_ctx(nm);
  return@p2 E;

@r1__mei_cl_enable_device exists@
expression ret, nm;
expression E != {0};
statement S;
position p1, p2;
@@
 ret = mei_cl_enable_device(nm);
 if (\(ret < 0\|ret != 0\)) S
  ... when != mei_cl_disable_device(nm)
 if@p1 (...) {
   ... when != mei_cl_disable_device(nm)
       when forall
   return@p2 E;
  }

@depends on r1__mei_cl_enable_device@
expression r1__mei_cl_enable_device.nm, r1__mei_cl_enable_device.E;
position r1__mei_cl_enable_device.p2;
@@
+ mei_cl_disable_device(nm);
  return@p2 E;

@r1__kgdb_register_io_module exists@
expression ret, nm;
expression E != {0};
statement S;
position p1, p2;
@@
 ret = kgdb_register_io_module(nm);
 if (\(ret < 0\|ret != 0\)) S
  ... when != kgdb_unregister_io_module(nm)
 if@p1 (...) {
   ... when != kgdb_unregister_io_module(nm)
       when forall
   return@p2 E;
  }

@depends on r1__kgdb_register_io_module@
expression r1__kgdb_register_io_module.nm, r1__kgdb_register_io_module.E;
position r1__kgdb_register_io_module.p2;
@@
+ kgdb_unregister_io_module(nm);
  return@p2 E;

@r1__fimc_ctrls_create exists@
expression ret, nm;
expression E != {0};
statement S;
position p1, p2;
@@
 ret = fimc_ctrls_create(nm);
 if (\(ret < 0\|ret != 0\)) S
  ... when != fimc_ctrls_delete(nm)
 if@p1 (...) {
   ... when != fimc_ctrls_delete(nm)
       when forall
   return@p2 E;
  }

@depends on r1__fimc_ctrls_create@
expression r1__fimc_ctrls_create.nm, r1__fimc_ctrls_create.E;
position r1__fimc_ctrls_create.p2;
@@
+ fimc_ctrls_delete(nm);
  return@p2 E;

@r1__i8042_install_filter exists@
expression ret, nm;
expression E != {0};
statement S;
position p1, p2;
@@
 ret = i8042_install_filter(nm);
 if (\(ret < 0\|ret != 0\)) S
  ... when != i8042_remove_filter(nm)
 if@p1 (...) {
   ... when != i8042_remove_filter(nm)
       when forall
   return@p2 E;
  }

@depends on r1__i8042_install_filter@
expression r1__i8042_install_filter.nm, r1__i8042_install_filter.E;
position r1__i8042_install_filter.p2;
@@
+ i8042_remove_filter(nm);
  return@p2 E;

@r1__register_vt_notifier exists@
expression ret, nm;
expression E != {0};
statement S;
position p1, p2;
@@
 ret = register_vt_notifier(nm);
 if (\(ret < 0\|ret != 0\)) S
  ... when != unregister_vt_notifier(nm)
 if@p1 (...) {
   ... when != unregister_vt_notifier(nm)
       when forall
   return@p2 E;
  }

@depends on r1__register_vt_notifier@
expression r1__register_vt_notifier.nm, r1__register_vt_notifier.E;
position r1__register_vt_notifier.p2;
@@
+ unregister_vt_notifier(nm);
  return@p2 E;

@r1__iio_device_register exists@
expression ret, nm;
expression E != {0};
statement S;
position p1, p2;
@@
 ret = iio_device_register(nm);
 if (\(ret < 0\|ret != 0\)) S
  ... when != iio_device_unregister(nm)
 if@p1 (...) {
   ... when != iio_device_unregister(nm)
       when forall
   return@p2 E;
  }

@depends on r1__iio_device_register@
expression r1__iio_device_register.nm, r1__iio_device_register.E;
position r1__iio_device_register.p2;
@@
+ iio_device_unregister(nm);
  return@p2 E;

@r1__jsm_tty_init exists@
expression ret, nm;
expression E != {0};
statement S;
position p1, p2;
@@
 ret = jsm_tty_init(nm);
 if (\(ret < 0\|ret != 0\)) S
  ... when != jsm_remove_uart_port(nm)
 if@p1 (...) {
   ... when != jsm_remove_uart_port(nm)
       when forall
   return@p2 E;
  }

@depends on r1__jsm_tty_init@
expression r1__jsm_tty_init.nm, r1__jsm_tty_init.E;
position r1__jsm_tty_init.p2;
@@
+ jsm_remove_uart_port(nm);
  return@p2 E;

@r1__pci_save_state exists@
expression ret, nm;
expression E != {0};
statement S;
position p1, p2;
@@
 ret = pci_save_state(nm);
 if (\(ret < 0\|ret != 0\)) S
  ... when != pci_restore_state(nm)
 if@p1 (...) {
   ... when != pci_restore_state(nm)
       when forall
   return@p2 E;
  }

@depends on r1__pci_save_state@
expression r1__pci_save_state.nm, r1__pci_save_state.E;
position r1__pci_save_state.p2;
@@
+ pci_restore_state(nm);
  return@p2 E;

@r1__gpiochip_add exists@
expression ret, nm;
expression E != {0};
statement S;
position p1, p2;
@@
 ret = gpiochip_add(nm);
 if (\(ret < 0\|ret != 0\)) S
  ... when != gpiochip_remove(nm)
 if@p1 (...) {
   ... when != gpiochip_remove(nm)
       when forall
   return@p2 E;
  }

@depends on r1__gpiochip_add@
expression r1__gpiochip_add.nm, r1__gpiochip_add.E;
position r1__gpiochip_add.p2;
@@
+ gpiochip_remove(nm);
  return@p2 E;

@r1__vq_init exists@
expression ret, nm;
expression E != {0};
statement S;
position p1, p2;
@@
 ret = vq_init(nm);
 if (\(ret < 0\|ret != 0\)) S
  ... when != vq_term(nm)
 if@p1 (...) {
   ... when != vq_term(nm)
       when forall
   return@p2 E;
  }

@depends on r1__vq_init@
expression r1__vq_init.nm, r1__vq_init.E;
position r1__vq_init.p2;
@@
+ vq_term(nm);
  return@p2 E;

@r1__iscsit_get_tpg exists@
expression ret, nm;
expression E != {0};
statement S;
position p1, p2;
@@
 ret = iscsit_get_tpg(nm);
 if (\(ret < 0\|ret != 0\)) S
  ... when != iscsit_put_tpg(nm)
 if@p1 (...) {
   ... when != iscsit_put_tpg(nm)
       when forall
   return@p2 E;
  }

@depends on r1__iscsit_get_tpg@
expression r1__iscsit_get_tpg.nm, r1__iscsit_get_tpg.E;
position r1__iscsit_get_tpg.p2;
@@
+ iscsit_put_tpg(nm);
  return@p2 E;

@r1__sas_notify_lldd_dev_found exists@
expression ret, nm;
expression E != {0};
statement S;
position p1, p2;
@@
 ret = sas_notify_lldd_dev_found(nm);
 if (\(ret < 0\|ret != 0\)) S
  ... when != sas_notify_lldd_dev_gone(nm)
 if@p1 (...) {
   ... when != sas_notify_lldd_dev_gone(nm)
       when forall
   return@p2 E;
  }

@depends on r1__sas_notify_lldd_dev_found@
expression r1__sas_notify_lldd_dev_found.nm, r1__sas_notify_lldd_dev_found.E;
position r1__sas_notify_lldd_dev_found.p2;
@@
+ sas_notify_lldd_dev_gone(nm);
  return@p2 E;

@r1__wa_rpipes_create exists@
expression ret, nm;
expression E != {0};
statement S;
position p1, p2;
@@
 ret = wa_rpipes_create(nm);
 if (\(ret < 0\|ret != 0\)) S
  ... when != wa_rpipes_destroy(nm)
 if@p1 (...) {
   ... when != wa_rpipes_destroy(nm)
       when forall
   return@p2 E;
  }

@depends on r1__wa_rpipes_create@
expression r1__wa_rpipes_create.nm, r1__wa_rpipes_create.E;
position r1__wa_rpipes_create.p2;
@@
+ wa_rpipes_destroy(nm);
  return@p2 E;

@r1__v4l2_fh_open exists@
expression ret, nm;
expression E != {0};
statement S;
position p1, p2;
@@
 ret = v4l2_fh_open(nm);
 if (\(ret < 0\|ret != 0\)) S
  ... when != v4l2_fh_release(nm)
 if@p1 (...) {
   ... when != v4l2_fh_release(nm)
       when forall
   return@p2 E;
  }

@depends on r1__v4l2_fh_open@
expression r1__v4l2_fh_open.nm, r1__v4l2_fh_open.E;
position r1__v4l2_fh_open.p2;
@@
+ v4l2_fh_release(nm);
  return@p2 E;

@r1__dm_register_target exists@
expression ret, nm;
expression E != {0};
statement S;
position p1, p2;
@@
 ret = dm_register_target(nm);
 if (\(ret < 0\|ret != 0\)) S
  ... when != dm_unregister_target(nm)
 if@p1 (...) {
   ... when != dm_unregister_target(nm)
       when forall
   return@p2 E;
  }

@depends on r1__dm_register_target@
expression r1__dm_register_target.nm, r1__dm_register_target.E;
position r1__dm_register_target.p2;
@@
+ dm_unregister_target(nm);
  return@p2 E;

@r1__sa1111_enable_device exists@
expression ret, nm;
expression E != {0};
statement S;
position p1, p2;
@@
 ret = sa1111_enable_device(nm);
 if (\(ret < 0\|ret != 0\)) S
  ... when != sa1111_disable_device(nm)
 if@p1 (...) {
   ... when != sa1111_disable_device(nm)
       when forall
   return@p2 E;
  }

@depends on r1__sa1111_enable_device@
expression r1__sa1111_enable_device.nm, r1__sa1111_enable_device.E;
position r1__sa1111_enable_device.p2;
@@
+ sa1111_disable_device(nm);
  return@p2 E;

@r1__pcim_enable_device exists@
expression ret, nm;
expression E != {0};
statement S;
position p1, p2;
@@
 ret = pcim_enable_device(nm);
 if (\(ret < 0\|ret != 0\)) S
  ... when != pcim_pin_device(nm)
 if@p1 (...) {
   ... when != pcim_pin_device(nm)
       when forall
   return@p2 E;
  }

@depends on r1__pcim_enable_device@
expression r1__pcim_enable_device.nm, r1__pcim_enable_device.E;
position r1__pcim_enable_device.p2;
@@
+ pcim_pin_device(nm);
  return@p2 E;

@r1__vb2_queue_init exists@
expression ret, nm;
expression E != {0};
statement S;
position p1, p2;
@@
 ret = vb2_queue_init(nm);
 if (\(ret < 0\|ret != 0\)) S
  ... when != vb2_queue_release(nm)
 if@p1 (...) {
   ... when != vb2_queue_release(nm)
       when forall
   return@p2 E;
  }

@depends on r1__vb2_queue_init@
expression r1__vb2_queue_init.nm, r1__vb2_queue_init.E;
position r1__vb2_queue_init.p2;
@@
+ vb2_queue_release(nm);
  return@p2 E;

@r1__ps3_dma_region_create exists@
expression ret, nm;
expression E != {0};
statement S;
position p1, p2;
@@
 ret = ps3_dma_region_create(nm);
 if (\(ret < 0\|ret != 0\)) S
  ... when != ps3_dma_region_free(nm)
 if@p1 (...) {
   ... when != ps3_dma_region_free(nm)
       when forall
   return@p2 E;
  }

@depends on r1__ps3_dma_region_create@
expression r1__ps3_dma_region_create.nm, r1__ps3_dma_region_create.E;
position r1__ps3_dma_region_create.p2;
@@
+ ps3_dma_region_free(nm);
  return@p2 E;

@r1__ad7606_register_ring_funcs_and_init exists@
expression ret, nm;
expression E != {0};
statement S;
position p1, p2;
@@
 ret = ad7606_register_ring_funcs_and_init(nm);
 if (\(ret < 0\|ret != 0\)) S
  ... when != ad7606_ring_cleanup(nm)
 if@p1 (...) {
   ... when != ad7606_ring_cleanup(nm)
       when forall
   return@p2 E;
  }

@depends on r1__ad7606_register_ring_funcs_and_init@
expression r1__ad7606_register_ring_funcs_and_init.nm, r1__ad7606_register_ring_funcs_and_init.E;
position r1__ad7606_register_ring_funcs_and_init.p2;
@@
+ ad7606_ring_cleanup(nm);
  return@p2 E;

@r1__gpio_direction_input exists@
expression ret, nm;
expression E != {0};
statement S;
position p1, p2;
@@
 ret = gpio_direction_input(nm);
 if (\(ret < 0\|ret != 0\)) S
  ... when != gpio_free(nm)
 if@p1 (...) {
   ... when != gpio_free(nm)
       when forall
   return@p2 E;
  }

@depends on r1__gpio_direction_input@
expression r1__gpio_direction_input.nm, r1__gpio_direction_input.E;
position r1__gpio_direction_input.p2;
@@
+ gpio_free(nm);
  return@p2 E;

@r1__media_devnode_register exists@
expression ret, nm;
expression E != {0};
statement S;
position p1, p2;
@@
 ret = media_devnode_register(nm);
 if (\(ret < 0\|ret != 0\)) S
  ... when != media_devnode_unregister(nm)
 if@p1 (...) {
   ... when != media_devnode_unregister(nm)
       when forall
   return@p2 E;
  }

@depends on r1__media_devnode_register@
expression r1__media_devnode_register.nm, r1__media_devnode_register.E;
position r1__media_devnode_register.p2;
@@
+ media_devnode_unregister(nm);
  return@p2 E;

@r1__gsc_ctrls_create exists@
expression ret, nm;
expression E != {0};
statement S;
position p1, p2;
@@
 ret = gsc_ctrls_create(nm);
 if (\(ret < 0\|ret != 0\)) S
  ... when != gsc_ctrls_delete(nm)
 if@p1 (...) {
   ... when != gsc_ctrls_delete(nm)
       when forall
   return@p2 E;
  }

@depends on r1__gsc_ctrls_create@
expression r1__gsc_ctrls_create.nm, r1__gsc_ctrls_create.E;
position r1__gsc_ctrls_create.p2;
@@
+ gsc_ctrls_delete(nm);
  return@p2 E;

@r1__st_magn_allocate_ring exists@
expression ret, nm;
expression E != {0};
statement S;
position p1, p2;
@@
 ret = st_magn_allocate_ring(nm);
 if (\(ret < 0\|ret != 0\)) S
  ... when != st_magn_deallocate_ring(nm)
 if@p1 (...) {
   ... when != st_magn_deallocate_ring(nm)
       when forall
   return@p2 E;
  }

@depends on r1__st_magn_allocate_ring@
expression r1__st_magn_allocate_ring.nm, r1__st_magn_allocate_ring.E;
position r1__st_magn_allocate_ring.p2;
@@
+ st_magn_deallocate_ring(nm);
  return@p2 E;

@r1__eisa_driver_register exists@
expression ret, nm;
expression E != {0};
statement S;
position p1, p2;
@@
 ret = eisa_driver_register(nm);
 if (\(ret < 0\|ret != 0\)) S
  ... when != eisa_driver_unregister(nm)
 if@p1 (...) {
   ... when != eisa_driver_unregister(nm)
       when forall
   return@p2 E;
  }

@depends on r1__eisa_driver_register@
expression r1__eisa_driver_register.nm, r1__eisa_driver_register.E;
position r1__eisa_driver_register.p2;
@@
+ eisa_driver_unregister(nm);
  return@p2 E;

@r1__r600_ih_ring_alloc exists@
expression ret, nm;
expression E != {0};
statement S;
position p1, p2;
@@
 ret = r600_ih_ring_alloc(nm);
 if (\(ret < 0\|ret != 0\)) S
  ... when != r600_ih_ring_fini(nm)
 if@p1 (...) {
   ... when != r600_ih_ring_fini(nm)
       when forall
   return@p2 E;
  }

@depends on r1__r600_ih_ring_alloc@
expression r1__r600_ih_ring_alloc.nm, r1__r600_ih_ring_alloc.E;
position r1__r600_ih_ring_alloc.p2;
@@
+ r600_ih_ring_fini(nm);
  return@p2 E;

@r1__pwmchip_add exists@
expression ret, nm;
expression E != {0};
statement S;
position p1, p2;
@@
 ret = pwmchip_add(nm);
 if (\(ret < 0\|ret != 0\)) S
  ... when != pwmchip_remove(nm)
 if@p1 (...) {
   ... when != pwmchip_remove(nm)
       when forall
   return@p2 E;
  }

@depends on r1__pwmchip_add@
expression r1__pwmchip_add.nm, r1__pwmchip_add.E;
position r1__pwmchip_add.p2;
@@
+ pwmchip_remove(nm);
  return@p2 E;

@r1__InitAdapter exists@
expression ret, nm;
expression E != {0};
statement S;
position p1, p2;
@@
 ret = InitAdapter(nm);
 if (\(ret < 0\|ret != 0\)) S
  ... when != AdapterFree(nm)
 if@p1 (...) {
   ... when != AdapterFree(nm)
       when forall
   return@p2 E;
  }

@depends on r1__InitAdapter@
expression r1__InitAdapter.nm, r1__InitAdapter.E;
position r1__InitAdapter.p2;
@@
+ AdapterFree(nm);
  return@p2 E;

@r1__tty_alloc_file exists@
expression ret, nm;
expression E != {0};
statement S;
position p1, p2;
@@
 ret = tty_alloc_file(nm);
 if (\(ret < 0\|ret != 0\)) S
  ... when != tty_free_file(nm)
 if@p1 (...) {
   ... when != tty_free_file(nm)
       when forall
   return@p2 E;
  }

@depends on r1__tty_alloc_file@
expression r1__tty_alloc_file.nm, r1__tty_alloc_file.E;
position r1__tty_alloc_file.p2;
@@
+ tty_free_file(nm);
  return@p2 E;

@r1__register_reboot_notifier exists@
expression ret, nm;
expression E != {0};
statement S;
position p1, p2;
@@
 ret = register_reboot_notifier(nm);
 if (\(ret < 0\|ret != 0\)) S
  ... when != unregister_reboot_notifier(nm)
 if@p1 (...) {
   ... when != unregister_reboot_notifier(nm)
       when forall
   return@p2 E;
  }

@depends on r1__register_reboot_notifier@
expression r1__register_reboot_notifier.nm, r1__register_reboot_notifier.E;
position r1__register_reboot_notifier.p2;
@@
+ unregister_reboot_notifier(nm);
  return@p2 E;

@r1__xen_pcibk_config_init_dev exists@
expression ret, nm;
expression E != {0};
statement S;
position p1, p2;
@@
 ret = xen_pcibk_config_init_dev(nm);
 if (\(ret < 0\|ret != 0\)) S
  ... when != xen_pcibk_config_free_dev(nm)
 if@p1 (...) {
   ... when != xen_pcibk_config_free_dev(nm)
       when forall
   return@p2 E;
  }

@depends on r1__xen_pcibk_config_init_dev@
expression r1__xen_pcibk_config_init_dev.nm, r1__xen_pcibk_config_init_dev.E;
position r1__xen_pcibk_config_init_dev.p2;
@@
+ xen_pcibk_config_free_dev(nm);
  return@p2 E;

@r1__r600_parse_extended_power_table exists@
expression ret, nm;
expression E != {0};
statement S;
position p1, p2;
@@
 ret = r600_parse_extended_power_table(nm);
 if (\(ret < 0\|ret != 0\)) S
  ... when != r600_free_extended_power_table(nm)
 if@p1 (...) {
   ... when != r600_free_extended_power_table(nm)
       when forall
   return@p2 E;
  }

@depends on r1__r600_parse_extended_power_table@
expression r1__r600_parse_extended_power_table.nm, r1__r600_parse_extended_power_table.E;
position r1__r600_parse_extended_power_table.p2;
@@
+ r600_free_extended_power_table(nm);
  return@p2 E;

@r1__task_handoff_register exists@
expression ret, nm;
expression E != {0};
statement S;
position p1, p2;
@@
 ret = task_handoff_register(nm);
 if (\(ret < 0\|ret != 0\)) S
  ... when != task_handoff_unregister(nm)
 if@p1 (...) {
   ... when != task_handoff_unregister(nm)
       when forall
   return@p2 E;
  }

@depends on r1__task_handoff_register@
expression r1__task_handoff_register.nm, r1__task_handoff_register.E;
position r1__task_handoff_register.p2;
@@
+ task_handoff_unregister(nm);
  return@p2 E;

@r1__ps3_mmio_region_create exists@
expression ret, nm;
expression E != {0};
statement S;
position p1, p2;
@@
 ret = ps3_mmio_region_create(nm);
 if (\(ret < 0\|ret != 0\)) S
  ... when != ps3_free_mmio_region(nm)
 if@p1 (...) {
   ... when != ps3_free_mmio_region(nm)
       when forall
   return@p2 E;
  }

@depends on r1__ps3_mmio_region_create@
expression r1__ps3_mmio_region_create.nm, r1__ps3_mmio_region_create.E;
position r1__ps3_mmio_region_create.p2;
@@
+ ps3_free_mmio_region(nm);
  return@p2 E;

@r1__scsi_dma_map exists@
expression ret, nm;
expression E != {0};
statement S;
position p1, p2;
@@
 ret = scsi_dma_map(nm);
 if (\(ret < 0\|ret != 0\)) S
  ... when != scsi_dma_unmap(nm)
 if@p1 (...) {
   ... when != scsi_dma_unmap(nm)
       when forall
   return@p2 E;
  }

@depends on r1__scsi_dma_map@
expression r1__scsi_dma_map.nm, r1__scsi_dma_map.E;
position r1__scsi_dma_map.p2;
@@
+ scsi_dma_unmap(nm);
  return@p2 E;

@r1__enable_irq_wake exists@
expression ret, nm;
expression E != {0};
statement S;
position p1, p2;
@@
 ret = enable_irq_wake(nm);
 if (\(ret < 0\|ret != 0\)) S
  ... when != disable_irq_wake(nm)
 if@p1 (...) {
   ... when != disable_irq_wake(nm)
       when forall
   return@p2 E;
  }

@depends on r1__enable_irq_wake@
expression r1__enable_irq_wake.nm, r1__enable_irq_wake.E;
position r1__enable_irq_wake.p2;
@@
+ disable_irq_wake(nm);
  return@p2 E;

@r1__lu_device_type_init exists@
expression ret, nm;
expression E != {0};
statement S;
position p1, p2;
@@
 ret = lu_device_type_init(nm);
 if (\(ret < 0\|ret != 0\)) S
  ... when != lu_device_type_fini(nm)
 if@p1 (...) {
   ... when != lu_device_type_fini(nm)
       when forall
   return@p2 E;
  }

@depends on r1__lu_device_type_init@
expression r1__lu_device_type_init.nm, r1__lu_device_type_init.E;
position r1__lu_device_type_init.p2;
@@
+ lu_device_type_fini(nm);
  return@p2 E;

