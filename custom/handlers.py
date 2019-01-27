from flask import Flask, request, Response
from werkzeug.exceptions import BadRequest, HTTPException, Forbidden, Unauthorized, NotAcceptable, NotFound

def _home_get_handler():
    response = Response(response='Home', status=200, mimetype='text/plain', content_type='text/plain')
    return response

def _user_post_handler():
    raise Exception('Errore Test Users!')
    response = Response(response='Users', status=200, mimetype='text/plain', content_type='text/plain')
    return response

def _test_get_handler(id=None):
    msg = "Tests"
    msg = msg + " ID:" + str(id) if (id) else msg
    response = Response(response=msg, status=200, mimetype='text/plain', content_type='text/plain')
    return response

def _test_post_handler():
    response = Response(response='Tests', status=200, mimetype='text/plain', content_type='text/plain')
    return response

Handelrs = {
    'home_get': _home_get_handler,    
    'user_post': _user_post_handler,  
    'test_get': _test_get_handler,  
    'test_post': _test_post_handler,  
}