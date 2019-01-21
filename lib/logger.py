import getpass
import inspect
from datetime import datetime

import sys, os
sys.path.insert(1, os.path.join(sys.path[0], '..')) #Shortcut to import from parent Directory
from config.config import Config

class Logger:
    @staticmethod
    def debug(execution_id, msg, payload = None):
        curframe = inspect.currentframe()
        calframe = inspect.getouterframes(curframe, 2)
        caller = calframe[1][3]
        _log(msg, payload, 0, caller, execution_id)

    @staticmethod
    def info(execution_id, msg, payload = None):
        curframe = inspect.currentframe()
        calframe = inspect.getouterframes(curframe, 2)
        caller = calframe[1][3]
        _log(msg, payload, 1, caller, execution_id)
    
    @staticmethod
    def warning(execution_id, msg, payload = None):
        curframe = inspect.currentframe()
        calframe = inspect.getouterframes(curframe, 2)
        caller = calframe[1][3]
        _log(msg, payload, 2, caller, execution_id)
    
    @staticmethod
    def error(execution_id, msg, payload = None):
        curframe = inspect.currentframe()
        calframe = inspect.getouterframes(curframe, 2)
        caller = calframe[1][3]
        _log(msg, payload, 3, caller, execution_id)
    
    @staticmethod
    def fatal(execution_id, msg, payload = None):
        curframe = inspect.currentframe()
        calframe = inspect.getouterframes(curframe, 2)
        caller = calframe[1][3]
        _log(msg, payload, 4, caller, execution_id)

_Severity = {
    0: 'DEBUG',
    1: 'INFO',
    2: 'WARNING',
    3: 'ERROR',
    4: 'FATAL'
}

def _logConsole(msg, payload, severity, scope, execution_id):
    userName = getpass.getuser()
    loginId = userName
    
    _now = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S.%f')[:-2]

    _severity_string = _Severity[severity]
    
    line = _now + " >>> " + loginId + " | " + scope + " | " + _severity_string + " | " + execution_id + " | " + msg
    if(payload is not None):
        line += " | " + str(payload)

    print(line)

def _logDB(msg, payload, severity, scope, execution_id):
    pass

def _logFS(msg, payload, severity, scope, execution_id):
    userName = getpass.getuser()
    loginId = userName
    
    _now = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S.%f')[:-2]

    _severity_string = _Severity[severity]
    
    line = _now + " >>> " + loginId + " | " + scope + " | " + _severity_string + " | " + execution_id + " | " + msg
    if(payload is not None):
        line += " | " + str(payload)

    if(not os.path.exists(Config.journal_file_path)):
        os.makedirs(Config.journal_file_path)
    
    pathfilename = Config.journal_file_path + Config.journal_file_prefixname + "_" + datetime.utcnow().strftime('%Y_%m_%d') + ".txt"

    if os.path.exists(pathfilename):
        append_write = 'a' # append if already exists
    else:
        append_write = 'w' # make a new file if not

    highscore = open(pathfilename, append_write)
    highscore.write(line + '\n')
    highscore.close()

def _log(msg, payload, severity, scope, execution_id):
    try: 
        _logConsole(msg, payload, severity, scope, execution_id)
    except Exception as e:
        print("Console Logger failure")
        print(str(e))

    if(Config.journal_db_connection):
        try:
            _logDB(msg, payload, severity, scope, execution_id)
        except Exception as e:
            print("DB Logger failure!")
            print(str(e))

    if(Config.journal_file_path and Config.journal_file_prefixname):
        try:
            _logFS(msg, payload, severity, scope, execution_id)
        except Exception as e:
            print("File Logger failure!")
            print(str(e))