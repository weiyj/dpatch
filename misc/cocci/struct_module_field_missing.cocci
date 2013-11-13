@r1@
declarer name module_init;
identifier fn_init;
@@
module_init(fn_init);

@r2@
declarer name module_exit;
identifier fn_exit;
@@
module_exit(fn_exit);

@r3@
declarer name module_acpi_driver;
declarer name module_comedi_pcmcia_driver;
declarer name module_pci_driver;
declarer name module_usb_driver;
declarer name module_comedi_usb_driver;
declarer name module_platform_driver;
declarer name module_virtio_driver;
declarer name module_amba_driver;
declarer name module_gameport_driver;
declarer name module_platform_driver_probe;
declarer name module_comedi_driver;
declarer name module_hid_driver;
declarer name module_serio_driver;
declarer name module_comedi_pci_driver;
declarer name module_i2c_driver;
declarer name module_spi_driver;
identifier i_driver;
@@
(
module_acpi_driver(i_driver);
|
module_comedi_pcmcia_driver(i_driver);
|
module_pci_driver(i_driver);
|
module_usb_driver(i_driver);
|
module_comedi_usb_driver(i_driver);
|
module_platform_driver(i_driver);
|
module_virtio_driver(i_driver);
|
module_amba_driver(i_driver);
|
module_gameport_driver(i_driver);
|
module_platform_driver_probe(i_driver);
|
module_comedi_driver(i_driver);
|
module_hid_driver(i_driver);
|
module_serio_driver(i_driver);
|
module_comedi_pci_driver(i_driver);
|
module_i2c_driver(i_driver);
|
module_spi_driver(i_driver);
)


@r__agp_bridge_driver depends on (r1 && r2) || r3@
identifier nm;
position p;
@@
struct agp_bridge_driver nm@p = {
...,
  .owner = THIS_MODULE,
...
};

@depends on (r1 && r2) || r3@
identifier nm;
position p != {r__agp_bridge_driver.p};
@@
struct agp_bridge_driver nm@p = {
...,
+ .owner = THIS_MODULE,
};

@r__atmdev_ops depends on (r1 && r2) || r3@
identifier nm;
position p;
@@
struct atmdev_ops nm@p = {
...,
  .owner = THIS_MODULE,
...
};

@depends on (r1 && r2) || r3@
identifier nm;
position p != {r__atmdev_ops.p};
@@
struct atmdev_ops nm@p = {
...,
+ .owner = THIS_MODULE,
};

@r__block_device_operations depends on (r1 && r2) || r3@
identifier nm;
position p;
@@
struct block_device_operations nm@p = {
...,
  .owner = THIS_MODULE,
...
};

@depends on (r1 && r2) || r3@
identifier nm;
position p != {r__block_device_operations.p};
@@
struct block_device_operations nm@p = {
...,
+ .owner = THIS_MODULE,
};

@r__consw depends on (r1 && r2) || r3@
identifier nm;
position p;
@@
struct consw nm@p = {
...,
  .owner = THIS_MODULE,
...
};

@depends on (r1 && r2) || r3@
identifier nm;
position p != {r__consw.p};
@@
struct consw nm@p = {
...,
+ .owner = THIS_MODULE,
};

@r__gpio_chip depends on (r1 && r2) || r3@
identifier nm;
position p;
@@
struct gpio_chip nm@p = {
...,
  .owner = THIS_MODULE,
...
};

@depends on (r1 && r2) || r3@
identifier nm;
position p != {r__gpio_chip.p};
@@
struct gpio_chip nm@p = {
...,
+ .owner = THIS_MODULE,
};

@r__i2c_adapter depends on (r1 && r2) || r3@
identifier nm;
position p;
@@
struct i2c_adapter nm@p = {
...,
  .owner = THIS_MODULE,
...
};

@depends on (r1 && r2) || r3@
identifier nm;
position p != {r__i2c_adapter.p};
@@
struct i2c_adapter nm@p = {
...,
+ .owner = THIS_MODULE,
};

@r__iio_info depends on (r1 && r2) || r3@
identifier nm;
position p;
@@
struct iio_info nm@p = {
...,
  .driver_module = THIS_MODULE,
...
};

@depends on (r1 && r2) || r3@
identifier nm;
position p != {r__iio_info.p};
@@
struct iio_info nm@p = {
...,
+ .driver_module = THIS_MODULE,
};

@r__iio_trigger_ops depends on (r1 && r2) || r3@
identifier nm;
position p;
@@
struct iio_trigger_ops nm@p = {
...,
  .owner = THIS_MODULE,
...
};

@depends on (r1 && r2) || r3@
identifier nm;
position p != {r__iio_trigger_ops.p};
@@
struct iio_trigger_ops nm@p = {
...,
+ .owner = THIS_MODULE,
};

@r__media_file_operations depends on (r1 && r2) || r3@
identifier nm;
position p;
@@
struct media_file_operations nm@p = {
...,
  .owner = THIS_MODULE,
...
};

@depends on (r1 && r2) || r3@
identifier nm;
position p != {r__media_file_operations.p};
@@
struct media_file_operations nm@p = {
...,
+ .owner = THIS_MODULE,
};

@r__net_proto_family depends on (r1 && r2) || r3@
identifier nm;
position p;
@@
struct net_proto_family nm@p = {
...,
  .owner = THIS_MODULE,
...
};

@depends on (r1 && r2) || r3@
identifier nm;
position p != {r__net_proto_family.p};
@@
struct net_proto_family nm@p = {
...,
+ .owner = THIS_MODULE,
};

@r__parport_operations depends on (r1 && r2) || r3@
identifier nm;
position p;
@@
struct parport_operations nm@p = {
...,
  .owner = THIS_MODULE,
...
};

@depends on (r1 && r2) || r3@
identifier nm;
position p != {r__parport_operations.p};
@@
struct parport_operations nm@p = {
...,
+ .owner = THIS_MODULE,
};

@r__phy_ops depends on (r1 && r2) || r3@
identifier nm;
position p;
@@
struct phy_ops nm@p = {
...,
  .owner = THIS_MODULE,
...
};

@depends on (r1 && r2) || r3@
identifier nm;
position p != {r__phy_ops.p};
@@
struct phy_ops nm@p = {
...,
+ .owner = THIS_MODULE,
};

@r__pppox_proto depends on (r1 && r2) || r3@
identifier nm;
position p;
@@
struct pppox_proto nm@p = {
...,
  .owner = THIS_MODULE,
...
};

@depends on (r1 && r2) || r3@
identifier nm;
position p != {r__pppox_proto.p};
@@
struct pppox_proto nm@p = {
...,
+ .owner = THIS_MODULE,
};

@r__proto_ops depends on (r1 && r2) || r3@
identifier nm;
position p;
@@
struct proto_ops nm@p = {
...,
  .owner = THIS_MODULE,
...
};

@depends on (r1 && r2) || r3@
identifier nm;
position p != {r__proto_ops.p};
@@
struct proto_ops nm@p = {
...,
+ .owner = THIS_MODULE,
};

@r__ptp_clock_info depends on (r1 && r2) || r3@
identifier nm;
position p;
@@
struct ptp_clock_info nm@p = {
...,
  .owner = THIS_MODULE,
...
};

@depends on (r1 && r2) || r3@
identifier nm;
position p != {r__ptp_clock_info.p};
@@
struct ptp_clock_info nm@p = {
...,
+ .owner = THIS_MODULE,
};

@r__pwm_ops depends on (r1 && r2) || r3@
identifier nm;
position p;
@@
struct pwm_ops nm@p = {
...,
  .owner = THIS_MODULE,
...
};

@depends on (r1 && r2) || r3@
identifier nm;
position p != {r__pwm_ops.p};
@@
struct pwm_ops nm@p = {
...,
+ .owner = THIS_MODULE,
};

@r__regulator_desc depends on (r1 && r2) || r3@
identifier nm;
position p;
@@
struct regulator_desc nm@p = {
...,
  .owner = THIS_MODULE,
...
};

@depends on (r1 && r2) || r3@
identifier nm;
position p != {r__regulator_desc.p};
@@
struct regulator_desc nm@p = {
...,
+ .owner = THIS_MODULE,
};

@r__rt2x00debug depends on (r1 && r2) || r3@
identifier nm;
position p;
@@
struct rt2x00debug nm@p = {
...,
  .owner = THIS_MODULE,
...
};

@depends on (r1 && r2) || r3@
identifier nm;
position p != {r__rt2x00debug.p};
@@
struct rt2x00debug nm@p = {
...,
+ .owner = THIS_MODULE,
};

@r__team_mode depends on (r1 && r2) || r3@
identifier nm;
position p;
@@
struct team_mode nm@p = {
...,
  .owner = THIS_MODULE,
...
};

@depends on (r1 && r2) || r3@
identifier nm;
position p != {r__team_mode.p};
@@
struct team_mode nm@p = {
...,
+ .owner = THIS_MODULE,
};

@r__v4l2_clk_ops depends on (r1 && r2) || r3@
identifier nm;
position p;
@@
struct v4l2_clk_ops nm@p = {
...,
  .owner = THIS_MODULE,
...
};

@depends on (r1 && r2) || r3@
identifier nm;
position p != {r__v4l2_clk_ops.p};
@@
struct v4l2_clk_ops nm@p = {
...,
+ .owner = THIS_MODULE,
};

@r__v4l2_file_operations depends on (r1 && r2) || r3@
identifier nm;
position p;
@@
struct v4l2_file_operations nm@p = {
...,
  .owner = THIS_MODULE,
...
};

@depends on (r1 && r2) || r3@
identifier nm;
position p != {r__v4l2_file_operations.p};
@@
struct v4l2_file_operations nm@p = {
...,
+ .owner = THIS_MODULE,
};

@r__vfio_iommu_driver_ops depends on (r1 && r2) || r3@
identifier nm;
position p;
@@
struct vfio_iommu_driver_ops nm@p = {
...,
  .owner = THIS_MODULE,
...
};

@depends on (r1 && r2) || r3@
identifier nm;
position p != {r__vfio_iommu_driver_ops.p};
@@
struct vfio_iommu_driver_ops nm@p = {
...,
+ .owner = THIS_MODULE,
};

@r__videocodec depends on (r1 && r2) || r3@
identifier nm;
position p;
@@
struct videocodec nm@p = {
...,
  .owner = THIS_MODULE,
...
};

@depends on (r1 && r2) || r3@
identifier nm;
position p != {r__videocodec.p};
@@
struct videocodec nm@p = {
...,
+ .owner = THIS_MODULE,
};

@r__watchdog_ops depends on (r1 && r2) || r3@
identifier nm;
position p;
@@
struct watchdog_ops nm@p = {
...,
  .owner = THIS_MODULE,
...
};

@depends on (r1 && r2) || r3@
identifier nm;
position p != {r__watchdog_ops.p};
@@
struct watchdog_ops nm@p = {
...,
+ .owner = THIS_MODULE,
};

@r__wf_control_ops depends on (r1 && r2) || r3@
identifier nm;
position p;
@@
struct wf_control_ops nm@p = {
...,
  .owner = THIS_MODULE,
...
};

@depends on (r1 && r2) || r3@
identifier nm;
position p != {r__wf_control_ops.p};
@@
struct wf_control_ops nm@p = {
...,
+ .owner = THIS_MODULE,
};

@r__wf_sensor_ops depends on (r1 && r2) || r3@
identifier nm;
position p;
@@
struct wf_sensor_ops nm@p = {
...,
  .owner = THIS_MODULE,
...
};

@depends on (r1 && r2) || r3@
identifier nm;
position p != {r__wf_sensor_ops.p};
@@
struct wf_sensor_ops nm@p = {
...,
+ .owner = THIS_MODULE,
};

