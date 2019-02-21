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
        if (result_uri is not None) :
            delivery_uri = getDeliveryId(result_uri)

            result_id = result_uri.replace(os.getenv('BASE_URI_MYSQL'), "")
            delivery_id = delivery_uri.replace(os.getenv('BASE_URI_MYSQL'),"")
            
            # Retrieve assessment result
            uri = os.getenv('SERVER_URL') + os.getenv('GET_RESULT_URI') + 'result=' + os.getenv('BASE_URI') + result_id + '&delivery=' + os.getenv('BASE_URI') + delivery_id
            r = requests.get(uri, headers={'Accept': 'application/xml'}, auth=('admin', 't40@ppsdm'))
            # Update data from parsed assessment result
            #print(uri)
            data.update(assessmentResultParser(r,tool_id))
            data.update(regulerGrader(data))
            data.update(papiParser(data))
            #return r
            # Serve assessment result
        

    return jsonify(data = data)


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
    #retval = None
    retval = []
    cur = conn.cursor()
    #print("c_id = ")
    #print(c_id)
    cur.execute("SELECT * FROM plugin_ims_lti_tool WHERE custom_params ='MAIN' AND c_id = %s", (c_id))
    #cur.execute("SELECT * FROM plugin_ims_lti_tool WHERE custom_params ='MAIN' AND c_id = %s LIMIT 1", (c_id))
    #cur.execute("SELECT * FROM plugin_ims_lti_tool WHERE c_id = %s", (c_id))

    for row in cur:
        print(row[0])
        #retval = row[0]
        retval.append(row[0])
        #print("retval = ")
        #print(retval)

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

    return items

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