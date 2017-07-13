# 1. Upload to PyPI:
# python3 setup.py sdist
# python3 setup.py sdist upload
#
# 2. Check if everything looks all right: https://pypi.python.org/pypi/SoMaJo
#
# 3. Go to https://github.com/tsproisl/SoMaJo/releases/new and
# create a new release

from os import path
from setuptools import setup

here = path.abspath(path.dirname(__file__))
with open(path.join(here, 'README.rst')) as fh:
    long_description = fh.read()

version = "1.4.0"

setup(
    name='SoMaJo',
    version=version,
    author='Thomas Proisl, Peter Uhrig',
    author_email='thomas.proisl@fau.de',
    packages=[
        'somajo',
        # 'somajo.test',
    ],
    scripts=[
        'bin/tokenizer',
    ],
    package_data={
        'somajo': ["abbreviations.txt",
                   "camel_case_tokens.txt",
                   "single_token_abbreviations.txt",
                   "tokens_with_plus_or_ampersand.txt"]
    },
    url="https://github.com/tsproisl/SoMaJo",
    download_url='https://github.com/tsproisl/SoMaJo/archive/v%s.tar.gz' % version,
    license='GNU General Public License v3 or later (GPLv3+)',
    description='A tokenizer and sentence splitter for German web and social media texts.',
    long_description=long_description,
    install_requires=[
        "regex",
    ],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
        'Natural Language :: German',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Topic :: Text Processing :: Linguistic',
    ],
)
