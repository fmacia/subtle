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

import re

from bs4 import BeautifulSoup
from subtle.core import Web


class subtitulos_es(Web):
    def __init__(self, video):
        self.sitio = 'http://www.subtitulos.es'
        self.video = video
        self.anotaciones = video.args.annotations
        self.idioma = self.idioma(video.args.language)
        self.link = None
        
        self.video.notificacion.n('Buscando en %s' % self.sitio, False)
    
    def idioma(self, idioma):
        """Configura el idioma para que sea aceptado por la web"""
        idiomas = {'en' : 'English',
                   'es' : 'Español (España)',
                   'es-lat' : 'Español (Latinoamérica)',
                   'cat' : 'Català'}
        
        if idioma not in idiomas:
            idioma = idiomas['es']
        else:
            idioma = idiomas[idioma]
        
        return idioma
    
    def buscar_nombre(self):
        """Consigue el nombre de la serie usado en la web.
        Esto sirve para series como spartacus, que en la web es spartacus:blood and sand
        """
        url_indice = '%s/series' % self.sitio
        html_indice = self.abrir_url(url_indice)
        if html_indice:
            sopa_indice = BeautifulSoup(html_indice)
            serie_web = sopa_indice.find('a', text = re.compile(self.video.serie))
            if serie_web:
                #self.nombre_serie = serie_web.text.encode('ascii', 'ignore')
                self.nombre_serie = serie_web.text
                return True
            else:
                return False
        else:
            self.nombre_serie = ''
            return False
    
    def buscar_subs(self):
        """Saca los subs encontrados para el capítulo y parsea el HTML"""
        serie_sin_espacios = self.nombre_serie.replace(' ', '-')
 
        url_episodio = '%s/%s/%dx%d' % (self.sitio, serie_sin_espacios, self.video.temporada, self.video.episodio)
        html_episodio = self.abrir_url(url_episodio)
        if html_episodio:
            sopa_episodio = BeautifulSoup(html_episodio)
            #nombre del episodio
            if self.video.titulo is None:
                self.video.titulo = re.sub('.* - ', '', sopa_episodio.find('h1', {'id' : 'cabecera-subtitulo'}).text)
            versiones = sopa_episodio.find_all('div', {'id' : 'version'})
            for version in versiones:
                print(version)
                #extraer datos
                #versión, eliminando posibles líneas en blanco
                version_web = ''.join(version.find('p', {'class' : 'title-sub'}).text.splitlines())

                if self.comprobar_version(self.video.version, version_web):
                    #idiomas
                    idiomas = version.find_all('li', {'class' : 'li-idioma'})
                    for idioma in idiomas:
                        idioma_web = idioma.text
                        #if re.search("%s" % self.idioma, idioma_web):
                        if idioma_web == self.idioma:
                            completado = porcentaje_completado = idioma.find('li', {'class' : 'li-estado green'})
                            if completado:
                                #sacar enlace
                                #TODO: mejorar la expresion
                                self.link = idioma.next_sibling.next_sibling.a['href']                 
                                return 0
        return 1
    
    def get_subtitles(self):
        """Principal, se conecta, busca y descarga los subtítulos"""
        if self.anotaciones:
            #en subtitulos.es no he encontrado una manera de buscar con anotaciones
            self.video.notificacion.n('No se pueden buscar subtítulos con anotaciones para sordos en %s' % self.sitio, False)
            ret = 1
        else:
            if self.buscar_nombre():
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
