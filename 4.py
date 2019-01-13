from flask import g
import pymysql



def grader(itemResult,totalQ):
    subtest_name = itemResult.attrib['identifier'].split('_')[1].lower()
    print('entering TPA module : ' + itemResult.attrib['identifier'])
    
    return data