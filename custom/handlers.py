from flask import Flask, request, Response
from werkzeug.exceptions import BadRequest, HTTPException, Forbidden, Unauthorized, NotAcceptable, NotFound

def _home_get_handler():
    raise Forbidden('Errore Test Home!')
    return Response('Home', status=200, mimetype='text/plain')

def _user_post_handler():
    raise Exception('Errore Test Users!')
    return Response('Users', status=200, mimetype='text/plain')

Handelrs = {
    'home_get': _home_get_handler,    
    'user_post': _user_post_handler,  
}