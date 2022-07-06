from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.callback_data import CallbackData
from emoji import emojize


kb_start = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)

cb_event = CallbackData("event", "event_id")
cb_event_del = CallbackData("event_del", "event_id")
cb_participant_del = CallbackData("participant_del", "participant_id")
cb_part_exp = CallbackData("part_exp", "part_id")
cb_part_exps = CallbackData("part_exps", "part_id")
cb_exp_del = CallbackData('exp_del', 'exp_id')
cb_part_excl = CallbackData("part_excl", "part_id")
cb_exp_excl = CallbackData("exp_excl", "exp_id")
cb_excl_del = CallbackData('excl_del', 'excl_id')

btn_new_event = InlineKeyboardButton(emojize('Новое событие:tada:', language='alias'), callback_data='new_event')
btn_del_event = InlineKeyboardButton(emojize('Удалить событие:wastebasket:', language='alias'), callback_data='del_event')

btn_participants = InlineKeyboardButton(emojize(':bust_in_silhouette:Люди', language='alias'), callback_data='participants')
btn_add_participant = InlineKeyboardButton(emojize(':plus::bust_in_silhouette:', language='alias'), callback_data='add_participant')
btn_add_participants = InlineKeyboardButton(emojize(':plus::bust_in_silhouette::bust_in_silhouette::bust_in_silhouette:',
                                                    language='alias'), callback_data='add_participants')
btn_del_participant = InlineKeyboardButton(emojize(':minus::bust_in_silhouette:', language='alias'), callback_data='del_participant')

btn_expenses = InlineKeyboardButton(emojize(':moneybag:Траты', language='alias'), callback_data='expenses')
btn_add_expense = InlineKeyboardButton(emojize(':plus::moneybag:', language='alias'), callback_data='add_expense')
btn_add_expenses = InlineKeyboardButton(emojize(':plus::moneybag::moneybag::moneybag:', language='alias'), callback_data='add_expenses')
btn_del_expense = InlineKeyboardButton(emojize(':minus::moneybag:', language='alias'), callback_data='del_expense')

btn_exclusions = InlineKeyboardButton(emojize(':no_entry_sign:Исключения', language='alias'), callback_data='exclusions')
btn_add_exclusion = InlineKeyboardButton(emojize(':plus::no_entry_sign:', language='alias'), callback_data='add_exclusion')
btn_del_exclusion = InlineKeyboardButton(emojize(':minus::no_entry_sign:', language='alias'), callback_data='del_exclusion')

btn_report = InlineKeyboardButton(emojize(':receipt:Отчёт', language='alias'), callback_data='report')

btn_back = InlineKeyboardButton(emojize('Назад:arrow_left:', language='alias'), callback_data='back')
btn_back_to_event = InlineKeyboardButton(emojize('Назад:arrow_left:', language='alias'), callback_data='back_to_event')


kb_current_event = InlineKeyboardMarkup(row_width=4)
kb_current_event.row(btn_participants, btn_add_participant, btn_add_participants, btn_del_participant)
kb_current_event.row(btn_expenses, btn_add_expense, btn_add_expenses, btn_del_expense)
kb_current_event.row(btn_exclusions, btn_add_exclusion, btn_del_exclusion)
kb_current_event.row(btn_report, btn_back)


class EquallyStates(StatesGroup):
    NEW_EVENT = State()
    NEW_PARTICIPANT = State()
    NEW_PARTICIPANTS = State()
    NEW_TITLE = State()
    NEW_PRICE = State()
    NEW_EXPENSES = State()