from config import *
from button import *
from func import *


@dp.callback_query_handler(text='add_participant')
async def add_participant(call: types.CallbackQuery):
    await EquallyStates.NEW_PARTICIPANT.set()
    try:
        await call.message.delete()
    except MessageCantBeDeleted:
        pass
    mes = emojize(f'Отправь имя участника события <b>{await get_current_event_title(call.from_user.id)}</b>.', language='alias')
    await bot.send_message(call.from_user.id, mes)


@dp.callback_query_handler(text='add_participants')
async def add_participants(call: types.CallbackQuery):
    await EquallyStates.NEW_PARTICIPANTS.set()
    mes = emojize(f'Отправь участников события <b>{await get_current_event_title(call.from_user.id)}</b> списком, каждого с новой строки', language='alias')
    await call.message.edit_text(mes)
    await call.answer()
    
    
@dp.message_handler(state=EquallyStates.NEW_PARTICIPANTS)
async def add_participants_db(msg: types.Message, state: FSMContext):
    await state.finish()
    event_id = await get_current_event_id(msg.from_user.id)
    list_names = msg.text.split('\n')
    list_add_names, no_add_names = [], []
    for i in list_names:
        check_name = session.query(Participant).filter(Participant.name == i, Participant.event_id == event_id).count()
        if check_name > 0:
            no_add_names.append(i)
        else:
            new_participant = Participant(name=i, event_id=event_id)
            session.add(new_participant)
            list_add_names.append(i)
        session.commit()
    mes = emojize(f'<u>Список добавленных участников события - <b>{await get_current_event_title(msg.from_user.id)}</b>:</u>', language='alias')
    for i in list_add_names:
        mes += emojize(f'\n:bust_in_silhouette:{i}', language='alias')
    if len(no_add_names) > 0:
        mes += emojize(f'\n\n<u>Повторяющиеся участники:</u>')
        for i in no_add_names:
            mes += emojize(f'\n<s>:bust_in_silhouette:{i}</s>', language='alias')
    await bot.send_message(msg.from_user.id, mes, reply_markup=kb_participant)


@dp.message_handler(state=EquallyStates.NEW_PARTICIPANT)
async def add_participant_db(msg: types.Message, state: FSMContext):
    event_id = await get_current_event_id(msg.from_user.id)
    check_name = session.query(Participant).filter(Participant.name == msg.text, Participant.event_id == event_id).count()
    if check_name > 0:
        mes = f'Участник <b>{msg.text}</b> уже существует. Отправь другое имя.'
        await bot.send_message(msg.from_user.id, mes)
    else:
        await state.finish()
        new_participant = Participant(name=msg.text, event_id=event_id)
        session.add(new_participant)
        session.commit()
        mes = emojize(f'Участник <b>{msg.text}</b> добавлен.\nУчастники события - <b>{await get_current_event_title(msg.from_user.id)}</b>:', language='alias')
        current_event = await get_current_event(msg.from_user.id)
        for i in current_event.participants:
            mes += emojize(f'\n:bust_in_silhouette: <em>{i.name}</em>', language='alias')
        await bot.send_message(msg.from_user.id, mes, reply_markup=kb_participant)


@dp.callback_query_handler(text='participants')
async def show_participants(call: types.CallbackQuery):
    mes = emojize(f'Участники события - <b>{await get_current_event_title(call.from_user.id)}</b>:', language='alias')
    current_event = await get_current_event(call.from_user.id)
    for i in current_event.participants:
        mes += emojize(f'\n:bust_in_silhouette: <em>{i.name}</em>', language='alias')
    await call.message.edit_text(mes, reply_markup=kb_participant)
    await call.answer()


@dp.callback_query_handler(text='del_participant')
async def choose_participant_for_del(call: types.CallbackQuery):
    kb_participant_del = InlineKeyboardMarkup(row_width=1)
    current_event = await get_current_event(call.from_user.id)
    for i in current_event.participants:
        kb_participant_del.insert(InlineKeyboardButton(text=i.name, callback_data=cb_participant_del.new(participant_id=i.id)))
    kb_participant_del.row(btn_back_part)
    await call.message.edit_text('Выберите участника для удаления:', reply_markup=kb_participant_del)
    await call.answer()


@dp.callback_query_handler(cb_participant_del.filter())
async def del_event(call: types.CallbackQuery, callback_data: dict):
    name = session.query(Participant.name).filter(Participant.id == callback_data['participant_id']).first()[0]
    if len(session.query(Participant).filter(Participant.id == callback_data['participant_id']).first().expenses) > 0:
        mes = emojize(f'Участника :bust_in_silhouette:<b>{name}</b> нельзя удалить, сначала удалите его траты:moneybag:', language='alias')
    else:
        session.query(Exclusion).filter(Exclusion.participant_id == callback_data['participant_id']).delete()
        session.query(Participant).filter(Participant.id == callback_data['participant_id']).delete()
        session.commit()
        mes = emojize(f'Участник <b>{name}</b> удалён.', language='alias')
    mes += emojize(f'\nУчастники события - <b>{await get_current_event_title(call.from_user.id)}</b>:', language='alias')
    current_event = await get_current_event(call.from_user.id)
    for i in current_event.participants:
        mes += emojize(f'\n:bust_in_silhouette: <em>{i.name}</em>', language='alias')
    await call.message.edit_text(mes, reply_markup=kb_participant)
    await call.answer()
    
    
@dp.callback_query_handler(text='back_part')
async def back_to_part(call: types.CallbackQuery):
    await show_participants(call=call)
    
    