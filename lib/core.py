from flask import Flask, request, Response
from json import dumps
from sqlalchemy import create_engine
from werkzeug.exceptions import BadRequest, HTTPException, Forbidden, Unauthorized, NotAcceptable, NotFound
from datetime import datetime
import uuid
import traceback
from inspect import getmembers
from pprint import pprint
from .logger import Logger
from .utilities import Utilities

import sys, os
sys.path.insert(1, os.path.join(sys.path[0], '..')) #Shortcut to import from parent Directory

from custom.handlers import Handelrs
from custom.routes import Routes
from config.config import Config

app = Flask(__name__)

_execution_id = None
_start_watch = None

def _trace_request_db(request):
    _data = _retrieve_request_info(request)

    _now = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-2]

    _dialect = Config.journal_db_connection['dialect']
    _storage = Config.journal_db_connection['storage']
    engine = create_engine(_dialect + ":///" + _storage)
    connection = engine.connect()

    _headers = None
    if(request.headers.keys()):
        _headers = []
        for key in request.headers.keys():
            _value = request.headers.get(key)
            _headers.append({key: _value})

    _body = None
    if(request.data):
        _body = str(request.get_data().decode('utf-8'))
        _body = _body.replace('\r', '')
        _body = _body.replace('\n', '')
        _body = _body.replace('\t', '')
        _body = _body.strip()

    connection.execute(
        'INSERT INTO [Request] ([OperationId], [Timestamp], [RemoteIp], [RemotePort], [RemoteProxyIp], [RemoteProxyPort], [LocalIp], [LocalPort], [Protocol], [Verb], [Path], [Headers], [Body]) VALUES (:operationid, :timestamp, :remoteip, :remoteport, :remoteproxyip, :remoteproxyport, :localip, :localport, :protocol, :verb, :path, :headers, :body)',
        { 
            'operationid': _execution_id, 
            'timestamp': _now, 
            'remoteip': _data['address'],
            'remoteport': _data['port'], 
            'remoteproxyip': dumps(_data['behindProxyAddresses']) if(_data['behindProxyAddresses']) else None,
            'remoteproxyport': dumps(_data['behindProxyPorts']) if(_data['behindProxyPorts']) else None,
            'localip': _data['localAddress'], 
            'localport': _data['localPort'], 
            'protocol': _data['protocol'],
            'verb': _data['method'],
            'path': _data['path'],
            'headers': dumps(_headers) if (_headers) else None, 
            'body': _body if(_body) else None
        }
    )

def _retrieve_request_info(request):
    _port = request.environ.get('REMOTE_PORT')
    _address = request.remote_addr
    _behindProxyAddresses = None
    if(request.environ.get('HTTP_X_FORWARDED_FOR')):
        try: 
            _behindProxyAddresses = [x.strip() for x in request.environ.get('HTTP_X_FORWARDED_FOR').split(',')]
        except: 
            pass
    _behindProxyPorts = None
    if(request.environ.get('HTTP_X_FORWARDED_PORT')):
        try: 
            _behindProxyPorts = [int(x.strip()) for x in request.environ.get('HTTP_X_FORWARDED_PORT').split(',')]
        except: 
            pass

    if(_behindProxyAddresses):
        _behindProxyAddresses.append(_address)
        _address = str(_behindProxyAddresses[0])        
        _behindProxyAddresses.pop(0)

    if(_behindProxyPorts):
        _behindProxyPorts.append(_port)
        _port = _behindProxyPorts[0]        
        _behindProxyPorts.pop(0)

    _method = request.method.upper()
    _path = request.path
    _protocol = request.scheme.upper()

    _local = None
    if(request.host):
        _local = [x.strip() for x in request.host.split(':')]
    _localAddress = None
    if(_local and _local[0]):
        _localAddress = _local[0] 
    _localPort = None
    if(_local and _local[1] and _local[1].isdigit()):
        _localPort = int(_local[1]) 

    return {
        'address': _address,
        'port': _port,
        'behindProxyAddresses': _behindProxyAddresses,
        'behindProxyPorts': _behindProxyPorts,
        'method': _method,
        'path': _path,
        'protocol': _protocol,
        'localAddress': _localAddress,
        'localPort': _localPort
    }

def _trace_response_db(response, request):
    _data = _retrieve_response_info(response, request)
    
    _now = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-2]

    _dialect = Config.journal_db_connection['dialect']
    _storage = Config.journal_db_connection['storage']
    engine = create_engine(_dialect + ":///" + _storage)
    connection = engine.connect()

    _headers = None
    if(response.headers.keys()):
        _headers = []
        for key in response.headers.keys():
            _value = response.headers.get(key)
            _headers.append({key: _value})

    _body = None
    if(response.data):
        _body = str(response.get_data().decode('utf-8'))
        _body = _body.replace('\r', '')
        _body = _body.replace('\n', '')
        _body = _body.replace('\t', '')
        _body = _body.strip()

    connection.execute(
        'INSERT INTO [Response] ([OperationId], [Timestamp], [Status], [RemoteIp], [RemotePort], [LocalIp], [LocalPort], [Headers], [Body]) VALUES (:operationid, :timestamp, :status, :remoteip, :remoteport, :localip, :localport, :headers, :body)',
        { 
            'operationid': _execution_id, 
            'timestamp': _now, 
            'status': _data['status'],
            'remoteip': _data['address'],
            'remoteport': _data['port'], 
            'localip': _data['localAddress'], 
            'localport': _data['localPort'], 
            'headers': dumps(_headers) if(_headers) else None,  
            'body': _body if(_body) else None
        }
    )

def _retrieve_response_info(response, request):
    _request_info = _retrieve_request_info(request)

    _port = _request_info['port']
    _address = _request_info['address']
    _behindProxyAddress = _request_info['behindProxyAddresses']
    if(_behindProxyAddress):
        _address = str(_behindProxyAddress[0])
    _behindProxyPorts = _request_info['behindProxyPorts']
    if(_behindProxyPorts):
        _port = str(_behindProxyPorts[0])
    _status = response.status_code
    _local = None
    if(request.host):
        _local = [x.strip() for x in request.host.split(':')]
    _localAddress = None
    if(_local and _local[0]):
        _localAddress = _local[0] 
    _localPort = None
    if(_local and _local[1] and _local[1].isdigit()):
        _localPort = int(_local[1]) 

    return {
        'address': _address,
        'port': _port,
        'localAddress': _localAddress,
        'localPort': _localPort,
        'status': _status
    }

@app.before_request
def before_middleware():
    global _execution_id
    _execution_id = str(uuid.uuid1()).lower()
    global _start_watch
    _start_watch = datetime.now()

    _request_info = _retrieve_request_info(request)

    _port = _request_info['port']
    _address = _request_info['address']
    _method = _request_info['method']
    _path = _request_info['path']
    _protocol = _request_info['protocol']

    Logger.info(_execution_id, "Incoming " + _protocol + " Request from Remote Socket " + str(_address) + ":" + str(_port) + ". '" + _method + "' for '" + _path + "'")
        
    try :
        _trace_request_db(request) 
    except Exception as err :
        Logger.warning(_execution_id, 'Error during Request Tracing', str(err)) 

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
    _end_watch = datetime.now()
    _delta = round((_end_watch - _start_watch).microseconds/1000)
    Logger.info(_execution_id, "Completed in " + Utilities.elapsedTime(_delta) + " (mm:ss.ms)")
    try :
        _trace_response_db(response, request) 
    except Exception as err :
        Logger.warning(_execution_id, 'Error during Request Tracing', str(err)) 
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