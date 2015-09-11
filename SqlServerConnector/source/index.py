# -*- coding: utf-8 -*-
import os
#import pyodbc
import re

from bottle import route, run, request
from bottle import TEMPLATE_PATH, jinja2_template as template
from bottle import static_file
from jinja2 import Environment, FileSystemLoader
#from db.connector import getCursor,closeConnection
from db.connector import connector,ConnectorException

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATE_PATH.append(BASE_DIR + "/views")

env = Environment(loader = FileSystemLoader('templates'))

# For BootStrap
@route('/css/<filename>')
def css_dir(filename):
    """ set css dir """
    return static_file(filename, root=BASE_DIR+"/static/css")

@route('/js/<filename>')
def js_dir(filename):
    """ set js dir """
    return static_file(filename, root=BASE_DIR+"/static/js")

@route('/img/<filename>')
def img_dir(filename):
    """ set img file """
    return static_file(filename, root=BASE_DIR+"/static/img")

@route('/font/<filename>')
def font_dir(filename):
    """ set font file """
    return static_file(filename, root=BASE_DIR+"/static/fonts")

@route('/<filename>')
def favicon(filename):
    return static_file(filename, root=BASE_DIR)

# For handsontable
@route('/dist/<filename>')
def handsontable(filename):
    return static_file(filename, root=BASE_DIR+"/static/dist")

@route('/top', method='GET')
def top():
    # get parameter from request body
    sql = request.forms.get('sql')
    responseData = []

    if sql != '':
        responseData = sql

    if responseData != '':
        return template('top' )
    else:
        return template('top' ,result=responseData)

@route('/query', method='GET')
@route('/query', method='POST')
def query():

    # get connector class(singleton)
    con = connector()

    # for return value
    theadList = []
    rowDataList = []

    # get parameter from request body
    sql = request.forms.get('sql')

    if sql is not None:
        # trim space
        repSql = " ".join(sql.split())
        # match = re.match(r'.*from (.*) ', repSql)
        # tableName = match.group(1)
        headerRender = True

        try:
            cur = con.getCursor()

            cur.execute(repSql)

            rows = cur.fetchall()
            for row in rows:
                rowData = []
                rowStr = []

                colNum = 0
                for t in row.cursor_description:
                    if headerRender:
                        theadList.append(t[0])

                    rowStr = row[colNum]
                    if rowStr is None:
                        rowStr = 'NULL'
                    elif  isinstance(rowStr, str):
                        rowStr = rowStr.decode('shift-jis')

                    rowData.append(rowStr)
                    colNum = colNum + 1
                headerRender = False
                rowDataList.append(rowData)

        except (con.pyodbc.Error) as e:

            print str(type(e))
            print str(e.args).decode('shift-jis')
            print str(e.message)
    else:
        sql = ''

    return template('query',query=sql , theadList=theadList, tbodyList=rowDataList, suggestItem=get_table_name_list(con)).encode('utf-8')

@route('/open', method='GET')
def open():
    con = connector()
    con.openConnection()
    return template('query')

@route('/end', method='GET')
def end():
    try:
        con = connector()
        con.closeConnection()
    except(ConnectorException) as e:
        return template('query', error=e.str)
    return template('query')

def get_table_name_list(con):
    retList = []

    cur = con.getCursor()
    sql_table_name_list = "SELECT NAME FROM sysobjects WITH(NOLOCK) WHERE xtype = 'U' ORDER BY NAME"
    cur.execute(sql_table_name_list)

    rows = cur.fetchall()
    for row in rows:
        rowStr = []

        colNum = 0
        for t in row.cursor_description:
            rowStr = row[colNum]
            if rowStr is None:
                rowStr = 'NULL'
            else:
                rowStr = rowStr.decode('shift-jis')

            retList.append(rowStr)
            colNum = colNum + 1

    return retList


if __name__ == "__main__":
    # localhost:8080 で公開するように実行
    run(host="localhost", port=8080, debug=True, reloader=True)
