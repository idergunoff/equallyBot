from config import *
from button import *
from func import *


text_help_start = emojize('Бот Equally помогает правильно разделить расходы')
text_help_part = emojize('Добавление/удаление участников')
text_help_expense = emojize('Добавление/удаление трат')
text_help_exclusion = emojize('Добавление/удаление исключений')



@dp.message_handler(commands=['help'])
@logger.catch
async def help_start(msg: types.Message):
    await bot.send_message(msg.from_user.id, text_help_start, reply_markup=kb_help)
    logger.info(f'Push "/help" - user "{msg.from_user.id} - {msg.from_user.username}"')


@dp.callback_query_handler(text='help_part')
@logger.catch
async def help_part(call: types.CallbackQuery):
    await call.message.edit_text(text_help_part, reply_markup=kb_help)
    await call.answer()
    logger.info(f'User "{call.from_user.id} - {call.from_user.username}" PUSH "help_part"')


@dp.callback_query_handler(text='help_expense')
@logger.catch
async def help_expense(call: types.CallbackQuery):
    await call.message.edit_text(text_help_expense, reply_markup=kb_help)
    await call.answer()
    logger.info(f'User "{call.from_user.id} - {call.from_user.username}" PUSH "help_expense"')


@dp.callback_query_handler(text='help_exclusion')
@logger.catch
async def help_exclusion(call: types.CallbackQuery):
    await call.message.edit_text(text_help_exclusion, reply_markup=kb_help)
    await call.answer()
    logger.info(f'User "{call.from_user.id} - {call.from_user.username}" PUSH "help_exclusion"')


@dp.callback_query_handler(text='help_about')
@logger.catch
async def help_about(call: types.CallbackQuery):
    await call.message.edit_text(text_help_start, reply_markup=kb_help)
    await call.answer()
    logger.info(f'User "{call.from_user.id} - {call.from_user.username}" PUSH "help_about"')


@dp.callback_query_handler(text='help_back')
@logger.catch
async def help_back(call: types.CallbackQuery):
    kb_events = InlineKeyboardMarkup(row_width=3)
    events = session.query(Event).filter(Event.user_id == call.from_user.id).order_by(Event.id).all()
    for i in events:
        kb_events.insert(InlineKeyboardButton(text=i.title, callback_data=cb_event.new(event_id=i.id)))
    kb_events.row(btn_new_event, btn_del_event)
    mes = emojize(str(call.from_user.first_name) + ", добро пожаловать в EquallyBot! Выберите событие или создайте новое.", language='alias')
    await call.message.edit_text(mes, reply_markup=kb_events)
    await call.answer()
    logger.info(f'User "{call.from_user.id} - {call.from_user.username}" PUSH "help_back"')




