from flask import g
import pymysql



def grader(itemResult):
    subtest_name = itemResult.attrib['identifier'].split('_')[1].lower()
    print('entering TPA module : ' + itemResult.attrib['identifier'])

    if 'tpa_total' not in g:
        g.tpa_total = 0

    if 'tpa_max_score' not in g:
        g.cfit_max_score = 0

    if 'tpa_correct' not in g:
        g.tpa_correct = 0

    if 'tpa_incorrect' not in g:
        g.tpa_incorrect = 0

    if 'tpa_empty' not in g:
        g.tpa_empty = 0

    if 'subtest_score' not in g:
        g.subtest_score = {}

    if 'reset_object' not in g:
        g.reset_object = 0
    
    if g.reset_object == 1:
        g.tpa_correct = 0
        g.tpa_incorrect = 0
        g.tpa_empty = 0
        g.reset_object = 0
        g.subtest_score = {}
        g.subtest_score['verbal'] = 0
        g.subtest_score['kuantitatif'] = 0
        g.subtest_score['penalaran'] = 0
    
    itemGrade = {}
    score = 0
    max_score = 0
    response = None

    for subelem in itemResult:
        #print(subelem.tag)
        sub_identifier = subelem.attrib['identifier']
        sub_split = sub_identifier.split('_')
        if subelem.attrib['identifier'] == 'SCORE' :
            for subelem2 in subelem:
                score = int(subelem2.text)
                #print(sub_identifier, ' : ' ,score)
                g.tpa_correct += score
                if subtest_name in g.subtest_score:
                    g.subtest_score[subtest_name] += score
                else:
                    g.subtest_score[subtest_name] = score
                #itemGrade[itemResult.attrib['identifier']] = score
        elif subelem.attrib['identifier'] == 'MAXSCORE' :
            for subelem2 in subelem:
                max_score = int(subelem2.text)
                g.tpa_max_score += max_score
        elif sub_split[0] == 'RESPONSE' :
            for subelem2 in subelem:
                for subelem3 in subelem2:
                    response = subelem3.text
                    #print(response)
                    if response == None :
                        g.tpa_empty += 1
                    itemGrade["candidate_response"] = response


    g.tpa_incorrect = 50 - g.tpa_correct - g.tpa_empty
    data = {}
    data["type"] = 'tpa'
    data["scores"] = {}

    g.subtest_score['verbal'] = g.subtest_score['subtest1'] + g.subtest_score['subtest2'] + g.subtest_score['subtest3']
    g.subtest_score['kuantitatif'] = g.subtest_score['subtest4'] + g.subtest_score['subtest6'] + g.subtest_score['subtest5']
    g.subtest_score['penalaran'] = g.subtest_score['subtest7'] + g.subtest_score['subtest9'] + g.subtest_score['subtest8']
    #data[subtest_name] = g.tpa_correct
    #data["scores"]["scaled-6"] = scale.scale('cfit-to-6', g.cfit_correct)
    #data["scores"]["scaled-20"] = scale.scale('cfit-to-20', g.cfit_correct)
    #data["scores"]["total"] = g.apm_total
    #data["scores"]["max_score"] = g.apm_max_score
    data["answers"] = {}
    data["answers"]["correct"] = g.tpa_correct
    data["answers"]["incorrect"] = g.tpa_incorrect
    data["answers"]["empty"] = g.tpa_empty
    data["scores"] = g.subtest_score
    
    return data