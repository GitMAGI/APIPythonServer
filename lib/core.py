from flask import Flask, request, Response
from werkzeug.exceptions import BadRequest, HTTPException, Forbidden, Unauthorized, NotAcceptable, NotFound
from inspect import getmembers
from pprint import pprint

import sys, os
sys.path.insert(1, os.path.join(sys.path[0], '..')) #Shortcut to import from parent Directory
from custom.handlers import Handelrs
from custom.routes import Routes
from config.config import Config

app = Flask(__name__)

@app.before_request
def before_middleware():
    print('endpoint: %s, url: %s, path: %s' % (request.endpoint, request.url, request.path))

@app.before_request
def authorize():
    if(request.path == Config.app_authentication_path):
        return Response('Home', status=200, mimetype='text/plain')
    else:
        raise Unauthorized("Errore. Non autorizzato")

@app.before_request
def authenticate():
    raise Unauthorized("Errore. Non Autenticato")

@app.after_request
def finally_middleware(response):
    return response

@app.errorhandler(Exception)
def error_middleware(e):
    if isinstance(e, HTTPException):
        return Response(e.description, status=type(e).code, mimetype='text/plain')
    else:
        return Response(str(e), status=500, mimetype='text/plain')

if Routes is not None and len(Routes):
    for Route in Routes:
        path = Route['path']
        handler = Handelrs[Route['handler']]
        methods = Route['methods']
        app.route(path, methods = methods)(handler)