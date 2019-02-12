from flask import g
from ..tool import scale
import pymysql

def grader(itemResult,totalQ):
    print('entering ADKUDAG4 module')

    if 'adkudag4_total' not in g:
        g.adkudag4_total = 0

    if 'adkudag4_max_score' not in g:
        g.adkudag4_max_score = 0

    if 'adkudag4_correct' not in g:
        g.adkudag4_correct = 0

    if 'adkudag4_incorrect' not in g:
        g.adkudag4_incorrect = 0

    if 'adkudag4_empty' not in g:
        g.adkudag4_empty = 0

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
                g.adkudag4_total = g.adkudag4_total + score
                g.adkudag4_correct += score
        elif subelem.attrib['identifier'] == 'MAXSCORE' :
            for subelem2 in subelem:
                max_score = int(subelem2.text)
                g.adkudag4_max_score += max_score
        elif sub_split[0] == 'RESPONSE' :
            for subelem2 in subelem:
                for subelem3 in subelem2:
                    response = subelem3.text
                    if response == None :
                        g.adkudag4_empty += 1
                    #print('response : ' , response)
                    itemGrade["candidate_response"] = response


#    elif score == max_score :
 #       g.adkudag4_correct += 1
  #  else :
   #     g.adkudag4_incorrect += 1

    g.adkudag4_incorrect = totalQ - g.adkudag4_correct - g.adkudag4_empty
    data = {}
    data["type"] = 'adkudag4'
    data["scores"] = {}
    data["scores"]["scale20"] = scale.scale('adkudag4', g.adkudag4_correct)
    data["scores"]["scale6"] = scale.scale('20to6', data["scores"]["scale20"])
    #data["scores"]["scale-20"] = scale.scale('cfit-to-20', g.adkudag4_correct)
    #data["scores"]["total"] = g.apm_total
    #data["scores"]["max_score"] = g.apm_max_score
    data["answers"] = {}
    data["answers"]["correct"] = g.adkudag4_correct
    data["answers"]["incorrect"] = g.adkudag4_incorrect
    data["answers"]["empty"] = g.adkudag4_empty
    data["attributes"] = itemGrade
    print(' TOTAL ADKUDAG4 : ', g.adkudag4_total)
    return data