#! /usr/bin/env python
from subprocess import call
from bottle import route, run, static_file, request
import os, glob

BASEDIR = '/usr/local/SketchWS'

images = {}
for f in glob.glob("%s/*/base.*" % BASEDIR):
  name, ext = os.path.splitext(f)
  base = os.path.basename(os.path.dirname(name))
  images[base] = ext

@route('/')
def index():
    return static_file('index.html', root='static')

@route('/<filename>')
def static(filename):
    return static_file(filename, root='static')

@route('/sketch/<name>/<filename>')
def static(name, filename):
    return static_file(filename, root="%s/%s" % (BASEDIR, name))

@route('/upload', method='POST')
def upload():
    img = request.files.get('img')
    name, ext = os.path.splitext(img.filename)
    path = "%s/%s" % (BASEDIR, name)
    try:
      os.makedirs(path)
    except:
      pass
    img.save("%s/base%s" % (path, ext), overwrite=True)
    convert_to_sketch(path, ext)
    images[name] = ext
    return images

@route('/print')
def print_it():
    pass

def convert_to_sketch(path, ext):
  call("convert -alpha off %s/base%s -set colorspace Gray -separate -average %s/0.png" % (path, ext, path), shell=True)
  call("convert %s/0.png -edge 3 -normalize -negate %s/e.png" % (path, path), shell=True)
  call("convert %s/0.png -sketch 0x20+120 %s/s.png" % (path, path), shell=True)
  call("composite -compose darken %s/e.png %s/s.png %s/1.pgm" % (path, path, path), shell=True)
  call("potrace -t 2 -p %s/1.pgm" % path, shell=True)
  call("pstoedit -f gcode %s/1.ps %s/sketch.gcode" % (path, path), shell=True)
  call("convert -resize 128x128 %s/1.ps %s/thumb.png" % (path, path), shell=True)

run()
