from flask import g
from tool import scale
import pymysql




def grader(itemResult,totalQ):
    validity = True
    validity_message = ""
    print('inside PAPI module')

    if 'papi_score' not in g:
        #print("create g.papi_score")
        g.papi_score = {
        'e' : 0,
        'n' : 0,
        'a' : 0,
        'x' : 0,
        'b' : 0,
        'o' : 0,
        'z' : 0,
        'k' : 0,
        'w' : 0,
        'c' : 0,
        'l' : 0,
        'g' : 0,
        'r' : 0,
        'd' : 0,
        't' : 0,
        's' : 0,
        'i' : 0,
        'v' : 0,
        'f' : 0,
        'p' : 0
        }

    if 'papi_score_scaled' not in g:
        #print("create g.papi_score")
        g.papi_score_scaled = {
        'e' : 0,
        'n' : 0,
        'a' : 0,
        'x' : 0,
        'b' : 0,
        'o' : 0,
        'z' : 0,
        'k' : 0,
        'w' : 0,
        'c' : 0,
        'l' : 0,
        'g' : 0,
        'r' : 0,
        'd' : 0,
        't' : 0,
        's' : 0,
        'i' : 0,
        'v' : 0,
        'f' : 0,
        'p' : 0
        }




    if 'apm_total' not in g:
        g.apm_total = 0

    if 'apm_max_score' not in g:
        g.apm_max_score = 0

    if 'apm_correct' not in g:
        g.apm_correct = 0

    if 'apm_incorrect' not in g:
        g.apm_incorrect = 0

    if 'apm_empty' not in g:
        g.apm_empty = 0

    itemGrade = {}
    score = 0
    max_score = 0
    response = None

    for subelem in itemResult:
        sub_identifier = subelem.attrib['identifier']
        #print(sub_identifier)
        sub_split = sub_identifier.split('_')
        if subelem.attrib['identifier'] == 'SCORE' :
            for subelem2 in subelem:
                score = int(subelem2.text)
                g.apm_total += score
        elif subelem.attrib['identifier'] == 'MAXSCORE' :
            for subelem2 in subelem:
                max_score = int(subelem2.text)
                g.apm_max_score += max_score
        elif sub_split[0] == 'RESPONSE' :
            #print('inside response')
            for subelem2 in subelem:
                for subelem3 in subelem2:
                    response = subelem3.text
                    print('response : ', response)
                    if response is not None :
                        papi_alpha = response.split('_')
                        
                        if papi_alpha[0].lower() == 'k':
                            #pass
                            g.papi_score[papi_alpha[0].lower()] = g.papi_score[papi_alpha[0].lower()] + 1
                            prescale = scale.scale('papikostik_k', g.papi_score[papi_alpha[0].lower()])
                        elif papi_alpha[0].lower() == 'z':
                            #pass
                            g.papi_score[papi_alpha[0].lower()] = g.papi_score[papi_alpha[0].lower()] + 1
                            prescale = scale.scale('papikostik_z', g.papi_score[papi_alpha[0].lower()])     
                        else :
                            #pass
                            g.papi_score[papi_alpha[0].lower()] = g.papi_score[papi_alpha[0].lower()] + 1
                            prescale = g.papi_score[papi_alpha[0].lower()]
                            #g.papi_score_scaled[papi_alpha[0].lower()] = scale.scale('papikostik20', g.papi_score[papi_alpha[0].lower()])
                        g.papi_score_scaled[papi_alpha[0].lower()] = scale.scale('papikostik20', prescale)
                            #print('papi_score : ' , g.papi_score[papi_alpha[0].lower()])
                            #print('papi_score_scaled : ' , papi_score_scaled[papi_alpha[0].lower()])
                    else :
                        g.apm_empty += 1
                        validity = False
                        validity_message ='there are unanswered questions'
                    itemGrade["candidate_response"] = response



    data = {}
    data["type"] = 'papi'
    data["scores"] = {}
    data["scores"]["raw"] = g.papi_score
    data["scores"]["scale20"] = g.papi_score_scaled
    data["scores"]["total"] = g.apm_total
    data["scores"]["max_score"] = g.apm_max_score
    data["scores"]["validity"] = validity
    data["scores"]["validity_message"] = validity_message
    data["answers"] = {}
    data["answers"]["empty"] = g.apm_empty
    data["attributes"] = itemGrade
    #print (g.papi_score)
    #g.papi['e'] += 1
    #print (g.papi['e'])
    #print (g.papi_score_scaled)
    return data