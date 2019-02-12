from flask import g
from ..tool import scale
import pymysql

def grader(itemResult,totalQ):
    print('entering CFIT module')

    if 'cfit_total' not in g:
        g.cfit_total = 0

    if 'cfit_max_score' not in g:
        g.cfit_max_score = 0

    if 'cfit_correct' not in g:
        g.cfit_correct = 0

    if 'cfit_incorrect' not in g:
        g.cfit_incorrect = 0

    if 'cfit_empty' not in g:
        g.cfit_empty = 0

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
                g.cfit_correct += score
        elif subelem.attrib['identifier'] == 'MAXSCORE' :
            for subelem2 in subelem:
                max_score = int(subelem2.text)
                g.cfit_max_score += max_score
        elif sub_split[0] == 'RESPONSE' :
            for subelem2 in subelem:
                for subelem3 in subelem2:
                    response = subelem3.text
                    print(response)
                    if response == None :
                        g.cfit_empty += 1
                    itemGrade["candidate_response"] = response


    g.cfit_incorrect = totalQ - g.cfit_correct - g.cfit_empty
    data = {}
    data["type"] = 'cfit'
    data["scores"] = {}
    data["scores"]["scaled-6"] = scale.scale('cfit-to-6', g.cfit_correct)
    data["scores"]["scaled-20"] = scale.scale('cfit-to-20', g.cfit_correct)
    #data["scores"]["total"] = g.apm_total
    #data["scores"]["max_score"] = g.apm_max_score
    data["answers"] = {}
    data["answers"]["correct"] = g.cfit_correct
    data["answers"]["incorrect"] = g.cfit_incorrect
    data["answers"]["empty"] = g.cfit_empty
    data["attributes"] = itemGrade
    return data