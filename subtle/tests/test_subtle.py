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
from subtle.core import Video
from subtle.utils import Notificacion


def setup():
    print "SETUP!"

def teardown():
    print "TEAR DOWN!"

#Tests de notificaciones
def test_Notificacion_comprobar_burbuja():
    """El notificador se encuentra"""
    #objeto notificación
    n = Notificacion()
    assert n.comprobar_burbuja() == 0
    
def test_Notificacion_comprobar_burbuja_error():
    """El notificador no se encuentra"""
    #objeto notificación
    n = Notificacion('notificador_no_existente')
    assert n.comprobar_burbuja() == 1
    
def test_Notificacion_notificar():
    """Muestra una notificación de prueba"""
    n = Notificacion()
    n.n('Hola Don Pepito')
    
#FIN tests de notificaciones

#def test_cargar_datos():
#    """Carga de datos con información válida
#    debe mostrarse una burbuja de notificación con los datos del vídeo"""
#    a = Video('Futurama.S07E14.HDTV.x264-EVOLVE', [])
#    print('a')
