#!/usr/bin/env python2
# -*- coding: utf-8 -*-
try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

entry_points = {
    'console_scripts' : [
        'subtle = subtle.subtle:main'
    ]
}

config = dict(
    description='Descargador automático de subtítulos',
    author='Francisco Jesús Macía Espín(fmacia)',
    url='digitalwaste.wordpress.com',
    download_url='https://github.com/fmacia/subtle',
    author_email='fjmaciaespin@gmail.com',
    version='0.2',
    install_requires=['nose', 'beautifulsoup4', 'guessit'],
    entry_points=entry_points,
    packages=['subtle', 'tests'],
    scripts=[],
    name='subtle',
    license='GPL v3',
    long_description= open('README.txt').read(),
    platforms= ['UNIX', 'Windows'],
    classifiers= 
        [
            'Development Status :: 3 - Alpha',
            'Environment :: Console',
            'Intended Audience :: End Users/Desktop',
            'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
            'Natural Language :: Spanish',
            'Operating System :: POSIX :: Linux',
            'Operating System :: Microsoft :: Windows',
            'Programming Language :: Python :: 2',
            'Programming Language :: Python :: 2.7',
            'Topic :: Multimedia :: Video',
            'Topic :: Software Development :: Libraries :: Python Modules',
            
        ],
    )

setup(**config)