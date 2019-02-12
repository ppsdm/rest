from flask import g
from ..tool import scale
import pymysql

def grader(itemResult,totalQ):
    print('entering ComPre module')

    if 'compre_total' not in g:
        g.compre_total = 0

    if 'compre_max_score' not in g:
        g.compre_max_score = 0

    if 'compre_correct' not in g:
        g.compre_correct = 0

    if 'compre_incorrect' not in g:
        g.compre_incorrect = 0

    if 'compre_empty' not in g:
        g.compre_empty = 0

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
                g.compre_total = g.compre_total + score
                g.compre_correct += score
        elif subelem.attrib['identifier'] == 'MAXSCORE' :
            for subelem2 in subelem:
                max_score = int(subelem2.text)
                g.compre_max_score += max_score
        elif sub_split[0] == 'RESPONSE' :
            for subelem2 in subelem:
                for subelem3 in subelem2:
                    response = subelem3.text
                    if response == None :
                        g.compre_empty += 1
                    #print('response : ' , response)
                    itemGrade["candidate_response"] = response



    g.compre_incorrect = totalQ - g.compre_correct - g.compre_empty
    data = {}
    data["type"] = 'compre'
    data["scores"] = {}
    data["scores"]["scale20"] = scale.scale('compre', g.compre_correct)
    data["scores"]["scale6"] = scale.scale('20to6', data["scores"]["scale20"])
    #data["scores"]["scale-20"] = scale.scale('cfit-to-20', g.compre_correct)
    #data["scores"]["total"] = g.apm_total
    #data["scores"]["max_score"] = g.apm_max_score
    data["answers"] = {}
    data["answers"]["correct"] = g.compre_correct
    data["answers"]["incorrect"] = g.compre_incorrect
    data["answers"]["empty"] = g.compre_empty
    data["attributes"] = itemGrade
    print(' TOTAL compre : ', g.compre_total)
    return data