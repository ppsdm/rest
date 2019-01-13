from flask import g
import scale
import pymysql

def grader(itemResult,totalQ):
    print('entering tkdinfo module')

    if 'tkdinfo_total' not in g:
        g.tkdinfo_total = 0

    if 'tkdinfo_max_score' not in g:
        g.tkdinfo_max_score = 0

    if 'tkdinfo_correct' not in g:
        g.tkdinfo_correct = 0

    if 'tkdinfo_incorrect' not in g:
        g.tkdinfo_incorrect = 0

    if 'tkdinfo_empty' not in g:
        g.tkdinfo_empty = 0

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
                g.tkdinfo_total = g.tkdinfo_total + score
                g.tkdinfo_correct += score
        elif subelem.attrib['identifier'] == 'MAXSCORE' :
            for subelem2 in subelem:
                max_score = int(subelem2.text)
                g.tkdinfo_max_score += max_score
        elif sub_split[0] == 'RESPONSE' :
            for subelem2 in subelem:
                for subelem3 in subelem2:
                    response = subelem3.text
                    if response == None :
                        g.tkdinfo_empty += 1
                    #print('response : ' , response)
                    itemGrade["candidate_response"] = response


    g.tkdinfo_incorrect = totalQ - g.tkdinfo_correct - g.tkdinfo_empty
    data = {}
    data["type"] = 'tkdinfo'
    data["scores"] = {}
    data["scores"]["scale20"] = scale.scale('tkdinfo', g.tkdinfo_correct)
    data["scores"]["scale6"] = scale.scale('20to6', data["scores"]["scale20"])
    #data["scores"]["scale-20"] = scale.scale('cfit-to-20', g.tkdinfo_correct)
    #data["scores"]["total"] = g.apm_total
    #data["scores"]["max_score"] = g.apm_max_score
    data["answers"] = {}
    data["answers"]["correct"] = g.tkdinfo_correct
    data["answers"]["incorrect"] = g.tkdinfo_incorrect
    data["answers"]["empty"] = g.tkdinfo_empty
    data["attributes"] = itemGrade
    print(' TOTAL tkdinfo : ', g.tkdinfo_total)
    return data