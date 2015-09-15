#! /usr/bin/env python
from subprocess import call
from bottle import route, run, static_file, request, template
import os, glob

try:
  os.makedirs(sketches)
except:
  pass

images = {}
for f in glob.glob("sketches/*/base.*"):
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
    return static_file(filename, root="sketches/%s" % (name))

@route('/upload', method='POST')
def upload():
    img = request.files.get('img')
    name, ext = os.path.splitext(img.filename)
    path = "sketches/%s" % (name)
    try:
      os.makedirs(path)
    except:
      pass
    img.save("%s/base%s" % (path, ext), overwrite=True)
    call("./convert_to_sketch %s %s" % (name, ext), shell=True)
    images[name] = ext
    return images

@route('/sketches/<name>/print')
def print_it(sketch):
    call("./print_sketch %s" % sketch, shell=True)

run()
