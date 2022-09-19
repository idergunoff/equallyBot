from config import *
from button import *
from func import *


@dp.callback_query_handler(text='add_expense')
@logger.catch
async def choose_part_to_exp(call: types.CallbackQuery):
    kb_part_exp = InlineKeyboardMarkup(row_width=1)
    current_event = await get_current_event(call.from_user.id)
    for i in current_event.participants:
        kb_part_exp.insert(InlineKeyboardButton(text=i.name, callback_data=cb_part_exp.new(part_id=i.id)))
    kb_part_exp.row(btn_back_expense)
    await call.message.edit_text('Кто платил?', reply_markup=kb_part_exp)
    logger.info(f'User "{call.from_user.id} - {call.from_user.username}" PUSH "add_expense"')
    await call.answer()


@dp.callback_query_handler(text='add_expenses')
@logger.catch
async def add_expenses(call: types.CallbackQuery):
    kb_part_exps = InlineKeyboardMarkup(row_width=1)
    current_event = await get_current_event(call.from_user.id)
    for i in current_event.participants:
        kb_part_exps.insert(InlineKeyboardButton(text=i.name, callback_data=cb_part_exps.new(part_id=i.id)))
    kb_part_exps.row(btn_back_expense)
    await call.message.edit_text('Загрузка трат списком. Кто платил?', reply_markup=kb_part_exps)
    logger.info(f'User "{call.from_user.id} - {call.from_user.username}" PUSH "add_expenses"')
    await call.answer()


@dp.callback_query_handler(cb_part_exp.filter())
@logger.catch
async def send_title_exp(call: types.CallbackQuery, callback_data: dict):
    name = session.query(Participant.name).filter(Participant.id == callback_data['part_id']).first()[0]
    new_expense = Expense(participant_id=callback_data['part_id'], event_id=await get_current_event_id(call.from_user.id), date=datetime.today())
    session.add(new_expense)
    session.commit()
    await EquallyStates.NEW_TITLE.set()
    try:
        await call.message.delete()
    except MessageCantBeDeleted:
        pass
    mes = emojize(f'Отправь название траты участника :bust_in_silhouette:<b>{name}</b>:', language='alias')
    await bot.send_message(call.from_user.id, mes)
    logger.info(f'User "{call.from_user.id}" - "{call.from_user.username}" CHOOSE PART')


@dp.callback_query_handler(cb_part_exps.filter())
@logger.catch
async def send_list_expenses(call: types.CallbackQuery, callback_data: dict):
    name = session.query(Participant.name).filter(Participant.id == callback_data['part_id']).first()[0]
    new_expense = Expense(participant_id=callback_data['part_id'], event_id=await get_current_event_id(call.from_user.id), date=datetime.today())
    session.add(new_expense)
    session.commit()
    await EquallyStates.NEW_EXPENSES.set()
    try:
        await call.message.delete()
    except MessageCantBeDeleted:
        pass
    mes = emojize(f'Отправь траты участника :bust_in_silhouette:<b>{name}</b>: списком.\nКаждую трату записывайте с новой строки, '
                  f'название траты и ее стоимость разделяйте значком - @', language='alias')
    await bot.send_message(call.from_user.id, mes)
    logger.info(f'User "{call.from_user.id}" - "{call.from_user.username}" CHOOSE PART')


@dp.message_handler(state=EquallyStates.NEW_TITLE)
@logger.catch
async def add_title_expense(msg: types.Message, state: FSMContext):
    expense_id = session.query(Expense.id).filter(Expense.event_id == await get_current_event_id(msg.from_user.id)).\
        order_by(desc(Expense.date)).first()[0]
    session.query(Expense).filter(Expense.id == expense_id).update({'title': msg.text}, synchronize_session='fetch')
    session.commit()
    await EquallyStates.NEW_PRICE.set()
    mes = emojize(f'Отправь стоимость траты <b>{msg.text}</b>:', language='alias')
    await bot.send_message(msg.from_user.id, mes)
    logger.info(f'User "{msg.from_user.id} - {msg.from_user.username}" SEND TITLE EXP')


@dp.message_handler(state=EquallyStates.NEW_PRICE)
@logger.catch
async def add_price_expense(msg: types.Message, state: FSMContext):
    await state.finish()
    expense_id = session.query(Expense.id).filter(Expense.event_id == await get_current_event_id(msg.from_user.id)).\
        order_by(desc(Expense.date)).first()[0]
    try:
        price = round(float(eval(msg.text.replace(',', '.'))), 2)
        session.query(Expense).filter(Expense.id == expense_id).update({'price': price}, synchronize_session='fetch')
        session.commit()
        expense = session.query(Expense).filter(Expense.id == expense_id).first()
        mes = emojize(f'Добавлена трата:moneybag: <b>{expense.title}</b> - <em>{str(expense.price)}</em> участника <b>{expense.participant.name}</b>', language='alias')
        logger.success(f'User "{msg.from_user.id} - {msg.from_user.username}" ADD EXPENSE')
    except (NameError, SyntaxError):
        mes = emojize(f'Внимание!!!\nОшибка добавления траты! стоимость траты должна быть числом!')
        session.query(Expense).filter(Expense.id == expense_id).delete()
        session.commit()
        logger.error(f'User "{msg.from_user.id} - {msg.from_user.username}" ERROR PRICE "{msg.text}" IN "add_expense"')
    await bot.send_message(msg.from_user.id, mes, reply_markup=kb_expense)


@dp.message_handler(state=EquallyStates.NEW_EXPENSES)
@logger.catch
async def add_title_expense(msg: types.Message, state: FSMContext):
    await state.finish()
    part_id = session.query(Expense.participant_id).filter(Expense.event_id == await get_current_event_id(msg.from_user.id)).\
        order_by(desc(Expense.date)).first()[0]
    expense_id = session.query(Expense.id).filter(Expense.event_id == await get_current_event_id(msg.from_user.id)). \
        order_by(desc(Expense.date)).first()[0]
    session.query(Expense).filter(Expense.id == expense_id).delete()
    session.commit()
    add_expense = []
    list_expenses = msg.text.split('\n')
    for i in list_expenses:
        try:
            i_exp = i.split('@')
            i_price = round(float(eval(i_exp[1].replace(',', '.'))), 2)
            new_expense = Expense(title=i_exp[0], price=i_price, participant_id=part_id,
                              event_id=await get_current_event_id(msg.from_user.id), date=datetime.today())
            session.add(new_expense)
            add_expense.append([i_exp[0], i_price])
        except IndexError:
            mes = emojize(f'Внимание!!!\nОшибка добавления траты! Название и стоимость траты должны быть разделены "@"!')
            await bot.send_message(msg.from_user.id, mes)
            logger.error(f'User "{msg.from_user.id} - {msg.from_user.username}" ERROR LIST "{i_exp}" IN "add_expenses"')
        except (NameError, SyntaxError):
            mes = emojize(f'Внимание!!!\nОшибка добавления траты! стоимость траты должна быть числом!')
            await bot.send_message(msg.from_user.id, mes)
            logger.error(f'User "{msg.from_user.id} - {msg.from_user.username}" ERROR PRICE "{i_exp[1]}" IN "add_expenses"')
    part_name = session.query(Participant.name).filter(Participant.id == part_id).first()[0]
    mes = emojize(f'<u>Добавлены траты участника <b>{part_name}</b>:</u>')
    for i in add_expense:
        mes += emojize(f'\n:moneybag: <b>{i[0]}</b> - <em>{str(i[1])}</em>', language='alias')
    await bot.send_message(msg.from_user.id, mes, reply_markup=kb_expense)
    logger.success(f'User "{msg.from_user.id} - {msg.from_user.username}" ADD {str(len(add_expense))} EXPENSES')


@dp.callback_query_handler(text='expenses')
@logger.catch
async def show_expenses(call: types.CallbackQuery):
    logger.info(f'User "{call.from_user.id} - {call.from_user.username}" PUSH "expenses"')
    mes = emojize(f'Траты:moneybag: события <b>{await get_current_event_title(call.from_user.id)}</b>:', language='alias')
    current_event = await get_current_event(call.from_user.id)
    all_sum = 0
    for i in current_event.participants:
        if len(i.expenses) > 0:
            part_sum = 0
            for j in i.expenses:
                part_sum += j.price
            mes += emojize(f'\n\n<u>:bust_in_silhouette:<b>{i.name}</b> (<em>{str(round(part_sum, 2))}</em>)</u>', language='alias')
            all_sum += part_sum
            for j in i.expenses:
                mes += emojize(f'\n:moneybag: {j.title} - <em>{str(j.price)}</em>', language='alias')
    mes += emojize(f'\n\nОбщая сумма трат:moneybag: - <em>{str(round(all_sum, 2))}</em>', language='alias')
    await call.message.edit_text(mes, reply_markup=kb_expense)
    await call.answer()


@dp.callback_query_handler(text='del_expense')
@logger.catch
async def choose_expenses_for_del(call: types.CallbackQuery):
    logger.info(f'User "{call.from_user.id} - {call.from_user.username}" PUSH "del_expenses"')
    current_event = await get_current_event(call.from_user.id)
    current_event = await get_current_event(call.from_user.id)
    current_event = await get_current_event(call.from_user.id)
    kb_exp_del = InlineKeyboardMarkup(row_width=1)
    for i in current_event.expenses:
        text_button = emojize(f':bust_in_silhouette:{i.participant.name} :moneybag:{i.title} - {str(i.price)}', language='alias')
        kb_exp_del.insert(InlineKeyboardButton(text=text_button, callback_data=cb_exp_del.new(exp_id=i.id)))
    kb_exp_del.row(btn_back_expense)
    await call.message.edit_text('Выберите трату для удаления:', reply_markup=kb_exp_del)
    await call.answer()


@dp.callback_query_handler(cb_exp_del.filter())
@logger.catch
async def del_expense(call: types.CallbackQuery, callback_data: dict):
    del_expense = session.query(Expense).filter(Expense.id == callback_data['exp_id']).first()
    name, title, price = del_expense.participant.name, del_expense.title, del_expense.price
    session.query(Expense).filter(Expense.id == callback_data['exp_id']).delete()
    session.commit()
    logger.success(f'User "{call.from_user.id} - {call.from_user.username}" DEL EXP')
    mes = emojize(f'Трата участника :bust_in_silhouette:<b>{name}</b> :moneybag:<u>{title}</u> (<em>{str(price)}</em>) удалена.', language='alias')
    await call.message.edit_text(mes, reply_markup=kb_expense)
    await call.answer()


@dp.callback_query_handler(text='back_expense')
async def back_to_expense(call: types.CallbackQuery):
    await show_expenses(call=call)
