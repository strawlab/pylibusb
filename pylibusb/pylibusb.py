import sys
import ctypes

__all__ = ['USBError','USBNoDataAvailableError','bulk_read','bulk_write',
           'claim_interface', 'find_busses','find_devices','get_busses',
           'init','interrupt_read','interrupt_write','open',
           'set_configuration','set_debug']
           
if sys.platform.startswith('linux'):
    __all__.extend(['get_driver_np','detach_kernel_driver_np'])

class USBError(RuntimeError):
    pass

class USBNoDataAvailableError(USBError):
    pass

if sys.platform.startswith('linux'):
    c_libusb_shared_library = '/usr/lib/libusb.so'
    c_libusb = ctypes.cdll.LoadLibrary(c_libusb_shared_library)
elif sys.platform.startswith('win'):
    c_libusb = ctypes.CDLL(r'C:\WINDOWS\system32\libusb0.dll')

#####################################
# typedefs and defines
if sys.platform.startswith('linux'):
    PATH_MAX = 4096 # HACK! should get from header file...
    LIBUSB_PATH_MAX = PATH_MAX+1
elif sys.platform.startswith('win'):
    LIBUSB_PATH_MAX = 512 # From usb.h of win32 libusb source

if hasattr(ctypes,'c_uint8'):
    uint8 = ctypes.c_uint8
    uint16 = ctypes.c_uint16
else:
    uint8 = ctypes.c_ubyte
    uint16 = ctypes.c_ushort

# datatypes
# Forward Declarations
usb_device_p = ctypes.POINTER('usb_device')
usb_bus_p = ctypes.POINTER('usb_bus')
usb_dev_handle_p = ctypes.POINTER('usb_dev_handle')
usb_config_descriptor_p = ctypes.POINTER('usb_config_descriptor')
usb_interface_p = ctypes.c_void_p # XXX define...

# structures
class usb_device_descriptor(ctypes.Structure):
    _fields_ = [('bLength',uint8),
                ('bDescriptorType',uint8),
                ('bcdUSB',uint16),
                ('bDeviceClass',uint8),
                ('bDeviceSubClass',uint8),
                ('bDeviceProtocol',uint8),
                ('bMaxPacketSize0',uint8),
                ('idVendor',uint16),
                ('idProduct',uint16),
                ('bcdDevice',uint16),
                ('iManufacturer',uint8),
                ('iProduct',uint8),
                ('iSerialNumber',uint8),
                ('bNumConfigurations',uint8)]

class usb_device(ctypes.Structure):
    _fields_ = [('next',usb_device_p),
                ('prev',usb_device_p),
                ('filename',ctypes.c_char*(LIBUSB_PATH_MAX)),
                ('bus',usb_bus_p),
                ('descriptor',usb_device_descriptor),
                ('config',usb_config_descriptor_p),
                ('dev',ctypes.c_void_p),
                ('devnum',uint8),
                ('num_children',uint8),
                ('children',ctypes.POINTER(usb_device_p))
                ]
    
class usb_bus(ctypes.Structure):
    _fields_ = [('next',usb_bus_p),
                ('prev',usb_bus_p),
                ('dirname',ctypes.c_char*(LIBUSB_PATH_MAX)),
                ('devices',usb_device_p),
                ('location',ctypes.c_ulong),
                ('root_dev',usb_device_p),
                ]

class usb_config_descriptor(ctypes.Structure):
    _pack_ = 1 # packed structure
    _fields_ = [('bLength',uint8),
                ('bDescriptorType',uint8),
                ('wTotalLength',uint16),
                ('bNumInterfaces',uint8),
                ('bConfigurationValue',uint8),
                ('iConfiguration',uint8),
                ('bmAttributes',uint8),
                ('MaxPower',uint8),
                ('interface',usb_interface_p),
                ('extra',ctypes.POINTER(uint8)),
                ('extralen',ctypes.c_int)
                ]

class usb_dev_handle(ctypes.Structure):
    # opaque struct
    pass

# Set the pointer to the structure
ctypes.SetPointerType(usb_device_p, usb_device)
ctypes.SetPointerType(usb_bus_p, usb_bus)
ctypes.SetPointerType(usb_dev_handle_p, usb_dev_handle)
ctypes.SetPointerType(usb_config_descriptor_p, usb_config_descriptor)

# structure wrappers
class config_descriptor(object):
    """wraps usb_config_descriptor structure"""
    def __init__(self,cval):
        if type(cval) != usb_config_descriptor:
            raise TypeError('need struct usb_config_descriptor')
        self.cval = cval
    def get_bConfigurationValue(self):
        return self.cval.bConfigurationValue
    bConfigurationValue = property(get_bConfigurationValue)

class device_descriptor(object):
    """wraps usb_device_descriptor structure"""
    def __init__(self,cval):
        if type(cval) != usb_device_descriptor:
            raise TypeError('need struct usb_device_descriptor')
        self.cval = cval
        
    def get_idProduct(self):
        return self.cval.idProduct
    idProduct = property(get_idProduct)
    
    def get_idVendor(self):
        return self.cval.idVendor
    idVendor = property(get_idVendor)

    def get_bNumConfigurations(self):
        return self.cval.bNumConfigurations
    bNumConfigurations = property(get_bNumConfigurations)
    
class device(object):
    """wraps pointer to usb_device structure"""
    def __init__(self,cval):
        if type(cval) != usb_device_p:
            raise TypeError('need pointer to struct usb_device')
        self.cval = cval
        self.next = self # prepare for iterating
    def __iter__(self):
        return self
    def next(self):
        result = self.next
        if result is None:
            raise StopIteration
        # prepare for next iteration
        self.next = _CheckDevice(result.cval.contents.next)
        return result
    def get_descriptor(self):
        return device_descriptor(self.cval.contents.descriptor)
    descriptor = property(get_descriptor)
    def get_config(self):
        result = []
        n_configs = self.descriptor.bNumConfigurations
        for i in range(n_configs):
            result.append(config_descriptor( self.cval.contents.config[i] ))
        return result
    config = property(get_config)

class bus(object):
    """wraps pointer to usb_bus structure"""
    def __init__(self,cval):
        if type(cval) != usb_bus_p:
            raise TypeError('need pointer to struct usb_bus')
        self.cval = cval
        self.next = self # prepare for iterating
    def __iter__(self):
        return self
    def next(self):
        result = self.next
        if result is None:
            raise StopIteration
        # prepare for next iteration
        self.next = _CheckBus(result.cval.contents.next)
        return result
    def get_devices(self):
        devices = self.cval.contents.devices
        result = device(devices)
        return result
    devices = property(get_devices)

def _CheckBus(b):
    if bool(b):
        return bus(b)
    else:
        return None

def _CheckDevice(b):
    if bool(b):
        return device(b)
    else:
        return None 
    
#####################################
# function definitions
c_libusb.usb_get_busses.restype = usb_bus_p
c_libusb.usb_open.restype = usb_dev_handle_p
c_libusb.usb_strerror.restype = ctypes.c_char_p

c_libusb.usb_bulk_read.argtypes = [usb_dev_handle_p, ctypes.c_int,
                                        ctypes.c_char_p, ctypes.c_int, ctypes.c_int]
c_libusb.usb_bulk_write.argtypes = [usb_dev_handle_p, ctypes.c_int,
                                         ctypes.c_char_p, ctypes.c_int, ctypes.c_int]
c_libusb.usb_claim_interface.argtypes = [usb_dev_handle_p, ctypes.c_int]
c_libusb.usb_interrupt_read.argtypes = [usb_dev_handle_p, ctypes.c_int,
                                        ctypes.c_char_p, ctypes.c_int, ctypes.c_int]
c_libusb.usb_interrupt_write.argtypes = [usb_dev_handle_p, ctypes.c_int,
                                         ctypes.c_char_p, ctypes.c_int, ctypes.c_int]
c_libusb.usb_set_configuration.argtypes = [usb_dev_handle_p, ctypes.c_int]

#####################################
# wrapper

def CHK(result):
    if result < 0:
        errstr = c_libusb.usb_strerror()
        if errstr == "could not get bound driver: No data available":
            exc_class = USBNoDataAvailableError
        else:
            exc_class = USBError
        raise exc_class("%d: %s"%(result,errstr))
    return result

def bulk_read(libusb_handle,endpoint,buf,timeout):
    if not isinstance(libusb_handle,usb_dev_handle_p):
        raise ValueError("expected instance of usb_dev_handle_p")
    return CHK(c_libusb.usb_bulk_read(libusb_handle, endpoint,
                                    buf, len(buf), timeout))

def bulk_write(libusb_handle,endpoint,buf,timeout):
    if not isinstance(libusb_handle,usb_dev_handle_p):
        raise ValueError("expected instance of usb_dev_handle_p")
    return CHK(c_libusb.usb_bulk_write(libusb_handle, endpoint,
                                    buf, len(buf), timeout))

def claim_interface(libusb_handle,value):
    if not isinstance(libusb_handle,usb_dev_handle_p):
        raise ValueError("expected instance of usb_dev_handle_p")
    return CHK(c_libusb.usb_claim_interface(libusb_handle, value))

def find_busses():
    c_libusb.usb_find_busses()

def find_devices():
    c_libusb.usb_find_devices()
    
def get_busses():
    return _CheckBus(c_libusb.usb_get_busses())

def init():
    c_libusb.usb_init()

def interrupt_read(libusb_handle,endpoint,buf,timeout):
    if not isinstance(libusb_handle,usb_dev_handle_p):
        raise ValueError("expected instance of usb_dev_handle_p")
    return CHK(c_libusb.usb_interrupt_read(libusb_handle, endpoint,
                                           buf, len(buf), timeout))
    
def interrupt_write(libusb_handle,endpoint,buf,timeout):
    if not isinstance(libusb_handle,usb_dev_handle_p):
        raise ValueError("expected instance of usb_dev_handle_p")
    return CHK(c_libusb.usb_interrupt_write(libusb_handle, endpoint,
                                            buf, len(buf), timeout))

def open(dev):
    if not isinstance(dev,device):
        raise ValueError('open() must be called with pylibusb.device instance')
    libusb_handle = c_libusb.usb_open(dev.cval)
    if not bool(libusb_handle):
        raise USBError("could not open device '%s'"%str(dev))
    return libusb_handle

def set_configuration(libusb_handle,value):
    if not isinstance(libusb_handle,usb_dev_handle_p):
        raise ValueError("expected instance of usb_dev_handle_p")
    return CHK(c_libusb.usb_set_configuration(libusb_handle, value))

def set_debug(val):
    c_libusb.usb_set_debug(val)

# Platform-specific (non-portable) additions

if sys.platform.startswith('linux'):
    def get_driver_np(libusb_handle,interface):
        if not isinstance(libusb_handle,usb_dev_handle_p):
            raise ValueError("expected instance of usb_dev_handle_p")
        LEN = 55
        name = ctypes.create_string_buffer(LEN)
        try:
            CHK(c_libusb.usb_get_driver_np(
                libusb_handle, interface, ctypes.byref(name), LEN))
        except USBNoDataAvailableError, err:
            return ''
        return name.value
    def detach_kernel_driver_np(libusb_handle,interface):
        if not isinstance(libusb_handle,usb_dev_handle_p):
            raise ValueError("expected instance of usb_dev_handle_p")
        return CHK(c_libusb.usb_detach_kernel_driver_np(libusb_handle, interface))

        
