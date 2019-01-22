from flask import Flask, request, Response
from werkzeug.exceptions import BadRequest, HTTPException, Forbidden, Unauthorized, NotAcceptable, NotFound
from datetime import datetime
import uuid
import traceback
from inspect import getmembers
from pprint import pprint
from logger import Logger
import sys, os
sys.path.insert(1, os.path.join(sys.path[0], '..')) #Shortcut to import from parent Directory
from custom.handlers import Handelrs
from custom.routes import Routes
from config.config import Config

app = Flask(__name__)

_execution_id = None
_start_watch = None

def _trace_request_db(request):
    pass

@app.before_request
def before_middleware():
    _execution_id = str(uuid.uuid1()).lower()
    _start_watch = datetime.now()

    _port = request.environ.get('REMOTE_PORT')
    _address = request.remote_addr
    _behindProxyAddress = request.access_route
    if(_behindProxyAddress):
        _address = _behindProxyAddress
    _method = request.method
    _path = request.path
    _protocol = request.schema

    Logger.info(_execution_id, "Incoming " + _protocol + " Request from Remote Socket " + str(_address) + ":" + str(_port) + ". '" + _method + "' for '" + _path + "'")
        
    try :
        _trace_request_db(request) 
    except Exception as err :
        Logger.warning(_execution_id, 'Error during Request Tracing', traceback.format_exc()) 


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
    print("Arrivo uguale")
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