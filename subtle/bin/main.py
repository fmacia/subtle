#!/usr/bin/env python
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
import argparse
import os
import sys
import time


#Añadir la carpeta principal del programa al PYTHONPATH para poder hacer los import
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(__file__)), '../..')))

from subtle.core import *
from subtle.utils import *
import subtle.webs as webs

nombre_programa = 'Subtle'
version_programa = '0.5'
autor_programa = 'Fran Macía (fj.macia.espin@gmail.com)'

def main():    
    """Controla si se monitoriza una carpeta o se buscan subtítulos normalmente"""

    parser = argumentos()
    args = parser.parse_args()
    
    video = Video(args)
    
    if args.videos:
        #OPCIÓN -d: monitorizar carpeta
        if args.daemon:
            if os.path.isdir(args.videos[0]):
                video.notificacion.n('Monitorizando carpeta %s.' % args.videos[0].decode('utf-8'), kwargs=args.__dict__)
                ret = monitorizar()
                if ret == 0:
                    video.notificacion.n('Finalizando monitorización.')
                else:
                    video.notificacion.n('No se ha podido monitorizar la carpeta (se requiere la librería python-watchdog).', False, 40)
            else:
                video.notificacion.n('Se debe introducir una carpeta a monitorizar.')
        else:
            #funcionamiento normal
            ret = 0
            for archivo in args.videos:
                #TODO: hacer que no sea recursivo por defecto (que haya que poner opcion -r)
                #TODO: tambien hacer que sea recursivo de verdad -> crear funcion listar archivos (recursiva)
                if os.path.isdir(archivo):
                    #carpeta
                    lista_archivos = listar_archivos(archivo)
                    #sacar lista de archivos (funcion recursiva)
                    for sub_archivo in lista_archivos:
                        ret = get_subtitles(video, sub_archivo, args)
                else:
                    #archivo
                    ret = get_subtitles(video, archivo, args)
        return ret
    else:
        parser.print_help()
        return 0

def listar_archivos(carpeta):
    """Devuelve una lista con los archivos de una carpeta"""
    ret = []
    if os.path.exists(carpeta):
        for(_, _, archivos) in os.walk(carpeta):
            ret.extend(archivos)
    else:
        print("Carpeta inexistente.")
    return ret

def monitorizar(args):
    """Monitoriza una carpeta en espera de que aparezcan nuevos archivos"""
    try:
        from watchdog.observers import Observer
        event_handler = AddedHandler(args)
        observer = Observer()
        observer.schedule(event_handler, args.videos[0], recursive=True)
        observer.start()
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            #TODO: FUTURO: hacer que interrumpa la monitorizacion de otra manera ¿otra funcion?
            observer.stop()
        observer.join()
        return 0
    except:
        return 1
    
def argumentos():
    """Parsea los argumentos que le lleguen al programa"""
    
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
    parser.add_argument('-d', '--daemon', action='store_true',
                      help = 'Ejecutar en segundo plano y autodescargar subtítulos cuando aparezcan vídeos nuevos')
    parser.add_argument('-l', '--language',
                      help = 'Especificar el idioma. Por defecto, español')
    parser.add_argument('-a', '--annotations', action='store_true',
                      help = 'Especificar si se quieren subtítulos con anotaciones')
    parser.add_argument('-V', '--version', action='version', version='%s versión %s, creado por %s' % (nombre_programa, version_programa, autor_programa),
                      help = 'Muestra la versión del programa')
    parser.add_argument('-F', '--folder',
                      help = 'Especificar la ruta donde se descargarán los subtítulos')
    parser.add_argument('videos', nargs = '*')
    return parser
    
def get_subtitles(video, archivo, args):
    """Busca subtítulos para un archivo"""
    
    ret = None
    #extraer los datos a partir del archivo
    video.cargar_archivo(archivo)
    #mostrar en terminal el nombre del vídeo como separador
    print('\n')
    video.notificacion.n("Vídeo: %s" % (video.nombre_video + video.extension), False)
    video.notificacion.n(separador("Vídeo: %s" % (video.nombre_video + video.extension), pegar = False), False, -1)
    
    if not args.info:
        if args.force or not os.path.exists(os.path.join(video.ruta, '%s.srt' % video.nombre_video)):
            if video.buscar_por_hash or video.buscar_por_nombre:
                #video.notificacion.n('Buscando subtítulos...')
                if not args.web:
                    #buscar subtítulos en los distintos sitios
                    for sitio in webs.sitios:
                        web = getattr(webs, sitio)(video)
                        ret = web.get_subtitles()
                        if ret == 0:
                            break
                #OPCIÓN -w: selección manual de web
                else:
                    web_recortada = recortar_url(args.web)
                    if web_recortada in webs.sitios:
                        web = getattr(webs, web_recortada)(video)
                        ret = web.get_subtitles()
                    else:
                        video.notificacion.n('No se pueden buscar subtítulos en %s' % args.web)
            else:
                video.notificacion.n('No se puede buscar subtítulos para este archivo.')
                ret = 1
            if ret == 1:
                video.notificacion.n('No se han encontrado subtítulos.')
            return ret
        else:
            video.notificacion.n('Ya existen los subtítulos.')
    #OPCIÓN -i: información sobre el vídeo
    else:
        video.notificacion.n(video.__str__())
        ret = 0
    
    return ret

if __name__ == '__main__':
    sys.exit(main())
