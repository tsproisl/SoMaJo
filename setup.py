# 1. Upload to PyPI:
# python3 setup.py sdist
# twine upload dist/*
#
# 2. Check if everything looks all right: https://pypi.python.org/pypi/SoMaJo
#
# 3. Go to https://github.com/tsproisl/SoMaJo/releases/new and
# create a new release

from os import path
from setuptools import setup

version = {}
with open("somajo/version.py") as fh:
    exec(fh.read(), version)

here = path.abspath(path.dirname(__file__))
with open(path.join(here, 'README.rst')) as fh:
    long_description = fh.read()

setup(
    name='SoMaJo',
    version=version["__version__"],
    author='Thomas Proisl, Peter Uhrig',
    author_email='thomas.proisl@fau.de',
    packages=[
        'somajo',
        # 'somajo.test',
    ],
    scripts=[
        'bin/somajo-tokenizer',
    ],
    package_data={
        'somajo': ["abbreviations_de.txt",
                   "abbreviations_en.txt",
                   "camel_case_tokens.txt",
                   "eos_abbreviations.txt",
                   "non-breaking_hyphenated_words_en.txt",
                   "non-breaking_prefixes_en.txt",
                   "non-breaking_suffixes_en.txt",
                   "single_token_abbreviations_de.txt",
                   "single_token_abbreviations_en.txt",
                   "tokens_with_plus_or_ampersand.txt"]
    },
    url="https://github.com/tsproisl/SoMaJo",
    download_url='https://github.com/tsproisl/SoMaJo/archive/v%s.tar.gz' % version["__version__"],
    license='GNU General Public License v3 or later (GPLv3+)',
    description='A tokenizer and sentence splitter for German and English web and social media texts.',
    long_description=long_description,
    install_requires=[
        "regex>=2019.02.18",
    ],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
        'Natural Language :: German',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Topic :: Text Processing :: Linguistic',
    ],
)
