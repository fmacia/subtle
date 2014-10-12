#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright 2013 Francisco Jesús Macía Espín <fjmaciaespin@gmail.com>

'''
Subtle is an automatic subtitle downloader for videos
Copyright (C) 2013 Francisco Jesús Macía Espín (fmacia)

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

#para lanzarlo desde consola
entry_points = {
    'console_scripts' : [
        'subtle = subtle.bin.main:main'
    ]
}

#TODO: en scripts meter un sh para el .desktop (si es root en usr share)

config = dict(
    description='Descargador automático de subtítulos',
    author='Francisco Jesús Macía Espín(fmacia)',
    url='digitalwaste.wordpress.com',
    download_url='http://fmacia.github.com/subtle/',
    author_email='fjmaciaespin@gmail.com',
    version='0.5',
    install_requires=['beautifulsoup4', 'guessit', 'watchdog'],
    entry_points=entry_points,
    #packages=['subtle', 'subtle.webs', 'subtle.bin', 'bs4', 'guessit', 'guessit.transfo'],
    packages=['subtle', 'subtle.webs', 'subtle.bin'],
    include_package_data=True,
    name='subtle',
    license='GPL v3',
    long_description=open('README.rst').read(),
    platforms=['UNIX', 'Windows'],
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
    scripts=['subtle/bin/postinstalacion.py']
    )

setup(**config)
