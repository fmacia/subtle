#!/usr/bin/env python2
# -*- coding: utf8 -*-
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

from bs4 import BeautifulSoup
import guessit
import os
import re
import sys
import urllib2
import argparse


class Video:
    """
    Clase del vídeo
    """
    def __init__(self, archivo):
        self.archivo = archivo
        self.ruta = ''
        self.nombre_video = ''
        self.version = ''
        self.serie = ''
        self.temporada = ''
        self.episodio = ''
        self.nombre_episodio = ''
        self.enlace_sub = ''
    
    def cargar_datos(self):
        """
        Función que se encarga de extraer los datos del archivo e insertarlos en las variables
        """
        #relativo al archivo
        #TODO: cambiar barras / por os.path.join
        self.ruta = os.path.dirname(self.archivo) + '/'
        self.nombre_video = os.path.splitext(os.path.basename(self.archivo))[0]
                
        #uso del módulo guessit para sacar los datos a partir del nombre del archivo
        guess = guessit.guess_video_info(self.archivo)
        if guess['type'] != 'unknown':
            self.version = guess.get('releaseGroup')
            self.serie = guess.get('series')
            self.temporada = guess.get('season')
            self.episodio = guess.get('episodeNumber')
            
            #otros datos
            self.idioma = 'España'.decode('utf-8') #para que reconozca la ñ
            return 0
        else:
            print("No se ha podido extraer los datos")
            return 1
        
    def descargar_sub_addic7ed(self):
        """
        Función que se encarga de descargar los subtítulos de addic7ed
        """
        sitio = 'http://www.addic7ed.com'
        #sacar el id del idioma elegido
        id_idioma = ''
        if re.match('España', self.idioma, re.IGNORECASE):
            id_idioma = '|5|'
        elif re.match('English', self.idioma, re.IGNORECASE):
            id_idioma = '|1|'
        
        if id_idioma == '':
            return 1

        serie_sin_espacios = self.serie.replace(' ', '_')
        
        #sacar id de la serie
        html_busqueda = urllib2.urlopen('%s/search.php?search=%s' % (sitio, serie_sin_espacios)).read()
        sopa_busqueda = BeautifulSoup(html_busqueda)
        id_serie = re.sub('/show/', '' , sopa_busqueda.find('span', {'class' : 'titulo'}).a['href'])
        
        #buscar enlace de la versión
        html_version = urllib2.urlopen('%s/ajax_loadShow.php?show=%s&season=%s&langs=%s' % (sitio, id_serie, self.temporada, id_idioma)).read()
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
                    self.nombre_episodio = columna.text
                elif i == 4: #versión
                    if columna.text != self.version:
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
        return 1
    
    def descargar_sub_subtitulos_es(self):
        """
        Función que se encarga de descargar los subtítulos de subtitulos.es
        """
        sitio = 'http://www.subtitulos.es'
        #serie_sin_espacios = re.sub(' ', '-', self.serie)
        serie_sin_espacios = self.serie.replace(' ', '-')
        
        html_episodio = urllib2.urlopen('%s/%s/%dx%d' % (sitio, serie_sin_espacios, self.temporada, self.episodio)).read()
        sopa_episodio = BeautifulSoup(html_episodio)
        self.nombre_episodio = re.sub('.* - ', '', sopa_episodio.find('h1', {'id' : 'cabecera-subtitulo'}).text)
        #comprobar versión
        versiones = sopa_episodio.find_all('div', {'id' : 'version'})
        for version in versiones:
            version_actual = version.find('p', {'class' : 'title-sub'}).text
            if re.search("%s" % self.version, version_actual, re.IGNORECASE):
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
        return 1
    
    def guardar_archivo(self, sitio):
        """
        Función que guarda el archivo
        """
        #descargar el subtítulo
        request = urllib2.Request(self.enlace_sub)
        #hay que decir que venimos de la propia página o no descargará
        request.add_header('Referer', sitio)
        subs = urllib2.urlopen(request).read()
        try:
            with open('%s%s.srt' % (self.ruta, self.nombre_video), 'wb') as archivo:
                archivo.write(subs)
                print(u"Descargando subtítulos para %s S%dE%d de %s" % (self.serie, self.temporada, self.episodio, sitio))
                return 0
        except IOError, e:
            if e.errno == e.errno.EPERM:
                print("No se ha podido crear el archivo de subtítulos. Permiso denegado")
            return 2

    def __str__(self):
        return "Datos del episodio\nRuta del archivo: %s\nNombre del vídeo: %s\nVersión: %s\nSerie: %s\nTemporada: %s\nEpisodio: %s\nNombre del episodio: %s\n" % (self.ruta, self.nombre_video, self.version, self.serie, self.temporada, self.episodio, self.nombre_episodio)

def main():
    """
    Función principal del script
    """

    args = sys.argv
    if len(args) > 1:
        ret = 0
        for arg in args[1:]:
            #TODO: comprobar si arg es una carpeta y hacer un for sobre todos los videos
            capi = Video(arg)
            if capi.cargar_datos() == 0:
                #probar a descargar de subtitulos.es primero. si no, de addic7ed
                subs_es = capi.descargar_sub_subtitulos_es()
                add = 0
                if subs_es == 1:
                    add = capi.descargar_sub_addic7ed()
                    if add == 1:
                        print("No se han encontrado subtítulos")
                if subs_es == 2 or add == 2:
                    ret = 2
                ret = 0
            else:
                ret = 3
        #returns aquí
        return ret
    else:
        print('Uso: subtle [nombre del vídeo]')
        #parser.print_help()
        return 0


if __name__ == '__main__':
    sys.exit(main())