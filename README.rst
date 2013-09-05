======
Subtle
======

Subtle es un descargador automático de subtítulos para series
Es un proyecto personal de Francisco Jesús Macía Espín (fmacia) <fjmaciaespin@gmail.com>

Instalación
===========

Con pip (método preferido)
--------------------------

pip instalará automáticamente las dependencias necesarias

$ pip install subtle


A partir de las fuentes
------------------------

Se necesitan tener instalados los siguientes módulos de python: 'beautifulsoup4', 'guessit'
Opcionalmente, se necesita watchdog para poder usar le modo de monitorización

(dentro de la carpeta descomprimida)
$ python2 setup.py install

Uso
---

Una vez instalado, el programa se usa así::

subtle [opciones] video1 [video2 ...]

positional arguments:
  videos

optional arguments:
  -v, --verbose         Ver mensajes de depuración
  -q, --quiet           No mostrar nada por pantalla
  -h, --help            Muestra este mensaje de ayuda
  -i, --info            Mostrar la información del vídeo y salir
  -f, --force           Forzar sobreescritura de subtítulos ya existentes
  -t, --title           Añade el título al nombre del archivo de vídeo si no
                        lo tiene
  -c, --check           Solo comprueba la existencia del subtítulo sin
                        descargarlo
  -w WEB, --web WEB     Especificar directamente la web en la que buscar
  -r RECURSIVE, --recursive RECURSIVE
                        Descargar subtítulos para los vídeos de subcarpetas
  -l LANGUAGE, --language LANGUAGE
                        Especificar el idioma -> es: Español de España, lat:
                        Español de Latinoamérica, en: Inglés
  -V, --version         Muestra la versión del programa
  -F FOLDER, --folder FOLDER
                        Especificar la ruta donde se descargarán los
                        subtítulos
