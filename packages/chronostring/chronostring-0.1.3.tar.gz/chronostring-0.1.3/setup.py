import os
from setuptools import setup, find_packages

setup(
    name='chronostring',
    version=open('VERSION').read(),
    description='Extracts and structures dates and times from natural French text.',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    author='Jean-Marie Favreau',
    url='https://forge.chapril.org/jmtrivial/chronostring',
    author_email='jeanmarie.favreau@free.fr',
    packages=find_packages(),
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: GNU Affero General Public License v3',
    ],
    python_requires='>=3.7',
)
