#include "usb.h"
#include <stdio.h>

#ifdef __unix__
#define TEST_PYLIBUSB_API void
#else
#define TEST_PYLIBUSB_API __declspec(dllexport)
#endif

TEST_PYLIBUSB_API print_endpoint_descriptor( struct usb_endpoint_descriptor* endpt) {
  printf("      usb_endpoint_descriptor at %p\n",endpt);
  printf("        bLength: %d\n",endpt->bLength);
  printf("        bDescriptorType: %d\n",endpt->bDescriptorType);
  printf("        bEndpointAddress: %d (%x)\n",endpt->bEndpointAddress,endpt->bEndpointAddress);
  printf("        wMaxPacketSize: %d\n",endpt->wMaxPacketSize);
}

TEST_PYLIBUSB_API print_interface_descriptor( struct usb_interface_descriptor* ifdscr) {
  int i;
  printf("    usb_interface_descriptor at %p\n",ifdscr);
  printf("      bLength: %d\n",ifdscr->bLength);
  printf("      bDescriptorType: %d\n",ifdscr->bDescriptorType);
  printf("      bInterfaceNumber: %d\n",ifdscr->bInterfaceNumber);
  printf("      bAlternateSetting: %d\n",ifdscr->bAlternateSetting);
  printf("      bNumEndpoints: %d\n",ifdscr->bNumEndpoints);
  printf("      bInterfaceClass: %d\n",ifdscr->bInterfaceClass);
  printf("      bInterfaceSubClass: %d\n",ifdscr->bInterfaceSubClass);
  printf("      bInterfaceProtocol: %d\n",ifdscr->bInterfaceProtocol);
  printf("      iInterface: %d\n",ifdscr->iInterface);
  for (i=0;i<ifdscr->bNumEndpoints;i++) {
    print_endpoint_descriptor(&(((struct usb_endpoint_descriptor *)(ifdscr->endpoint))[i]));
  }
}

TEST_PYLIBUSB_API print_interface( struct usb_interface* iface) {
  int i;
  printf("  usb_interface at %p\n",iface);
  printf("    num_altsetting: %d\n",iface->num_altsetting);
  for (i=0;i<iface->num_altsetting;i++) {
    print_interface_descriptor(&((iface->altsetting)[i]));
  }
}

TEST_PYLIBUSB_API print_config( struct usb_config_descriptor* cfg ) {
  int i;
  printf("usb_config_descriptor at %p\n",cfg);
  printf("  bLength: %d\n",cfg->bLength);
  printf("  bDescriptorType: %d\n",cfg->bDescriptorType);
  printf("  wTotalLength: %d\n",cfg->wTotalLength);
  printf("  bNumInterfaces: %d\n",cfg->bNumInterfaces);
  printf("  bConfigurationValue: %d\n",cfg->bConfigurationValue);
  printf("  iConfiguration: %d\n",cfg->iConfiguration);
  printf("  bmAttributes: %d\n",cfg->bmAttributes);
  printf("  MaxPower: %d\n",cfg->MaxPower);
  for (i=0;i<cfg->bNumInterfaces;i++) {
    print_interface(&((cfg->interface)[i]));
  }
}

TEST_PYLIBUSB_API print_device_descriptor( struct usb_device_descriptor *dd) {
  printf("usb_device_descriptor at %p\n",dd);
  printf("  bNumConfigurations: %d\n",dd->bNumConfigurations);
  printf("  idVendor: %x\n",dd->idVendor);
  printf("  idProduct: %x\n",dd->idProduct);
}

TEST_PYLIBUSB_API print_device(struct usb_device* dev) {
  int i;
  printf("usb_device at %p\n",dev);
  print_device_descriptor( &(dev->descriptor) );
  for (i=0;i<(dev->descriptor.bNumConfigurations);i++) {
    print_config(&(dev->config[i]));
  }
}
