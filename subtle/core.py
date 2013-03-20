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
from bs4 import BeautifulSoup
import os
import re
import argparse
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

class Video:
    #TODO: documentar errorlevels
    #0 = todo correcto
    #1 = no se ha podido extraer los datos del video o no hay idioma (o este no está reconocido)
    #2 = error
    #3 = no se han cargado los datos
    """
    Clase del vídeo
    """
    def __init__(self, archivo, args):
        self.archivo = '%s' % archivo
        self.ruta = ''
        self.nombre_video = ''
        self.extension = ''
        self.version = ''
        self.serie = ''
        self.temporada = None
        self.episodio = None
        self.nombre_episodio = ''
        self.enlace_sub = ''
        self.codec = '' 
        self.formato = ''
        self.tamano = ''
        self.tipo = ''
        
        self.args = args
    
    def cargar_datos(self):
        """
        Función que se encarga de extraer los datos del archivo e insertarlos en las variables
        """
        #datos relativos al archivo
        self.ruta = os.path.dirname(self.archivo)
        self.nombre_video, self.extension = os.path.splitext(os.path.basename(self.archivo))

        #uso del módulo guessit para sacar los datos a partir del nombre del archivo
        guess = guessit.guess_video_info(self.archivo)
        if guess['type'] != 'unknown':
            self.version = guess.get('releaseGroup')
            self.serie = guess.get('series')
            self.temporada = guess.get('season')
            self.episodio = guess.get('episodeNumber')
            self.nombre_episodio = guess.get('title') if guess.get('title') is not None else ''
            self.codec = guess.get('videoCodec')
            self.formato = guess.get('format')
            self.tamano = guess.get('screenSize') if guess.get('screenSize') is not None else ''
            self.tipo = guess.get('type')
            
            #idioma
            return self.reconocer_idioma(self.args.language)
        else:
            self.notificar('No se ha podido extraer los datos de "%s"\n' % self.archivo)
            return 1
        
    def reconocer_idioma(self, idioma):
        #TODO: habrá que hacer un reconocimiento de idioma por cada página
        #TODO: añadir idiomas
        idiomas = {
                   'es' : 'España',
                   'lat' : 'Latinoamérica',
                   'en' : 'English'
                   }
        if idioma:
            if idioma.lower() in idiomas:
                self.idioma = idiomas[idioma.lower()]
                return 0
            else:
                self.notificar('No se ha podido detectar el idioma')
                return 1
        #valor por defecto si no se especifica idioma
        else:
            self.idioma = 'España'
            return 0
        
    def descargar_sub_addic7ed(self):
        """
        Función que se encarga de descargar los subtítulos de addic7ed
        """
        sitio = 'http://www.addic7ed.com'
        #sacar el id del idioma elegido
        id_idioma = ''
        if self.idioma == 'España':
            id_idioma = '|5|'
        elif self.idioma == 'English':
            id_idioma = '|1|'
        
        if id_idioma == '':
            self.notificar('No se ha podido detectar el idioma')
            return 1

        serie_sin_espacios = self.serie.replace(' ', '_')
        
        #sacar id de la serie
        url_busqueda = '%s/search.php?search=%s' % (sitio, serie_sin_espacios)
        html_busqueda = self.abrir_url(url_busqueda)
        if html_busqueda:
            sopa_busqueda = BeautifulSoup(html_busqueda)
            titulo_web = sopa_busqueda.find('span', {'class' : 'titulo'})
            if titulo_web:
                id_serie = re.sub('/show/', '' , titulo_web.a['href'])
            else:
                self.notificar('No se ha encontrado el vídeo en %s' % sitio, False)
                return 1

            #buscar enlace de la versión
            url_version = '%s/ajax_loadShow.php?show=%s&season=%s&langs=%s' % (sitio, id_serie, self.temporada, id_idioma)
            html_version = self.abrir_url(url_version)
            if html_version:
                sopa_version = BeautifulSoup(html_version)
                filas = sopa_version.find_all('tr', {'class' : 'epeven completed'})
                for fila in filas:
                    #comprobar datos
                    coincidencia = True
                    i = 0
                    for columna in fila:
                        if i == 1: #número de episodio
                            if int(columna.text) != self.episodio:
                                coincidencia = False                        
                        elif i == 2: #nombre de episodio
                            if not self.episodio:
                                self.nombre_episodio = columna.text
                        elif i == 4: #versión
                            if not self.comprobar_version(columna.text):
                                coincidencia = False
                        elif i == 5: #porcentaje completado
                            if columna.text != 'Completed':
                                coincidencia = False
                        elif i == 9: #enlace
                            self.enlace_sub = sitio + columna.a['href']
                        
                        #otras columnas
                        #0: número de temporada
                        #3: idioma
                        #6: sordos
                        #7: corregidos
                        #8: HD
                        
                        i = i + 1
                    if coincidencia == True:                
                        return self.guardar_archivo(sitio)
        self.notificar('No se han encontrado subtítulos en %s' % sitio, False)
        return 1
    
    def descargar_sub_subtitulos_es(self):
        """
        Función que se encarga de descargar los subtítulos de subtitulos.es
        """
        sitio = 'http://www.subtitulos.es'

        #sacar título de la serie: Con este sitio se puede acceder directamente a la página del capítulo,
        #pero algunas series tienen nombres distintos en el archivo y la web
        #ej: archivo: Spartacus - web: Spartacus: Blood and Sand
        #por lo tanto se busca el nombre en la lista de series para sacar el nombre que se usa en la web
        url_series = '%s/series' % sitio
        html_series = self.abrir_url(url_series)
        if html_series:
            sopa_series = BeautifulSoup(html_series)
            serie_web = sopa_series.find('a', text = re.compile(self.serie))
            #Según dani hay que hacer más tolerante la búsqueda de la serie
            if serie_web:
                self.serie = serie_web.text.encode('ascii', 'ignore')
            else:
                self.notificar('No se ha encontrado el vídeo en %s' % sitio, False)
                return 1
            
        serie_sin_espacios = self.serie.replace(' ', '-')


        url_episodio = '%s/%s/%dx%d' % (sitio, serie_sin_espacios, self.temporada, self.episodio)
        html_episodio = self.abrir_url(url_episodio)
        if html_episodio:
            sopa_episodio = BeautifulSoup(html_episodio)
            #nombre del episodio
            if not self.nombre_episodio:
                self.nombre_episodio = re.sub('.* - ', '', sopa_episodio.find('h1', {'id' : 'cabecera-subtitulo'}).text)
            #comprobar versión
            versiones = sopa_episodio.find_all('div', {'id' : 'version'})
            for version in versiones:
                version_actual = version.find('p', {'class' : 'title-sub'}).text
                if self.comprobar_version(version_actual):
                    #comprobar idioma
                    idiomas = version.find_all('ul', {'class' : 'sslist'})
                    for lengua in idiomas:
                        idioma_actual = lengua.find('strong').text
                        if re.search("%s" % self.idioma, idioma_actual):
                            porcentaje_completado = lengua.find('li', {'class' : 'li-estado green'})
                            if porcentaje_completado:
                                if porcentaje_completado.text.strip() == 'Completado':
                                    #sacar enlace
                                    self.enlace_sub = lengua.next_sibling.next_sibling.a['href']                       
                                    return self.guardar_archivo(sitio)
        self.notificar('No se han encontrado subtítulos en %s' % sitio, False)
        return 1
    
    def comprobar_version(self, version_web):
        """
        Comprueba si la versión de la web es la misma que la del archivo y 
        las equivalencias entre versiones
        
        Las versiones LOL y SYS siempre son compatibles con la 720p DIMENSION; XII siempre con 720p
        IMMERSE; 2HD siempre con 720p 2HD; BiA siempre 720p BiA; FoV siempre 720p FoV
        """

        if self.version.lower() in ('lol', 'sys', 'dimension'):
            version_a_buscar = 'lol|sys|dimension'
        elif self.version.lower() in ('xii', 'immerse'):
            version_a_buscar = 'xii|immerse'
        else:
            version_a_buscar = self.version
        
        return re.search(version_a_buscar, version_web, re.IGNORECASE)
    
    def guardar_archivo(self, sitio):
        """
        Función que guarda el archivo
        """
        #refactorizar en dos?
        #buscar y descargar
        
        #si solo se quiere comprobar
        if self.args.check:
            self.notificar('Subtítulos encontrados en %s' % sitio)
            return 0
        
        #comprobar la existencia del archivo de subtítulos si no se especifica la opción -f
        if not self.args.force:
            if os.path.exists(os.path.join(self.ruta, self.nombre_video + '.srt')):
                self.notificar('Ya existe un archivo de subtítulos. No se reemplaza')
                return 2
            
        #cambiar el título del archivo si se especifica la opción -t
        if self.args.title:

            #Nombre nuevo = serie+temp+episodio+NOMBRE_CAPI+resto del nombre
            #expresión que saca la primera parte de la cadena
            patron = re.compile('.*E\d\d|.*\dX\d\d', re.IGNORECASE)
            #extraer la primera parte de la cadena
            cadena1 = re.search(patron, self.nombre_video).group(0)
            #extraer la segunda parte de la cadena
            cadena2 = re.sub(patron, '', self.nombre_video)
            #rearmar el nombre del archivo
            nombre_nuevo = '.'.join((cadena1, self.nombre_episodio.replace(' ', '.') + cadena2 + self.extension))
            
            #cambiar el nombre al archivo original
            if os.path.exists(self.archivo):
                try:
                    os.rename(self.archivo, os.path.join(self.ruta, nombre_nuevo))
                    self.nombre_video = nombre_nuevo
                except IOError as e:
                    if e.errno == 13:
                        self.notificar('No se ha podido renombrar el archivo original. Permiso denegado')
                    return 2

        #descargar el subtítulo
        request = urllib2.Request(self.enlace_sub)
        #hay que decir que venimos de la propia página o no descargará
        request.add_header('Referer', sitio)
        subs = self.abrir_url(request)
        if subs:
            try:
                #OPCION: -F - Elegir la ruta de descarga
                
                if self.args.folder:
                    ruta_subs = self.args.folder
                else:
                    ruta_subs = self.ruta
                
                #with open('%s%s.srt' % (self.ruta, self.nombre_video), 'wb') as archivo:
                with open(os.path.join(ruta_subs, '%s.srt' % self.nombre_video), 'wb') as archivo:
                    archivo.write(subs)
                    #self.notificar(u'Descargando subtítulos para %s %dx%d de %s' % (self.serie, self.temporada, self.episodio, sitio))
                    self.notificar('Descargando subtítulos de %s' % sitio)
                    return 0
            except IOError as e:
                if e.errno == 13:
                    self.notificar("No se ha podido crear el archivo de subtítulos. Permiso denegado")
                return 2
        self.notificar('No se han encontrado subtítulos en %s' % sitio, False)
        return 1
    
    def datos(self):
        """
        Devuelve una descripción simple del vídeo
        """
        if self.tipo == 'episode':
            return '%s %dx%d' % (self.serie, self.temporada, self.episodio)
        else:
            return 'TO-DO'
        

    def notificar(self, mensaje, burbuja = True, titulo = None):
        if not self.args.quiet:
            if titulo is None:
                titulo = self.nombre_video + self.extension
    
            if burbuja or self.args.verbose:
                #burbuja de notificación
                from distutils.spawn import find_executable
                
                notificador = 'notify-send'
                #comprobar que se pueden mandar notificaciones
                if find_executable(notificador) is not None:
                    import subprocess
                    ruta_icono = '/home/frans/Programación/Python/Subtle/icono_subtle.ico'
                    subprocess.Popen([notificador, '-i', ruta_icono, titulo, mensaje])
            
            #mostrar texto por consola
            print(mensaje)
        
    def abrir_url(self, url):
        """
        Función que lee el contenido de una url
        """
        #TODO comoprobar que devuelve el read de una url vacía
        #TODO ver que pasa cuando no hay inet
        try:
            if python_vers == 2:
                html = urllib2.urlopen(url).read()
            else:
                html = urllib.request.urlopen(url).read()
        except urllib2.HTTPError as e:
            if e.code == 404:
                self.notificar('No existe la página que se ha buscado')
            return False
        return html

    def __str__(self):
        return self.__unicode__()
    
    def __unicode__(self):
        return ("Ruta del archivo: %s\nNombre del vídeo: %s\nExtensión: %s\n"
               "Serie: %s\nTemporada: %s\nEpisodio: %s\nVersión: %s\nCódec: %s\nNombre del episodio: %s\n"
               "Formato: %s\nTamaño pantalla: %s\nTipo: %s\n") % (
                                               self.ruta, self.nombre_video,
                                               self.extension, self.serie, 
                                               self.temporada, self.episodio,
                                               self.version, self.codec,
                                               self.nombre_episodio, 
                                               self.formato, self.tamano,
                                               self.tipo)
