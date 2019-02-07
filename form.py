from flask import g
import scale

def grader(itemResult,totalQ):
    print('entering FORM module')
    if 'pekerjaan' not in g:
        g.pekerjaan = 0


    itemGrade = {}
    score = 0
    max_score = 0
    response = None

    for subelem in itemResult:
        sub_identifier = subelem.attrib['identifier']
        #print(sub_identifier)
        sub_split = sub_identifier.split('_')
        if subelem.attrib['identifier'] == 'SCORE' :
            for subelem2 in subelem:
                score = int(subelem2.text)
        elif subelem.attrib['identifier'] == 'MAXSCORE' :
            for subelem2 in subelem:
                max_score = int(subelem2.text)
        elif subelem.attrib['identifier'] == 'tujuan_test' :
            for subelem2 in subelem:
                for subelem3 in subelem2:
                    itemGrade["tujuan_test"] = subelem3.text
        elif subelem.attrib['identifier'] == 'jabatan_saatini' :
            for subelem2 in subelem:
                for subelem3 in subelem2:
                    itemGrade["jabatan_saatini"] = subelem3.text
        elif subelem.attrib['identifier'] == 'prospek_jabatan' :
            for subelem2 in subelem:
                for subelem3 in subelem2:
                    itemGrade["prospek_jabatan"] = subelem3.text
        elif subelem.attrib['identifier'] == 'nomor_test' :
            for subelem2 in subelem:
                for subelem3 in subelem2:
                    itemGrade["nomor_test"] = subelem3.text
        elif subelem.attrib['identifier'] == 'nama_perusahaan' :
            for subelem2 in subelem:
                for subelem3 in subelem2:
                    itemGrade["nama_perusahaan"] = subelem3.text
        elif sub_split[0] == 'RESPONSE' :
            for subelem2 in subelem:
                for subelem3 in subelem2:
                    response = subelem3.text


    data = {}
    data["type"] = 'form'
    data["scores"] = {}

    data["answers"] = itemGrade
    data["attributes"] = itemGrade
    return data