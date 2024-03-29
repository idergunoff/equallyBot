from aiogram.utils import executor

from participant import *
from expense import *
from exclusion import *
from help import *


# todo: донат

@dp.message_handler(commands=['start'])
@logger.catch
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
        logger.success(f'Add new user - {user_name}; {msg.from_user.id}')
    kb_events = InlineKeyboardMarkup(row_width=3)
    events = session.query(Event).filter(Event.user_id == msg.from_user.id).order_by(Event.id).all()
    for i in events:
        kb_events.insert(InlineKeyboardButton(text=i.title, callback_data=cb_event.new(event_id=i.id)))
    kb_events.row(btn_new_event, btn_del_event)
    mes = emojize(str(msg.from_user.first_name) + ", добро пожаловать в EquallyBot! Выберите событие или создайте новое.", language='alias')
    await bot.send_message(msg.from_user.id, mes, reply_markup=kb_events)
    logger.info(f'Push "/start" - user "{msg.from_user.id} - {msg.from_user.username}"')


@dp.callback_query_handler(text='new_event')
@logger.catch
async def new_event(call: types.CallbackQuery):
    await EquallyStates.NEW_EVENT.set()
    mes = emojize('Отправь название события. Не больше 25 символов.', language='alias')
    await bot.send_message(call.from_user.id, mes)
    logger.info(f'User "{call.from_user.id} - {call.from_user.username}" push "NEW EVENT"')


@dp.message_handler(state=EquallyStates.NEW_EVENT)
@logger.catch
async def add_event(msg: types.Message, state: FSMContext):
    check_title = session.query(Event).filter(Event.title == msg.text, Event.user_id == msg.from_user.id).count()
    if check_title > 0 or len(msg.text) > 25:
        mes = f'Событие <b>{msg.text}</b> у вас уже существует или название слишком длинное. Отправь другое название.'
        await bot.send_message(msg.from_user.id, mes, parse_mode=types.ParseMode.HTML)
        logger.info(f'User "{msg.from_user.id} - {msg.from_user.username}" !!!error-name')
    else:
        await state.finish()
        session.query(Event).filter(Event.user_id == msg.from_user.id).update({'current_event': False}, synchronize_session='fetch')
        new_user_event = Event(title=msg.text, user_id=msg.from_user.id)
        session.add(new_user_event)
        session.commit()
        logger.success(f'User "{msg.from_user.id} - {msg.from_user.username}" add new event "{msg.text}"')
        mes = emojize(f'Вы добвили событие - <b>{msg.text}</b> .', language='alias')
        await bot.send_message(msg.from_user.id, mes, parse_mode=types.ParseMode.HTML)
        await start(msg=msg)


@dp.callback_query_handler(text='del_event')
@logger.catch
async def choose_event_for_del(call: types.CallbackQuery):
    kb_event_del = InlineKeyboardMarkup(row_width=3)
    events = session.query(Event).filter(Event.user_id == call.from_user.id).order_by(Event.id).all()
    for i in events:
        kb_event_del.insert(InlineKeyboardButton(text=i.title, callback_data=cb_event_del.new(event_id=i.id)))
    kb_event_del.row(btn_back)
    await call.message.edit_text('Выберите событие для удаления:', reply_markup=kb_event_del)
    logger.info(f'User "{call.from_user.id} - {call.from_user.username}" push "DEL EVENT"')
    await call.answer()


@dp.callback_query_handler(cb_event_del.filter())
@logger.catch
async def del_event(call: types.CallbackQuery, callback_data: dict):
    title_event = session.query(Event.title).filter(Event.id == callback_data['event_id']).first()[0]
    session.query(Exclusion).filter(Exclusion.event_id == callback_data['event_id']).delete()
    session.query(Expense).filter(Expense.event_id == callback_data['event_id']).delete()
    session.query(Participant).filter(Participant.event_id == callback_data['event_id']).delete()
    session.query(Event).filter(Event.id == callback_data['event_id']).delete()
    session.commit()
    logger.success(f'User "{call.from_user.id} - {call.from_user.username}" delete event "{title_event}"')
    kb_events = InlineKeyboardMarkup(row_width=3)
    events = session.query(Event).filter(Event.user_id == call.from_user.id).order_by(Event.id).all()
    for i in events:
        kb_events.insert(InlineKeyboardButton(text=i.title, callback_data=cb_event.new(event_id=i.id)))
    kb_events.row(btn_new_event, btn_del_event)
    mes = emojize(f"Событие <b>{title_event}</b> удалено! Выберите событие или создайте новое.", language='alias')
    await call.message.edit_text(mes, parse_mode=types.ParseMode.HTML, reply_markup=kb_events)
    await call.answer()


@dp.callback_query_handler(text='back')
@logger.catch
async def back(call: types.CallbackQuery):
    logger.info(f'User "{call.from_user.id} - {call.from_user.username}" PUSH "back"')
    kb_events = InlineKeyboardMarkup(row_width=3)
    events = session.query(Event).filter(Event.user_id == call.from_user.id).order_by(Event.id).all()
    for i in events:
        kb_events.insert(InlineKeyboardButton(text=i.title, callback_data=cb_event.new(event_id=i.id)))
    kb_events.row(btn_new_event, btn_del_event)
    mes = emojize(f"Выберите событие или создайте новое.", language='alias')
    await call.message.edit_text(mes, parse_mode=types.ParseMode.HTML, reply_markup=kb_events)
    await call.answer()


@dp.callback_query_handler(text='back_to_event')
@logger.catch
async def back_to_event(call: types.CallbackQuery):
    logger.info(f'User "{call.from_user.id} - {call.from_user.username}" PUSH "back_to_event"')
    mes = emojize(f'Выбрано событие - <b>{await get_current_event_title(call.from_user.id)}</b>', language='alias')
    await call.message.edit_text(mes, reply_markup=kb_current_event)
    await call.answer()


@dp.callback_query_handler(cb_event.filter())
@logger.catch
async def del_event(call: types.CallbackQuery, callback_data: dict):
    session.query(Event).filter(Event.user_id == call.from_user.id).update({'current_event': False}, synchronize_session='fetch')
    session.query(Event).filter(Event.id == callback_data['event_id']).update({'current_event': True}, synchronize_session='fetch')
    session.commit()
    mes = emojize(f'Выбрано событие - <b>{await get_current_event_title(call.from_user.id)}</b>', language='alias')
    await call.message.edit_text(mes, reply_markup=kb_current_event)
    await call.answer()


@dp.callback_query_handler(text='report')
@logger.catch
async def report(call: types.CallbackQuery):
    logger.info(f'User "{call.from_user.id} - {call.from_user.username}" push "REPORT"')
    mes = emojize(':receipt:<u><b>Отчёт:</b></u>', language='alias')
    current_event = await get_current_event(call.from_user.id)
    spent, debt = dict(), dict()
    for i in current_event.participants:
        spent[i.name], debt[i.name] = 0, 0
    for i in current_event.expenses:
        spent[i.participant.name] += i.price
        count_part = len(current_event.participants) - len(i.exclusions)
        excl_names = [k.participant.name for k in i.exclusions]
        for j in current_event.participants:
            if j.name not in excl_names:
                debt[j.name] = round((debt[j.name] + i.price / count_part), 2)
    for name in debt:
        session.query(Participant).filter(Participant.event_id == current_event.id, Participant.name == name).\
            update({'spent': round(spent[name], 2), 'debt': round(debt[name], 2)}, synchronize_session='fetch')
        if spent[name] > 0:
            diff = round((spent[name] - debt[name]), 2)
            if diff > 0:
                spent[name], debt[name] = diff, 0
            else:
                spent[name], debt[name] = 0, abs(diff)
    session.commit()
    sum_expenses = 0
    for i in session.query(Participant.spent).filter(Participant.event_id == current_event.id).all():
        sum_expenses += i[0]
    mes += emojize(f'\n:moneybag:Общая сумма: <em>{str(round(sum_expenses, 2))}</em>', language='alias')
    for name in debt:
        part = session.query(Participant).filter(Participant.event_id == current_event.id, Participant.name == name).first()
        mes += emojize(f'\n\n<u>:bust_in_silhouette:<b>{name}</b></u>', language='alias')
        mes += emojize(f'\n:moneybag:Потратил: {str(part.spent)}\n:pinched_fingers:Доля трат: {str(part.debt)}', language='alias')
        if len(part.exclusions) > 0:
            mes += emojize('\n:no_entry_sign:<b><u>Исключения</u></b>:no_entry_sign:', language='alias')
            if len(part.exclusions) > len(current_event.expenses) / 2:
                mes += emojize('\n:no_entry_sign:<b><s>Всё</s></b> кроме:', language='alias')
                list_exp_id = []
                for excl in part.exclusions:
                    list_exp_id.append(excl.expense.id)
                for exp in current_event.expenses:
                    if exp.id not in list_exp_id:
                        mes += emojize(f'\n:moneybag: {exp.title} - <em>{str(exp.price)}</em>', language='alias')
            else:
                for i in part.exclusions:
                    mes += emojize(f'\n:no_entry_sign:<s>{i.expense.title} (<em>{str(i.expense.price)})</em></s>', language='alias')
        mes += emojize('\n:warning:')
        if part.spent > part.debt:
            mes += emojize(f'\n{name}   :point_right:   :zero:', language='alias')
        while debt[name] >= 0.25:
            for key in debt:
                if spent[key] > 0:
                    diff = round((spent[key] - debt[name]), 2)
                    if diff > 0:
                        mes += emojize(f'\n{name}   :point_right:   {key}   <b>{str(debt[name])}</b>:money_with_wings:', language='alias')
                        spent[key], debt[name] = diff, 0
                    else:
                        mes += emojize(f'\n{name}   :point_right:   {key}   <b>{str(spent[key])}</b>:money_with_wings:', language='alias')
                        spent[key], debt[name] = 0, abs(diff)
                    break
    mes += emojize('\n\nПосчитано с помощью @EquallyBot')
    await call.message.edit_text(mes, reply_markup=kb_current_event)
    logger.success(f'User "{call.from_user.id} - {call.from_user.username}" calculate report "{current_event.title} - {current_event.id}"')
    await call.answer()




async def shutdown(dispatcher: Dispatcher):
    await dispatcher.storage.close()
    await dispatcher.storage.wait_closed()


if __name__ == '__main__':
    executor.start_polling(dp, on_shutdown=shutdown)


