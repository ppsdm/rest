import pymysql, logging

class UserService(object):
  """User service class."""

  def __init__(self):
    """UserService constructor."""
  
  def getUserById(self, user_id):
    """
    Get user by their id.
    :param int user_id id of user profile to fetch
    :return dict user profile dict
    """
    conn = pymysql.connect(host='db.aws.ppsdm.com', port=3306, user='ppsdm', passwd='ppsdm-mysql', db='chamilo_ppsdm_db')
    cur = conn.cursor(pymysql.cursors.DictCursor)
    logging.info('Querying SQL')
    # get some user fields + all associated extra_fields + value
    cur.execute("SELECT user.id, user.firstname, user.lastname, user.username, user.email, user.official_code, \
          user.phone, user.picture_uri, user.language, efv.value, ef.variable, ef.display_text \
        FROM user INNER JOIN extra_field_values AS efv \
          ON user.id = efv.item_id INNER JOIN extra_field AS ef ON ef.id = efv.field_id \
          WHERE user.id = %s", user_id)
    i = 0
    extra_fields = []
    data = {}
    for row in cur:
        if (i == 0):
            data.update({'id': row['id']})
            data.update({'firstname': row['firstname']})
            data.update({'lastname': row['lastname']})
            data.update({'username': row['username']})
            data.update({'official_code': row['official_code']})
            data.update({'email': row['email']})
            data.update({'phone': row['phone']})
            data.update({'picture_uri': row['picture_uri']})
            data.update({'language': row['language']})
        extra_fields.append({row['variable']: row['value'], 'display_text': row['display_text']})
        data.update({'extra_fields': extra_fields})
        i += 1
    cur.close()
    conn.close()
    return data