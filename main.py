import ssl
from config.config import Config
from lib.core import app

app_hostname = Config.app_hostname
app_http_port = Config.app_http_port
app_https_port = Config.app_https_port
https_options_key_pathfilename = Config.https_options_key_pathfilename
https_options_cert_pathfilename = Config.https_options_cert_pathfilename

if __name__ == '__main__':
    #app.run(host=app_hostname, port=app_http_port, debug=True)

    context = ssl.SSLContext(ssl.PROTOCOL_SSLv23)
    context.load_cert_chain(https_options_cert_pathfilename, https_options_key_pathfilename)
    app.run(host=app_hostname, port=app_https_port, debug=None, ssl_context=context)