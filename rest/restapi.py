import apm
import disc
import cfit
import papi
import adkudag4
import gatb4, tese, tkdinfo, tkdanalogiverbal, tkdidiot
import compre
import os.path
import requests
import xml.etree.ElementTree as ET
from flask import Flask, jsonify, render_template, send_from_directory
from flask_restplus import Resource, Api
from config import settings

app = Flask(__name__)
api = Api(app)

namespaces = {'owl': 'http://www.imsglobal.org/xsd/imsqti_result_v2p1'}

SERVER_URL = 'http://cat.ppsdm.com/'
BASE_URI = 'http://cat.ppsdm.com%2Fppsdm_cat.rdf%23'

GET_LATEST_URI = 'taoResultServer/QtiRestResults/getLatest?'
GET_RESULT_URI = 'taoResultServer/QtiRestResults/getQtiResultXml?'

##
## @brief Parse given assessment result
##
## @param result The assessment result from fetch request
##
## @return Object with calculated scores, answers, and testItems
##
def assessmentResultParser(result) :
    # Create a new object
    scores = {}
    answers = {}
    testItems = {}

    items = {}

    # Parse assessment result
    assessmentResult = ET.ElementTree(ET.fromstring(result.text))
    for itemResult in assessmentResult.iterfind('owl:itemResult', namespaces):
        testItem = {}
        answers = {}
        scores = {}
        identifier = itemResult.attrib['identifier']
        #print('isinde item result', identifier)
        mod_name = identifier.split('_')[0].lower()

        testItem["id"] = identifier
        testItem["mod_name"] = mod_name

        try:
            itemGrade = eval(mod_name).grader(itemResult)
            scores[mod_name] = itemGrade["scores"]
            answers[mod_name] = itemGrade["answers"]
            testItem["attributes"] = itemGrade["attributes"]
        except:
            testItem["error"] = "no function"
        items[mod_name] = {
            "scores":scores,
            "answers":answers,
            "testItems":testItems,
            "type": mod_name 
        }
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
        # Retrieve assessment result
        uri = SERVER_URL + GET_RESULT_URI + 'result=' + BASE_URI + result_id + '&delivery=' + BASE_URI + delivery_id
        r = requests.get(uri, headers={'Accept': 'application/xml'}, auth=('admin', 'admin123'))
        # Update data from parsed assessment result
        data.update(assessmentResultParser(r))

        # Serve assessment result
        return jsonify(data = data)

if __name__ == '__main__':
    app.config.from_object(settings)
    app.run()
