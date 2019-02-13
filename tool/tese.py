from flask import g
from tool import scale
import pymysql

def grader(itemResult,totalQ):
    print('entering tese module')

    if 'tese_total' not in g:
        g.tese_total = 0

    if 'tese_max_score' not in g:
        g.tese_max_score = 0

    if 'tese_correct' not in g:
        g.tese_correct = 0

    if 'tese_incorrect' not in g:
        g.tese_incorrect = 0

    if 'tese_empty' not in g:
        g.tese_empty = 0

    itemGrade = {}
    score = 0
    max_score = 0
    response = None

    for subelem in itemResult:
        sub_identifier = subelem.attrib['identifier']
        sub_split = sub_identifier.split('_')
        if subelem.attrib['identifier'] == 'SCORE' :
            for subelem2 in subelem:
                score = int(subelem2.text)
                print(sub_identifier, ' : ' ,score)
                g.tese_total = g.tese_total + score
                g.tese_correct += score
        elif subelem.attrib['identifier'] == 'MAXSCORE' :
            for subelem2 in subelem:
                max_score = int(subelem2.text)
                g.tese_max_score += max_score
        elif sub_split[0] == 'RESPONSE' :
            for subelem2 in subelem:
                for subelem3 in subelem2:
                    response = subelem3.text
                    if response == None :
                        g.tese_empty += 1
                    #print('response : ' , response)
                    itemGrade["candidate_response"] = response


    g.tese_incorrect = totalQ - g.tese_correct - g.tese_empty
    data = {}
    data["type"] = 'tese'
    data["scores"] = {}
    data["scores"]["scale20"] = scale.scale('tese', g.tese_correct)
    data["scores"]["scale6"] = scale.scale('20to6', data["scores"]["scale20"])
    #data["scores"]["scale-20"] = scale.scale('cfit-to-20', g.tese_correct)
    #data["scores"]["total"] = g.apm_total
    #data["scores"]["max_score"] = g.apm_max_score
    data["answers"] = {}
    data["answers"]["correct"] = g.tese_correct
    data["answers"]["incorrect"] = g.tese_incorrect
    data["answers"]["empty"] = g.tese_empty
    data["attributes"] = itemGrade
    print(' TOTAL tese : ', g.tese_total)
    return data