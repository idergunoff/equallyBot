from config import *
from button import *
from func import *


@dp.callback_query_handler(text='add_expense')
async def choose_part_to_exp(call: types.CallbackQuery):
    kb_part_exp = InlineKeyboardMarkup(row_width=1)
    current_event = await get_current_event(call.from_user.id)
    for i in current_event.participants:
        kb_part_exp.insert(InlineKeyboardButton(text=i.name, callback_data=cb_part_exp.new(part_id=i.id)))
    kb_part_exp.row(btn_back_to_event)
    await call.message.edit_text('Кто платил?', reply_markup=kb_part_exp)
    await call.answer()


@dp.callback_query_handler(cb_part_exp.filter())
async def send_title_exp(call: types.CallbackQuery, callback_data: dict):
    new_expense = Expense(participant_id=callback_data['part_id'], event_id=await get_current_event_id(call.from_user.id), date=datetime.today())
    session.add(new_expense)
    session.commit()
    await EquallyStates.NEW_TITLE.set()
    await call.message.delete()
    mes = emojize('Отправь название траты:')
    await bot.send_message(call.from_user.id, mes)


@dp.message_handler(state=EquallyStates.NEW_TITLE)
async def add_title_expense(msg: types.Message, state: FSMContext):
    expense_id = session.query(Expense.id).filter(Expense.event_id == await get_current_event_id(msg.from_user.id)).\
        order_by(desc(Expense.date)).first()[0]
    session.query(Expense).filter(Expense.id == expense_id).update({'title': msg.text}, synchronize_session='fetch')
    session.commit()
    await EquallyStates.NEW_PRICE.set()
    mes = emojize(f'Отправь стоимость траты <b>{msg.text}</b>:')
    await bot.send_message(msg.from_user.id, mes)


@dp.message_handler(state=EquallyStates.NEW_PRICE)
async def add_price_expense(msg: types.Message, state: FSMContext):
    await state.finish()
    expense_id = session.query(Expense.id).filter(Expense.event_id == await get_current_event_id(msg.from_user.id)).\
        order_by(desc(Expense.date)).first()[0]
    price = float(msg.text.replace(',', '.', 1))
    session.query(Expense).filter(Expense.id == expense_id).update({'price': price}, synchronize_session='fetch')
    session.commit()
    expense = session.query(Expense).filter(Expense.id == expense_id).first()
    mes = emojize(f'Добавлена трата:moneybag: <b>{expense.title}</b> - <em>{str(expense.price)}</em> участника <b>{expense.participant.name}</b>')
    await bot.send_message(msg.from_user.id, mes, reply_markup=kb_current_event)


@dp.callback_query_handler(text='expenses')
async def show_expenses(call: types.CallbackQuery):
    mes = emojize(f'Траты:moneybag: события <b>{await get_current_event_title(call.from_user.id)}</b>:')
    current_event = await get_current_event(call.from_user.id)
    all_sum = 0
    for i in current_event.participants:
        if len(i.expenses) > 0:
            part_sum = 0
            for j in i.expenses:
                part_sum += j.price
            mes += emojize(f'\n\n<u>:bust_in_silhouette:<b>{i.name}</b> (<em>{str(round(part_sum, 2))}</em>)</u>')
            all_sum += part_sum
            for j in i.expenses:
                mes += emojize(f'\n:moneybag: {j.title} - <em>{str(j.price)}</em>')
    mes += emojize(f'\n\nОбщая сумма трат:moneybag: - <em>{str(round(all_sum, 2))}</em>')
    await call.message.edit_text(mes, reply_markup=kb_current_event)
    await call.answer()


@dp.callback_query_handler(text='del_expense')
async def choose_expenses_for_del(call: types.CallbackQuery):
    current_event = await get_current_event(call.from_user.id)
    kb_exp_del = InlineKeyboardMarkup(row_width=1)
    for i in current_event.expenses:
        text_button = emojize(f':bust_in_silhouette:{i.participant.name} :moneybag:{i.title} - {str(i.price)}')
        kb_exp_del.insert(InlineKeyboardButton(text=text_button, callback_data=cb_exp_del.new(exp_id=i.id)))
    kb_exp_del.row(btn_back_to_event)
    await call.message.edit_text('Выберите трату для удаления:', reply_markup=kb_exp_del)
    await call.answer()


@dp.callback_query_handler(cb_exp_del.filter())
async def del_expense(call: types.CallbackQuery, callback_data: dict):
    del_expense = session.query(Expense).filter(Expense.id == callback_data['exp_id']).first()
    name, title, price = del_expense.participant.name, del_expense.title, del_expense.price
    session.query(Expense).filter(Expense.id == callback_data['exp_id']).delete()
    session.commit()
    mes = emojize(f'Трата участника :bust_in_silhouette:<b>{name}</b> :moneybag:<u>{title}</u> (<em>{str(price)}</em>) удалена.')
    await call.message.edit_text(mes, reply_markup=kb_current_event)
    await call.answer()