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

#Archivo de funciones generales

from __future__ import unicode_literals
import os
import logging
#import i18n
#_ = i18n.language.ugettext #use ugettext instead of getttext to avoid unicode errors

def separador(cadena, separador = '=', pegar = True, doble_fila = False):
    """Añade una línea de caracteres para destacar / separar una cadena
    
    :param cadena:
            Cadena a destacar.
    :param separador:
            Carácter que se usará como separador.
    :param pegar:
            Devolver la cadena junto al separador o sólo el separador.
    """
    if pegar:
        cadena = cadena + "\n" + '%s' % separador * len(cadena)
        cadena += "\n"
        return cadena
    return separador * len(cadena) + "\n"

def recortar_url(url):
    """Elimina http://www. de una url si lo tiene, y cambia los puntos por guiones bajos.
    Para comprobar si existe en el array de webs de subtle"""
    import re

    url = re.sub('^http://', '', url)
    url = re.sub('^www.', '', url)
    return re.sub('\.', '_', url)

def extension(archivo):
    """Get the file extension."""
    return os.path.splitext(archivo)[-1].lower()

def excepciones_archivos(e):
    """Maneja los mensajes que se mostrarán en las excepciones de archivos"""
    mensaje = ''
    if e.errno == 13:
        mensaje = "\nPermiso denegado."
    elif e.errno == 28: #puede depender sel SO
        mensaje = "\nNo queda espacio en disco."
    return mensaje

def intercambiar(variable, reemplazo = 'Desconocido'):
    """Intercambia un valor None por el reemplazo que se le diga"""
    if variable is not None:
        return variable
    else:
        return reemplazo

def check_os():
    """Comprueba el so operativo que se está usando"""
    import platform
    so = platform.system()
    #platform.release() -> más detalles, por ejemplo en linux creo que es la versión del kernel
    if so.lower().startswith('linux'):
        return 'linux'
    elif so.lower().startswith('windows'):
        return 'windows'
    elif so.lower().startswith('darwin'):
        return 'mac'
    else:
        return 'unknown'

def comprobar_log(crear = True):
    """
    Comprueba la existencia del archivo de log y si es modificable (para escribir en él).
    En caso de no existir, intentará crearlo.
    Devuelve la ruta del archivo en caso afirmativo, false si no puede escribir
    """
    #TODO: enganche para ruta personalizada

    #ruta a la HOME independiente del so
    ruta_home = os.path.expanduser("~")
    so = check_os()

    if so == 'linux':
        ruta_log = os.path.join(ruta_home, '.config/subtle/log')
    else: #TODO: rutas de windows y mac
        return False

    if os.path.isfile(ruta_log):    #comprobar si es un archivo (lo cual de paso comprueba si existe)
        if os.access(ruta_log, os.W_OK):    #comprobar si se puede escribir
            return ruta_log
        else: #no se puede escribir
            #TODO: print diciendo que no se puede escribir el log a no ser que se pase la -q (creo que hace falta hacer args global)
            return False
    elif crear == True:   #no existe, intentar crearlo
        try:
            basedir = os.path.dirname(ruta_log)
            if not os.path.exists(basedir):
                os.makedirs(basedir)
            archivo = open(ruta_log, 'wb')
            archivo.close()
            return ruta_log
        except IOError as e:
            #TODO: mensaje diciendo que no se puede crear el log
            return False
    else:
        return False

class Notificacion(object):
    """Crea burbujas de notificación, guarda el log e imprime por pantalla"""

    def __init__(self, notificador = 'notify-send', titulo = None, icono = None, urgencia = 'normal', tiempo = None, kwargs = {}):
        #TODO: probar a cambiar el kwargs de la firma por **kwargs y el get por kwargs['x']
        #TODO: extras de notify-send (noitify-send) --help)
        self.quiet = kwargs.get('quiet', False)
        self.verbose = kwargs.get('verbose', False)
        
        if not self.quiet:
            self.notificador = notificador
            self.comprobar_burbuja()
            #configuración por defecto de la burbuja de notificación
            if self.mostrar_burbuja:
                self.titulo = titulo
                self.icono = icono
                self.urgencia = urgencia
                self.tiempo = tiempo
        else:
            self.mostrar_burbuja = False
            self.registro = False
        
        #comenzar log
        ruta_log = comprobar_log()
        if ruta_log:
            self.logueable = True
            self.logger = logging.getLogger('subtle')
            handler = logging.FileHandler(ruta_log)
            formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
            self.logger.setLevel(10)
        else:
            self.logueable = False
    
    def set_titulo(self, titulo):
        """Modifica el título de la notificación"""
        self.titulo = titulo
    
    def notificar(self, mensaje, mostrar_burbuja = True, nivel_log = 20):
        """Principal, lanza las tres funciones"""
        if not self.quiet:
            if (self.mostrar_burbuja and mostrar_burbuja) or (self.mostrar_burbuja and self.verbose):
                self.burbuja(mensaje)
            print((mensaje))
        #log
        if self.logueable and nivel_log >= 0:
            self.logger.log(nivel_log, mensaje)
        
    def n(self, mensaje, mostrar_burbuja = True, nivel_log = 20):
        """Máscara de notificar"""
        self.notificar(mensaje, mostrar_burbuja, nivel_log)
    
    def burbuja(self, mensaje):
        """Crea una burbuja de notificación"""
        import subprocess
        
        #crear array dependiendo de los añadidos de la burbuja
        #notificador
        burbuja = ['notify-send']
        #icono
        if self.icono:
            burbuja.append('-i')
            burbuja.append(self.icono)
        #urgencia (low, normal, critical)
        if self.urgencia in ('low', 'normal', 'critical'):
            burbuja.append('-u')
            burbuja.append(self.urgencia)
        #tiempo (milisegundos)
        if self.tiempo:
            burbuja.append('-t')
            burbuja.append(str(self.tiempo))
        #título
        if self.titulo:
            burbuja.append(self.titulo)
        #mensaje
        burbuja.append(mensaje)

        subprocess.Popen(burbuja)
    
    def comprobar_burbuja(self):
        """Comprueba si existe un método de crear burbujas de notificación"""
        from distutils.spawn import find_executable
        #comprobar que se pueden mandar notificaciones
        if find_executable(self.notificador) is not None:
            self.mostrar_burbuja = True
            return 0
        else:
            self.mostrar_burbuja = False
            return 1

    def registro(self):
        #TODO: loguear
        pass
        
def subtle_extensiones():
    #TODO: quitar de aqui
    return ('.mp4', '.avi', '.mkv')

#TODO: mover a otro archivo?
import sqlite3
class Bbdd:
    """Abstrae la base de datos sqlite"""
    #TODO: al cambiar notificar a clase, se ha roto la funcionalidad. arreglar
    def __init__(self, ruta):
        self.con = None
        self.conectar(ruta)

    def conectar(self, ruta):
        """Crea o conecta la base de datos"""
        try:
            #crear / conectar bbdd de sqlite
            self.con = sqlite3.connect(ruta)
        except Exception as e:
            notificar('Ha ocurrido un error al conectar a la base de datos.')
            notificar(e, False)
        finally:
            return self.con
            
    def desconectar(self):
        """Desconecta la base de datos"""
        self.con.close()

    def ex(self, sql, args = None, commit = False, many = False):
        """Ejecuta la sentencia sql, llamada ex (execute) para acortar
        args: array de variables de sustitución para los comodines del sql"""
        c = self.con.cursor()
        try:
            if args is not None:
                if not isinstance(args, (list, tuple)):
                    args = (args,)
            else:
                args = ()
                
            if commit and many:
                    c.executemany(sql, args)
            else:
                    c.execute(sql, args)
                    
            if not commit:
                return c.fetchall()
            else:
                self.con.commit()

        except Exception as e:
            notificar('Ha ocurrido un error al interactuar con la base de datos')
            print(e)
            self.con.rollback()
            return 1
        c.close()

    def ex_m(self, sql, args = None, commit = False):
        """Ejecuta varias sentencias sql"""
        return self.ex(sql, args, commit, True)
    
    def w(self, sql, args = None):
        """Máscara de ex() para hacer commit en la bd, w(write) para acortar"""
        return self.ex(sql, args, True)
    
    def w_m(self, sql, args = None):
        """Máscara de ex() para hacer commit de varias sentencias en la bd, w(write) para acortar"""
        return self.ex(sql, args, True, True)
    
    def r(self, sql, args = None):
        """Máscara de ex() para leer de la base de datos"""
        return self.ex(sql, args, False)
        
    def r_range(self, sql, args = None, limit = 1, offset = 0):
        """Máscara de r() para leer X filas de la base de datos"""
        #de esta manera es compatible con sqlite, mysql y postgresql
        sql += 'LIMIT %d OFFSET %d' % (limit, offset)
        return self.r(sql, args)
    
    def r_one(self, sql, args = None):
        """Máscara de r() para leer la primera fila de la base de datos"""
        return self.r_range(sql, args)
