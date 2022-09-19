from config import *


@logger.catch
async def get_current_event(user_id):
    return session.query(Event).filter(Event.user_id == user_id, Event.current_event == True).first()


@logger.catch
async def get_current_event_id(user_id):
    return session.query(Event.id).filter(Event.user_id == user_id, Event.current_event == True).first()[0]


@logger.catch
async def get_current_event_title(user_id):
    return session.query(Event.title).filter(Event.user_id == user_id, Event.current_event == True).first()[0]
