from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.callback_data import CallbackData
from emoji import emojize


kb_start = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)

cb_event = CallbackData("event", "event_id")    # выбор события
cb_event_del = CallbackData("event_del", "event_id")    # выбор события для удаления
cb_participant_del = CallbackData("participant_del", "participant_id")  # участник для удаления
cb_part_exp = CallbackData("part_exp", "part_id")   # участник для траты
cb_part_exps = CallbackData("part_exps", "part_id") # участник для трат списком
cb_part_except = CallbackData("part_except", "part_id") # участник для исключения "всё кроме"
cb_exp_except = CallbackData("exp_except", "exp_id", "part_id")    # трата для исключения "всё кроме"
cb_exp_del = CallbackData('exp_del', 'exp_id')  # трата для удаления
cb_part_excl = CallbackData("part_excl", "part_id") # участник для удаления
cb_exp_excl = CallbackData("exp_excl", "exp_id")    # трата для исключения
cb_excl_del = CallbackData('excl_del', 'excl_id')   # исключение для удаления
cb_cancel_except = CallbackData('cancel_except', 'part_id') # участник для отмены исключения "всё кроме"


btn_new_event = InlineKeyboardButton(emojize('Новое событие:tada:', language='alias'), callback_data='new_event')
btn_del_event = InlineKeyboardButton(emojize('Удалить событие:wastebasket:', language='alias'), callback_data='del_event')

btn_participants = InlineKeyboardButton(emojize(':bust_in_silhouette:Участники', language='alias'), callback_data='participants')
btn_add_participant = InlineKeyboardButton(emojize(':plus::bust_in_silhouette:Добавить участника', language='alias'), callback_data='add_participant')
btn_add_participants = InlineKeyboardButton(emojize(':plus::bust_in_silhouette::bust_in_silhouette::bust_in_silhouette:Добавить списком',
                                                    language='alias'), callback_data='add_participants')
btn_del_participant = InlineKeyboardButton(emojize(':minus::bust_in_silhouette:Удалить участника', language='alias'), callback_data='del_participant')

btn_expenses = InlineKeyboardButton(emojize(':moneybag:Траты', language='alias'), callback_data='expenses')
btn_add_expense = InlineKeyboardButton(emojize(':plus::moneybag:Добавить трату', language='alias'), callback_data='add_expense')
btn_add_expenses = InlineKeyboardButton(emojize(':plus::moneybag::moneybag::moneybag:Добавить списком', language='alias'), callback_data='add_expenses')
btn_del_expense = InlineKeyboardButton(emojize(':minus::moneybag:Удалить трату', language='alias'), callback_data='del_expense')

btn_exclusions = InlineKeyboardButton(emojize(':no_entry_sign:Исключения', language='alias'), callback_data='exclusions')
btn_add_exclusion = InlineKeyboardButton(emojize(':plus::no_entry_sign:Добавить исключение', language='alias'), callback_data='add_exclusion')
btn_add_except = InlineKeyboardButton(emojize(':plus::no_entry_sign::no_entry_sign::no_entry_sign::moneybag:Добавить всё, кроме', language='alias'),
                                      callback_data='add_except')
btn_del_exclusion = InlineKeyboardButton(emojize(':minus::no_entry_sign:Удалить исключение', language='alias'), callback_data='del_exclusion')

btn_report = InlineKeyboardButton(emojize(':receipt:Отчёт', language='alias'), callback_data='report')

btn_back = InlineKeyboardButton(emojize('Назад:arrow_left:', language='alias'), callback_data='back')
btn_back_to_event = InlineKeyboardButton(emojize('Назад:arrow_left:', language='alias'), callback_data='back_to_event')
btn_back_part = InlineKeyboardButton(emojize('Назад:bust_in_silhouette::arrow_left:', language='alias'), callback_data='back_part')
btn_back_expense = InlineKeyboardButton(emojize('Назад:moneybag::arrow_left:', language='alias'), callback_data='back_expense')
btn_back_exclusion = InlineKeyboardButton(emojize('Назад:no_entry_sign::arrow_left:', language='alias'), callback_data='back_exclusion')
btn_done_except = InlineKeyboardButton(emojize('Готово!:thumbs_up:', language='alias'), callback_data='done_except')


kb_current_event = InlineKeyboardMarkup(row_width=2)
kb_current_event.add(btn_participants).add(btn_expenses).add(btn_exclusions)
kb_current_event.row(btn_report, btn_back)

kb_participant = InlineKeyboardMarkup()
kb_expense = InlineKeyboardMarkup()
kb_exclusion = InlineKeyboardMarkup()
kb_participant.add(btn_participants).add(btn_add_participant).add(btn_add_participants).add(btn_del_participant).add(btn_back_to_event)
kb_expense.add(btn_expenses).add(btn_add_expense).add(btn_add_expenses).add(btn_del_expense).add(btn_back_to_event)
kb_exclusion.add(btn_exclusions).add(btn_add_exclusion).add(btn_add_except).add(btn_del_exclusion).add(btn_back_to_event)

class EquallyStates(StatesGroup):
    NEW_EVENT = State()
    NEW_PARTICIPANT = State()
    NEW_PARTICIPANTS = State()
    NEW_TITLE = State()
    NEW_PRICE = State()
    NEW_EXPENSES = State()