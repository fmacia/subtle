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

from __future__ import unicode_literals
import sys
import argparse
from core import Video
from utils import *

def main():
    """
    Función principal del script
    """
    
    #parsear los parámetros que se le pasan al programa
    parser = argparse.ArgumentParser(
        description = 'Descarga archivos de subtítulos para series',
        usage = 'Uso: %(prog)s [opciones] video1 [video2 ...]',
        add_help = False)
    parser.add_argument('-v', '--verbose', action='store_true',
                      help = 'Ver mensajes de depuración')
    parser.add_argument('-q', '--quiet', action='store_true',
                      help = 'No mostrar nada por pantalla')
    parser.add_argument('-h', '--help', action='store_true',
                      help = 'Muestra este mensaje de ayuda')
    parser.add_argument('-i', '--info', action='store_true',
                      help = 'Mostrar la información del vídeo y salir')
    parser.add_argument('-f', '--force', action='store_true',
                      help = 'Forzar sobreescritura de subtítulos ya existentes')
    parser.add_argument('-t', '--title', action='store_true',
                      help = 'Añade el título al nombre del archivo de vídeo si no lo tiene')
    parser.add_argument('-c', '--check', action='store_true',
                      help = 'Solo comprueba la existencia del subtítulo sin descargarlo')
    parser.add_argument('-w', '--web',
                      help = 'Especificar directamente la web en la que buscar')
    parser.add_argument('-d', '--daemon',
                      help = 'Ejecutar en segundo plano y autodescargar subtítulos cuando aparezcan videos nuevos')
    parser.add_argument('-r', '--recursive',
                      help = 'Descargar subtítulos para los vídeos de subcarpetas')
    parser.add_argument('-l', '--language',
                      help = 'Especificar el idioma -> es: Español de España, lat: Español de Latinoamérica, en: Inglés')
#    parser.add_argument('-a', '--annotations', action='store_true',
#                      help = 'Especificar si se quieren subtítulos con anotaciones')
    parser.add_argument('-V', '--version', action='version', version='%(prog)s versión 0.3',
                      help = 'Muestra la versión del programa')
    parser.add_argument('-F', '--folder',
                      help = 'Especificar la ruta donde se descargarán los subtítulos')
    parser.add_argument('videos', nargs='*')
    args = parser.parse_args()

    if args.help:
        parser.print_help()
        return 0
    elif args.videos:
        ret = 0
        for video in args.videos:
            #si es una carpeta
            #if os.path.isdir(video):
                #recorrer todos los archivos
            #si es un video    
            capi = Video(video, args)
            if capi.cargar_datos() == 0:
                #mostrar en terminal los datos del vídeo como separador
                cad_separador = 'Vídeo: %s' % (capi.nombre_video + capi.extension)
                if not args.quiet:
                    print("%s\n%s" % (cad_separador, separador(cad_separador)))
                
                #OPCIÓN -i: mostrar info sobre el vídeo
                if args.info:
                    capi.notificar(capi.__str__())
                    continue
                
                #OPCIÓN -w: hacer un diccionario de webs que se pueden usar
                #si lo que se pasa por aprámetro no está ahi, mensaje y salir
                #si está, ejecutar esa descarga
                #si no se especifica, probar primero de subtitulos.es y luego de addic7ed
                #ESTO ES LO QUE MÁS URGE REFACTORIZAR
                if args.web:
                    #listado de páginas disponibles
                    webs = ('http://subtitulos.es', 'http://www.addic7ed.com')
                    
                    if args.web in webs:
                        if args.web == webs[0]:
                            return capi.descargar_sub_subtitulos_es()
                        else:
                            return capi.descargar_sub_addic7ed()
                    capi.notificar('Sitio web no reconocida por el programa')
                    ret = 2

                #probar a descargar de subtitulos.es primero. si no, de addic7ed
                subs_es = capi.descargar_sub_subtitulos_es()
                add = 0
                if subs_es == 1:
                    add = capi.descargar_sub_addic7ed()

                if add == 1:
                    ret = 1
                elif subs_es == 2 or add == 2:
                    ret = 2
                else:
                    ret = 0
            else:
                ret = 3
        if ret == 1:
            capi.notificar('No se han encontrado subtítulos para %s' % capi.datos())
        return ret
    else:
        parser.print_help()
        return 0


if __name__ == '__main__':
    sys.exit(main())
