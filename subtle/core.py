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

import os
import re
import sys
import guessit
#import i18n
#_ = i18n.language.ugettext #use ugettext instead of getttext to avoid unicode errors

import urllib.request, urllib.error, urllib.parse

#import de mis paquetes
from subtle.utils import *

class Web(object):
    """Métodos relacionados con las webs, clase padre"""
    
    def abrir_url(self, url):
        """Lee el contenido de una url"""
        #TODO comprobar qué devuelve el read de una url vacía
        #TODO ver qué pasa cuando no hay internet
        try:
            peticion = urllib.request.Request(url)
            #hay que decir que venimos de la propia página o algunos sitios no descargarán
            peticion.add_header('Referer', self.sitio)
            #mentimos sobre el user agent para que no piense que somos un bot
            peticion.add_header('User-Agent', 'Mozilla/5.0')
            #enviamos la petición
            html = urllib.request.urlopen(peticion).read()
            return html

        except urllib.error.HTTPError as e:
            if e.code == 404:
                self.video.notificacion.n('No existe la página %s' % self.sitio, False)
            elif e.code == 403:
                self.video.notificacion.n('Acceso no permitido a %s' % self.sitio, False)
            else:
                self.video.notificacion.n('Ha habido un problema al conectar a %s' % self.sitio, False)
            return False

    def descargar(self, enlace=None):
        subs = self.abrir_url(self.link)
        if subs:
            self.video.guardar_archivo(subs)
            return 0
        else:
            return 1

    def sacar_id(self):
        pass

    def sacar_titulo(self):
        pass
    
    def existe_sub(self):
        pass
    
    def idioma(self):
        pass
    
    def version(self):
        pass

    def comprobar_version(self, version_video, version_web):
        """Comprueba si la versión de la web es la misma que la del archivo y 
        las equivalencias entre versiones"""
        if not version_video:
            version_a_buscar = 'lol|sys|dimension|afg|xii|immerse|asap'
        elif version_video.lower() in ('lol', 'sys', 'dimension', 'afg'):
            version_a_buscar = 'lol|sys|dimension|afg'
        elif version_video.lower() in ('xii', 'immerse', 'asap'):
            version_a_buscar = 'xii|immerse|asap'
        else:
            version_a_buscar = version_video
         
        return re.search(version_a_buscar, version_web, re.IGNORECASE)

def ruta_icono():
    """Devuelve la ruta del icono del programa"""
    if sys.platform == 'win32':
        rutas = (os.path.join(os.getcwd(), 'subtle.ico'))
    else:
        #posibles sitios donde puede encontrarse el icono
        rutas = ('/usr/share/pixmaps/subtle.ico', os.path.normpath(os.path.join(os.path.realpath(__file__), '..', 'subtle.ico')))

    for ruta in rutas:
        if os.path.exists(ruta):
            return ruta
    return None

class Video(object):
    """Métodos relacionados con los archivos"""
    def __init__(self, args):
        #se usa el decode para que no pete con las tildes (se recibe como str porque viene del argparser)
        self.args = args
        self.notificacion = Notificacion(titulo = 'Subtle', icono = ruta_icono())
    
    def cargar_archivo(self, archivo):
        """Obtener los datos del nuevo archivo"""
        #se usa el decode para que no pete con las tildes (se recibe como str porque viene del argparser)
        #TODO: convertir a unicode para que no pete con las tildes
        #self.archivo = archivo.decode('utf-8')
        self.archivo = archivo
        self.ruta_original = os.path.dirname(self.archivo)
        #OPCION: -F - Elegir la ruta de descarga                 
        self.ruta = self.ruta_original if not self.args.folder else self.args.folder
        self.nombre_video, self.extension = os.path.splitext(os.path.basename(self.archivo))
        self.notificacion.set_titulo(self.nombre_video + self.extension)
        #sacar hash y bytesize del archivo
        self.hashFile()
        #rellenar datos del archivo
        self.guess()
    
    def guess(self):
        """Extrae los datos del nombre del archivo y los carga en las variables"""
        #TODO: esto se podria quitar, supongo, es mas que nada una lista de variables
        self.version = None
        self.serie = None
        self.temporada = None
        self.episodio = None
        self.titulo = None
        self.codec = None
        self.formato = None
        self.tamano = None
        self.tipo = None #Episodio, película o desconocido

        #uso del módulo guessit para sacar los datos a partir del nombre del archivo
        guess = guessit.guess_video_info(self.archivo)
        if guess['type'] == 'episode':
            self.version = guess.get('releaseGroup')
            self.serie = guess.get('series')
            self.temporada = guess.get('season')
            self.episodio = guess.get('episodeNumber')
            self.titulo = guess.get('title')
            self.codec = guess.get('videoCodec')
            self.formato = guess.get('format')
            self.tamano = guess.get('screenSize')
            self.tipo = guess.get('type')

            self.buscar_por_nombre = True if self.version is not None else False
        #cuando hay nombres raros, tipo cuacuacua.avi, entra aquí
        elif guess['type'] == 'movie':
            self.tipo = guess.get('type')
            self.titulo = guess.get('title')
            self.buscar_por_nombre = False
        else:
            self.buscar_por_nombre = False
            
        return 0 if self.buscar_por_nombre == True else 1
    
    def guardar_archivo(self, datos):
        """Crea un archivo a partir de los datos de una variable"""
        try:
            #renombrar archivo de vídeo
            if self.args.title:
                self.renombrar(self.titulo)

            archivo = open(os.path.join(self.ruta, '%s.srt' % self.nombre_video), 'wb')
            archivo.write(datos)
            archivo.close()
            self.notificacion.n('Guardando archivo de subtítulos.')
            return 0
        except IOError as e:
            mensaje = "Ha ocurrido un error al guardar el archivo."
            mensaje += excepciones_archivos(e)
            self.notificacion.n(mensaje)
            return 2
    
    def renombrar(self, nuevo_nombre, insertar = True):
        """Renombra el archivo"""
        try:
            #No renombrar completamente, insertar título en el nombre actual
            if insertar:
                #Nombre nuevo = serie+temporada+episodio+NOMBRE_CAPI+resto del nombre
                #expresión que saca la primera parte de la cadena
                patron = re.compile('.*E\d\d|.*\dX\d\d', re.IGNORECASE)
                #extraer la primera parte de la cadena
                cadena1 = re.search(patron, self.nombre_video).group(0)
                #extraer la segunda parte de la cadena
                cadena2 = re.sub(patron, '', self.nombre_video)
                #rearmar el nombre del archivo
                self.nombre_video = '.'.join((cadena1, nuevo_nombre.replace(' ', '.') + cadena2))
            else:
                self.nombre_video = nuevo_nombre
            
            #cambiar el nombre al archivo original
            if os.path.exists(self.archivo):
                os.rename(self.archivo, os.path.join(self.ruta_original, self.nombre_video + self.extension))
            return 0
        except IOError as e:
            mensaje = "Ha ocurrido un error al renombrar el archivo."
            mensaje += excepciones_archivos(e)
            self.notificacion.n(mensaje)
            return 2
    
    def cambiar_ruta(self, nueva_ruta):
        """Cambia la ruta en la que se guardará el archivo de subtítulos"""
        self.ruta = nueva_ruta
        return 0
    
    def existe_archivo_subs(self):
        """Comprueba si ya existe un archivo de subtítulos"""
        if os.path.exists(os.path.join(self.ruta, '%s.srt' % self.nombre_video)):
            return True
        else:
            return False

    def descomprimir(self, archivo):
        """Descomprime un archivo gzip"""
        import zlib
        try:
            return zlib.decompress(archivo, 16+zlib.MAX_WBITS)
        except:
            self.notificacion.n('No se ha podido descomprimir el archivo.', False, 40)
            return 0

    def hashFile(self):
        """Crea el hash de un archivo, para buscar en Opensubtitles (código cogido de su página y adaptado)"""
        #@see http://trac.opensubtitles.org/projects/opensubtitles/wiki/HashSourceCodes
        #por alguna razón una división de enteros me devuelve un float...
        import struct
        try:

            self.bytesize = os.path.getsize(self.archivo)
            longlongformat = 'q'  # long long
            bytesize = struct.calcsize(longlongformat)

            f = open(self.archivo, "rb")

            filesize = os.path.getsize(self.archivo)
            hash = filesize

            if filesize < 65536 * 2:
                return "SizeError"

            for x in range(int(65536/bytesize)):
                buffer = f.read(bytesize)
                (l_value,)= struct.unpack(longlongformat, buffer)
                hash += l_value
                hash = hash & 0xFFFFFFFFFFFFFFFF #to remain as 64bit number


            f.seek(max(0,filesize-65536),0)
            for x in range(int(65536/bytesize)):
                buffer = f.read(bytesize)
                (l_value,)= struct.unpack(longlongformat, buffer)
                hash += l_value
                hash = hash & 0xFFFFFFFFFFFFFFFF

            f.close()
            returnedhash =  "%016x" % hash
            self.hash = returnedhash
            self.buscar_por_hash = True
            return self.hash

        except(IOError):
            self.hash = 'IOError'
            self.bytesize = 0
            self.buscar_por_hash = False
            return self.hash

    def __str__(self):
        return self.__unicode__()
    
    def __unicode__(self):        
        #episodio de una serie
        if self.tipo == 'episode':
            variables = (self.ruta, self.nombre_video,
                    self.extension, self.tipo, self.serie, 
                    self.temporada, self.episodio,
                    self.version, self.codec,
                    self.titulo, 
                    self.formato, self.tamano)
            variables = list(map(intercambiar, variables))
            datos = ("Ruta del archivo: %s\nNombre del vídeo: %s\nExtensión: %s\nTipo: %s\n"
            "Serie: %s\nTemporada: %s\nEpisodio: %s\nVersión: %s\nCódec: %s\nNombre del episodio: %s\n"
            "Formato: %s\nTamaño pantalla: %s\n") % tuple(variables)
        #película
        elif self.tipo == 'movie':
            variables = (self.ruta, self.nombre_video, self.extension, self.titulo)
            variables = list(map(intercambiar, variables))
            datos = "Ruta del archivo: %s\nNombre del vídeo: %s\nExtensión: %s\nTipo de vídeo: Película\nTítulo: %s\n" % tuple(variables)
        #desconocido
        else:
            datos = "%s\nNo se han podido extraer los datos." % self.archivo
        return datos

try:
    from watchdog.events import FileSystemEventHandler
    class AddedHandler(FileSystemEventHandler):
        """Controla qué hacer cuando aparecen nuevos archivos"""
        def __init__(self, args):
            self.args = args
    
        def on_created(self, event):
            get_subtitles(event.src_path, self.args)
        
        def on_moved(self, event):
            get_subtitles(event.dest_path, self.args)
    MONITORIZACION = True
except:
    MONITORIZACION = False
