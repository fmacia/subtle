#!/usr/bin/python2.7
# -*- coding: utf8 -*-
'''
Created on 14/02/2013

Subtle, descargador automático de subtítulos
Versión 0.1, descarga en español (de España) o inglés de subtitulos.es o addic7ed.com

@author: fmacia
'''

from bs4 import BeautifulSoup
import guessit
import os
import re
import sys
import urllib2


class Video:
    #TODO: poner opción para cambiar el nombre del archivo añadiendo el título
    #TODO: compatibilidad entre versions (LOL con DIMENSION por ejemplo)
    #TODO: dar la opcion de descargar subs con acotaciones para sordos
    #parametros: -h ayuda, -s silencio, -v verbose, -f no sobreescribir -t añadir titulo al archivo
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
        self.ruta = os.path.dirname(self.archivo) + '/'
        self.nombre_video = os.path.splitext(os.path.basename(self.archivo))[0]
                
        #uso del módulo guessit para sacar los datos a partir del nombre del archivo
        guess = guessit.guess_video_info(self.archivo)
        self.version = guess.get('releaseGroup')
        self.serie = guess.get('series')
        self.temporada = guess.get('season')
        self.episodio = guess.get('episodeNumber')
        
        #otros datos
        self.idioma = 'España'.decode('utf-8') #para que reconozca la ñ
        
    def descargar_sub_addic7ed(self):
        """
        Función que se encarga de descargar los subtítulos de addic7ed
        """
        sitio = 'http://www.addic7ed.com'
        #sacar el id del idioma elegido
        id_idioma = ''
        if re.match('Español', self.idioma, re.IGNORECASE):
            id_idioma = '|5|'
        elif re.match('English', self.idioma, re.IGNORECASE):
            id_idioma = '|1|'
        
        if id_idioma == '':
            return 1
        
        serie_sin_espacios = re.sub(' ', '_', self.serie)
        
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
                #descargar el subtítulo
                request = urllib2.Request(self.enlace_sub)
                #hay que decir que venimos de la propia página o no descargará
                request.add_header('Referer', sitio)
                subs = urllib2.urlopen(request).read()
                
                with open(self.ruta + self.nombre_video + '.srt', 'wb') as code:
                    code.write(subs)
                    print 'Descargando subtítulos para %s S%dE%d de %s' % (self.serie, self.temporada, self.episodio, sitio)
                    return 0
        return 1
    
    def descargar_sub_subtitulos_es(self):
        """
        Función que se encarga de descargar los subtítulos de subtitulos.es
        """
        sitio = 'http://www.subtitulos.es'
        serie_sin_espacios = re.sub(' ', '-', self.serie)
        
        html_episodio = urllib2.urlopen('%s/%s/%dx%d' % (sitio, serie_sin_espacios, self.temporada, self.episodio)).read()
        sopa_episodio = BeautifulSoup(html_episodio)
        #TODO: sacar titulo
        #comprobar versión
        versiones = sopa_episodio.find_all('div', {'id' : 'version'})
        for version in versiones:
            version_actual = version.find('p', {'class' : 'title-sub'}).text
            if re.search("%s" % self.version, version_actual):
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
                                #descargar el subtítulo
                                request = urllib2.Request(self.enlace_sub)
                                #hay que decir que venimos de la propia página o no descargará
                                request.add_header('Referer', sitio)
                                subs = urllib2.urlopen(request).read()
                                
                                with open(self.ruta + self.nombre_video + '.srt', 'wb') as code:
                                    code.write(subs)
                                    print 'Descargando subtítulos para %s S%dE%d de %s' % (self.serie, self.temporada, self.episodio, sitio)
                                    return 0
        return 1        

    def __str__(self):
        return "Datos del episodio\nRuta del archivo: %s\nNombre del vídeo: %s\nVersión: %s\nSerie: %s\nTemporada: %s\nEpisodio: %s\nNombre del episodio: %s\n" % (self.ruta, self.nombre_video, self.version, self.serie, self.temporada, self.episodio, self.nombre_episodio)

def main(args):
    if len(args) >= 2:
        capi = Video(args[1])
        capi.cargar_datos()
        
        #probar a descargar de subtitulos.es primero. si no, de addic7ed
        if capi.descargar_sub_subtitulos_es() != 0:
            if capi.descargar_sub_addic7ed() != 0:
                print "No se han encontrado subtítulos"        
        return 0
    else:
        print "Uso: %s [nombre del vídeo]" % (args[0])
        return 0

if __name__ == '__main__':
    sys.exit(main(sys.argv))