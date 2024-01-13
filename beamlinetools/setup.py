import sys
from os import path

from setuptools import find_packages, setup

import versioneer

setup(name='beamlinetools',
      version=versioneer.get_version(),
      cmdclass=versioneer.get_cmdclass(),
      description='A collection of tools and plans specific to BEAMLINE_name ',
      url='https://gitlab.helmholtz-berlin.de/bessyII/bluesky/INSERT_URL',
      author='Will Smith, Simone Vadilonga, Sebastian Kazarski',
      author_email='simone.vadilonga@helmholtz-berlin.de',
      # license='MIT',
      packages=find_packages(exclude=['docs', 'tests']),
      install_requires=[
          'ophyd',
          'numpy',
          'anyio',
          'httpx',
          'tiled',
          'orjson'
      ]
      # zip_safe=False
)
