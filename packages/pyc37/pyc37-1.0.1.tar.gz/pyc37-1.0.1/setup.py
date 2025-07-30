import sys
from setuptools import setup, find_packages


if not sys.version_info[0] == 3:
    sys.exit("[ERROR] Package syncrhrophasor is only available for Python 3.")


setup(name = 'pyc37',
      packages = find_packages(),
      version = '1.0.1',
      description = 'Synchrophasor module represents implementation of IEEE C37.118.2 standard in Python.',
      author = 'Ahmad Kammonah',
      author_email = 'contact@ahmadkammonah.com',
      license = "BSD-3",
      url = 'https://github.com/ahmadkammonah/pyc37',
      download_url = 'https://github.com/iicsys/pypmu/tarball/1.0.0-alpha',
      keywords = ['pyc37', 'pypmu', 'pdc', 'pmu', 'power-systems', 'ieeec37118'],
      classifiers=[
                    "Development Status :: 3 - Alpha",
                    "Intended Audience :: Science/Research",
                    "Programming Language :: Python :: 3",
                    "Topic :: Scientific/Engineering",
                    "License :: OSI Approved :: BSD License",
      ],
)