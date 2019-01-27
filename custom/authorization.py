from werkzeug.exceptions import BadRequest, HTTPException, Forbidden, Unauthorized, NotAcceptable, NotFound
import json

import sys, os
sys.path.insert(1, os.path.join(sys.path[0], '..')) #Shortcut to import from parent Directory
from config.config import Config
from lib.utilities import Utilities

class Authorization:
    @staticmethod
    def authorize(_user_id, _user_name, user_groups, _method, _path):
        if not user_groups or len(user_groups) == 0 :
            raise Forbidden("You don't have rights to perform this operation")

        acls = None
        with open(Config.acl_json_path_filename) as fs:
            acls = json.load(fs)

        if(not acls or len(acls) == 0):
            raise Forbidden("You don't have rights to perform this operation")

        user_acls = []
        for user_group in user_groups:
            for acl in acls:
                if(acl and acl['Subject'].lower().strip() == user_group.lower().strip()):
                    user_acls.append(acl)

        if(not user_acls or len(user_acls) == 0):
            raise Forbidden("You don't have rights to perform this operation")

        forbidden = True
        for user_acl in user_acls:
            acl_methods = user_acl['Action']
            acl_paths = user_acl['Object']

            if(not user_acl or not acl_methods or not acl_paths):
                continue

            if(
                (acl_methods == '*' or (Utilities.findInArray(acl_methods, _method, True))) and
                (acl_paths == '*' or (Utilities.findInArray(acl_paths, _path, True)))
            ):            
                forbidden = False
                break

        if(forbidden):
            raise Forbidden("You don't have rights to perform this operation")