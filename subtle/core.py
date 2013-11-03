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
import os
import re
import sys
import guessit
try:
    #python2
    import urllib2
    python_vers = 2
except:
    #python3
    import urllib.request, urllib.error, urllib.parse
    python_vers = 3

#import de mis paquetes
from utils import *
from watchdog.events import FileSystemEventHandler

class Web(object):
    """Métodos relacionados con las webs, clase padre"""
    
    def abrir_url(self, url):
        """Lee el contenido de una url"""
        #TODO comprobar qué devuelve el read de una url vacía
        #TODO ver qué pasa cuando no hay internet
        try:
            if python_vers == 2:
                html = urllib2.urlopen(url).read()
            else:
                html = urllib.request.urlopen(url).read()
            return html
        except urllib2.HTTPError as e:
            if e.code == 404:
                self.video.notificacion.n('No existe la página que se ha buscado.')
        except urllib2.URLError as e:
            self.video.notificacion.n('No se ha podido conectar a %s.' % self.sitio, False)
            return False

    def descargar(self):
        #TODO: soporte de python 3
        request = urllib2.Request(self.link)
        #hay que decir que venimos de la propia página o no descargará
        request.add_header('Referer', self.sitio)
        subs = self.abrir_url(request)
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
        if version_video.lower() in ('lol', 'sys', 'dimension', 'afg'):
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
    def __init__(self, archivo, args):
        #se usa el decode para que no pete con las tildes (se recibe como str porque viene del argparser)
        self.args = args
        self.archivo = archivo.decode('utf-8')
        self.ruta_original = os.path.dirname(self.archivo)
        #OPCION: -F - Elegir la ruta de descarga                 
        self.ruta = self.ruta_original if not self.args.folder else self.args.folder
        self.nombre_video, self.extension = os.path.splitext(os.path.basename(self.archivo))
        #icono
        ico = ruta_icono()
        self.notificacion = Notificacion(titulo = self.nombre_video + self.extension, icono = ico)
        #sacar hash y bytesize del archivo
        self.hashfile()
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
            self.notificacion.n('No se ha podido descomprimir el archivo')
            return 0

    def hashfile(self):
        """Crea el hash de un archivo, para buscar en Opensubtitles (código cogido de su página)"""
        import struct
         
        try:
            self.bytesize = os.path.getsize(self.archivo)
            
            longlongformat = str('q')  # long long 
            bytesize = struct.calcsize(longlongformat)
                    
            f = open(self.archivo, "rb") 
                    
            filesize = os.path.getsize(self.archivo) 
            hash_num = filesize 
                
            if filesize < 65536 * 2: 
                return "SizeError" 
             
            for x in range(65536/bytesize): 
                buff = f.read(bytesize) 
                (l_value,)= struct.unpack(longlongformat, buff)  
                hash_num += l_value 
                hash_num = hash_num & 0xFFFFFFFFFFFFFFFF #to remain as 64bit number  
                     

            f.seek(max(0,filesize-65536),0) 
            for x in range(65536/bytesize): 
                    buff = f.read(bytesize) 
                    (l_value,)= struct.unpack(longlongformat, buff)  
                    hash_num += l_value 
                    hash_num = hash_num & 0xFFFFFFFFFFFFFFFF 
             
            f.close() 
            returnedhash =  "%016x" % hash_num
            self.hash = returnedhash 
            self.buscar_por_hash = True
            return returnedhash
    
        except:
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
            variables = map(intercambiar, variables)
            datos = ("Ruta del archivo: %s\nNombre del vídeo: %s\nExtensión: %s\nTipo: %s\n"
            "Serie: %s\nTemporada: %s\nEpisodio: %s\nVersión: %s\nCódec: %s\nNombre del episodio: %s\n"
            "Formato: %s\nTamaño pantalla: %s\n") % tuple(variables)
        #película
        elif self.tipo == 'movie':
            variables = (self.ruta, self.nombre_video, self.extension, self.titulo)
            variables = map(intercambiar, variables)
            datos = "Ruta del archivo: %s\nNombre del vídeo: %s\nExtensión: %s\nTipo de vídeo: Película\nTítulo: %s\n" % tuple(variables)
        #desconocido
        else:
            datos = "%s\nNo se han podido extraer los datos." % self.archivo
        return datos

class AddedHandler(FileSystemEventHandler):
    """Controla qué hacer cuando aparecen nuevos archivos"""
    def __init__(self, args):
        self.args = args

    def on_created(self, event):
        get_subtitles(event.src_path, self.args)
    
    def on_moved(self, event):
        get_subtitles(event.dest_path, self.args)
