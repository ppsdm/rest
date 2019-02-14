import tool
from tool import apm as apm
from tool import disc as disc
from tool import cfit as cfit
from tool import papi as papi
from tool import adkudag4 as adkudag4
from tool import gatb4 as gatb4, tese as tese, tkdinfo as tkdinfo, tkdanalogiverbal as tkdanalogiverbal, tkdidiot as tkdidiot, tpa as tpa, form as form
from tool import compre as compre
import os.path
import requests
import xml.etree.ElementTree as ET
from flask import Flask, jsonify, render_template, send_from_directory
from flask_restplus import Resource, Api
from config import settings
import pymysql
from flask import g
import json
import logging
from controller import user_controller
from controller import interpret_controller
from controller import result_controller
from collections import Counter

from tool import scale as scale

from grader import reguler as reguler
from grader import disc as disc
from grader import papi as papi

app = Flask(__name__)
api = Api(app)




def getToolId(resultId) :
    conn = pymysql.connect(host='db.aws.ppsdm.com', port=3306, user='ppsdm', passwd='ppsdm-mysql', db='catdb')
    retval = None
    cur = conn.cursor()
    cur.execute("SELECT * FROM lti_result_identifiers WHERE delivery_execution_id = %s LIMIT 1", (BASE_URI_MYSQL + str(resultId)))

    for row in cur:
        retval = json.loads(row[1])
        #print(retval["plugin_ims_lti_tool"])

    cur.close()
    conn.close()

    return retval["plugin_ims_lti_tool"]




@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),'favicon.ico', mimetype='image/vnd.microsoft.icon')

@api.route('/test')
class Test(Resource):
    def get(self):
        return render_template('hello.html')

@api.route('/getlatest/<string:testtaker_id>/<string:delivery_id>')
class Latest(Resource):
    def get(self, testtaker_id, delivery_id):
        # Assessment information
        data = {}
        data["type"] = "latestTestResult"
        data["id"] = delivery_id
        data["user_id"] = testtaker_id

        # Retrieve assessment result
        uri = SERVER_URL + GET_LATEST_URI + 'testtaker=' + BASE_URI + testtaker_id + '&delivery=' + BASE_URI + delivery_id
        r = requests.get(uri, headers={'Accept': 'application/xml'}, auth=('admin', 't40@ppsdm'))

        # Update data from parsed assessment result
        data.update(assessmentResultParser(r))

        # Serve assessment result
        return jsonify(data = data)

@api.route('/getresultfromuri/<string:result_id>/<string:delivery_id>')
class Resultfromuri(Resource):
    def get(self, result_id, delivery_id):
        # Assessment information
        data = {}
        #data["type"] = "testResult"
        data["id"] = delivery_id
        data["result_id"] = result_id
        tool_id = getToolId(result_id)

        # Retrieve assessment result
        uri = SERVER_URL + GET_RESULT_URI + 'result=' + BASE_URI + result_id + '&delivery=' + BASE_URI + delivery_id
        r = requests.get(uri, headers={'Accept': 'application/xml'}, auth=('admin', 't40@ppsdm'))
        # Update data from parsed assessment result
        data.update(assessmentResultParser(r,tool_id))

        # Serve assessment result
        return jsonify(data = data)


@api.route('/getresultOLD/<string:user_id>/<string:c_id>')
class ResultOLD(Resource):
    def get(self, user_id, c_id):
        # Assessment information
  
        data = {}
        #data["type"] = "testResult"
        tool_id = getLtiTools(c_id)
        result_uri = getResultId(user_id, tool_id)
        delivery_uri = getDeliveryId(result_uri)

        result_id = result_uri.replace(BASE_URI_MYSQL, "")
        delivery_id = delivery_uri.replace(BASE_URI_MYSQL,"")

        # Retrieve assessment result
        uri = SERVER_URL + GET_RESULT_URI + 'result=' + BASE_URI + result_id + '&delivery=' + BASE_URI + delivery_id
        r = requests.get(uri, headers={'Accept': 'application/xml'}, auth=('admin', 't40@ppsdm'))
        # Update data from parsed assessment result
        data.update(assessmentResultParser(r,tool_id))

        # Serve assessment result
        return jsonify(data = data)

@api.route('/getsummary/<string:delivery_id>')
class Summary(Resource):
    def get(self, delivery_id):
        # Assessment information
        data = {}
        summary_data = {}
        #data["type"] = "testResult"
        #data["id"] = delivery_id

        conn = pymysql.connect(host='db.aws.ppsdm.com', port=3306, user='ppsdm', passwd='ppsdm-mysql', db='catdb')
        retval = None
        mysql_uri = BASE_URI_MYSQL + delivery_id
        #print(mysql_uri)
        cur = conn.cursor()
        cur.execute("SELECT * FROM results_storage WHERE delivery = %s", (mysql_uri))
        #print(cur.description)
        
        for row in cur:
            data = {}
            
            retval = row[0]
            print(row[0]) #result
            result_uri = row[0].split('#')[1]
            g.reset_object = 1
            uri = SERVER_URL + GET_RESULT_URI + 'result=' + BASE_URI + result_uri + '&delivery=' + BASE_URI + delivery_id
            r = requests.get(uri, headers={'Accept': 'application/xml'}, auth=('admin', 't40@ppsdm'))
            data.update(assessmentResultParser(r))
            summary_data[result_uri] = data

            #print(row[1]) #testtaker
        #retval = cur.fetchone()
        cur.close()
        conn.close()

        return jsonify(data = summary_data)

@api.route('/getUserProfile/<string:user_id>')
class UserProfile(Resource):
    def get(self, user_id):
        # user profile data
        logging.info('UserProfile.get(%s)', user_id)
        user = user_controller.getUser(user_id)
        return jsonify(data = user)

@api.route('/getInterpret/<string:tool_name>/<string:score>')
class Interpret(Resource):
    def get(self, tool_name,score):
        # user profile data
        #logging.info('UserProfile.get(%s)', user_id)
        res = {}
        if (tool_name == "papi") :
            res = interpret_controller.getPapi(score)
            #print(res['id'])
        #uraian = user_controller.getUser(user_id)
        return jsonify(data = res)

@api.route('/getResult/<string:user_id>/<string:c_id>')
class Result(Resource):
    def get(self, user_id, c_id):
        res = {}
        reguler_psikotes_list = ['4','10']
        disc_list = ['8']
        papi_list = ['15']
        if c_id in reguler_psikotes_list:
            res = reguler.get(self, user_id, c_id)
        if c_id in papi_list:
            res = papi.get(self, user_id, c_id)
        return res


if __name__ == '__main__':
    app.config.from_object(settings)
    app.run()
