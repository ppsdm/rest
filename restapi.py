import apm as apm
import disc as disc
import cfit as cfit
import papi as papi
import adkudag4 as adkudag4
import gatb4 as gatb4, tese as tese, tkdinfo as tkdinfo, tkdanalogiverbal as tkdanalogiverbal, tkdidiot as tkdidiot, tpa as tpa
import compre as compre
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

app = Flask(__name__)
api = Api(app)

namespaces = {'owl': 'http://www.imsglobal.org/xsd/imsqti_result_v2p1'}

SERVER_URL = 'http://cat.ppsdm.com/'
BASE_URI = 'http://cat.ppsdm.com%2Fppsdm_cat.rdf%23'
BASE_URI_MYSQL = 'http://cat.ppsdm.com/ppsdm_cat.rdf#'

GET_LATEST_URI = 'taoResultServer/QtiRestResults/getLatest?'
GET_RESULT_URI = 'taoResultServer/QtiRestResults/getQtiResultXml?'

def getToolId(resultId) :
    conn = pymysql.connect(host='db.aws.ppsdm.com', port=3306, user='ppsdm', passwd='ppsdm-mysql', db='catdb')
    retval = None
    cur = conn.cursor()
    cur.execute("SELECT * FROM lti_result_identifiers WHERE delivery_execution_id = %s LIMIT 1", (BASE_URI_MYSQL + resultId))

    for row in cur:
        retval = json.loads(row[1])
        #print(retval["plugin_ims_lti_tool"])

    cur.close()
    conn.close()

    return retval["plugin_ims_lti_tool"]

def testconfig(toolId) :
    conn = pymysql.connect(host='db.aws.ppsdm.com', port=3306, user='ppsdm', passwd='ppsdm-mysql', db='ppsdmdb')
    retval = {}
    #print(scalename)
    cur = conn.cursor()
    cur.execute("SELECT * FROM subtest_config WHERE lti_tool_id = %s", (toolId))
    #print(cur.description)
    for row in cur:
        retval[row[1]] = row[3]
        #print(row[2])
    #retval = cur.fetchone()
    cur.close()
    conn.close()
    return retval
##
## @brief Parse given assessment result
##
## @param result The assessment result from fetch request
##
## @return Object with calculated scores, answers, and testItems
##
def assessmentResultParser(result,toolId) :
    # Create a new object
    scores = {}
    answers = {}
    testItems = {}
    errors = ""

    items = {}
    totalQ = {}
    totalQ = testconfig(toolId)
    # Parse assessment result
    assessmentResult = ET.ElementTree(ET.fromstring(result.text))

    for itemResult in assessmentResult.iterfind('owl:itemResult', namespaces):
        #testItems.clear()
        answers = {}
        scores = {}
        errors = ""
        #identifier = ""
        identifier = itemResult.attrib['identifier']
        testItems[identifier] = {}
        #print('isinde item result', identifier)
        mod_name = identifier.split('_')[0].lower()
        
        
        if mod_name not in totalQ:
            totalQ[mod_name] = 0
        #testItems["mod_name"] = mod_name

        try:
            itemGrade = eval(mod_name).grader(itemResult,totalQ[mod_name])
            scores = itemGrade["scores"]
            answers = itemGrade["answers"]
            if "items" in itemGrade:
             testItems[identifier] = itemGrade["items"]
            #testItems[identifier]["attributes"] = itemGrade["attributes"]
            #print("success")
            items[mod_name] = {
                "scores":scores,
                "answers":answers,
                "testItems":testItems[identifier],
                "type": mod_name,
                "errors" : errors
            }

        except:
            errors = "invalid"
            print('no function for ' + identifier)

#        items[mod_name] = {
 #               "scores":scores,
  #              "answers":answers,
   #             "testItems":testItems[identifier],
    #            "type": mod_name,
     #           "errors" : errors
      #  }

        #testItems.append(testItem)
    return items
    # Return assessment result
    #return {
        #"scores":scores,
        #"answers":answers,
        ##"testItems":testItems,
        #"type": mod_name
   # }

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
        r = requests.get(uri, headers={'Accept': 'application/xml'}, auth=('admin', 'admin123'))

        # Update data from parsed assessment result
        data.update(assessmentResultParser(r))

        # Serve assessment result
        return jsonify(data = data)

@api.route('/getresult/<string:result_id>/<string:delivery_id>')
class Result(Resource):
    def get(self, result_id, delivery_id):
        # Assessment information
        data = {}
        #data["type"] = "testResult"
        data["id"] = delivery_id
        data["result_id"] = result_id
        tool_id = getToolId(result_id)

        # Retrieve assessment result
        uri = SERVER_URL + GET_RESULT_URI + 'result=' + BASE_URI + result_id + '&delivery=' + BASE_URI + delivery_id
        r = requests.get(uri, headers={'Accept': 'application/xml'}, auth=('admin', 'admin123'))
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
            r = requests.get(uri, headers={'Accept': 'application/xml'}, auth=('admin', 'admin123'))
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

if __name__ == '__main__':
    app.config.from_object(settings)
    app.run()
