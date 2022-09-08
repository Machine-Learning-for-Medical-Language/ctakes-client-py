try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

import os
here = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_descr = f.read()

setup(
    name='ctakes-client',
    version='0.2.4',
    description='cTAKES client support for accessing cTAKES COVID REST service',
    long_description=long_descr,
    url='https://github.com/comorbidity/ctakes-client-python',
    author='Andy McMurry, PhD',
    license='Apache License 2.0',
    keywords='Apache cTAKES clinical NLP Unified Medical Language System',
    include_package_data=True,
    packages=["ctakes", "tests"]
)
