from config import *
from button import *
from func import *


@dp.callback_query_handler(text='add_exclusion')
async def choose_part_to_excl(call: types.CallbackQuery):
    kb_part_excl = InlineKeyboardMarkup(row_width=1)
    current_event = await get_current_event(call.from_user.id)
    for i in current_event.participants:
        kb_part_excl.insert(InlineKeyboardButton(text=i.name, callback_data=cb_part_excl.new(part_id=i.id)))
    kb_part_excl.row(btn_back_to_event)
    await call.message.edit_text('Выберите участника для исключения:', reply_markup=kb_part_excl)
    await call.answer()


@dp.callback_query_handler(cb_part_excl.filter())
async def choose_exp_to_excl(call: types.CallbackQuery, callback_data: dict):
    rnd_expense = session.query(Expense.id).filter(Expense.event_id == await get_current_event_id(call.from_user.id)).first()[0]
    new_exclusion = Exclusion(participant_id=callback_data['part_id'], expense_id=rnd_expense,
                          event_id=await get_current_event_id(call.from_user.id), date=datetime.today())
    session.add(new_exclusion)
    session.commit()
    name_excl = session.query(Participant.name).filter(Participant.id == callback_data['part_id']).first()[0]
    kb_exp_excl = InlineKeyboardMarkup(row_width=1)
    current_event = await get_current_event(call.from_user.id)
    for i in current_event.expenses:
        text_button = emojize(f':bust_in_silhouette:{i.participant.name} :moneybag:{i.title} - {str(i.price)}')
        kb_exp_excl.insert(InlineKeyboardButton(text=text_button, callback_data=cb_exp_excl.new(exp_id=i.id)))
    await call.message.edit_text(emojize(f'Выберите трату-исключение для :bust_in_silhouette:<b>{name_excl}</b>:'),
                                 reply_markup=kb_exp_excl)
    await call.answer()


@dp.callback_query_handler(cb_exp_excl.filter())
async def add_exclusion(call: types.CallbackQuery, callback_data: dict):
    cur_excl = \
    session.query(Exclusion).filter(Exclusion.event_id == await get_current_event_id(call.from_user.id)).order_by(
        desc(Exclusion.date)).first()
    session.query(Exclusion).filter(Exclusion.id == cur_excl.id).update({'expense_id': callback_data['exp_id']},
                                                                         synchronize_session='fetch')
    session.commit()
    if session.query(Exclusion).filter(Exclusion.participant_id == cur_excl.participant_id,
                                           Exclusion.expense_id == callback_data['exp_id']).count() > 1:
        session.query(Exclusion).filter(Exclusion.id == cur_excl.id).delete()
        session.commit()
        mes = emojize('Данное исключение уже существует.')
    elif session.query(Exclusion).filter(Exclusion.expense_id == callback_data['exp_id']).count() == \
        session.query(Participant).filter(Participant.event_id == await get_current_event_id(call.from_user.id)).count():
        session.query(Exclusion).filter(Exclusion.id == cur_excl.id).delete()
        session.commit()
        mes = emojize('Исключение не может быть добавлено для всех участников.')
    else:
        excl = session.query(Exclusion).filter(Exclusion.id == cur_excl.id).first()
        mes = emojize(f'Для :bust_in_silhouette:<b>{excl.participant.name}</b> \nдобавлено исключение '
                      f'\n:no_entry_sign:<s>{excl.expense.title} (<em>{excl.expense.price}</em>)</s>')
    await call.message.edit_text(mes, reply_markup=kb_current_event)
    await call.answer()



@dp.callback_query_handler(text='exclusions')
async def show_exclusions(call: types.CallbackQuery):
    mes = emojize(f'Исключения:no_entry_sign: события <b>{await get_current_event_title(call.from_user.id)}</b>:')
    current_event = await get_current_event(call.from_user.id)
    for i in current_event.participants:
        if len(i.exclusions) > 0:
            mes += emojize(f'\n\n<u>:bust_in_silhouette:<b>{i.name}</b></u>')
            for j in i.exclusions:
                mes += emojize(f'\n<s>:no_entry_sign: {j.expense.title} (<em>{str(j.expense.price)}</em>)</s>')
    await call.message.edit_text(mes, reply_markup=kb_current_event)
    await call.answer()


@dp.callback_query_handler(text='del_exclusion')
async def choose_exclusion_for_del(call: types.CallbackQuery):
    current_event = await get_current_event(call.from_user.id)
    kb_excl_del = InlineKeyboardMarkup(row_width=1)
    for i in current_event.exclusions:
        text_button = emojize(f':bust_in_silhouette:{i.participant.name} :no_entry_sign:{i.expense.title} - {str(i.expense.price)}')
        kb_excl_del.insert(InlineKeyboardButton(text=text_button, callback_data=cb_excl_del.new(excl_id=i.id)))
    kb_excl_del.row(btn_back_to_event)
    await call.message.edit_text('Выберите исключение для удаления:', reply_markup=kb_excl_del)
    await call.answer()


@dp.callback_query_handler(cb_excl_del.filter())
async def del_exclusion(call: types.CallbackQuery, callback_data: dict):
    del_excl = session.query(Exclusion).filter(Exclusion.id == callback_data['excl_id']).first()
    name, title, price = del_excl.participant.name, del_excl.expense.title, del_excl.expense.price
    session.query(Exclusion).filter(Exclusion.id == callback_data['excl_id']).delete()
    session.commit()
    mes = emojize(f'Исключение \n:no_entry_sign:<s>{title} (<em>{str(price)}</em>)</s> \nучастника:bust_in_silhouette:<b>{name}</b> \nудалено.')
    await call.message.edit_text(mes, reply_markup=kb_current_event)
    await call.answer()