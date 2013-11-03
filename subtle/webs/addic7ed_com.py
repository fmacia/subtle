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

import re

from bs4 import BeautifulSoup
from subtle.core import Web


class addic7ed_com(Web):
    def __init__(self, video):
        self.sitio = 'http://www.addic7ed.com'
        self.video = video
        self.anotaciones = video.args.annotations
        self.idioma = self.idioma(video.args.language)
        self.link = None
        
        self.video.notificacion.n('Buscando en %s' % self.sitio, False)

    def idioma(self, idioma):
        """Configura el idioma para que sea aceptado por la web"""
        #TODO: convertir en diccionario, poner sus respectivos numeros
        idiomas = {'en' : 1,
                   'it' : 7,
                   'pt' : 9,
                   'pt-br' : 10,
                   'ro' : 26,
                   'es' : 5,
                   'es-lat' : 6,
                   'fr' : 8,
                   'el' : 27,
                   'ar' : 38,
                   'de' : 11,
                   'hr' : 31,
                   'da' : 30,
                   'id' : 37,
                   'he' : 23,
                   'ja' : 32,
                   'sv' : 18,
                   'ru' : 19,
                   'bg' : 35,
                   'zh' : 24,
                   'cs' : 14,
                   'nl' : 17,
                   'fi' : 28,
                   'hu' : 20,
                   'pl' : 21,
                   'sk' : 25,
                   'tr' : 16}
        
        if idioma not in idiomas:
            idioma = idiomas['es']
        else:
            idioma = idiomas[idioma]
        
        return idioma

    def buscar_id(self):
        """Saca el id de la serie"""
        self.serie_sin_espacios = self.video.serie.replace(' ', '_')
        url_id = '%s/search.php?search=%s' % (self.sitio, self.serie_sin_espacios)
        html_id = self.abrir_url(url_id)
        if html_id:
            sopa_id = BeautifulSoup(html_id)
            result = sopa_id.find('span', {'class' : 'titulo'})
            if result:
                self.id_serie = re.sub('/show/', '' , result.a['href'])
                return True
            else:
                #TODO: opcion 2, buscar en indice de series
                return False
        else:
            self.id_serie = 0
            return False
    
    def buscar_subs(self):
        """Saca los subs encontrados para el capítulo y parsea el HTML"""
        #TODO: hearing impaired
        url_temporada = '%s/ajax_loadShow.php?show=%s&season=%s&langs=|%s|&hi=%d' % (self.sitio, 
                                                                            self.id_serie, 
                                                                            self.video.temporada, 
                                                                            self.idioma,
                                                                            self.anotaciones)
        html_temporada = self.abrir_url(url_temporada)
        if html_temporada:
            sopa_temporada = BeautifulSoup(html_temporada)
            #comprobar idioma
            tabla_idiomas = sopa_temporada.find('div', {'id' : 'langs'})
            if tabla_idiomas.find_all('input', {'id' : 'lang%d' % self.idioma}):
                filas = sopa_temporada.find_all('tr', {'class' : 'epeven completed'})
                for fila in filas:
                    #extraer datos de la tabla
                    columnas = fila.find_all('td')
                    episodio_web = int(columnas[1].text)
                    completado = columnas[5].text
                    titulo_web = columnas[2].text
                    if self.video.titulo is None:
                        self.video.titulo = titulo_web
                    version_web = columnas[4].text
                    link_web = self.sitio + columnas[9].a['href']
    
                    if episodio_web == self.video.episodio:
                        if completado == 'Completed':
                            if self.comprobar_version(self.video.version, version_web):
                                #descargar
                                self.link = link_web
                                return 0
        return 1
    
    def get_subtitles(self):
        """Principal, se conecta, busca y descarga los subtítulos"""
        if self.buscar_id():
            self.buscar_subs()
            if self.link:
                if not self.video.args.check:
                    self.descargar()
                else:
                    self.video.notificacion.n('Subtítulos encontrados en %s' % self.sitio)
                ret = 0
            else:
                self.video.notificacion.n('No se han encontrado subtítulos en %s' % self.sitio, False)
                ret = 1
        else:
            self.video.notificacion.n('No se ha encontrado el vídeo en %s' % self.sitio, False)
            ret = 1

        return ret
