import logging
from ..service import interpret_service

class InterpretController(object):
  """Interpret controller."""

  @staticmethod
  def getPapi(score):
    """Get user by user user_id.
    :param int user_id user id
    :return dict user dictionary combined with extra_field
    """
    #logging.info('UserController.getUser(%s)', user_id)
    uraian = interpret_service.getPapi(score)
    return uraian
  

  def getPapiInterpretationById(self,score):
    """Get user by user user_id.
    :param int user_id user id
    :return dict user dictionary combined with extra_field
    """
    #logging.info('UserController.getUser(%s)', user_id)
    uraian = interpret_service.getPapiInterpretationById(score)
    return uraian