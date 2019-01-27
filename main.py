import ssl
import socket
import uuid
from config.config import Config
from lib.core import app
from lib.logger import Logger

app_hostname = Config.app_hostname
app_http_port = Config.app_http_port
app_https_port = Config.app_https_port
https_options_key_pathfilename = Config.https_options_key_pathfilename
https_options_cert_pathfilename = Config.https_options_cert_pathfilename

def serverBootHttp():
    _port = str(app_http_port)
    _address = socket.gethostbyname(app_hostname.strip())
    _full_address = "http//" + _address + ":" + _port
    _full_hostname = "http://" + app_hostname + ":" + _port
    Logger.info(str(uuid.uuid1()).lower(), "Server is listening at " + _full_address + " or " + _full_hostname)

def serverBootHttps():
    _port = str(app_http_port)
    _address = socket.gethostbyname(app_hostname.strip())
    _full_address = "https://" + _address + ":" + _port
    _full_hostname = "https://" + app_hostname + ":" + _port
    Logger.info(str(uuid.uuid1()).lower(), "Server is listening at " + _full_address + " or " + _full_hostname)

if __name__ == '__main__':
    
    serverBootHttp()
    app.run(host=app_hostname, port=app_http_port, debug=False)
    '''
    context = ssl.SSLContext(ssl.PROTOCOL_SSLv23)
    context.load_cert_chain(https_options_cert_pathfilename, https_options_key_pathfilename)
    serverBootHttps()
    app.run(host=app_hostname, port=app_https_port, debug=None, ssl_context=context)
    '''