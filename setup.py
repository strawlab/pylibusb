from setuptools import setup

setup(name='pylibusb',
      description='libusb wrapper (ctypes based)',
      url='https://code.astraw.com/projects/pylibusb',
      version='0.1',
      author='Andrew Straw',
      author_email='strawman@astraw.com',
      packages = ['pylibusb'],
      install_requires = ['ctypes'],
      zip_safe=True)
