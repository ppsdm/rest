from flask import g
import scale
import pymysql

def grader(itemResult,totalQ):
    print('entering GATB4 module')

    if 'gatb4_total' not in g:
        g.gatb4_total = 0

    if 'gatb4_max_score' not in g:
        g.gatb4_max_score = 0

    if 'gatb4_correct' not in g:
        g.gatb4_correct = 0

    if 'gatb4_incorrect' not in g:
        g.gatb4_incorrect = 0

    if 'gatb4_empty' not in g:
        g.gatb4_empty = 0

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
                g.gatb4_total = g.gatb4_total + score
                g.gatb4_correct += score
        elif subelem.attrib['identifier'] == 'MAXSCORE' :
            for subelem2 in subelem:
                max_score = int(subelem2.text)
                g.gatb4_max_score += max_score
        elif sub_split[0] == 'RESPONSE' :
            for subelem2 in subelem:
                for subelem3 in subelem2:
                    response = subelem3.text
                    if response == None :
                        g.gatb4_empty += 1
                    #print('response : ' , response)
                    itemGrade["candidate_response"] = response


    g.gatb4_incorrect = totalQ - g.gatb4_correct - g.gatb4_empty
    data = {}
    data["type"] = 'gatb4'
    data["scores"] = {}
    data["scores"]["scaled"] = scale.scale('gatb4-aritmatika', g.gatb4_correct)
    #data["scores"]["scale-20"] = scale.scale('cfit-to-20', g.gatb4_correct)
    #data["scores"]["total"] = g.apm_total
    #data["scores"]["max_score"] = g.apm_max_score
    data["answers"] = {}
    data["answers"]["correct"] = g.gatb4_correct
    data["answers"]["incorrect"] = g.gatb4_incorrect
    data["answers"]["empty"] = g.gatb4_empty
    data["attributes"] = itemGrade
    print(' TOTAL GATB4 : ', g.gatb4_total)
    return data