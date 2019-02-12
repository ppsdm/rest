from flask import g
from ..tool import scale
import pymysql

#scaled = scale.scale('pcas-1-c', '7')
#print(scaled)
#reno = scale.scale('pcas-2-d', '7')
#print(reno)

def matching_graphs(disc_score,totalQ):
    #use with disc3 values
    _di = ''
    _ds = ''
    _dc = ''
    _is = ''
    _ic = ''
    _sc = ''

    valid = False
    retval = None

    dpos = 0
    ipos = 0
    spos = 0
    cpos = 0

    dpos = 1 if disc_score['d3'] >= 20 else 0
    ipos = 1 if disc_score['i3'] >= 20 else 0
    spos = 1 if disc_score['s3'] >= 20 else 0
    cpos = 1 if disc_score['c3'] >= 20 else 0

    if disc_score['d3'] > disc_score['i3']:
        _di = '>'
    elif disc_score['d3'] < disc_score['i3']:
        _di = '<'
    else:
        _di = '='

    if disc_score['d3'] > disc_score['s3']:
        _ds = '>'
    elif disc_score['d3'] < disc_score['s3']:
        _ds = '<'
    else:
        _ds = '='

    if disc_score['d3'] > disc_score['c3']:
        _dc = '>'
    elif disc_score['d3'] < disc_score['c3']:
        _dc = '<'
    else:
        _dc = '='

    if disc_score['i3'] > disc_score['s3']:
        _is = '>'
    elif disc_score['i3'] < disc_score['s3']:
        _is = '<'
    else:
        _is = '='

    if disc_score['i3'] > disc_score['c3']:
        _ic = '>'
    elif disc_score['i3'] < disc_score['c3']:
        _ic = '<'
    else:
        _ic = '='

    if disc_score['s3'] > disc_score['c3']:
        _sc = '>'
    elif disc_score['s3'] < disc_score['c3']:
        _sc = '<'
    else:
        _sc = '='

    print(disc_score['d3'], ' : ', disc_score['i3'], ' : ', disc_score['s3'], ' : ', disc_score['c3'])
    print(dpos, ' : ', ipos, ' : ', spos, ' : ', cpos)
    print('di : ', _di, 'ds : ', _ds, 'dc : ', _dc, 'is : ', _is, 'ic : ', _ic, 'sc : ', _sc)
    conn = pymysql.connect(host='db.aws.ppsdm.com', port=3306, user='ppsdm', passwd='ppsdm-mysql', db='atsdb')

    cur = conn.cursor()
    cur.execute("SELECT * FROM pcas_grafik_ref"
     " WHERE di = '" + _di + "' AND ds = '" + _ds  +
     "' AND dc = '" + _dc +
     "' AND `is` = '" + _is +
     "' AND ic = '" + _ic +
     "' AND sc = '" + _sc +
     "' AND `d-pos` = %s" + 
     " AND `i-pos` = %s" + 
     " AND `s-pos` = %s" + 
     " AND `c-pos` = %s" 
    , (dpos, ipos, spos, cpos))
    rowcount = 0
    matches = ''
    for row in cur:
        rowcount = rowcount + 1
        retval = row
        matches = matches + ',' + row[0] 
        valid = True
        print(row)

    if rowcount > 1:
        valid = False
        retval = 'there are multiple matches ' + matches
    cur.close()
    conn.close()
    return valid, retval


def grader(itemResult):
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
    responses_array = {}
    score = 0
    max_score = 0
    response = None
    validity = True
    choice = 0

    disc_score = {
        'd1' : None,
        'd2' : None,
        'd3' : None,
        'i1' : None,
        'i2' : None,
        'i3' : None,
        's1' : None,
        's2' : None,
        's3' : None,
        'c1' : None,
        'c2' : None,
        'c3' : None,
        'disc1' : None,
        'disc2' : None

    }

    keys_dict = {
        '1' : {         
            '1' : {
                'M' : 'c',
                'L' : 'd'
            },
            '2' : {
                'M' : 'e',
                'L' : 'j'
            },
            '3' : {
                'M' : 'a',
                'L' : 'b'
            },
            '4' : {
                'M' : 'i',
                'L' : 'h'
            }
        },
        '2' : {
            '1' : {
                'M' : 'i',
                'L' : 'f'
            },
            '2' : {
                'M' : 'a',
                'L' : 'b'
            },
            '3' : {
                'M' : 'g',
                'L' : 'h'
            },
            '4' : {
                'M' : 'c',
                'L' : 'd'
            }
        },
        '3' : {
            '1' : {
                'M' : 'i',
                'L' : 'b'
            },
            '2' : {
                'M' : 'g',
                'L' : 'h'
            },
            '3' : {
                'M' : 'c',
                'L' : 'j'
            },
            '4' : {
                'M' : 'e',
                'L' : 'f'
            }
        },
        '4' : {
            '1' : {
                'M' : 'c',
                'L' : 'd'
            },
            '2' : {
                'M' : 'i',
                'L' : 'b'
            },
            '3' : {
                'M' : 'e',
                'L' : 'f'
            },
            '4' : {
                'M' : 'g',
                'L' : 'j'
            }
        },
        '5' : {
            '1' : {
                'M' : 'i',
                'L' : 'h'
            },
            '2' : {
                'M' : 'i',
                'L' : 'f'
            },
            '3' : {
                'M' : 'c',
                'L' : 'j'
            },
            '4' : {
                'M' : 'a',
                'L' : 'j'
            }
        },
        '6' : {
            '1' : {
                'M' : 'a',
                'L' : 'b'
            },
            '2' : {
                'M' : 'i',
                'L' : 'h'
            },
            '3' : {
                'M' : 'e',
                'L' : 'j'
            },
            '4' : {
                'M' : 'c',
                'L' : 'j'
            }
        },
        '7' : {
            '1' : {
                'M' : 'e',
                'L' : 'f'
            },
            '2' : {
                'M' : 'i',
                'L' : 'b'
            },
            '3' : {
                'M' : 'g',
                'L' : 'h'
            },
            '4' : {
                'M' : 'i',
                'L' : 'd'
            }
        },
        '8' : {
            '1' : {
                'M' : 'g',
                'L' : 'j'
            },
            '2' : {
                'M' : 'a',
                'L' : 'b'
            },
            '3' : {
                'M' : 'e',
                'L' : 'f'
            },
            '4' : {
                'M' : 'c',
                'L' : 'd'
            }
        },
        '9' : {
            '1' : {
                'M' : 'c',
                'L' : 'd'
            },
            '2' : {
                'M' : 'i',
                'L' : 'f'
            },
            '3' : {
                'M' : 'g',
                'L' : 'j'
            },
            '4' : {
                'M' : 'a',
                'L' : 'b'
            }
        },
        '10' : {
            '1' : {
                'M' : 'i',
                'L' : 'h'
            },
            '2' : {
                'M' : 'i',
                'L' : 'd'
            },
            '3' : {
                'M' : 'e',
                'L' : 'f'
            },
            '4' : {
                'M' : 'a',
                'L' : 'b'
            }
        },
        '11' : {
            '1' : {
                'M' : 'e',
                'L' : 'f'
            },
            '2' : {
                'M' : 'i',
                'L' : 'd'
            },
            '3' : {
                'M' : 'g',
                'L' : 'j'
            },
            '4' : {
                'M' : 'a',
                'L' : 'b'
            }
        },
        '12' : {
            '1' : {
                'M' : 'e',
                'L' : 'f'
            },
            '2' : {
                'M' : 'c',
                'L' : 'd'
            },
            '3' : {
                'M' : 'a',
                'L' : 'b'
            },
            '4' : {
                'M' : 'g',
                'L' : 'j'
            }
        },
        '13' : {
            '1' : {
                'M' : 'c',
                'L' : 'd'
            },
            '2' : {
                'M' : 'a',
                'L' : 'b'
            },
            '3' : {
                'M' : 'e',
                'L' : 'j'
            },
            '4' : {
                'M' : 'i',
                'L' : 'h'
            }
        },
        '14' : {
            '1' : {
                'M' : 'a',
                'L' : 'b'
            },
            '2' : {
                'M' : 'i',
                'L' : 'h'
            },
            '3' : {
                'M' : 'e',
                'L' : 'f'
            },
            '4' : {
                'M' : 'c',
                'L' : 'd'
            }
        },
        '15' : {
            '1' : {
                'M' : 'g',
                'L' : 'h'
            },
            '2' : {
                'M' : 'a',
                'L' : 'b'
            },
            '3' : {
                'M' : 'i',
                'L' : 'f'
            },
            '4' : {
                'M' : 'c',
                'L' : 'd'
            }
        },
        '16' : {
            '1' : {
                'M' : 'e',
                'L' : 'j'
            },
            '2' : {
                'M' : 'c',
                'L' : 'd'
            },
            '3' : {
                'M' : 'a',
                'L' : 'j'
            },
            '4' : {
                'M' : 'g',
                'L' : 'h'
            }
        },
        '17' : {
            '1' : {
                'M' : 'e',
                'L' : 'f'
            },
            '2' : {
                'M' : 'g',
                'L' : 'j'
            },
            '3' : {
                'M' : 'a',
                'L' : 'b'
            },
            '4' : {
                'M' : 'i',
                'L' : 'd'
            }
        },
        '18' : {
            '1' : {
                'M' : 'e',
                'L' : 'f'
            },
            '2' : {
                'M' : 'a',
                'L' : 'b'
            },
            '3' : {
                'M' : 'i',
                'L' : 'h'
            },
            '4' : {
                'M' : 'c',
                'L' : 'd'
            }
        },
        '19' : {
            '1' : {
                'M' : 'i',
                'L' : 'b'
            },
            '2' : {
                'M' : 'g',
                'L' : 'h'
            },
            '3' : {
                'M' : 'e',
                'L' : 'f'
            },
            '4' : {
                'M' : 'e',
                'L' : 'j'
            }
        },
        '20' : {
            '1' : {
                'M' : 'i',
                'L' : 'h'
            },
            '2' : {
                'M' : 'e',
                'L' : 'f'
            },
            '3' : {
                'M' : 'c',
                'L' : 'd'
            },
            '4' : {
                'M' : 'a',
                'L' : 'j'
            }
        },
        '21' : {
            '1' : {
                'M' : 'i',
                'L' : 'f'
            },
            '2' : {
                'M' : 'a',
                'L' : 'b'
            },
            '3' : {
                'M' : 'g',
                'L' : 'j'
            },
            '4' : {
                'M' : 'c',
                'L' : 'd'
            }
        },
        '22' : {
            '1' : {
                'M' : 'a',
                'L' : 'b'
            },
            '2' : {
                'M' : 'i',
                'L' : 'h'
            },
            '3' : {
                'M' : 'i',
                'L' : 'f'
            },
            '4' : {
                'M' : 'c',
                'L' : 'j'
            }
        },
        '23' : {
            '1' : {
                'M' : 'a',
                'L' : 'b'
            },
            '2' : {
                'M' : 'i',
                'L' : 'd'
            },
            '3' : {
                'M' : 'e',
                'L' : 'f'
            },
            '4' : {
                'M' : 'g',
                'L' : 'j'
            }
        },
        '24' : {
            '1' : {
                'M' : 'g',
                'L' : 'h'
            },
            '2' : {
                'M' : 'c',
                'L' : 'd'
            },
            '3' : {
                'M' : 'e',
                'L' : 'f'
            },
            '4' : {
                'M' : 'a',
                'L' : 'b'
            }
        },
    }



    tally = {
        'a' : 0,
        'b' : 0,
        'c':0,
        'd':0,
        'e':0,
        'f':0,
        'g':0,
        'h':0,
        'i':0,
        'j':0
    }
    scaled_score = {}

    indexer = 0
    for subelem in itemResult:
        sub_identifier = subelem.attrib['identifier']

        sub_split = sub_identifier.split('_')
        if subelem.attrib['identifier'] == 'SCORE' :
            for subelem2 in subelem:
                score = int(subelem2.text)
                g.apm_total += score
        elif subelem.attrib['identifier'] == 'MAXSCORE' :
            for subelem2 in subelem:
                max_score = int(subelem2.text)
                g.apm_max_score += max_score
        elif sub_split[0] == 'RESPONSE' :
            #print('sub_identifier',sub_identifier)

            try:
                if sub_split[1] == 'DISC':
                    #print(sub_split[0])
                    for subelem2 in subelem:
                        for subelem3 in subelem2:
                            #
                            if subelem3.text != None: #check if subelem is not None and can be strip()
                                response = subelem3.text.strip()
                                number = sub_split[3]
                                indexer = int(number)
                                print(indexer, ' : ', subelem3.text)
                                split_response = response.split(' ')
                                lmresponse = split_response[0]
                                choice = split_response[1].split('_')[1]
                                if number not in responses_array:
                                    responses_array[number] = {}
                                if lmresponse not in responses_array[number]:
                                    responses_array[number][lmresponse] = {}
                                    cursor = indexer
                                    #print('indexer :', cursor)
                                    pcas_aspect_letter = keys_dict[str (indexer)][choice][lmresponse]
                                    responses_array[number][lmresponse] = pcas_aspect_letter
                                    tally[pcas_aspect_letter] = tally[pcas_aspect_letter] + 1
                                else:
                                    validity = False #duplicate membuat tidak valid
                                    responses_array[number][lmresponse] = 'DUPLICATE'
                                #print(number, lmresponse, choice )
                                #print(responses_array)
                                itemGrade["candidate_response"] = response
                            else:
                                #print('subelem3.text is None!! ', sub_split[3])
                                number = sub_split[3]
                                if number not in responses_array:
                                    responses_array[number] = {}
            except IndexError:
                print('[DISC] !!!ERROR!!!! ', sub_identifier)

    if response == None :
        g.apm_empty += 1
    elif score == max_score :
        g.apm_correct += 1
    else :
        g.apm_incorrect += 1

    data = {}
    data["type"] = "disc"
    data["scores"] = {}
    data["scores"]["total"] = g.apm_total
    data["scores"]["max_score"] = g.apm_max_score
    data["answers"] = responses_array
    data["answers"]["correct"] = tally
    data["answers"]["incorrect"] = g.apm_incorrect
    data["answers"]["empty"] = g.apm_empty
    data["attributes"] = itemGrade
    
    data["scores"]['disc'] = disc_score

    def set_invalid(validvalue, message):
        data["scores"]["validity"] = validvalue
        print('NOT VALID!!!', message)
        return

    def validate(tally):
        validity = True
        tally_sum = 0
        reason = 'none'
        for key in tally:
            tally_sum = tally_sum + tally[key]
        if tally_sum != 48:
            validity = False
            print(tally_sum)
            reason = 'there are unanswered questions'
        #check if all question answered
        return validity, reason
    def calculate_disc(tally):
        #print(disc_score)
        
        d1 = scale.scale('pcas-1-d', tally['a'])
        d2 = scale.scale('pcas-2-d', tally['b'])
        d3 = scale.scale('pcas-3-d', tally['a'] - tally['b'])
        i1 = scale.scale('pcas-1-i', tally['c'])
        i2 = scale.scale('pcas-2-i', tally['d'])
        i3 = scale.scale('pcas-3-i', tally['c'] - tally['d'])
        s1 = scale.scale('pcas-1-s', tally['e'])
        s2 = scale.scale('pcas-2-s', tally['f'])
        s3 = scale.scale('pcas-3-s', tally['e'] - tally['f'])
        c1 = scale.scale('pcas-1-c', tally['g'])
        c2 = scale.scale('pcas-2-c', tally['h'])
        c3 = scale.scale('pcas-3-c', tally['g'] - tally['h'])

        disc_score['d1'] = d1
        disc_score['d2'] = d2
        disc_score['d3'] = d3
        disc_score['i1'] = i1
        disc_score['i2'] = i2
        disc_score['i3'] = i3
        disc_score['s1'] = s1
        disc_score['s2'] = s2
        disc_score['s3'] = s3
        disc_score['c1'] = c1
        disc_score['c2'] = c2
        disc_score['c3'] = c3
        disc_score['valid_1'] = tally['i']
        disc_score['valid_2'] = tally['j']
        #for key in tally:
        #    scaled_score[key] = scale.scale('pcas-1-c', '7')
         #   print(key)

    validity = validate(tally)
    if validity[0]: #check for validity from return value
        calculate_disc(tally)
        print('entering ....')
        disc_graph = matching_graphs(disc_score)
        print('before if...')
        if disc_graph[0]:
            data["scores"]["validity"] = True
            data["scores"]["graph"] = disc_graph[1][0]

            print('VALID!!!')
        else:
            print('should set invalid')
            set_invalid(False, disc_graph[1])
    else:
        print('is is here?')
        set_invalid(False, validity[1])

    print(tally)
    print(disc_score)
    #print(keys[4])
    #print(tally['a'])
    return data
