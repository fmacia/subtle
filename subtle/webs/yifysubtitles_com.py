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
from subtle.core import Web
import json
import zipfile
import os

def sort_rating(lista):
    return lista['rating']

class yifysubtitles_com(Web):
    def __init__(self, video):
        self.sitio = 'http://api.ysubs.com'
        self.sitio_descarga = 'http://www.yifysubtitles.com'
        self.video = video
        self.idioma = self.idioma(video.args.language)
        self.link = None

    def buscar_id(self):
        """Busca la id de la película en la base de datos de IMDB usando la Open Movie Database
        @see http://www.omdbapi.com"""

        self.titulo_sin_espacios = self.video.titulo.replace(' ', '+')
        url_omdb = 'http://www.omdbapi.com'
        url_id = '%s/?t=%s' % (url_omdb, self.titulo_sin_espacios)
        html_id = self.abrir_url(url_id, True)
        if html_id:
            datos_omdb = json.loads(html_id)
            if datos_omdb['Response'] == 'True':
                return datos_omdb['imdbID']

        self.video.notificacion.n('No se han encontrado datos de la película', False, 30)
        return False

    def idioma(self, idioma):
        """Configura el idioma para que sea aceptado por la web"""
        idiomas = {
            'ar': 'arabic',
            'bg': 'bulgarian',
            'bn': 'bengali',
            'bs': 'bosnian',
            'cs': 'czech',
            'da': 'danish',
            'de': 'german',
            'el': 'greek',
            'en': 'english',
            'es': 'spanish',
            'et': 'estonian',
            'fa': 'farsi-persian',
            'fi': 'finnish',
            'fr': 'french',
            'he': 'hebrew',
            'hr': 'croatian',
            'hu': 'hungarian',
            'id': 'indonesian',
            'it': 'italian',
            'ja': 'japanese',
            'ko': 'korean',
            'lt': 'lithuanian',
            'mk': 'macedonian',
            'ms': 'malay',
            'nl': 'dutch',
            'no': 'norwegian',
            'pl': 'polish',
            'pt': 'portuguese',
            'pt-br': 'brazilian-portuguese',
            'ro': 'romanian',
            'ru': 'russian',
            'sl': 'slovenian',
            'sq': 'albanian',
            'sr': 'serbian',
            'sv': 'swedish',
            'th': 'thai',
            'tr': 'turkish',
            'uk': 'ukrainian',
            'ur': 'urdu',
            'vi': 'vietnamese',
            'zh': 'chinese',
        }

        if idioma not in idiomas:
            idioma = idiomas['es']
        else:
            idioma = idiomas[idioma]

        return idioma

    def get_subtitles(self):
        """Principal, se conecta, busca y descarga los subtítulos"""
        self.id = self.buscar_id()
        if self.id:
            url = '%s/subs/%s' % (self.sitio, self.id)
            result = self.abrir_url(url, True)
            if result:
                datos_sub = json.loads(result)
                if datos_sub['success'] == True:
                    if datos_sub['subs'][self.id][self.idioma]: #comprobar que hay subs para el idioma escogido
                        mejor_sub = max(datos_sub['subs'][self.id][self.idioma], key=sort_rating)
                        self.link = self.sitio_descarga + mejor_sub['url']
                        subs_comprimidos = self.abrir_url(self.link)

                        self.descargar()
                        #esto baja el .zip, seuir por aqui
                        #self.descargar(mejor_sub['url'])
                        return 0

                elif datos_sub['message'] == 'maintenance in progress':   #no se ha encontrado, o la página no funciona bien
                    self.video.notificacion.n('%s se encuentra en mantenimiento, imposible descargar por ahora' % self.sitio, False, 30)
        return 1

    def descargar(self):
        self.sub = self.abrir_url(self.link)

        #los archivos de yifysubtitles vienen en zip, por lo que se descarga el zip, se descomprime y se borra
        self.video.guardar_archivo(self.sub, '.zip')
        with zipfile.ZipFile(os.path.join(self.video.ruta, '%s.zip' % self.video.nombre_video)) as zf:
            for member in zf.infolist():
                datos = zf.read(member)
        os.remove(os.path.join(self.video.ruta, '%s.zip' % self.video.nombre_video))
        if datos:
            self.video.guardar_archivo(datos)
            return 0
        else:
            return 2
