#!/usr/bin/env python2
# -*- coding: utf-8 -*-
# Copyright 2013 Francisco Jesús Macía Espín <fjmaciaespin@gmail.com>

#caso de prueba: descargar de subs_es
#caso de prueba: descargar de addic7ed
#caso de prueba probar a abrir urls que existan y que no existan
#caso de prueba: guardar archivos donde se tengan permisos y donde no

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

#import sys 
#import os
#sys.path.insert(0, os.path.abspath('..'))

from nose.tools import *
from subtle import Video


def setup():
    print "SETUP!"

def teardown():
    print "TEAR DOWN!"

def test_basic():
    a = Video('aaa')
    print "I RAN!"
