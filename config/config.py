class Config:
    app_hostname = 'WIN10-DEV'
    app_http_port = 8080
    app_https_port = 443
    https_options_key_pathfilename = '/Temp/APINodeServer.local/certificates/key-20190111-162019.pem'
    https_options_cert_pathfilename = '/Temp/APINodeServer.local/certificates/cert-20190111-162019.crt'

    app_authentication_path = "/v1/auth"