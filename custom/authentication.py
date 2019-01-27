from werkzeug.exceptions import BadRequest, HTTPException, Forbidden, Unauthorized, NotAcceptable, NotFound
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship, Session
from sqlalchemy import Table, create_engine, Column, ForeignKey, Integer, String, DateTime, Boolean
import hashlib
import base64
from datetime import datetime

import sys, os
sys.path.insert(1, os.path.join(sys.path[0], '..')) #Shortcut to import from parent Directory
from config.config import Config

_Base = declarative_base()

class Authentication:
    @staticmethod
    def authenticate(body):
        if(body):
            username = body['username'] if 'username' in body else None
            password = body['password'] if 'password' in body else None

        # Request Validation
        errs = []
        if(not username):
            errs.append("username")
        if(not password):
            errs.append("password")
        if(len(errs) > 0):
            raise BadRequest('Missing mandatory fields: ', ", ".join(map(str, errs)))     

        _user = _getUserByUsername(username)
        if(not _user):
            raise Unauthorized("Can't access your account")

        hashAlg = _user['PasswordHASHAlgorithm']
        hashPassDB = str(_user['PasswordHASH']).strip()
        hashPassRaw = hashlib.new(hashAlg, bytes(password, 'utf8')).digest()
        hashPass =  base64.b64encode(hashPassRaw).decode('utf8').strip()

        if(hashPassDB == hashPass):
            _now = datetime.now()
            if(_user['ExpirationDate'] and _user['ExpirationDate'] < _now):
                raise Unauthorized("Account Expired")
            
            if(_user['PasswordExpirationDate'] and _user['PasswordExpirationDate'] < _now):
                raise Unauthorized("Password Expired")

            if(_user['UnlockingDate'] and _user['UnlockingDate'] > _now):
                raise Unauthorized("Account Locked. Will be unlocked at " + _user['UnlockingDate'].strftime('%Y-%m-%d %H:%M:%S.%f')[:-2])

            if(_user['Disabled']):
                raise Unauthorized("Account Disabled")
        else:
            raise Unauthorized("Can't access your account")

        _groups = _getGroupsByUsername(username)
                
        _user_name = _user['Username']
        _user_id = _user['UserId']
        _group_names = []
        for _group in _groups:
            _group_names.append(_group['GroupName'])

        return {
            'id' : _user_id,
            'username': _user_name,
            'groups': _group_names
        }

def _getUserByUsername(username):
    _dialect = Config.account_db_connection['dialect']
    _storage = Config.account_db_connection['storage']
    engine = create_engine(_dialect + ":///" + _storage)
    connection = engine.connect()
    Session = sessionmaker(bind=engine)
    session = Session()

    try:  
        _data = None      
        _results = session.query(User).filter(User.Username == username).first()
        if(_results):
            _data = _results.__dict__
        return _data
    except:
        raise
    finally:
        session.close()
        connection.close()
        engine.dispose()

def _getGroupsByUsername(username):
    _dialect = Config.account_db_connection['dialect']
    _storage = Config.account_db_connection['storage']
    engine = create_engine(_dialect + ":///" + _storage)
    connection = engine.connect()
    Session = sessionmaker(bind=engine)
    session = Session()

    try:  
        _data = None      
        _results = session.query(Group).filter(Group.Users.any(User.Username == username)).all()
        if(_results):
            _data = []
            for _result in _results:
                _data.append(_result.__dict__)
        return _data
    except:
        raise
    finally:
        session.close()
        connection.close()
        engine.dispose()

_groupmember_association_table = Table('GroupMember', _Base.metadata,
    Column('GroupId', String, ForeignKey('Group.GroupId')),
    Column('UserId', String, ForeignKey('Account.UserId'))
)

class User(_Base):
    __tablename__ = 'Account'

    UserId = Column(String, primary_key=True)
    Username = Column(String, nullable=False)
    PasswordHASH = Column(String, nullable=False)
    PasswordHASHAlgorithm = Column(String, nullable=False)
    Email = Column(String, nullable=False)
    EmailForRecovery = Column(String, nullable=False)
    PasswordExpirationDate = Column(DateTime)
    Deleted = Column(Boolean, nullable=False)
    Disabled  = Column(Boolean, nullable=False)
    ExpirationDate = Column(DateTime)
    UnlockingDate = Column(DateTime)
    CreationUser = Column(String, nullable=False)
    CreationDate = Column(DateTime, nullable=False)
    LastModifiedUser = Column(String, nullable=False)
    LastModifiedDate = Column(DateTime, nullable=False)

    Groups = relationship("Group", secondary=_groupmember_association_table, back_populates="Users")

    def __init__(self, name):
        self.name = name

class Group(_Base):
    __tablename__ = 'Group'

    GroupId = Column(String, primary_key=True)
    GroupName = Column(String, nullable=False)
    CreationUser = Column(String, nullable=False)
    CreationDate = Column(DateTime, nullable=False)
    LastModifiedUser = Column(String, nullable=False)
    LastModifiedDate = Column(DateTime, nullable=False)

    Users = relationship("User", secondary=_groupmember_association_table, back_populates="Groups")

    def __init__(self, name):
        self.name = name    