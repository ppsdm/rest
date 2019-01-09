from flask import g
import scale
import pymysql

def grader(itemResult,totalQ):
    print('entering tkdanalogiverbal module')

    if 'tkdanalogiverbal_total' not in g:
        g.tkdanalogiverbal_total = 0

    if 'tkdanalogiverbal_max_score' not in g:
        g.tkdanalogiverbal_max_score = 0

    if 'tkdanalogiverbal_correct' not in g:
        g.tkdanalogiverbal_correct = 0

    if 'tkdanalogiverbal_incorrect' not in g:
        g.tkdanalogiverbal_incorrect = 0

    if 'tkdanalogiverbal_empty' not in g:
        g.tkdanalogiverbal_empty = 0

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
                g.tkdanalogiverbal_total = g.tkdanalogiverbal_total + score
                g.tkdanalogiverbal_correct += score
        elif subelem.attrib['identifier'] == 'MAXSCORE' :
            for subelem2 in subelem:
                max_score = int(subelem2.text)
                g.tkdanalogiverbal_max_score += max_score
        elif sub_split[0] == 'RESPONSE' :
            for subelem2 in subelem:
                for subelem3 in subelem2:
                    response = subelem3.text
                    if response == None :
                        g.tkdanalogiverbal_empty += 1
                    #print('response : ' , response)
                    itemGrade["candidate_response"] = response




    g.tkdanalogiverbal_incorrect = totalQ - g.tkdanalogiverbal_correct - g.tkdanalogiverbal_empty
    data = {}
    data["type"] = 'tkdanalogiverbal'
    data["scores"] = {}
    data["scores"]["scaled"] = scale.scale('tkd_analogi', g.tkdanalogiverbal_correct)
    #data["scores"]["scale-20"] = scale.scale('cfit-to-20', g.tkdanalogiverbal_correct)
    #data["scores"]["total"] = g.apm_total
    #data["scores"]["max_score"] = g.apm_max_score
    data["answers"] = {}
    data["answers"]["correct"] = g.tkdanalogiverbal_correct
    data["answers"]["incorrect"] = g.tkdanalogiverbal_incorrect
    data["answers"]["empty"] = g.tkdanalogiverbal_empty
    data["attributes"] = itemGrade
    print(' TOTAL tkdinfo : ', g.tkdanalogiverbal_total)
    return data