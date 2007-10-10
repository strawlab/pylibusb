####################################################################
#
#
# This is a short example program demonstrating the use of pylibusb.
#
#
####################################################################

import pylibusb as usb
import ctypes

def debug(*args):
    if 1:
        print args

########################################
        
usb.init()

if not usb.get_busses():
    usb.find_busses()
    usb.find_devices()

busses = usb.get_busses()

found = False
for bus in busses:
    for dev in bus.devices:
        debug('idVendor: 0x%04x idProduct: 0x%04x'%(dev.descriptor.idVendor,
                                                    dev.descriptor.idProduct))
        if (dev.descriptor.idVendor == 0x046d and
            dev.descriptor.idProduct == 0xc01b): # Logitech MX310 optical mouse
            found = True
            break
    if found:
        break
if not found:
    raise RuntimeError("Cannot find device.")

debug('found device',dev)
libusb_handle = usb.open(dev)

interface_nr = 0
if hasattr(usb,'get_driver_np'):
    # non-portable libusb extension
    name = usb.get_driver_np(libusb_handle,interface_nr)
    if name != '':
        debug("attached to kernel driver '%s', detaching."%name )
        usb.detach_kernel_driver_np(libusb_handle,interface_nr)

if dev.descriptor.bNumConfigurations > 1:
    debug("WARNING: more than one configuration, choosing first")

debug('setting configuration')
debug('dev.config[0]',dev.config[0])
config = dev.config[0]
debug('config.bConfigurationValue',config.bConfigurationValue)
usb.set_configuration(libusb_handle, config.bConfigurationValue)
debug('claiming interface')
debug('config.bNumInterfaces',config.bNumInterfaces)

usb.claim_interface(libusb_handle, interface_nr)

INPUT_BUFFER = ctypes.create_string_buffer(16)

while 1:
    try:
        # do your device-specific stuff here
        val = usb.bulk_read(libusb_handle, 0x82, INPUT_BUFFER, 1000)
    except usb.USBNoDataAvailableError:
        pass
