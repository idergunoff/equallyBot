from io import BytesIO


from aiogram.utils import executor

from participant import *
from expense import *
from exclusion import *
from fruit import *


# todo: пакетная загрузка участников и трат, кнопка назад при вводе, подпись в отчёт, донат

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
    session.query(Exclusion).filter(Exclusion.event_id == callback_data['event_id']).delete()
    session.query(Expense).filter(Expense.event_id == callback_data['event_id']).delete()
    session.query(Participant).filter(Participant.event_id == callback_data['event_id']).delete()
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


@dp.callback_query_handler(text='report')
async def report(call: types.CallbackQuery):
    mes = emojize(':receipt:<u><b>Отчёт:</b></u>')
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
    mes += emojize(f'\n:moneybag:Общая сумма: <em>{str(sum_expenses)}</em>')
    for name in debt:
        part = session.query(Participant).filter(Participant.event_id == current_event.id, Participant.name == name).first()
        mes += emojize(f'\n\n<u>:bust_in_silhouette:<b>{name}</b></u>')
        if len(part.exclusions) > 0:
            for i in part.exclusions:
                mes += emojize(f'\n:no_entry_sign:<s>{i.expense.title} (<em>{str(i.expense.price)})</em></s>')
        mes += emojize(f'\n:moneybag:Потратил: {str(part.spent)}\n:pinched_fingers:Доля трат: {str(part.debt)}')
        if part.spent > part.debt:
            mes += emojize(f'\n{name}     :point_right:     :zero:')
        while debt[name] >= 0.1:
            for key in debt:
                if spent[key] > 0:
                    diff = round((spent[key] - debt[name]), 2)
                    if diff > 0:
                        mes += emojize(f'\n{name}     :point_right:     {key}     <b>{str(debt[name])}</b>:money_with_wings:')
                        spent[key], debt[name] = diff, 0
                    else:
                        mes += emojize(f'\n{name}     :point_right:     {key}     <b>{str(spent[key])}</b>:money_with_wings:')
                        spent[key], debt[name] = 0, abs(diff)
                    break
    await call.message.edit_text(mes, reply_markup=kb_current_event)
    await call.answer()




async def shutdown(dispatcher: Dispatcher):
    await dispatcher.storage.close()
    await dispatcher.storage.wait_closed()


if __name__ == '__main__':
    executor.start_polling(dp, on_shutdown=shutdown)