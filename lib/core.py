from flask import Flask, request, jsonify, Response
import json
from sqlalchemy import create_engine
from werkzeug.exceptions import BadRequest, HTTPException, Forbidden, Unauthorized, NotAcceptable, NotFound
from datetime import datetime, timedelta
import uuid
import jwt
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
from custom.authentication import Authentication
from custom.authorization import Authorization

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

    try:
        connection.execute(
            'INSERT INTO [Request] ([OperationId], [Timestamp], [RemoteIp], [RemotePort], [RemoteProxyIp], [RemoteProxyPort], [LocalIp], [LocalPort], [Protocol], [Verb], [Path], [Headers], [Body]) VALUES (:operationid, :timestamp, :remoteip, :remoteport, :remoteproxyip, :remoteproxyport, :localip, :localport, :protocol, :verb, :path, :headers, :body)',
            { 
                'operationid': _execution_id, 
                'timestamp': _now, 
                'remoteip': _data['address'],
                'remoteport': _data['port'], 
                'remoteproxyip': json.dumps(_data['behindProxyAddresses']) if(_data['behindProxyAddresses']) else None,
                'remoteproxyport': json.dumps(_data['behindProxyPorts']) if(_data['behindProxyPorts']) else None,
                'localip': _data['localAddress'], 
                'localport': _data['localPort'], 
                'protocol': _data['protocol'],
                'verb': _data['method'],
                'path': _data['path'],
                'headers': json.dumps(_headers) if (_headers) else None, 
                'body': _body if(_body) else None
            }
        )
    except:
        raise
    finally:
        connection.close()
        engine.dispose()

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

    try:
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
                'headers': json.dumps(_headers) if(_headers) else None,  
                'body': _body if(_body) else None
            }
        )
    except:
        raise
    finally:
        connection.close()
        engine.dispose()

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
    finally:
        pass

@app.before_request
def error404_middleware():
    notfound = True
    _current_path = request.url_rule.rule if request.url_rule else request.path
    _current_method = request.method
    for rule in app.url_map.iter_rules():        
        if _current_method in rule.methods and _current_path == rule.rule:
            notfound = False
            break
    if (notfound):
        raise NotFound('Cannot ' + request.method + ' on ' + request.path)
    else:
        pass

@app.before_request
def authorize():
    if(request.path != Config.app_authentication_path):
        _auth_header = request.environ.get('HTTP_X_ACCESS_TOKEN') or request.environ.get('HTTP_AUTHORIZATION') # Express headers are auto converted to lowercase
        if(not _auth_header):
            raise Unauthorized("Token is missing")
        _jwt_token = _auth_header

        bearer, _, _jwt_token = _auth_header.partition(' ')
        if not bearer or bearer.lower() != "bearer":
            raise Unauthorized('A Bearer Token was expected')

        _user_id = None
        _user_name = None
        _user_groups = []

        _method = request.method
        _path = request.url_rule.rule if request.url_rule else request.path

        try:
            # AUTHENTICATION (JWT Validation)
            _decoded = jwt.decode(_jwt_token, Config.jwt_secret)
            _user = _decoded['data']['user'] if _decoded['data'] else None
            if(not _user):
                raise Unauthorized("User object not found into data of the Jwt")            
            _user_id = _user['id'] if 'id' in _user else None
            _user_name = _user['username'] if 'username' in _user else None
            _user_groups = _user['groups'] if 'groups' in _user else None
        except jwt.PyJWTError as e:
            msg = e.args[0] if e.args else "Token Decoding Error"
            if isinstance(e, jwt.DecodeError) :
                msg = "Invalid or Malformed Token"                
            elif isinstance(e, jwt.ExpiredSignatureError) :
                msg = "Token expired"            
            raise Unauthorized(msg)

        try:
            Authorization.authorize(_user_id, _user_name, _user_groups, _method, _path)
        except HTTPException as err:
            msg = err.description if err.description else str(err)
            raise Forbidden(msg)
        except Exception as err:
            msg = err.args[0] if hasattr(err, 'args') else str(err)
            raise Forbidden(msg)
        finally:
            pass
    else:
        pass

@app.after_request
def finally_middleware(response):
    _end_watch = datetime.now()
    _delta = round((_end_watch - _start_watch).microseconds/1000)
    Logger.info(_execution_id, "Completed in " + Utilities.elapsedTime(_delta) + " (mm:ss.ms)")
    try :
        _trace_response_db(response, request) 
    except Exception as err :
        Logger.warning(_execution_id, 'Error during Response Tracing', str(err)) 
    finally:
        return response

@app.errorhandler(Exception)
def error_middleware(e):
    response_data = None
    response_status = 500
    response_mimetype = 'text/plain'
    response_content_type = 'text_plain'
    response_headers = None
    response_direct_passthrough = False

    if isinstance(e, HTTPException):
        Logger.error(_execution_id, e.description, str(e))

        response_data = e.description
        response_status = type(e).code
        response_content_type = 'text/plain'
        response_mimetype = 'text/plain'
        response_headers = None
        response_direct_passthrough = False
    else:   
        Logger.error(_execution_id, str(e), None)

        response_data = 'Service Unavailable'
        response_status = 500
        response_content_type = 'text/plain'
        response_mimetype = 'text/plain'
        response_headers = None
        response_direct_passthrough = False

    response = app.response_class(
        response=response_data, 
        status=response_status, 
        headers=response_headers, 
        mimetype=response_mimetype, 
        content_type=response_content_type, 
        direct_passthrough=response_direct_passthrough
    )

    return response

def _authentication_handler():
    # VALIDATE AUTH Request
    if(not request.data):
        raise BadRequest('Request Body is missing') 

    body = json.loads(request.get_data())

    # AUTHENTICATION (Credentials) AND GET USER INFO
    data = Authentication.authenticate(body)
    
    # GENERATE JWT        
    jwt_token_expiration = datetime.now() + timedelta(minutes = int(Config.jwt_mins_validity))
    jwt_token_expiration_string = jwt_token_expiration.strftime('%Y-%m-%d %H:%M:%S.%f')[:-2]
    jwt_token = jwt.encode(
        {
            'exp':jwt_token_expiration, 
            'data': {
                'user': data 
            }
        }, 
        Config.jwt_secret
    )
    
    response = Response(
        response=json.dumps({
            "token": jwt_token.decode('utf8'),
            "expiration": jwt_token_expiration_string
        }),
        status=200, 
        mimetype='application/json', 
        content_type='application/json',
        direct_passthrough=False
    )
    return response

app.route(Config.app_authentication_path, methods=['POST'], strict_slashes=False)(_authentication_handler)
if Routes is not None and len(Routes):
    for Route in Routes:
        path = Route['path']
        handler = Handelrs[Route['handler']]
        methods = Route['methods']
        app.route(path, methods=methods, strict_slashes=False)(handler)