import json, os
import pymysql
from tool import apm as apm
from tool import disc as disc
from tool import cfit as cfit
from tool import papi as papi
from tool import adkudag4 as adkudag4
from tool import gatb4 as gatb4, tese as tese, tkdinfo as tkdinfo, tkdanalogiverbal as tkdanalogiverbal, tkdidiot as tkdidiot, tpa as tpa, form as form
from tool import compre as compre
from tool import scale as scale
from flask import g

from dotenv import load_dotenv
import requests
from flask import Flask, jsonify, render_template, send_from_directory
import xml.etree.ElementTree as ET
from tool import scale
load_dotenv()

import logging
from controller import user_controller
from controller import interpret_controller
from controller import result_controller
from collections import Counter



namespaces = {'owl': 'http://www.imsglobal.org/xsd/imsqti_result_v2p1'}

def get(self, user_id, c_id):
    # Assessment information
    #print("grader - apm")
    data = {}
    #data["type"] = "testResult"
    tool_ids = getLtiTools(c_id)
    for tool_id in tool_ids:
        print("tool id = ")
        print(tool_id)
        result_uri = getResultId(user_id, tool_id)
        delivery_uri = getDeliveryId(result_uri)

        result_id = result_uri.replace(os.getenv('BASE_URI_MYSQL'), "")
        delivery_id = delivery_uri.replace(os.getenv('BASE_URI_MYSQL'),"")
        
        # Retrieve assessment result
        uri = os.getenv('SERVER_URL') + os.getenv('GET_RESULT_URI') + 'result=' + os.getenv('BASE_URI') + result_id + '&delivery=' + os.getenv('BASE_URI') + delivery_id
        r = requests.get(uri, headers={'Accept': 'application/xml'}, auth=('admin', 't40@ppsdm'))
        # Update data from parsed assessment result
        #print(uri)
        #data.update(assessmentResultParser(r,tool_id))
        #data.update(regulerGrader(data))
        #data.update(papiParser(data))
        #return r
        # Serve assessment result
    return jsonify(data = data)


def getLtiTools(c_id) :
    conn = pymysql.connect(host='db.aws.ppsdm.com', port=3306, user='ppsdm', passwd='ppsdm-mysql', db='chamilo_ppsdm_db')
    #retval = None
    retval = []
    cur = conn.cursor()
    #print("c_id = ")
    #print(c_id)
    cur.execute("SELECT * FROM plugin_ims_lti_tool WHERE custom_params ='MAIN' AND c_id = %s", (c_id))

    for row in cur:
        print(row[0])
        #retval = row[0]
        retval.append(row[0])
        #print("retval = ")
        #print(retval)

    cur.close()
    conn.close()

    return retval

def getResultId(user_id, tool_id) :
    conn = pymysql.connect(host='db.aws.ppsdm.com', port=3306, user='ppsdm', passwd='ppsdm-mysql', db='catdb')
    retval = None
    cur = conn.cursor()
    #{"user":"PPSDM-Online-PPSDM-7","plugin_ims_lti_tool":"8"}
    query_string = '{"user":"PPSDM-Online-PPSDM-'+str(user_id)+'","plugin_ims_lti_tool":"'+str(tool_id)+'"}'
    cur.execute("SELECT * FROM lti_result_identifiers WHERE result_id = %s LIMIT 1", (query_string))

    for row in cur:
        retval = row[0]

    cur.close()
    conn.close()
    print('user_id :' + user_id)
    print('tool_id :' + str(tool_id))
    print(query_string)
    return retval

def getDeliveryId(result_id) :
    conn = pymysql.connect(host='db.aws.ppsdm.com', port=3306, user='ppsdm', passwd='ppsdm-mysql', db='catdb')
    retval = None
    cur = conn.cursor()

    cur.execute("SELECT * FROM results_storage WHERE result_id = %s LIMIT 1", (str(result_id)))

    for row in cur:
        retval = row[2]

    cur.close()
    conn.close()

    return retval