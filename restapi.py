import apm as apm
import disc as disc
import cfit as cfit
import papi as papi
import adkudag4 as adkudag4
import gatb4 as gatb4, tese as tese, tkdinfo as tkdinfo, tkdanalogiverbal as tkdanalogiverbal, tkdidiot as tkdidiot, tpa as tpa, form as form
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
from controller import interpret_controller
from collections import Counter

import scale as scale

app = Flask(__name__)
api = Api(app)

namespaces = {'owl': 'http://www.imsglobal.org/xsd/imsqti_result_v2p1'}

SERVER_URL = 'http://cat.ppsdm.com/'
BASE_URI = 'http://cat.ppsdm.com%2Fppsdm_cat.rdf%23'
BASE_URI_MYSQL = 'http://cat.ppsdm.com/ppsdm_cat.rdf#'

GET_LATEST_URI = 'taoResultServer/QtiRestResults/getLatest?'
GET_RESULT_URI = 'taoResultServer/QtiRestResults/getQtiResultXml?'

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

def getLtiTools(c_id) :
    conn = pymysql.connect(host='db.aws.ppsdm.com', port=3306, user='ppsdm', passwd='ppsdm-mysql', db='chamilo_ppsdm_db')
    retval = None
    cur = conn.cursor()
    #print("c_id = ")
    #print(c_id)
    cur.execute("SELECT * FROM plugin_ims_lti_tool WHERE custom_params ='MAIN' AND c_id = %s LIMIT 1", (c_id))

    for row in cur:
        retval = row[0]
        #print("retval = ")
        #print(retval)

    cur.close()
    conn.close()

    return retval

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

def testconfig(toolId) :
    conn = pymysql.connect(host='db.aws.ppsdm.com', port=3306, user='ppsdm', passwd='ppsdm-mysql', db='ppsdmdb')
    retval = {}
    #print(scalename)
    cur = conn.cursor()
    cur.execute("SELECT * FROM subtest_config WHERE lti_tool_id = %s", (str(toolId)))
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

    for testResult in assessmentResult.iterfind('owl:testResult', namespaces):
        datestamp = testResult.attrib['datestamp']
        items['datestamp'] = datestamp


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

def papiParser(dataObject) :
    items = dataObject
    papiscores = dataObject['papi']['scores']['raw']
    for papiscore in papiscores :
        #print(papiscore + str(papiscores[papiscore]))
        interpretationres = interpret_controller.getPapi(papiscore + str(papiscores[papiscore]))
        #print(": " + interpretationres['id'])
    papi_ids_2 = Counter(g.papi_id_list["2"])
    papi_id_2_dict = {}
    for papi_id_2 in papi_ids_2:
        if papi_ids_2[papi_id_2] == 1:
            papi_id_2_dict[papi_id_2] = interpret_controller.getPapiInterpretationById(papi_id_2)

    papi_ids_4 = Counter(g.papi_id_list["4"])
    papi_id_4_dict = {}
    for papi_id_4 in papi_ids_4:
        if papi_ids_4[papi_id_4] == 2:
            papi_id_4_dict[papi_id_4] = interpret_controller.getPapiInterpretationById(papi_id_4)


    papi_ids_6 = Counter(g.papi_id_list["6"])
    papi_id_6_dict = {}
    for papi_id_6 in papi_ids_6:
        if papi_ids_6[papi_id_6] == 3:
            papi_id_6_dict[papi_id_6] = interpret_controller.getPapiInterpretationById(papi_id_6)

    papi_ids_8 = Counter(g.papi_id_list["8"])
    papi_id_8_dict = {}
    for papi_id_8 in papi_ids_8:
        if papi_ids_8[papi_id_8] == 4:
            papi_id_8_dict[papi_id_8] = interpret_controller.getPapiInterpretationById(papi_id_8)

    papi_ids_10 = Counter(g.papi_id_list["10"])
    papi_id_10_dict = {}
    for papi_id_10 in papi_ids_10:
        if papi_ids_10[papi_id_10] == 5:
            papi_id_10_dict[papi_id_10] = interpret_controller.getPapiInterpretationById(papi_id_10)

    items['papi']['uraian_2'] = papi_id_2_dict
    items['papi']['uraian_4'] = papi_id_4_dict
    items['papi']['uraian_6'] = papi_id_6_dict
    items['papi']['uraian_8'] = papi_id_8_dict
    items['papi']['uraian_10'] = papi_id_10_dict
    papi_list = g.papi_id_list
    return items
def regulerGrader(dataObject) :
    # Create a new object
    items = dataObject
       
    items['output'] = {}
    items['output']['kecepatan20'] = scale.scale('kecepatanketelitian20',(
                                    items['apm']['answers']['correct'] + 
                                    items['apm']['answers']['incorrect'] + 
                                    items['compre']['answers']['correct'] + 
                                    items['compre']['answers']['incorrect'] +
                                    items['tkdinfo']['answers']['correct'] + 
                                    items['tkdinfo']['answers']['incorrect'] +
                                    items['tkdidiot']['answers']['correct'] + 
                                    items['tkdidiot']['answers']['incorrect'] +
                                    items['tkdanalogiverbal']['answers']['correct'] + 
                                    items['tkdanalogiverbal']['answers']['incorrect'] +
                                    items['gatb4']['answers']['correct'] + 
                                    items['gatb4']['answers']['incorrect'] +
                                    items['adkudag4']['answers']['correct'] + 
                                    items['adkudag4']['answers']['incorrect'] +
                                    items['tese']['answers']['correct'] + 
                                    items['tese']['answers']['incorrect'])  * 100.0 /246)

    items['output']['ketelitian20'] = scale.scale('kecepatanketelitian20',(items['apm']['answers']['correct'] + 
                                    items['compre']['answers']['correct'] + 
                                    items['tkdinfo']['answers']['correct'] + 
                                    items['tkdidiot']['answers']['correct'] +   
                                    items['tkdanalogiverbal']['answers']['correct'] + 
                                    items['gatb4']['answers']['correct'] + 
                                    items['adkudag4']['answers']['correct'] + 
                                    items['tese']['answers']['correct']) * 100.0 /246)

    items['output']['inteligensi_umum'] = scale.scale('20to6',round((items['apm']['scores']['scale20'] + items['gatb4']['scores']['scale20'] + items['tkdidiot']['scores']['scale20'])/3))
    items['output']['daya_tangkap'] = scale.scale('20to6',round((items['compre']['scores']['scale20'] + items['tkdanalogiverbal']['scores']['scale20'] + items['tese']['scores']['scale20'])/3))
    items['output']['pemecahan_masalah'] = scale.scale('20to6',round((items['apm']['scores']['scale20'] + items['tkdidiot']['scores']['scale20'] + items['gatb4']['scores']['scale20'] + items['tese']['scores']['scale20'])/4))
    items['output']['kemampuan_analisa_sintesa'] = scale.scale('20to6',round(((items['apm']['scores']['scale20'] * 3) + items['tkdidiot']['scores']['scale20'] + items['gatb4']['scores']['scale20'] + items['tese']['scores']['scale20'])/6))
    items['output']['logika_berpikir'] = scale.scale('20to6',round((items['tkdidiot']['scores']['scale20'] + items['gatb4']['scores']['scale20'] + items['tese']['scores']['scale20'])/3))
    items['output']['penalaran_verbal']  = scale.scale('20to6',round((items['compre']['scores']['scale20'] + items['tkdanalogiverbal']['scores']['scale20'] + items['tkdidiot']['scores']['scale20'])/3))
    items['output']['penalaran_numerik'] = scale.scale('20to6',round((items['gatb4']['scores']['scale20'] + items['tese']['scores']['scale20'])/2))
    items['output']['wawasan_pengetahuan'] = scale.scale('20to6',round((items['compre']['scores']['scale20'] + items['tkdinfo']['scores']['scale20'])/2))
    items['output']['kemampuan_abstrak'] = scale.scale('20to6',round(((items['apm']['scores']['scale20'] * 2)+ items['tkdidiot']['scores']['scale20'] + items['tese']['scores']['scale20'])/4))
    items['output']['kemampuan_praktis'] = scale.scale('20to6',round((items['adkudag4']['scores']['scale20'] + items['tese']['scores']['scale20'])/2))
    items['output']['kemampuan_keteknikan'] = scale.scale('20to6',items['tese']['scores']['scale20'])
    items['output']['daya_ingat'] =  scale.scale('20to6',round(((items['tkdinfo']['scores']['scale20'] * 2)+ items['compre']['scores']['scale20'] + items['adkudag4']['scores']['scale20'])/4))
    items['output']['kemampuan_dan_proses_belajar'] = scale.scale('20to6',round((items['apm']['scores']['scale20'] + items['compre']['scores']['scale20'] + items['tkdinfo']['scores']['scale20'])/3))

    items['output']['kematangan_sosial'] = scale.scale('20to6',round((items['papi']['scores']['scale20']['s'] + 
                                            items['papi']['scores']['scale20']['b'] +
                                             items['papi']['scores']['scale20']['o'] +
                                              items['papi']['scores']['scale20']['e'])/4))


    items['output']['stabilitas_emosi'] = scale.scale('20to6',round((items['papi']['scores']['scale20']['e'])/1))
    items['output']['penyesuaian_diri'] = scale.scale('20to6',round((items['papi']['scores']['scale20']['b'] + 
                                              items['papi']['scores']['scale20']['z'])/2))

    items['output']['pengendalian_diri'] = scale.scale('20to6',round((items['papi']['scores']['scale20']['z'] + 
                                            items['papi']['scores']['scale20']['b'] +
                                             items['papi']['scores']['scale20']['k'] +
                                              items['papi']['scores']['scale20']['e'])/4))

    items['output']['kepercayaan_diri'] = scale.scale('20to6',round((items['papi']['scores']['scale20']['z'] + 
                                             items['papi']['scores']['scale20']['k'] +
                                              items['papi']['scores']['scale20']['x'])/3))
    items['output']['penyesuaian_diri'] = scale.scale('20to6',round((items['papi']['scores']['scale20']['v'] + 
                                              items['papi']['scores']['scale20']['a'])/2))

    items['output']['kerjasama'] = scale.scale('20to6',round((items['papi']['scores']['scale20']['p'] + 
                                            items['papi']['scores']['scale20']['b'] +
                                             items['papi']['scores']['scale20']['k'] +
                                              items['papi']['scores']['scale20']['f'])/4))


    items['output']['hubungan_interpersonal'] = scale.scale('20to6',round((items['papi']['scores']['scale20']['x'] + 
                                            items['papi']['scores']['scale20']['b'] +
                                             items['papi']['scores']['scale20']['s'] +
                                              items['papi']['scores']['scale20']['o'])/4))

    items['output']['sistematika_kerja'] = scale.scale('20to6',round((items['papi']['scores']['scale20']['i'] + 
                                            items['papi']['scores']['scale20']['d'] +
                                             items['papi']['scores']['scale20']['c'] +
                                              items['papi']['scores']['scale20']['w'])/4))

    items['output']['fleksibilitas_kerja'] = scale.scale('20to6',round((items['papi']['scores']['scale20']['z'] + 
                                             items['papi']['scores']['scale20']['i'] +
                                              items['papi']['scores']['scale20']['w'])/3))


    items['output']['tempo_kerja'] = scale.scale('20to6',round((items['papi']['scores']['scale20']['t'] + 
                                            items['papi']['scores']['scale20']['v'] +
                                             items['output']['kecepatan20'] +
                                              items['papi']['scores']['scale20']['n'])/4))
    items['output']['ketekunan'] = scale.scale('20to6',round((items['papi']['scores']['scale20']['d'] + 
                                            items['adkudag4']['scores']['scale20'] + 
                                             items['output']['ketelitian20'] +
                                              items['papi']['scores']['scale20']['c'])/4))
    items['output']['ketelitian'] = scale.scale('20to6',items['output']['ketelitian20'])
    items['output']['daya_tahan_kerja_rutin'] = scale.scale('20to6',round((items['papi']['scores']['scale20']['g'] + 
                                                       items['papi']['scores']['scale20']['v'] +
                                                                             items['papi']['scores']['scale20']['z'] +
                                                                     items['papi']['scores']['scale20']['e'] +
                                              items['papi']['scores']['scale20']['n'])/5))

    items['output']['daya_tahan_dalam_stress'] = scale.scale('20to6',round((items['papi']['scores']['scale20']['g'] + 
                                             items['papi']['scores']['scale20']['e'] +
                                              items['papi']['scores']['scale20']['n'])/3))
    items['output']['motivasi_berprestasi'] = scale.scale('20to6',round((items['papi']['scores']['scale20']['g'] + 
                                             (items['papi']['scores']['scale20']['a'] * 3) +
                                               items['papi']['scores']['scale20']['v'] +
                                              items['papi']['scores']['scale20']['n'])/6))
    items['output']['orientasi_pelayanan'] = scale.scale('20to6',round((items['papi']['scores']['scale20']['k'] + 
                                             items['papi']['scores']['scale20']['f'] +
                                              items['papi']['scores']['scale20']['n'])/3))

    items['output']['komitmen_kerja'] = scale.scale('20to6',round((items['papi']['scores']['scale20']['g'] + 
                                              items['papi']['scores']['scale20']['n'])/2))
    items['output']['konsep_diri'] = scale.scale('20to6',round((items['papi']['scores']['scale20']['a'] + 
                                              items['papi']['scores']['scale20']['v'])/2))

    items['output']['inisiatif'] = scale.scale('20to6',round((items['papi']['scores']['scale20']['l'] + 
                                            items['papi']['scores']['scale20']['i'] +
                                             items['papi']['scores']['scale20']['t'] +
                                              items['papi']['scores']['scale20']['z'])/4))
    
    items['output']['subtest_rs_total'] = (items['apm']['answers']['correct'] + items['compre']['answers']['correct'] + items['gatb4']['answers']['correct'] + items['tkdinfo']['answers']['correct'] + items['tkdidiot']['answers']['correct'] + items['tkdanalogiverbal']['answers']['correct'] + 
                                            items['adkudag4']['answers']['correct'] + 
                                            items['tese']['answers']['correct'])
    items['output']['subtest_ss_total'] = (items['apm']['scores']['scale20'] + 
                                            items['compre']['scores']['scale20'] + 
                                            items['gatb4']['scores']['scale20'] + 
                                            items['tkdinfo']['scores']['scale20'] + 
                                            items['tkdidiot']['scores']['scale20'] + 
                                            items['tkdanalogiverbal']['scores']['scale20'] + 
                                            items['adkudag4']['scores']['scale20'] + 
                                            items['tese']['scores']['scale20'])
    items['output']['kecepatan_percentage'] = ((items['apm']['answers']['correct'] + 
                                    items['apm']['answers']['incorrect'] + 
                                    items['compre']['answers']['correct'] + 
                                    items['compre']['answers']['incorrect'] +
                                    items['tkdinfo']['answers']['correct'] + 
                                    items['tkdinfo']['answers']['incorrect'] +
                                    items['tkdidiot']['answers']['correct'] + 
                                    items['tkdidiot']['answers']['incorrect'] +
                                    items['tkdanalogiverbal']['answers']['correct'] + 
                                    items['tkdanalogiverbal']['answers']['incorrect'] +
                                    items['gatb4']['answers']['correct'] + 
                                    items['gatb4']['answers']['incorrect'] +
                                    items['adkudag4']['answers']['correct'] + 
                                    items['adkudag4']['answers']['incorrect'] +
                                    items['tese']['answers']['correct'] + 
                                    items['tese']['answers']['incorrect']) * 1.0 / 246)
    items['output']['ketelitian_percentage'] = ((items['apm']['answers']['correct'] + 
                                    items['compre']['answers']['correct'] + 
                                    items['tkdinfo']['answers']['correct'] + 
                                    items['tkdidiot']['answers']['correct'] + 
                                    items['tkdanalogiverbal']['answers']['correct'] + 
                                    items['gatb4']['answers']['correct'] + 
                                    items['adkudag4']['answers']['correct'] + 
                                    items['tese']['answers']['correct']) * 1.0 / 246)
    return items



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

@api.route('/getreguler/<string:user_id>/<string:c_id>')
class Reguler(Resource):
    def get(self, user_id, c_id):
        # Assessment information
  
        data = {}
        #data["type"] = "testResult"
        tool_id = getLtiTools(c_id)
        print("tool id = ")
        print(tool_id)
        result_uri = getResultId(user_id, tool_id)
        delivery_uri = getDeliveryId(result_uri)

        result_id = result_uri.replace(BASE_URI_MYSQL, "")
        delivery_id = delivery_uri.replace(BASE_URI_MYSQL,"")

        # Retrieve assessment result
        uri = SERVER_URL + GET_RESULT_URI + 'result=' + BASE_URI + result_id + '&delivery=' + BASE_URI + delivery_id
        r = requests.get(uri, headers={'Accept': 'application/xml'}, auth=('admin', 't40@ppsdm'))
        # Update data from parsed assessment result
        data.update(assessmentResultParser(r,tool_id))
        data.update(regulerGrader(data))
        data.update(papiParser(data))

        # Serve assessment result
        return jsonify(data = data)


@api.route('/getresult/<string:user_id>/<string:c_id>')
class Result(Resource):
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

if __name__ == '__main__':
    app.config.from_object(settings)
    app.run()
