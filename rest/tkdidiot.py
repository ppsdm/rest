from flask import g
import scale
import pymysql

def grader(itemResult):
    print('entering tkdidiot module')

    if 'tkdidiot_total' not in g:
        g.tkdidiot_total = 0

    if 'tkdidiot_max_score' not in g:
        g.tkdidiot_max_score = 0

    if 'tkdidiot_correct' not in g:
        g.tkdidiot_correct = 0

    if 'tkdidiot_incorrect' not in g:
        g.tkdidiot_incorrect = 0

    if 'tkdidiot_empty' not in g:
        g.tkdidiot_empty = 0

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
                g.tkdidiot_total = g.tkdidiot_total + score
                g.tkdidiot_correct += score
        elif subelem.attrib['identifier'] == 'MAXSCORE' :
            for subelem2 in subelem:
                max_score = int(subelem2.text)
                g.tkdidiot_max_score += max_score
        elif sub_split[0] == 'RESPONSE' :
            for subelem2 in subelem:
                for subelem3 in subelem2:
                    response = subelem3.text
                    if response == None :
                        g.tkdidiot_empty += 1
                    #print('response : ' , response)
                    itemGrade["candidate_response"] = response


    g.tkdidiot_incorrect = 15 - g.tkdidiot_correct - g.tkdidiot_empty
    data = {}
    data["type"] = 'tkdidiot'
    data["scores"] = {}
    data["scores"]["scaled"] = scale.scale('tkd_logika_idiot', g.tkdidiot_correct)
    #data["scores"]["scale-20"] = scale.scale('cfit-to-20', g.tkdidiot_correct)
    #data["scores"]["total"] = g.apm_total
    #data["scores"]["max_score"] = g.apm_max_score
    data["answers"] = {}
    data["answers"]["correct"] = g.tkdidiot_correct
    data["answers"]["incorrect"] = g.tkdidiot_incorrect
    data["answers"]["empty"] = g.tkdidiot_empty
    data["attributes"] = itemGrade
    print(' TOTAL tkdinfo : ', g.tkdidiot_total)
    return data