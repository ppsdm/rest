from flask import g
from tool import scale

def grader(itemResult,totalQ):
    print('entering APM module')
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
        sub_split = sub_identifier.split('_')
        if subelem.attrib['identifier'] == 'SCORE' :
            for subelem2 in subelem:
                score = int(subelem2.text)
                #g.apm_total += score
                g.apm_correct += score
        elif subelem.attrib['identifier'] == 'MAXSCORE' :
            for subelem2 in subelem:
                max_score = int(subelem2.text)
                g.apm_max_score += max_score
        elif sub_split[0] == 'RESPONSE' :
            for subelem2 in subelem:
                for subelem3 in subelem2:
                    response = subelem3.text
                    if response == None :
                        g.apm_empty += 1
                    itemGrade["candidate_response"] = response

    g.apm_incorrect = totalQ - g.apm_correct - g.apm_empty
    print("correct = " + str(g.apm_correct))
    print("total Q = " + str(totalQ))
    print("empty = " + str(g.apm_empty))
    data = {}
    data["type"] = 'apm'
    data["scores"] = {}
    data["scores"]["scale20"] = scale.scale('apm20', g.apm_correct)
    data["scores"]["scale6"] = scale.scale('20to6', data["scores"]["scale20"])
    #data["scores"]["total"] = g.apm_total
    #data["scores"]["max_score"] = g.apm_max_score
    data["answers"] = {}
    data["answers"]["correct"] = g.apm_correct
    data["answers"]["incorrect"] = g.apm_incorrect
    data["answers"]["empty"] = g.apm_empty
    data["attributes"] = itemGrade
    return data