# -*- coding: utf-8 -*-
import os
import pyodbc
import re
import yaml

from bottle import static_file

class connector(object):
    _singleton = None
    __init_once = True

    def __new__(cls, *a, **kw):
        if cls._singleton is None:
            cls._singleton = object.__new__(cls, *a, **kw)

        return cls._singleton

    def __init__(self):
        if self.__init_once:
            BASE_DIR = os.path.dirname(os.path.abspath(__file__))
            FILEIN_DICT = BASE_DIR+"/../../resources/db_conf.yaml"

            self.__conStr = ""

            # load configuration from yaml
            f = open(FILEIN_DICT, 'r')
            conf = yaml.load(f)

            for k, v in conf.items():
                if k == "driver":
                    self.__conStr=self.__conStr+k.upper()+"={"+v+"};"
                else:
                    self.__conStr=self.__conStr+k.upper()+"="+v+";"

            f.close()

            #print self.__conStr
            self.__connection = pyodbc.connect(self.__conStr)
            self.__cursor = self.__connection.cursor()
            self.pyodbc = pyodbc

            # get table definition
            #self.__cursor.execute()

            # call __init__ only once
            self.__init_once = False


    #
    def getCursor(self):
        return self.__cursor

    def closeConnection(self):
        try:
            self.__cursor.close()
            self.__connection.close()

            self.__cursor = None
            selr.__connection = None
        except(self.pyodbc.Error) as e:
            raise ConnectorException('Connection is already closed')

    def openConnection(self):
        if self.__connection is None:
            self.__connection = pyodbc.connect(self.__conStr)
            self.__cursor = self.__connection.cursor()
            self.pyodbc = pyodbc

class ConnectorException(object):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)
