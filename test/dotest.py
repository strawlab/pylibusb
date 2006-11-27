import ctypes, sys
import pylibusb as usb

pylibusbmod = usb.pylibusb
if sys.platform.startswith('linux'):
    c_test_shared_library = 'libtest_pylibusb.so'
    c_test = ctypes.cdll.LoadLibrary(c_test_shared_library)
elif sys.platform.startswith('win'):
    c_test_shared_library = 'test_pylibusb.dll'
    c_test = ctypes.CDLL(c_test_shared_library)
    
################
if not sys.platform.startswith('win'):
#if 1:
    c_test.print_config.restype = None
    c_test.print_config.argtypes = [pylibusbmod.usb_config_descriptor_p]
    c_test.print_interface.restype = None
    c_test.print_interface.argtypes = [pylibusbmod.usb_interface_p]
################

def debug(*args):
    if 1:
        print ' '.join([str(a) for a in args])

def printf(*args):
    debug(*args)

def print_device_descriptor(dd):
    printf("device_descriptor",dd)
    printf("  bNumConfigurations %x"%dd.bNumConfigurations)
    printf("  idVendor %x"%dd.idVendor)
    printf("  idProduct %x"%dd.idProduct)

def print_endpoint_descriptor(endpt):
    printf("      endpoint_descriptor",endpt)
    printf("        bLength: %d"%endpt.bLength)
    printf("        bDescriptorType: %d"%endpt.bDescriptorType)
    printf("        bEndpointAddress: %d"%endpt.bEndpointAddress)
    printf("        bmAttributes: %d"%endpt.bmAttributes)
    printf("        wMaxPacketSize: %d"%endpt.wMaxPacketSize)
    printf("        bInterval: %d"%endpt.bInterval)
    printf("        bRefresh: %d"%endpt.bRefresh)
    printf("        bSynchAddress: %d"%endpt.bSynchAddress)

def print_interface_descriptor(ifdscr):
    printf("    interface_descriptor",ifdscr)
    printf("      bLength: %d"%ifdscr.bLength)
    printf("      bDescriptorType: %d"%ifdscr.bDescriptorType)
    printf("      bInterfaceNumber: %d"%ifdscr.bInterfaceNumber)
    printf("      bAlternateSetting: %d"%ifdscr.bAlternateSetting)
    printf("      bNumEndpoints: %d"%ifdscr.bNumEndpoints)
    printf("      bInterfaceClass: %d"%ifdscr.bInterfaceClass)
    printf("      bInterfaceSubClass: %d"%ifdscr.bInterfaceSubClass)
    printf("      bInterfaceProtocol: %d"%ifdscr.bInterfaceProtocol)
    printf("      iInterface: %d"%ifdscr.iInterface)
    for i in range(ifdscr.bNumEndpoints):
        print_endpoint_descriptor(ifdscr.endpoint[i])

def print_interface(iface):
    printf("  interface",iface)
    printf("    num_altsetting: %d"%iface.num_altsetting)
    for i in range(iface.num_altsetting):
        print_interface_descriptor(iface.altsetting[i])
    
def print_config(cfg):
    printf("config",cfg)
    printf("  bLength",cfg.bLength)
    printf("  bDescriptorType",cfg.bDescriptorType)
    printf("  wTotalLength",cfg.wTotalLength)
    printf("  bNumInterfaces",cfg.bNumInterfaces)
    printf("  bConfigurationValue",cfg.bConfigurationValue)
    printf("  iConfiguration",cfg.iConfiguration)
    printf("  bmAttributes",cfg.bmAttributes)
    printf("  MaxPower",cfg.MaxPower)

    interfaces = cfg.interface
    for i in range(cfg.bNumInterfaces):
        print_interface(interfaces[i])
    
def print_device(dev):
    printf("device",dev)
    print_device_descriptor(dev.descriptor)
    for i in range(dev.descriptor.bNumConfigurations):
        print_config(dev.config[i])
        
if 1:
    if 1:
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
                if (dev.descriptor.idVendor == 0x1781 and
                    dev.descriptor.idProduct == 0x0BAF):
                    found = True
                    break
            if found:
                break
        if not found:
            raise RuntimeError("Cannot find device.")

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
        
        config = dev.config[0]
        print_config( config )
        
        debug('config.bConfigurationValue',config.bConfigurationValue)
        usb.set_configuration(libusb_handle, config.bConfigurationValue)


        print '## in C: ################################'
        c_test.print_device( dev.cval )
        print
        print '## in Python: ################################'
        print_device( dev )
        print
        
