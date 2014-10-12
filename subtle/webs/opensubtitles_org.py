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
from subtle.core import Web

class opensubtitles_org(Web):
    def __init__(self, video):
        self.sitio = 'http://www.opensubtitles.org'
        self.servidor = 'http://api.opensubtitles.org/xml-rpc'
        self.conexion = self.conectar()
        self.token = None
        self.idsub = None
        self.sub = None
        self.useragent = 'Pysubtle' 
        #Objeto vídeo
        self.video = video
        self.anotaciones = video.args.annotations
        #idioma
        self.idioma = self.idioma(video.args.language)
        
        self.video.notificacion.n('Buscando en %s' % self.sitio, False)
    
    def idioma(self, idioma):
        """Configura el idioma para que sea aceptado por la web"""
        idiomas = {
            'en' : 'eng',
            'fr' : 'fre',
            'hu' : 'hun',
            'cs' : 'cze',
            'pl' : 'pol',
            'sk' : 'slo',
            'pt' : 'por',
            'pt-br': 'pob',
            'es' : 'spa',
            'el' : 'ell',
            'ar' : 'ara',
            'sq' : 'alb',
            'hy' : 'arm',
            'ay' : 'ass',
            'bs' : 'bos',
            'bg' : 'bul',
            'ca' : 'cat',
            'zh' : 'chi',
            'hr' : 'hrv',
            'da' : 'dan',
            'nl' : 'dut',
            'eo' : 'epo',
            'et' : 'est',
            'fi' : 'fin',
            'gl' : 'glg',
            'ka' : 'geo',
            'de' : 'ger',
            'he' : 'heb',
            'hi' : 'hin',
            'is' : 'ice',
            'id' : 'ind',
            'it' : 'ita',
            'ja' : 'jpn',
            'kk' : 'kaz',
            'ko' : 'kor',
            'lv' : 'lav',
            'lt' : 'lit',
            'lb' : 'ltz',
            'mk' : 'mac',
            'ms' : 'may',
            'no' : 'nor',
            'oc' : 'oci',
            'fa' : 'per',
            'ro' : 'rum',
            'ru' : 'rus',
            'sr' : 'scc',
            'sl' : 'slv',
            'sv' : 'swe',
            'th' : 'tha',
            'tr' : 'tur',
            'uk' : 'ukr',
            'vi' : 'vie'}
        
        if idioma not in idiomas:
            idioma = idiomas['es']
        else:
            idioma = idiomas[idioma]
        
        return idioma
        
    def conectar(self):
        import xmlrpc.client
        return xmlrpc.client.ServerProxy(self.servidor)
    
    def serverinfo(self):
        return self.conexion.ServerInfo()
    
    def login(self, username = '', password = ''):
        try:           
            estado = self.conexion.LogIn(username, password, self.idioma, self.useragent)
            if estado['status'] == '200 OK':
                self.token = estado['token']
                return estado['token']
        except: 
            return None
    
    def logout(self):
        self.conexion.LogOut(self.token)
        
    def buscar_subs(self):
        """Busca subtítulos por hash o por datos del vídeo"""        
        if self.video.buscar_por_hash:
            datos = {'sublanguageid' : self.idioma,
                     'moviehash' : self.video.hash,
                     #se pasa el tamaño como cadena, si se pasa como número y el archivo es muy grande, salta excepción en xml-rpc
                     'moviebytesize': str(self.video.bytesize)}
        elif self.video.buscar_por_nombre:
            if self.video.tipo == 'episode':
                datos = {'sublanguageid' : self.idioma,
                         'query' : self.video.serie,
                         'season' : self.video.temporada,
                         'episode' : self.video.episodio}
            else:
                datos = {'sublanguageid' : self.idioma,
                         'query' : self.video.titulo}
        else:
            return {}
        #datos debe ser un array de arrays
        return self.conexion.SearchSubtitles(self.token, [datos])
    
    def descargar(self):
        result = self.conexion.DownloadSubtitles(self.token, [self.idsub])
        if result['status'] == '200 OK':
            #decodificar BASE64
            import base64
            self.sub = base64.b64decode(result['data'][0]['data'])
            #descomprimir
            self.sub = self.video.descomprimir(self.sub)
            self.video.guardar_archivo(self.sub)
            return 0
        else:
            return 2
        
    def elegir_sub(self, resultados):
        """Elige el subtítulo más óptimo de entre los que se encuentren"""
        if not self.anotaciones:
            self.video.titulo = resultados['data'][0]['MovieName']
            return resultados['data'][0]['IDSubtitleFile']
        else:
            for resultado in resultados['data']:
                if resultado['SubHearingImpaired'] == '1':
                    self.video.titulo = resultado['IDSubtitleFile']
                    return resultado['IDSubtitleFile']
            return False
        
    def get_subtitles(self, username = '', password = ''):
        """Principal, se conecta, busca y descarga los subtítulos"""
        ret = 0
        if self.login(username, password):
            result = self.buscar_subs()
            #TODO: meter comprobaciones del result en buscar_subs? mover a otra funcion vamos
            if result.get('data'):
                self.idsub = self.elegir_sub(result)
                if self.idsub:
                    if not self.video.args.check:
                        self.descargar()
                    else:
                        self.video.notificacion.n('Subtítulos encontrados en %s' % self.sitio)
                else:
                    self.video.notificacion.n('No se han encontrado subtítulos en %s' % self.sitio, False)
                    ret = 1
            else:
                self.video.notificacion.n('No se ha encontrado el vídeo en %s' % self.sitio, False)
                ret = 1
            self.logout()
        else:
            self.video.notificacion.n('No se ha podido conectar a %s' % self.sitio, False, 40)
            ret = 1
        return ret
