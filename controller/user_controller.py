import logging
from ..service import user_service

class UserController(object):
  """User controller."""

  @staticmethod
  def getUser(user_id):
    """Get user by user user_id.
    :param int user_id user id
    :return dict user dictionary combined with extra_field
    """
    logging.info('UserController.getUser(%s)', user_id)
    user = user_service.getUserById(user_id)
    return user
