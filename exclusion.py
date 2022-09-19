from config import *
from button import *
from func import *


@dp.callback_query_handler(text='add_exclusion')
@logger.catch
async def choose_part_to_excl(call: types.CallbackQuery):
    logger.info(f'User "{call.from_user.id} - {call.from_user.username}" PUSH "add_exclusion"')
    kb_part_excl = InlineKeyboardMarkup(row_width=1)
    current_event = await get_current_event(call.from_user.id)
    for i in current_event.participants:
        kb_part_excl.insert(InlineKeyboardButton(text=i.name, callback_data=cb_part_excl.new(part_id=i.id)))
    kb_part_excl.row(btn_back_exclusion)
    await call.message.edit_text('Выберите участника для исключения:', reply_markup=kb_part_excl)
    await call.answer()


@dp.callback_query_handler(cb_part_excl.filter())
@logger.catch
async def choose_exp_to_excl(call: types.CallbackQuery, callback_data: dict):
    logger.info(f'User "{call.from_user.id} - {call.from_user.username}" CHOOSE PART')
    rnd_expense = session.query(Expense.id).filter(Expense.event_id == await get_current_event_id(call.from_user.id)).first()[0]
    new_exclusion = Exclusion(participant_id=callback_data['part_id'], expense_id=rnd_expense,
                          event_id=await get_current_event_id(call.from_user.id), date=datetime.today())
    session.add(new_exclusion)
    session.commit()
    name_excl = session.query(Participant.name).filter(Participant.id == callback_data['part_id']).first()[0]
    kb_exp_excl = InlineKeyboardMarkup(row_width=1)
    current_event = await get_current_event(call.from_user.id)
    for i in current_event.expenses:
        text_button = emojize(f':bust_in_silhouette:{i.participant.name} :moneybag:{i.title} - {str(i.price)}', language='alias')
        kb_exp_excl.insert(InlineKeyboardButton(text=text_button, callback_data=cb_exp_excl.new(exp_id=i.id)))
    await call.message.edit_text(emojize(f'Выберите трату-исключение для :bust_in_silhouette:<b>{name_excl}</b>:', language='alias'),
                                 reply_markup=kb_exp_excl)
    await call.answer()


@dp.callback_query_handler(cb_exp_excl.filter())
@logger.catch
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
        logger.error(f'User "{call.from_user.id} - {call.from_user.username}" PART HAVE THIS EXCL')
        mes = emojize('Данное исключение уже существует.', language='alias')
    elif session.query(Exclusion).filter(Exclusion.expense_id == callback_data['exp_id']).count() == \
        session.query(Participant).filter(Participant.event_id == await get_current_event_id(call.from_user.id)).count():
        session.query(Exclusion).filter(Exclusion.id == cur_excl.id).delete()
        session.commit()
        logger.error(f'User "{call.from_user.id} - {call.from_user.username}" ALL PART HAVE EXCL')
        mes = emojize('Исключение не может быть добавлено для всех участников.', language='alias')
    else:
        excl = session.query(Exclusion).filter(Exclusion.id == cur_excl.id).first()
        mes = emojize(f'Для :bust_in_silhouette:<b>{excl.participant.name}</b> \nдобавлено исключение '
                      f'\n:no_entry_sign:<s>{excl.expense.title} (<em>{excl.expense.price}</em>)</s>', language='alias')
    await call.message.edit_text(mes, reply_markup=kb_exclusion)
    await call.answer()
    logger.success(f'User "{call.from_user.id} - {call.from_user.username}" ADD EXCL')



@dp.callback_query_handler(text='exclusions')
@logger.catch
async def show_exclusions(call: types.CallbackQuery):
    logger.info(f'User "{call.from_user.id} - {call.from_user.username}" PUSH "exclusions"')
    mes = emojize(f'Исключения:no_entry_sign: события <b>{await get_current_event_title(call.from_user.id)}</b>:', language='alias')
    current_event = await get_current_event(call.from_user.id)
    for i in current_event.participants:
        if len(i.exclusions) > 0:
            mes += emojize(f'\n\n<u>:bust_in_silhouette:<b>{i.name}</b></u>', language='alias')
            for j in i.exclusions:
                mes += emojize(f'\n:no_entry_sign: <s>{j.expense.title} (<em>{str(j.expense.price)}</em>)</s>', language='alias')
    await call.message.edit_text(mes, reply_markup=kb_exclusion)
    await call.answer()


@dp.callback_query_handler(text='del_exclusion')
@logger.catch
async def choose_part_exclusion_for_del(call: types.CallbackQuery):
    logger.info(f'User "{call.from_user.id} - {call.from_user.username}" PUSH "del_exclusion"')
    current_event = await get_current_event(call.from_user.id)
    kb_part_excl_del = InlineKeyboardMarkup(row_width=1)
    for i in current_event.participants:
        if len(i.exclusions) > 0:
            text_button = emojize(f':bust_in_silhouette:{i.name}')
            kb_part_excl_del.insert(InlineKeyboardButton(text=text_button, callback_data=cb_part_excl_del.new(part_id=i.id)))
    kb_part_excl_del.row(btn_back_exclusion)
    await call.message.edit_text('Выберите участника для удаления исключения:', reply_markup=kb_part_excl_del)
    await call.answer()


@dp.callback_query_handler(cb_part_excl_del.filter())
@logger.catch
async def choose_exclusion_for_del(call: types.CallbackQuery, callback_data: dict):
    logger.info(f'User "{call.from_user.id} - {call.from_user.username}" CHOOSE PART')
    part_exclusions = session.query(Exclusion).filter(Exclusion.participant_id == callback_data['part_id']).all()
    kb_excl_del = InlineKeyboardMarkup(row_width=1)
    for i in part_exclusions:
        text_button = emojize(f':bust_in_silhouette:{i.participant.name} :no_entry_sign:{i.expense.title} - {str(i.expense.price)}', language='alias')
        kb_excl_del.insert(InlineKeyboardButton(text=text_button, callback_data=cb_excl_del.new(excl_id=i.id)))
    kb_excl_del.row(btn_back_exclusion)
    await call.message.edit_text(f'Выберите исключение для удаления({len(part_exclusions)}):', reply_markup=kb_excl_del)
    await call.answer()


@dp.callback_query_handler(cb_excl_del.filter())
@logger.catch
async def del_exclusion(call: types.CallbackQuery, callback_data: dict):
    del_excl = session.query(Exclusion).filter(Exclusion.id == callback_data['excl_id']).first()
    name, title, price = del_excl.participant.name, del_excl.expense.title, del_excl.expense.price
    session.query(Exclusion).filter(Exclusion.id == callback_data['excl_id']).delete()
    session.commit()
    logger.success(f'User "{call.from_user.id} - {call.from_user.username}" DEL EXCL')
    mes = emojize(f'Исключение \n:no_entry_sign:<s>{title} (<em>{str(price)}</em>)</s> \nучастника:bust_in_silhouette:<b>{name}</b> \nудалено.', language='alias')
    await call.message.edit_text(mes, reply_markup=kb_exclusion)
    await call.answer()


@dp.callback_query_handler(text='add_except')
@logger.catch
async def choose_part_to_except(call: types.CallbackQuery):
    logger.info(f'User "{call.from_user.id} - {call.from_user.username}" PUSH "add_except"')
    kb_part_excl = InlineKeyboardMarkup(row_width=1)
    current_event = await get_current_event(call.from_user.id)
    for i in current_event.participants:
        kb_part_excl.insert(InlineKeyboardButton(text=i.name, callback_data=cb_part_except.new(part_id=i.id)))
    kb_part_excl.row(btn_back_exclusion)
    await call.message.edit_text('Выберите участника для исключений "Всё, кроме":', reply_markup=kb_part_excl)
    await call.answer()


@dp.callback_query_handler(cb_part_except.filter())
@logger.catch
async def choose_exp_to_except(call: types.CallbackQuery, callback_data: dict):
    current_event = await get_current_event(call.from_user.id)
    for exp in current_event.expenses:
        if session.query(Exclusion).filter(
                Exclusion.expense_id == exp.id,
                Exclusion.participant_id == callback_data['part_id']
        ).count() == 0:
            new_exclusion = Exclusion(participant_id=callback_data['part_id'], expense_id=exp.id,
                                      event_id=current_event.id, date=datetime.today())
            session.add(new_exclusion)
    session.commit()
    logger.info(f'User "{call.from_user.id} - {call.from_user.username}" CHOOSE PART')
    part = session.query(Participant).filter(Participant.id == callback_data['part_id']).first()
    kb_exp_except = InlineKeyboardMarkup(row_width=1)
    kb_exp_except.insert(InlineKeyboardButton(emojize('Отмена:no_entry_sign::arrow_left:', language='alias'),
                                             callback_data=cb_cancel_except.new(part_id=callback_data['part_id'])))
    for excl in part.exclusions:
        text_button = emojize(f':bust_in_silhouette:{excl.expense.participant.name} :moneybag:{excl.expense.title} - {str(excl.expense.price)}',
                              language='alias')
        kb_exp_except.insert(InlineKeyboardButton(text=text_button, callback_data=cb_exp_except.new(
            exp_id=excl.expense.id, part_id=callback_data['part_id'])))
    await call.message.edit_text(emojize(f'Выберите траты, которые не будут вклюены в исключения для '
                                         f'\n:bust_in_silhouette:<b>{part.name}</b>:', language='alias'),
                                 reply_markup=kb_exp_except)
    await call.answer()


@dp.callback_query_handler(cb_cancel_except.filter())
@logger.catch
async def cancel_except(call: types.CallbackQuery, callback_data: dict):
    logger.info(f'User "{call.from_user.id} - {call.from_user.username}" PUSH "cancel"')
    part = session.query(Participant).filter(Participant.id == callback_data['part_id']).first()
    for excl in part.exclusions:
        session.query(Exclusion).filter(Exclusion.id == excl.id).delete()
    session.commit()
    mes = emojize(
        f'Все исключения \nучастника:bust_in_silhouette:<b>{part.name}</b> \nудалены.',
        language='alias')
    await call.message.edit_text(mes, reply_markup=kb_exclusion)
    await call.answer()


@dp.callback_query_handler(cb_exp_except.filter())
@logger.catch
async def del_excl_except(call: types.CallbackQuery, callback_data: dict):
    session.query(Exclusion).filter(
        Exclusion.expense_id == callback_data['exp_id'],
        Exclusion.participant_id == callback_data['part_id']
    ).delete()
    session.commit()
    logger.success(f'User "{call.from_user.id} - {call.from_user.username}" ADD EXCL EXCEPT')
    part = session.query(Participant).filter(Participant.id == callback_data['part_id']).first()
    kb_exp_except = InlineKeyboardMarkup(row_width=1)
    kb_exp_except.insert(btn_done_except)
    for excl in part.exclusions:
        text_button = emojize(
            f':bust_in_silhouette:{excl.expense.participant.name} :moneybag:{excl.expense.title} - {str(excl.expense.price)}',
            language='alias')
        kb_exp_except.insert(InlineKeyboardButton(text=text_button, callback_data=cb_exp_except.new(
            exp_id=excl.expense.id, part_id=callback_data['part_id'])))
    await call.message.edit_text(
        emojize(f'Выберите траты, которые не будут вклюены в исключения для \n:bust_in_silhouette:<b>{part.name}</b>:'
                f'\nили нажмите "Готово:thumbs_up:"', language='alias'),
        reply_markup=kb_exp_except)
    await call.answer()


@dp.callback_query_handler(text='done_except')
@logger.catch
async def back_to_exclusion(call: types.CallbackQuery):
    logger.info(f'User "{call.from_user.id} - {call.from_user.username}" PUSH "done except"')
    await show_exclusions(call=call)


@dp.callback_query_handler(text='back_exclusion')
@logger.catch
async def back_to_exclusion(call: types.CallbackQuery):
    logger.info(f'User "{call.from_user.id} - {call.from_user.username}" PUSH "back_exclusion"')
    await show_exclusions(call=call)
