class Config:
    app_hostname = 'WIN10-DEV'
    app_http_port = 8080
    app_https_port = 443
    https_options_key_pathfilename = '/Temp/APIPythonServer.local/certificates/key-20190111-162019.pem'
    https_options_cert_pathfilename = '/Temp/APIPythonServer.local/certificates/cert-20190111-162019.crt'

    app_authentication_path = "/v1/auth"

    jwt_secret = "5QApqHFhIxT1Tb5hfaFp7G6XyNDrXFfR"
    jwt_mins_validity = 100

    journal_file_prefixname = 'journal'
    journal_file_path = '/Temp/APIPythonServer.local/logs/'
    journal_db_connection = {
        'dialect': 'sqlite',
        'storage': '/Temp/APIPythonServer.local/assets/ServerJournal.db3'        
    }

    account_db_connection = {
        'dialect': 'sqlite',
        'storage': '/Temp/APIPythonServer.local/assets/AccountRegistry.db3'
    }

    acl_json_path_filename = "/Temp/APIPythonServer.local/assets/ACL.json"