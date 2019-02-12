import pymysql, logging, os
from dotenv import load_dotenv
from ..constants.response_model.user import EXTRA_FIELD
from flask import g
from collections import Counter
""" load dotenv."""
load_dotenv()

class InterpretService(object):
  """Interpret service class."""

  def __init__(self):
    """InterpretService constructor."""
    self.extra_field = EXTRA_FIELD

  def getPapiInterpretationById(self, score):
      #print("INSIDE PAPI INTERPREATION ###################################################")
      conn = pymysql.connect(host=os.getenv('DB_HOST'), port=int(os.getenv('DB_PORT')), user=os.getenv('DB_USER'), passwd=os.getenv('DB_PASSWORD'), db='ppsdmdb')
      cur = conn.cursor(pymysql.cursors.DictCursor)
      cur.execute("SELECT *, CONCAT(aspek_1, aspek_1_value, \
        aspek_2, aspek_2_value, \
        aspek_3, aspek_3_value, \
        aspek_4, aspek_4_value, \
        aspek_5, aspek_5_value \
        ) as papicode from papi_interpretation_ref where id = %s", (score))
      cur.close()
      conn.close()
      for row in cur:
          res = row['papicode'] + "::" + row['description']
      return res

  def getPapi(self, score):
    """
    Get user by their id.
    :param int user_id id of user profile to fetch
    :return dict user profile dict
    """

    if 'papi_id_list' not in g:
        g.papi_id_list = {}
        g.papi_id_list['2'] = []
        g.papi_id_list['4'] = []
        g.papi_id_list['6'] = []
        g.papi_id_list['8'] = []
        g.papi_id_list['10'] = []

    temp_list = {}
    temp_list['2'] = []
    temp_list['4'] = []
    temp_list['6'] = []
    temp_list['8'] = []
    temp_list['10'] = []

    conn = pymysql.connect(host=os.getenv('DB_HOST'), port=int(os.getenv('DB_PORT')), user=os.getenv('DB_USER'), passwd=os.getenv('DB_PASSWORD'), db='ppsdmdb')
    cur = conn.cursor(pymysql.cursors.DictCursor)
    logging.info('Querying SQL')
    res= {}
    # get some user fields + all associated extra_fields + value
    if (len(score)  >= 2):
        res['aspek_1']  = score[0]
        res['aspek_1_value']  = score[1]
    else :
        res['aspek_1']  = ' '
        res['aspek_1_value']  = ' '
    if (len(score)  >= 4):
        res['aspek_2']  = score[2]
        res['aspek_2_value']  = score[3]
    else :
        res['aspek_2']  = ' '
        res['aspek_2_value']  = ' '
    if (len(score)  >= 6):
        res['aspek_3']  = score[4]
        res['aspek_3_value']  = score[5]
    else :
        res['aspek_3']  = ' '
        res['aspek_3_value']  = ' '
    if (len(score)  >= 8):
        res['aspek_4']  = score[6]
        res['aspek_4_value']  = score[7]
    else :
        res['aspek_4']  = ' '
        res['aspek_4_value']  = ' '
    if (len(score)  >= 10):
        res['aspek_5']  = score[8]
        res['aspek_5_value']  = score[9]
    else :
        res['aspek_5']  = ' '
        res['aspek_5_value']  = ' '
    print("papi execute :" + score)
    cur.execute("SELECT *, length(trim(papi_code)) as length  \
        FROM (select CONCAT(aspek_1, aspek_1_value, \
        aspek_2, aspek_2_value, \
        aspek_3, aspek_3_value, \
        aspek_4, aspek_4_value, \
        aspek_5, aspek_5_value \
        ) as papi_code, id, description from papi_interpretation_ref as T1) as T2 where \
        papi_code LIKE %s \
        AND papi_code LIKE %s \
        AND papi_code LIKE %s \
        AND papi_code LIKE %s \
        AND papi_code LIKE %s \
          ", (
          ('%' + res['aspek_1']+ res['aspek_1_value'] + '%'), \
          ('%'+ res['aspek_2']+ res['aspek_2_value'] + '%'), \
          ('%'+ res['aspek_3']+ res['aspek_3_value'] + '%'), \
          ('%'+ res['aspek_4']+ res['aspek_4_value'] + '%'), \
          ('%'+ res['aspek_5']+ res['aspek_5_value'] + '%')))

    cur.close()
    conn.close()
    #print ("row count : " + str(cur.rowcount))
    for row in cur:
        #print(row['id'])
        idx = str(len(row['papi_code'].strip()))
        temp_list[idx].append(row['id'])
        if row['id'] in g.papi_id_list[idx] :
            #pass
            g.papi_id_list[idx].append(row['id'])
        else :
            g.papi_id_list[idx].append(row['id'])
        #res[row['id']].update({'id': row['id']})
        #res['output'].update({'description': row['description']})
        #self.extra_field.update({row['variable']: {'value': row['value'], 'display_text': row['display_text']}})
        #data.update({'extra_fields': self.extra_field})
    

    #g.papi_id_list[score] = temp_list
    #reno_list = list(set(g.papi_id_list).intersection(temp_list))
    #print("reno list len : " + str(len(reno_list)))

    return res