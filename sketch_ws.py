#! /usr/bin/env python
from subprocess import call, Popen, PIPE
from bottle import route, run, static_file, request, template, Bottle
import sys, os, glob
import shlex

try:
  os.makedirs(sketches)
except:
  pass

sketch = {}
for f in glob.glob("sketches/*/base.*"):
    name, ext = os.path.splitext(f)
    base = os.path.basename(os.path.dirname(name))
    sketch[base] = ext

app = Bottle()

@app.route('/')
def index():
    return static_file('index.html', root='static')

@app.route('/<filename>')
def static(filename):
    return static_file(filename, root='static')

@app.route('/sketch')
def sketches():
    global sketch
    return sketch

@app.route('/sketch/<name>/<filename>')
def sketch_file(name, filename):
    return static_file(filename, root="sketches/%s" % (name))

@app.route('/upload', method='POST')
def upload():
    print "upload"
    global sketches
    img = request.files.get('img')
    name, ext = os.path.splitext(img.filename)
    path = "sketches/%s" % (name)
    try:
      os.makedirs(path)
    except:
      pass
    img.save("%s/base%s" % (path, ext), overwrite=True)
    command_with_status("./convert_to_sketch %s %s" % (name, ext))
    sketches[name] = ext

@app.route('/print')
def print_it():
    command_with_status("./print_sketch")

def command_with_status(cmd):
    wsock = request.environ.get('wsgi.websocket')
    if not wsock:
        abort(400, 'Expected WebSocket request.')
    opts = wsock.receive()
    args = shlex.split("%s %s" % (cmd, opts))

    try:
        pipe = Popen(args, stdout=PIPE).stdout
        while True:
            line = pipe.readline()
            if line:
                wsock.send(line)
            else:
                break
    except WebSocketError:
        pass

from gevent.pywsgi import WSGIServer
from geventwebsocket import WebSocketError
from geventwebsocket.handler import WebSocketHandler
server = WSGIServer(("0.0.0.0", 8080), app, handler_class=WebSocketHandler, log=sys.stderr)
app.debug = True
server.serve_forever()
