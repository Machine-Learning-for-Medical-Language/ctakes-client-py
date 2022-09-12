try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

import os
here = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_descr = f.read()

setup(
    name='ctakesclient',
    version='1.0.0',
    description='cTAKES client support for accessing cTAKES COVID REST service',
    long_description=long_descr,
    url='https://github.com/Machine-Learning-for-Medical-Language/ctakes-client-py',
    author='Andy McMurry, PhD',
    license='Apache License 2.0',
    keywords='Apache cTAKES clinical NLP Unified Medical Language System',
    include_package_data=True,
    packages=["ctakesclient", "tests"]
)
