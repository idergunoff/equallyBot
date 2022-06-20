from io import BytesIO


from aiogram.utils import executor

from participant import *
from expense import *
from fruit import *


@dp.message_handler(commands=['start'])
async def start(msg: types.Message):
    if not session.query(User).filter(User.telegram_id == msg.from_user.id).first():
        name_list = []
        if msg.from_user.first_name:
            name_list.append(msg.from_user.first_name)
        if msg.from_user.last_name:
            name_list.append(msg.from_user.last_name)
        user_name = ' '.join(name_list)
        new_user = User(telegram_id=msg.from_user.id, name=user_name)
        session.add(new_user)
        session.commit()
    kb_events = InlineKeyboardMarkup(row_width=3)
    events = session.query(Event).filter(Event.user_id == msg.from_user.id).order_by(Event.id).all()
    for i in events:
        kb_events.insert(InlineKeyboardButton(text=i.title, callback_data=cb_event.new(event_id=i.id)))
    kb_events.row(btn_new_event, btn_del_event)
    mes = emojize(str(msg.from_user.first_name) + ", добро пожаловать в EquallyBot! Выберите событие или создайте новое.")
    await bot.send_message(msg.from_user.id, mes, reply_markup=kb_events)


@dp.callback_query_handler(text='new_event')
async def new_event(call: types.CallbackQuery):
    await EquallyStates.NEW_EVENT.set()
    mes = emojize('Отправь название событя. Не больше 25 символов.')
    await bot.send_message(call.from_user.id, mes)


@dp.message_handler(state=EquallyStates.NEW_EVENT)
async def add_event(msg: types.Message, state: FSMContext):
    check_title = session.query(Event).filter(Event.title == msg.text, Event.user_id == msg.from_user.id).count()
    if check_title > 0 or len(msg.text) > 25:
        mes = f'Событие <b>{msg.text}</b> у вас уже существует или название слишком длинное. Отправь другое название.'
        await bot.send_message(msg.from_user.id, mes, parse_mode=types.ParseMode.HTML)
    else:
        await state.finish()
        session.query(Event).filter(Event.user_id == msg.from_user.id).update({'current_event': False}, synchronize_session='fetch')
        new_user_event = Event(title=msg.text, user_id=msg.from_user.id)
        session.add(new_user_event)
        session.commit()
        mes = emojize(f'Вы добвили событие - <b>{msg.text}</b> .')
        await bot.send_message(msg.from_user.id, mes, parse_mode=types.ParseMode.HTML)
        await start(msg=msg)


@dp.callback_query_handler(text='del_event')
async def choose_event_for_del(call: types.CallbackQuery):
    kb_event_del = InlineKeyboardMarkup(row_width=3)
    events = session.query(Event).filter(Event.user_id == call.from_user.id).order_by(Event.id).all()
    for i in events:
        kb_event_del.insert(InlineKeyboardButton(text=i.title, callback_data=cb_event_del.new(event_id=i.id)))
    kb_event_del.row(btn_back)
    await call.message.edit_text('Выберите событие для удаления:', reply_markup=kb_event_del)
    await call.answer()


@dp.callback_query_handler(cb_event_del.filter())
async def del_event(call: types.CallbackQuery, callback_data: dict):
    title_event = session.query(Event.title).filter(Event.id == callback_data['event_id']).first()[0]
    session.query(Event).filter(Event.id == callback_data['event_id']).delete()
    session.commit()
    kb_events = InlineKeyboardMarkup(row_width=3)
    events = session.query(Event).filter(Event.user_id == call.from_user.id).order_by(Event.id).all()
    for i in events:
        kb_events.insert(InlineKeyboardButton(text=i.title, callback_data=cb_event.new(event_id=i.id)))
    kb_events.row(btn_new_event, btn_del_event)
    mes = emojize(f"Событие <b>{title_event}</b> удалено! Выберите событие или создайте новое.")
    await call.message.edit_text(mes, parse_mode=types.ParseMode.HTML, reply_markup=kb_events)
    await call.answer()


@dp.callback_query_handler(text='back')
async def back(call: types.CallbackQuery):
    kb_events = InlineKeyboardMarkup(row_width=3)
    events = session.query(Event).filter(Event.user_id == call.from_user.id).order_by(Event.id).all()
    for i in events:
        kb_events.insert(InlineKeyboardButton(text=i.title, callback_data=cb_event.new(event_id=i.id)))
    kb_events.row(btn_new_event, btn_del_event)
    mes = emojize(f"Выберите событие или создайте новое.")
    await call.message.edit_text(mes, parse_mode=types.ParseMode.HTML, reply_markup=kb_events)
    await call.answer()


@dp.callback_query_handler(text='back_to_event')
async def back_to_event(call: types.CallbackQuery):
    mes = emojize(f'Выбрано событие - <b>{await get_current_event_title(call.from_user.id)}</b>')
    await call.message.edit_text(mes, reply_markup=kb_current_event)
    await call.answer()


@dp.callback_query_handler(cb_event.filter())
async def del_event(call: types.CallbackQuery, callback_data: dict):
    session.query(Event).filter(Event.user_id == call.from_user.id).update({'current_event': False}, synchronize_session='fetch')
    session.query(Event).filter(Event.id == callback_data['event_id']).update({'current_event': True}, synchronize_session='fetch')
    session.commit()
    mes = emojize(f'Выбрано событие - <b>{await get_current_event_title(call.from_user.id)}</b>')
    await call.message.edit_text(mes, reply_markup=kb_current_event)
    await call.answer()





# @dp.message_handler(content_types=['photo'])
# async def photo_handler(msg: types.Message):
#     file_id = msg.photo[-1].file_id
#     print(file_id)
#     file = await bot.get_file(file_id)
#     file_path = file.file_path
#     print(file_path)
#     await bot.send_photo(msg.from_user.id, file_id)



async def shutdown(dispatcher: Dispatcher):
    await dispatcher.storage.close()
    await dispatcher.storage.wait_closed()


if __name__ == '__main__':
    executor.start_polling(dp, on_shutdown=shutdown)