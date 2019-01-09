import pymysql



def scale(scalename, value):
    conn = pymysql.connect(host='db.aws.ppsdm.com', port=3306, user='ppsdm', passwd='ppsdm-mysql', db='ppsdmdb')
    retval = None
    if not(value is None):
        retval = value
    #print(scalename)
    cur = conn.cursor()
    cur.execute("SELECT * FROM scale_ref WHERE scale_name = %s AND unscaled <= %s ORDER BY unscaled DESC LIMIT 1", (scalename, value))
    #print(cur.description)
    for row in cur:
        retval = row[2]
        #print(row[2])
    #retval = cur.fetchone()
    cur.close()
    conn.close()
    #print('retval : ', retval)
    return retval