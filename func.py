from config import *


async def get_current_event(user_id):
    return session.query(Event).filter(Event.user_id == user_id, Event.current_event == True).first()


async def get_current_event_id(user_id):
    return session.query(Event.id).filter(Event.user_id == user_id, Event.current_event == True).first()[0]


async def get_current_event_title(user_id):
    return session.query(Event.title).filter(Event.user_id == user_id, Event.current_event == True).first()[0]