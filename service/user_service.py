import pymysql, logging, os
from dotenv import load_dotenv
from constants.response_model.user import EXTRA_FIELD
""" load dotenv."""
load_dotenv()

class UserService(object):
  """User service class."""

  def __init__(self):
    """UserService constructor."""
    self.extra_field = EXTRA_FIELD
  
  def getUserById(self, user_id):
    """
    Get user by their id.
    :param int user_id id of user profile to fetch
    :return dict user profile dict
    """
    conn = pymysql.connect(host=os.getenv('DB_HOST'), port=int(os.getenv('DB_PORT')), user=os.getenv('DB_USER'), passwd=os.getenv('DB_PASSWORD'), db='chamilo_ppsdm_db')
    cur = conn.cursor(pymysql.cursors.DictCursor)
    logging.info('Querying SQL')
    # get some user fields + all associated extra_fields + value
    cur.execute("SELECT user.id, user.firstname, user.lastname, user.address, user.username, user.email, user.official_code, \
          user.phone, user.picture_uri, user.language, efv.value, ef.variable, ef.display_text \
        FROM user INNER JOIN extra_field_values AS efv \
          ON user.id = efv.item_id INNER JOIN extra_field AS ef ON ef.id = efv.field_id \
          WHERE user.id = %s", user_id)
    i = 0
    data = {}
    for row in cur:
        #print(row)
        if (i == 0):
            data.update({'id': row['id']})
            data.update({'firstname': row['firstname']})
            data.update({'lastname': row['lastname']})
            data.update({'address': row['address']})
            data.update({'username': row['username']})
            data.update({'official_code': row['official_code']})
            data.update({'email': row['email']})
            data.update({'phone': row['phone']})
            data.update({'picture_uri': row['picture_uri']})
            data.update({'language': row['language']})
        self.extra_field.update({row['variable']: {'value': row['value'], 'display_text': row['display_text']}})
        data.update({'extra_fields': self.extra_field})
        i += 1
    cur.close()
    conn.close()
    return data