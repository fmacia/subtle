#!/usr/bin/env python2
# -*- encoding: utf-8 -*-
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

import os
import sys
import shutil
from distutils.sysconfig import get_python_lib

if sys.argv[1] == '-install':
    if sys.platform == 'win32':
        #crear enlace en el escritorio
        ruta_main = os.path.join(get_python_lib(), 'subtle', '__main__.py')
        escritorio = get_special_folder_path("CSIDL_DESKTOPDIRECTORY")
        
        create_shortcut(ruta_main, 
                        'Descargador automático de subtítulos', 
                        os.path.join(escritorio, 'Subtle.lnk'),
                        '',
                        '',
                        os.path.join(get_python_lib(), 'subtle', 'icono_subtle.ico'),
                        0
                        )

elif sys.argv[1] == '-remove':
    if sys.platform == 'win32':
        #eliminar el enlace del escritorio
        ruta_enlace = os.path.join(get_special_folder_path("CSIDL_DESKTOPDIRECTORY"), 'Subtle.lnk')
        if os.path.exists(ruta_enlace):
            os.remove(ruta_enlace)
